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
from safe.utilities.gis import (
    raster_to_vector_cells,
    intersect_lines_with_vector_cells)
from safe.storage.vector import Vector
from safe.common.utilities import get_utm_epsg, unique_filename
from safe.common.exceptions import GetDataError
from safe.gis.qgis_raster_tools import clip_raster
from safe.gis.qgis_vector_tools import (
    extent_to_geo_array,
    create_layer)
from safe.impact_reports.road_exposure_report_mixin import\
    RoadExposureReportMixin
import safe.messaging as m
from safe.messaging import styles


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

        message = m.Message(style_class='container')
        message.add(
            m.Heading(tr('Notes and assumptions'), **styles.INFO_STYLE))
        checklist = m.BulletedList()
        checklist.add(tr(
            'Roads are %s when %s levels exceed %.2f m.' %
            (hazard_terminology, hazard_object, threshold)))
        checklist.add(tr(
            'Roads are closed if they are %s.' % hazard_terminology))
        checklist.add(tr(
            'Roads are open if they are not %s.' % hazard_terminology))

        message.add(checklist)
        return message

    def run(self):
        """Run the impact function.

        :returns: A new line layer with inundated roads marked.
        :type: safe_layer
        """
        self.validate()
        self.prepare()

        self.provenance.append_step(
            'Calculating Step',
            'Impact function is calculating the impact.')

        target_field = self.target_field
        # Get parameters from layer's keywords
        road_class_field = self.exposure.keyword('road_class_field')
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
        ranges = OrderedDict()
        ranges[0] = [threshold_min, threshold_max]
        index, flood_cells_map = raster_to_vector_cells(
            small_raster,
            ranges,
            self.exposure.layer.crs())

        if len(flood_cells_map) == 0:
            message = tr(
                'There are no objects in the hazard layer with "value" > %s. '
                'Please check the value or use other extent.' % (
                    threshold_min, ))
            raise GetDataError(message)

        # Do the heavy work - for each road get flood polygon for that area and
        # do the intersection/difference to find out which parts are flooded
        intersect_lines_with_vector_cells(
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
        flooded_keyword = tr('Flooded in the threshold (m)')
        self.affected_road_categories = [flooded_keyword]
        self.affected_road_lengths = OrderedDict([
            (flooded_keyword, {})])
        self.road_lengths = OrderedDict()

        if line_layer.featureCount() < 1:
            raise ZeroImpactException()

        roads_data = line_layer.getFeatures()
        road_type_field_index = line_layer.fieldNameIndex(road_class_field)
        for road in roads_data:
            attributes = road.attributes()
            road_type = attributes[road_type_field_index]
            if road_type.__class__.__name__ == 'QPyNullVariant':
                road_type = tr('Other')
            geom = road.geometry()
            geom.transform(transform)
            length = geom.length()

            if road_type not in self.road_lengths:
                self.affected_road_lengths[flooded_keyword][road_type] = 0
                self.road_lengths[road_type] = 0

            self.road_lengths[road_type] += length
            if attributes[target_field_index] == 1:
                self.affected_road_lengths[
                    flooded_keyword][road_type] += length

        impact_summary = self.html_report()

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

        extra_keywords = {
            'impact_summary': impact_summary,
            'map_title': map_title,
            'legend_title': legend_title,
            'target_field': target_field
        }

        self.set_if_provenance()

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Convert QgsVectorLayer to inasafe layer and return it
        line_layer = Vector(
            data=line_layer,
            name=tr('Flooded roads'),
            keywords=impact_layer_keywords,
            style_info=style_info)
        self._impact = line_layer
        return line_layer
