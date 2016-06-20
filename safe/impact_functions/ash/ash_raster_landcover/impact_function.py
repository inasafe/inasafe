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
from safe.impact_functions.ash.ash_raster_landcover.metadata_definitions \
    import \
    AshRasterHazardLandCoverFunctionMetadata
from safe.impact_functions.bases.continuous_rh_classified_ve import \
    ContinuousRHClassifiedVE
from safe.impact_functions.generic.classified_polygon_landcover.\
    impact_function import _calculate_landcover_impact
from safe.utilities.i18n import tr
from safe.gis.reclassify_gdal import reclassify_polygonize
from safe.utilities.utilities import ranges_according_thresholds_list
from safe.storage.vector import Vector
from safe.common.utilities import unique_filename
from safe.gis.qgis_raster_tools import align_clip_raster
from safe.gis.qgis_vector_tools import extent_to_geo_array
from safe.impact_reports.land_cover_report_mixin import LandCoverReportMixin

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '5/24/16'


class AshRasterLandcoverFunction(
        ContinuousRHClassifiedVE,
        LandCoverReportMixin):
    # noinspection PyUnresolvedReferences
    """Simple impact function for ash raster on landcover."""
    _metadata = AshRasterHazardLandCoverFunctionMetadata()

    def __init__(self):
        """Constructor."""
        super(AshRasterLandcoverFunction, self).__init__()

        self.hazard_classes = [
            tr('Very Low'),
            tr('Low'),
            tr('Moderate'),
            tr('High'),
            tr('Very High'),
        ]
        self.affected_hazard_columns = self.hazard_classes

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: safe.messaging.Message
        """
        return []   # TODO: what to put here?

    def run(self):
        """Run the impact function.

        :returns: A vector layer with affected areas marked.
        :type: safe_layer
        """
        hazard_layer = self.hazard.layer
        exposure = self.exposure.layer

        # Thresholds for tsunami hazard zone breakdown.
        group_parameters = self.parameters['group_threshold']
        unit_abbrev = group_parameters.value_map['very_low_threshold'].unit.abbreviation
        unaffected_max = group_parameters.value_map['unaffected_threshold'].value
        very_low_max = group_parameters.value_map['very_low_threshold'].value
        low_max = group_parameters.value_map['low_threshold'].value
        medium_max = group_parameters.value_map['moderate_threshold'].value
        high_max = group_parameters.value_map['high_threshold'].value
        ranges = ranges_according_thresholds_list(
            [unaffected_max, very_low_max, low_max,
             medium_max, high_max, None])

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

        hazard = QgsVectorLayer(vector_file_path, 'ash vector', 'ogr')

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
                label=self.hazard_classes[0] + ': %.1f - %.1f %s' % (
                    unaffected_max, very_low_max, unit_abbrev),
                value=self.hazard_classes[0],
                colour='#2C6BA4',
                border_color='#000000',
                transparency=0),
            dict(
                label=self.hazard_classes[1] + ': %.1f - %.1f %s' % (
                    very_low_max + 0.1, low_max, unit_abbrev),
                value=self.hazard_classes[1],
                colour='#00A4D8',
                border_color='#000000',
                transparency=0),
            dict(
                label=self.hazard_classes[2] + ': %.1f - %.1f %s' % (
                    low_max + 0.1, medium_max, unit_abbrev),
                value=self.hazard_classes[2],
                colour='#FFEF36',
                border_color='#000000',
                transparency=0),
            dict(
                label=self.hazard_classes[3] + ': %.1f - %.1f %s' % (
                    medium_max + 0.1, high_max, unit_abbrev),
                value=self.hazard_classes[3],
                colour='#EFA951',
                border_color='#000000',
                transparency=0),
            dict(
                label=self.hazard_classes[4] + ': > %.1f %s' % (
                    high_max, unit_abbrev),
                value=self.hazard_classes[4],
                colour='#d62631',
                border_color='#000000',
                transparency=0),
        ]
        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        extra_keywords = {
            'map_title': self.metadata().key('map_title'),
            'target_field': self.target_field
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create vector layer and return
        impact_layer = Vector(
            data=impact_layer,
            name=self.metadata().key('layer_name'),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
