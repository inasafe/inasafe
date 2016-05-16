# coding=utf-8
"""Impact of flood on roads."""
from collections import OrderedDict

from qgis.core import (
    QGis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsGeometry,
    QgsPoint,
    QgsRectangle,
    QgsSpatialIndex,
    QgsVectorFileWriter,
    QgsVectorLayer
)
from PyQt4.QtCore import QVariant

from safe.common.exceptions import ZeroImpactException
from safe.impact_functions.bases.continuous_rh_classified_ve import \
    ContinuousRHClassifiedVE
from safe.impact_functions.inundation.flood_raster_road\
    .metadata_definitions import FloodRasterRoadsMetadata
from safe.utilities.i18n import tr
from safe.utilities.gis import add_output_feature, union_geometries
from safe.utilities.utilities import reorder_dictionary, main_type
from safe.storage.vector import Vector
from safe.common.utilities import get_utm_epsg, unique_filename
from safe.common.exceptions import GetDataError
from safe.gis.qgis_raster_tools import clip_raster
from safe.gis.qgis_vector_tools import (
    extent_to_geo_array,
    create_layer)
from safe.impact_reports.road_exposure_report_mixin import\
    RoadExposureReportMixin
from safe.definitions import structure_class_order


def _raster_to_vector_cells(
        raster, minimum_threshold, maximum_threshold, output_crs):
    """Generate vectors features (rectangles) for raster cells.

     Cells which are not within threshold (threshold_min < V < threshold_max)
     will be excluded. The provided CRS will be used to determine the
     CRS of the output vector cells layer.

    :param minimum_threshold: The minimum threshold for pixels to be included.
    :type minimum_threshold: float

    :param maximum_threshold: The maximum threshold for pixels to be included.
    :type maximum_threshold: float

    :param raster: A raster layer that will be vectorised.
    :type raster: QgsRasterLayer

    :param output_crs: The CRS to use for the output vector cells layer.
    :type output_crs: QgsCoordinateReferenceSystem

    :returns: A two-tuple containing a spatial index and a map (dict) where
        map keys are feature id's and the value is the feature for that id.
    :rtype: (QgsSpatialIndex, dict)
    """

    # get raster data
    provider = raster.dataProvider()
    extent = provider.extent()
    raster_cols = provider.xSize()
    raster_rows = provider.ySize()
    block = provider.block(1, extent, raster_cols, raster_rows)
    raster_xmin = extent.xMinimum()
    raster_ymax = extent.yMaximum()
    cell_width = extent.width() / raster_cols
    cell_height = extent.height() / raster_rows

    uri = "Polygon?crs=" + output_crs.authid()
    vl = QgsVectorLayer(uri, "cells", "memory")
    features = []

    # prepare coordinate transform to reprojection
    ct = QgsCoordinateTransform(raster.crs(), output_crs)

    for y in xrange(raster_rows):
        for x in xrange(raster_cols):
            # only use cells that are within the specified threshold
            value = block.value(y, x)
            if value < minimum_threshold or value > maximum_threshold:
                continue

            # construct rectangular polygon feature for the cell
            x0 = raster_xmin + (x * cell_width)
            x1 = raster_xmin + ((x + 1) * cell_width)
            y0 = raster_ymax - (y * cell_height)
            y1 = raster_ymax - ((y + 1) * cell_height)
            outer_ring = [
                QgsPoint(x0, y0), QgsPoint(x1, y0),
                QgsPoint(x1, y1), QgsPoint(x0, y1),
                QgsPoint(x0, y0)]
            # noinspection PyCallByClass
            geometry = QgsGeometry.fromPolygon([outer_ring])
            geometry.transform(ct)
            f = QgsFeature()
            f.setGeometry(geometry)
            features.append(f)

    _, features = vl.dataProvider().addFeatures(features)

    # construct a temporary map for fast access to features by their IDs
    # (we will be getting feature IDs from spatial index)
    flood_cells_map = {}
    for f in features:
        flood_cells_map[f.id()] = f

    # build a spatial index so we can quickly identify
    # flood cells overlapping roads
    if QGis.QGIS_VERSION_INT >= 20800:
        # woohoo we can use bulk insert (much faster)
        index = QgsSpatialIndex(vl.getFeatures())
    else:
        index = QgsSpatialIndex()
        for f in vl.getFeatures():
            index.insertFeature(f)

    return index, flood_cells_map


def _intersect_lines_with_vector_cells(
        line_layer,
        request,
        index,
        flood_cells_map,
        output_layer,
        target_field):
    """
    A helper function to find all vector cells that intersect with lines.

    In typical usage, you will have a roads layer and polygon cells from
    vectorising a raster layer. The goal is to obtain a subset of cells
    which intersect with the roads. This will then be used to determine
    if any given road segment is flooded.

    :param line_layer: Vector layer with containing linear features
        such as roads.
    :type line_layer: QgsVectorLayer

    :param request: Request for fetching features from lines layer.
    :type request: QgsFeatureRequest

    :param index: Spatial index with flood features.
    :type index: QgsSpatialIndex

    :param flood_cells_map: Map from flood feature IDs to actual features.
        See :func:`_raster_to_vector_cells` for more details.
    :type flood_cells_map: dict

    :param output_layer: Layer to which features will be written.
    :type output_layer: QgsVectorLayer

    :param target_field: Name of the field in output_layer which will receive
        information whether the feature is flooded or not.
    :type target_field: basestring

    :return: None
    """

    features = []
    fields = output_layer.dataProvider().fields()

    rd = 0
    for f in line_layer.getFeatures(request):
        # query flood cells located in the area of the road and build
        # a (multi-)polygon geometry with flooded area relevant to this road
        ids = index.intersects(f.geometry().boundingBox())
        geoms = [flood_cells_map[i].geometry() for i in ids]
        flood_geom = union_geometries(geoms)

        # find out which parts of the road are flooded
        in_geom = f.geometry().intersection(flood_geom)
        if in_geom and (in_geom.wkbType() == QGis.WKBLineString or
                        in_geom.wkbType() == QGis.WKBMultiLineString):
            add_output_feature(
                features, in_geom, 1,
                fields, f.attributes(), target_field)

        # find out which parts of the road are not flooded
        out_geom = f.geometry().difference(flood_geom)
        if out_geom and (out_geom.wkbType() == QGis.WKBLineString or
                         out_geom.wkbType() == QGis.WKBMultiLineString):
            add_output_feature(
                features, out_geom, 0,
                fields, f.attributes(), target_field)

        # every once in a while commit the created features to the output layer
        rd += 1
        if rd % 1000 == 0:
            output_layer.dataProvider().addFeatures(features)
            features = []

    output_layer.dataProvider().addFeatures(features)


class FloodRasterRoadsFunction(
        ContinuousRHClassifiedVE,
        RoadExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Simple impact function for inundation for road."""
    _metadata = FloodRasterRoadsMetadata()

    def __init__(self):
        """Constructor."""
        super(FloodRasterRoadsFunction, self).__init__()
        RoadExposureReportMixin.__init__(self)

    def notes(self):
        """Return the notes section of the report.

        .. versionadded: 3.2.1

        :return: The notes that should be attached to this impact report.
        :rtype: safe.messaging.Message
        """

        title = tr('Notes and assumptions')

        threshold = self.parameters['min threshold'].value
        hazard = self.hazard.keyword('hazard')
        hazard_terminology = tr('flooded')
        hazard_object = tr('flood')
        if hazard == 'flood':
            # Use flooded
            pass
        elif hazard == 'tsunami':
            hazard_terminology = tr('inundated')
            hazard_object = tr('water')

        fields = [
            tr('Roads are %s when %s levels exceed %.2f m.' %
               (hazard_terminology, hazard_object, threshold)),
            tr('Roads are closed if they are %s.' % hazard_terminology),
            tr('Roads are open if they are not %s.' % hazard_terminology)
        ]

        return {
            'title': title,
            'fields': fields
        }

    def run(self):
        """Run the impact function.

        :returns: A new line layer with inundated roads marked.
        :type: safe_layer
        """

        target_field = self.target_field

        # Get parameters from layer's keywords
        road_class_field = self.exposure.keyword('road_class_field')
        exposure_value_mapping = self.exposure.keyword('value_mapping')

        # Get parameters from IF parameter
        threshold_min = self.parameters['min threshold'].value
        threshold_max = self.parameters['max threshold'].value

        if threshold_min > threshold_max:
            message = tr(
                'The minimal threshold is greater than the maximal specified '
                'threshold. Please check the values.')
            raise GetDataError(message)

        # reproject self.extent to the hazard projection
        hazard_crs = self.hazard.layer.crs()
        hazard_authid = hazard_crs.authid()

        if hazard_authid == 'EPSG:4326':
            viewport_extent = self.requested_extent
        else:
            geo_crs = QgsCoordinateReferenceSystem()
            geo_crs.createFromSrid(4326)
            viewport_extent = extent_to_geo_array(
                QgsRectangle(*self.requested_extent), geo_crs, hazard_crs)

        # Align raster extent and viewport
        # assuming they are both in the same projection
        raster_extent = self.hazard.layer.dataProvider().extent()
        clip_xmin = raster_extent.xMinimum()
        # clip_xmax = raster_extent.xMaximum()
        clip_ymin = raster_extent.yMinimum()
        # clip_ymax = raster_extent.yMaximum()
        if viewport_extent[0] > clip_xmin:
            clip_xmin = viewport_extent[0]
        if viewport_extent[1] > clip_ymin:
            clip_ymin = viewport_extent[1]
        # TODO: Why have these two clauses when they are not used?
        # Commenting out for now.
        # if viewport_extent[2] < clip_xmax:
        #     clip_xmax = viewport_extent[2]
        # if viewport_extent[3] < clip_ymax:
        #     clip_ymax = viewport_extent[3]

        height = ((viewport_extent[3] - viewport_extent[1]) /
                  self.hazard.layer.rasterUnitsPerPixelY())
        height = int(height)
        width = ((viewport_extent[2] - viewport_extent[0]) /
                 self.hazard.layer.rasterUnitsPerPixelX())
        width = int(width)

        raster_extent = self.hazard.layer.dataProvider().extent()
        xmin = raster_extent.xMinimum()
        xmax = raster_extent.xMaximum()
        ymin = raster_extent.yMinimum()
        ymax = raster_extent.yMaximum()

        x_delta = (xmax - xmin) / self.hazard.layer.width()
        x = xmin
        for i in range(self.hazard.layer.width()):
            if abs(x - clip_xmin) < x_delta:
                # We have found the aligned raster boundary
                break
            x += x_delta
            _ = i

        y_delta = (ymax - ymin) / self.hazard.layer.height()
        y = ymin
        for i in range(self.hazard.layer.width()):
            if abs(y - clip_ymin) < y_delta:
                # We have found the aligned raster boundary
                break
            y += y_delta
        clip_extent = [x, y, x + width * x_delta, y + height * y_delta]

        # Clip hazard raster
        small_raster = clip_raster(
            self.hazard.layer, width, height, QgsRectangle(*clip_extent))

        # Filter geometry and data using the extent
        ct = QgsCoordinateTransform(
            QgsCoordinateReferenceSystem("EPSG:4326"),
            self.exposure.layer.crs())
        extent = ct.transformBoundingBox(QgsRectangle(*self.requested_extent))
        request = QgsFeatureRequest()
        request.setFilterRect(extent)

        # create template for the output layer
        line_layer_tmp = create_layer(self.exposure.layer)
        new_field = QgsField(target_field, QVariant.Int)
        line_layer_tmp.dataProvider().addAttributes([new_field])
        line_layer_tmp.updateFields()

        # create empty output layer and load it
        filename = unique_filename(suffix='.shp')
        QgsVectorFileWriter.writeAsVectorFormat(
            line_layer_tmp, filename, "utf-8", None, "ESRI Shapefile")
        line_layer = QgsVectorLayer(filename, "flooded roads", "ogr")

        # Create vector features from the flood raster
        # For each raster cell there is one rectangular polygon
        # Data also get spatially indexed for faster operation
        index, flood_cells_map = _raster_to_vector_cells(
            small_raster,
            threshold_min,
            threshold_max,
            self.exposure.layer.crs())

        if len(flood_cells_map) == 0:
            message = tr(
                'There are no objects in the hazard layer with "value" > %s. '
                'Please check the value or use other extent.' % (
                    threshold_min, ))
            raise GetDataError(message)

        # Do the heavy work - for each road get flood polygon for that area and
        # do the intersection/difference to find out which parts are flooded
        _intersect_lines_with_vector_cells(
            self.exposure.layer,
            request,
            index,
            flood_cells_map,
            line_layer,
            target_field)

        target_field_index = line_layer.dataProvider().\
            fieldNameIndex(target_field)

        # Generate simple impact report
        epsg = get_utm_epsg(self.requested_extent[0], self.requested_extent[1])
        output_crs = QgsCoordinateReferenceSystem(epsg)
        transform = QgsCoordinateTransform(
            self.exposure.layer.crs(), output_crs)

        classes = [tr('Flooded in the threshold (m)')]
        self.init_report_var(classes)

        if line_layer.featureCount() < 1:
            raise ZeroImpactException()

        roads_data = line_layer.getFeatures()
        road_type_field_index = line_layer.fieldNameIndex(road_class_field)

        for road in roads_data:
            attributes = road.attributes()

            usage = attributes[road_type_field_index]
            usage = main_type(usage, exposure_value_mapping)

            geom = road.geometry()
            geom.transform(transform)
            length = geom.length()

            affected = False
            if attributes[target_field_index] == 1:
                affected = True

            self.classify_feature(classes[0], usage, length, affected)

        self.reorder_dictionaries()

        # For printing map purpose
        map_title = tr('Roads inundated')
        legend_title = tr('Road inundated status')

        style_classes = [
            dict(
                label=tr('Not Inundated'), value=0,
                colour='#1EFC7C', transparency=0, size=0.5),
            dict(
                label=tr('Inundated'), value=1,
                colour='#F31A1C', transparency=0, size=0.5)]
        style_info = dict(
            target_field=target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        impact_data = self.generate_data()

        extra_keywords = {
            'map_title': map_title,
            'legend_title': legend_title,
            'target_field': target_field
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Convert QgsVectorLayer to inasafe layer and return it
        impact_layer = Vector(
            data=line_layer,
            name=tr('Flooded roads'),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
