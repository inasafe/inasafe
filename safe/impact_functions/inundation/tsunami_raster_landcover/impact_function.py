# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Tsunami Raster Impact on
Road

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

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
from safe.impact_functions.inundation.tsunami_raster_landcover.\
    metadata_definitions import (TsunamiRasterHazardLandCoverFunctionMetadata)
from safe.impact_functions.generic.classified_polygon_landcover.\
    impact_function import _calculate_landcover_impact
from safe.utilities.i18n import tr
from safe.gis.reclassify_gdal import reclassify_polygonize
from safe.utilities.utilities import ranges_according_thresholds
from safe.storage.vector import Vector
from safe.common.utilities import unique_filename
from safe.gis.qgis_raster_tools import align_clip_raster
from safe.gis.qgis_vector_tools import extent_to_geo_array
from safe.impact_reports.land_cover_report_mixin import LandCoverReportMixin

__author__ = 'etiennetrimaille'
__project_name__ = 'inasafe-dev'
__filename__ = 'impact_function.py'
__date__ = '11/03/16'
__copyright__ = 'etienne@kartoza.com'


class TsunamiRasterLandcoverFunction(ContinuousRHClassifiedVE):
    # noinspection PyUnresolvedReferences
    """Simple impact function for tsunami on landcover."""
    _metadata = TsunamiRasterHazardLandCoverFunctionMetadata()

    def __init__(self):
        """Constructor."""
        super(TsunamiRasterLandcoverFunction, self).__init__()

        self.hazard_classes = [
            tr('Dry Zone'),
            tr('Low Hazard Zone'),
            tr('Medium Hazard Zone'),
            tr('High Hazard Zone'),
            tr('Very High Hazard Zone'),
        ]
        # Only dry zone is not affected.
        self.affected_hazard_columns = self.hazard_classes[1:]

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: notes
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
                high_max.value, high_max.unit.abbreviation)
        ]
        # include any generic exposure specific notes from definitions
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions
        fields = fields + self.hazard_notes()
        return fields

    def run(self):
        """Run the impact function.

        :returns: A vector layer with affected areas marked.
        :type: safe_layer
        """
        hazard_layer = self.hazard.layer
        exposure = self.exposure.layer

        # Thresholds for tsunami hazard zone breakdown.
        low_max = self.parameters['low_threshold'].value
        medium_max = self.parameters['medium_threshold'].value
        high_max = self.parameters['high_threshold'].value
        ranges = ranges_according_thresholds(low_max, medium_max, high_max)

        hazard_value_to_class = {}
        for i, interval in enumerate(ranges):
            hazard_value_to_class[interval] = self.hazard_classes[i]

        # Get parameters from layer's keywords
        class_field = self.exposure.keyword('field')

        # reproject self.extent to the hazard projection
        hazard_crs = hazard_layer.crs()
        hazard_authid = hazard_crs.authid()

        if hazard_authid == 'EPSG:4326':
            viewport_extent = self.requested_extent
        else:
            geo_crs = QgsCoordinateReferenceSystem()
            geo_crs.createFromSrid(4326)
            viewport_extent = extent_to_geo_array(
                QgsRectangle(*self.requested_extent), geo_crs, hazard_crs)

        small_raster = align_clip_raster(hazard_layer, viewport_extent)

        # Create vector features from the flood raster
        hazard_class_attribute = 'hazard'
        vector_file_path = reclassify_polygonize(
            small_raster.source(), ranges, name_field=hazard_class_attribute)

        hazard = QgsVectorLayer(vector_file_path, 'tsunami', 'ogr')

        # prepare objects for re-projection of geometries
        crs_wgs84 = QgsCoordinateReferenceSystem('EPSG:4326')
        hazard_to_exposure = QgsCoordinateTransform(
            hazard.crs(), exposure.crs())
        wgs84_to_hazard = QgsCoordinateTransform(
            crs_wgs84, hazard.crs())
        wgs84_to_exposure = QgsCoordinateTransform(
            crs_wgs84, exposure.crs())

        extent = QgsRectangle(
            self.requested_extent[0], self.requested_extent[1],
            self.requested_extent[2], self.requested_extent[3])
        extent_hazard = wgs84_to_hazard.transformBoundingBox(extent)
        extent_exposure = wgs84_to_exposure.transformBoundingBox(extent)
        extent_exposure_geom = QgsGeometry.fromRect(extent_exposure)

        # make spatial index of hazard
        hazard_index = QgsSpatialIndex()
        hazard_features = {}
        for f in hazard.getFeatures(QgsFeatureRequest(extent_hazard)):
            f.geometry().transform(hazard_to_exposure)
            hazard_index.insertFeature(f)
            hazard_features[f.id()] = QgsFeature(f)

        # create impact layer
        filename = unique_filename(suffix='.shp')
        impact_fields = exposure.dataProvider().fields()
        impact_fields.append(QgsField(self.target_field, QVariant.String))
        writer = QgsVectorFileWriter(
            filename, 'utf-8', impact_fields, QGis.WKBPolygon, exposure.crs())

        # iterate over all exposure polygons and calculate the impact
        _calculate_landcover_impact(
            exposure, extent_exposure, extent_exposure_geom,
            hazard_class_attribute, hazard_features, hazard_index,
            hazard_value_to_class, impact_fields, writer)

        del writer
        impact_layer = QgsVectorLayer(filename, 'Impacted Land Cover', 'ogr')

        if impact_layer.featureCount() == 0:
            raise ZeroImpactException()

        zone_field = None
        if self.aggregator:
            zone_field = self.aggregator.exposure_aggregation_field

        impact_data = LandCoverReportMixin(
            question=self.question,
            impact_layer=impact_layer,
            target_field=self.target_field,
            ordered_columns=self.hazard_classes,
            affected_columns=self.affected_hazard_columns,
            land_cover_field=class_field,
            zone_field=zone_field
        ).generate_data()

        # Define style for the impact layer
        style_classes = [
            dict(
                label=self.hazard_classes[0] + ': 0m',
                value=self.hazard_classes[0],
                colour='#00FF00',
                border_color='#000000',
                transparency=0),
            dict(
                label=self.hazard_classes[1] + ': >0 - %.1f m' % low_max,
                value=self.hazard_classes[1],
                colour='#FFFF00',
                border_color='#000000',
                transparency=0),
            dict(
                label=self.hazard_classes[2] + ': %.1f - %.1f m' % (
                    low_max + 0.1, medium_max),
                value=self.hazard_classes[2],
                colour='#FFB700',
                border_color='#000000',
                transparency=0),
            dict(
                label=self.hazard_classes[3] + ': %.1f - %.1f m' % (
                    medium_max + 0.1, high_max),
                value=self.hazard_classes[3],
                colour='#FF6F00',
                border_color='#000000',
                transparency=0),
            dict(
                label=self.hazard_classes[4] + ' > %.1f m' % high_max,
                value=self.hazard_classes[4],
                colour='#FF0000',
                border_color='#000000',
                transparency=0),
        ]
        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        extra_keywords = {
            'map_title': self.map_title(),
            'target_field': self.target_field
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create vector layer and return
        impact_layer = Vector(
            data=impact_layer,
            name=self.map_title(),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
