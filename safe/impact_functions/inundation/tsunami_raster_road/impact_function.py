# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Tsunami Raster Impact on
Road

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from collections import OrderedDict

# Temporary hack until QGIS returns nodata values nicely
from osgeo import gdal
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
from PyQt4.QtCore import QVariant, QPyNullVariant
from safe.common.exceptions import ZeroImpactException
from safe.impact_functions.bases.continuous_rh_classified_ve import \
    ContinuousRHClassifiedVE
from safe.impact_functions.inundation.tsunami_raster_road\
    .metadata_definitions import TsunamiRasterRoadMetadata
from safe.utilities.i18n import tr
from safe.utilities.gis import add_output_feature, union_geometries
from safe.utilities.utilities import main_type, ranges_according_thresholds
from safe.storage.vector import Vector
from safe.common.utilities import get_utm_epsg, unique_filename
from safe.gis.qgis_raster_tools import align_clip_raster
from safe.gis.qgis_vector_tools import (
    extent_to_geo_array,
    create_layer)
from safe.impact_reports.road_exposure_report_mixin import\
    RoadExposureReportMixin
import logging

# Part of the temporary gdal transparency hack
# gdal.UseExceptions()

__author__ = 'etiennetrimaille'
__project_name__ = 'inasafe-dev'
__filename__ = 'impact_function.py'
__date__ = '11/03/16'
__copyright__ = 'etienne@kartoza.com'

LOGGER = logging.getLogger('InaSAFE')


def _raster_to_vector_cells(raster, ranges, output_crs):
    """Generate vectors features (rectangles) for raster cells.

     Cells which are not within one of the ranges will be excluded.
     The provided CRS will be used to determine the CRS of the output
     vector cells layer.

    :param ranges: A dictionary of ranges. The key will be the id the range.
    :type ranges: OrderedDict

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
    vl.dataProvider().addAttributes([QgsField('affected', QVariant.Int)])
    vl.updateFields()
    features = []

    # prepare coordinate transform to reprojection
    ct = QgsCoordinateTransform(raster.crs(), output_crs)
    rd = 0
    # Hack because QGIS does not return the
    # nodata value from the dataset properly in the python API
    dataset = gdal.Open(raster.source())
    no_data = dataset.GetRasterBand(1).GetNoDataValue()
    del dataset  # close the dataset
    y_cell_height = - cell_height
    LOGGER.debug('num row: %s' % raster_rows)
    LOGGER.debug('num column: %s' % raster_cols)
    for y in xrange(raster_rows):
        y_cell_height += cell_height
        y0 = raster_ymax - y_cell_height
        y1 = y0 - cell_height

        for x in xrange(raster_cols):
            # only use cells that are within the specified threshold
            value = block.value(y, x)
            current_threshold = None

            # Performance optimisation added in 3.4.1 - dont
            # waste time processing cells that have no data
            if value == no_data or value <= 0:
                continue

            for threshold_id, threshold in ranges.iteritems():

                # If, eg [0, 0], the value must be equal to 0.
                if threshold[0] == threshold[1] and threshold[0] == value:
                    current_threshold = threshold_id

                # If, eg [None, 0], the value must be less than 0.
                if threshold[0] is None and value <= threshold[1]:
                    current_threshold = threshold_id

                # If, eg [0, None], the value must be greater than 0.
                if threshold[1] is None and threshold[0] < value:
                    current_threshold = threshold_id

                # If, eg [0, 1], the value must be
                # between 0 excluded and 1 included.
                if threshold[0] < value <= threshold[1]:
                    current_threshold = threshold_id

                if current_threshold is not None:
                    # construct rectangular polygon feature for the cell
                    x_cell_width = x * cell_width
                    x0 = raster_xmin + x_cell_width
                    x1 = x0 + cell_width
                    outer_ring = [
                        QgsPoint(x0, y0), QgsPoint(x1, y0),
                        QgsPoint(x1, y1), QgsPoint(x0, y1),
                        QgsPoint(x0, y0)]
                    # noinspection PyCallByClass
                    geometry = QgsGeometry.fromPolygon([outer_ring])
                    geometry.transform(ct)
                    f = QgsFeature()
                    f.setGeometry(geometry)
                    f.setAttributes([current_threshold])
                    features.append(f)
                    break

            # every once in a while, add the created features to the output.
            rd += 1
            if rd % 1000 == 0:
                vl.dataProvider().addFeatures(features)
                features = []
    # Add the latest features
    vl.dataProvider().addFeatures(features)

    # construct a temporary map for fast access to features by their IDs
    # (we will be getting feature IDs from spatial index)
    flood_cells_map = {}
    for f in vl.getFeatures():
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
        flood_features = [flood_cells_map[i] for i in ids]

        for feature in flood_features:
            # find out which parts of the road are flooded
            in_geom = f.geometry().intersection(feature.geometry())
            if in_geom and (in_geom.wkbType() == QGis.WKBLineString or
                            in_geom.wkbType() == QGis.WKBMultiLineString):
                affected_value = feature.attributes()[0]
                if isinstance(affected_value, QPyNullVariant):
                    affected_value = 0
                add_output_feature(
                    features, in_geom, affected_value,
                    fields, f.attributes(), target_field)

        # find out which parts of the road are not flooded
        geoms = [j.geometry() for j in flood_features]
        out_geom = f.geometry().difference(union_geometries(geoms))
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

    # Add the latest features
    output_layer.dataProvider().addFeatures(features)


class TsunamiRasterRoadsFunction(
        ContinuousRHClassifiedVE,
        RoadExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Simple impact function for tsunami on roads."""
    _metadata = TsunamiRasterRoadMetadata()

    def __init__(self):
        """Constructor."""
        super(TsunamiRasterRoadsFunction, self).__init__()
        RoadExposureReportMixin.__init__(self)
        self.add_unaffected_column = False
        self.hazard_classes = [
            tr('Dry Zone'),
            tr('Low Hazard Zone'),
            tr('Medium Hazard Zone'),
            tr('High Hazard Zone'),
            tr('Very High Hazard Zone'),
        ]

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        # Thresholds for tsunami hazard zone breakdown.
        low_max = self.parameters['low_threshold']
        medium_max = self.parameters['medium_threshold']
        high_max = self.parameters['high_threshold']

        fields = [
            tr('Dry zone is defined as non-inundated area or has inundation '
               'depth is 0 %s') % low_max.unit.abbreviation,
            tr('Low tsunami hazard zone is defined as inundation depth is '
               'more than 0 %s but less than %.1f %s') % (
                low_max.unit.abbreviation,
                low_max.value,
                low_max.unit.abbreviation),
            tr('Medium tsunami hazard zone is defined as inundation depth '
               'is more than %.1f %s but less than %.1f %s') % (
                low_max.value,
                low_max.unit.abbreviation,
                medium_max.value,
                medium_max.unit.abbreviation),
            tr('High tsunami hazard zone is defined as inundation depth is '
               'more than %.1f %s but less than %.1f %s') % (
                medium_max.value,
                medium_max.unit.abbreviation,
                high_max.value,
                high_max.unit.abbreviation),
            tr('Very high tsunami hazard zone is defined as inundation depth '
               'is more than %.1f %s') % (
                high_max.value, high_max.unit.abbreviation),
            tr('Roads are closed if they are in low, medium, high, or very '
               'high tsunami hazard zone.'),
            tr('Roads are open if they are in dry zone.')
        ]
        # include any generic exposure specific notes from definitions_v3.py
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions_v3.py
        fields = fields + self.hazard_notes()
        return fields

    def run(self):
        """Run the impact function.

        :returns: A new line layer with inundated roads marked.
        :type: safe_layer
        """
        # Thresholds for tsunami hazard zone breakdown.
        low_max = self.parameters['low_threshold'].value
        medium_max = self.parameters['medium_threshold'].value
        high_max = self.parameters['high_threshold'].value

        target_field = self.target_field
        # Get parameters from layer's keywords
        road_class_field = self.exposure.keyword('road_class_field')
        exposure_value_mapping = self.exposure.keyword('value_mapping')

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

        # Clip hazard raster
        small_raster = align_clip_raster(self.hazard.layer, viewport_extent)

        # Create vector features from the flood raster
        # For each raster cell there is one rectangular polygon
        # Data also get spatially indexed for faster operation
        ranges = ranges_according_thresholds(low_max, medium_max, high_max)

        index, flood_cells_map = _raster_to_vector_cells(
            small_raster,
            ranges,
            self.exposure.layer.crs())

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

        # Roads breakdown
        self.init_report_var(self.hazard_classes)

        if line_layer.featureCount() < 1:
            raise ZeroImpactException()

        roads_data = line_layer.getFeatures()
        road_type_field_index = line_layer.fieldNameIndex(road_class_field)

        for road in roads_data:
            attributes = road.attributes()

            affected = attributes[target_field_index]
            if isinstance(affected, QPyNullVariant):
                continue
            else:
                hazard_zone = self.hazard_classes[affected]

            usage = attributes[road_type_field_index]
            usage = main_type(usage, exposure_value_mapping)

            geom = road.geometry()
            geom.transform(transform)
            length = geom.length()

            affected = False
            num_classes = len(self.hazard_classes)
            if attributes[target_field_index] in range(num_classes):
                affected = True
            self.classify_feature(hazard_zone, usage, length, affected)

        self.reorder_dictionaries()

        style_classes = [
            # FIXME 0 - 0.1
            dict(
                label=self.hazard_classes[0] + ': 0m',
                value=0,
                colour='#00FF00',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[1] + ': >0 - %.1f m' % low_max,
                value=1,
                colour='#FFFF00',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[2] + ': %.1f - %.1f m' % (
                    low_max + 0.1, medium_max),
                value=2,
                colour='#FFB700',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[3] + ': %.1f - %.1f m' % (
                    medium_max + 0.1, high_max),
                value=3,
                colour='#FF6F00',
                transparency=0,
                size=1
            ),

            dict(
                label=self.hazard_classes[4] + ' > %.1f m' % high_max,
                value=4,
                colour='#FF0000',
                transparency=0,
                size=1
            ),
        ]
        style_info = dict(
            target_field=target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        impact_data = self.generate_data()

        extra_keywords = {
            'map_title': self.map_title(),
            'legend_title': self.metadata().key('legend_title'),
            'target_field': target_field
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Convert QgsVectorLayer to inasafe layer and return it
        impact_layer = Vector(
            data=line_layer,
            name=self.map_title(),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
