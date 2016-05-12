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
    """Simple impact function for tsunami on roads."""
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
        for f in exposure.getFeatures(QgsFeatureRequest(extent_exposure)):
            geometry = f.geometry()
            bbox = geometry.boundingBox()
            # clip the exposure geometry to requested extent if necessary
            if not extent_exposure.contains(bbox):
                geometry = geometry.intersection(extent_exposure_geom)

            # find possible intersections with hazard layer
            impacted_geometries = []
            for hazard_id in hazard_index.intersects(bbox):
                hazard_id = hazard_features[hazard_id]
                hazard_geometry = hazard_id.geometry()
                impact_geometry = geometry.intersection(hazard_geometry)
                if not impact_geometry.wkbType() == QGis.WKBPolygon and \
                   not impact_geometry.wkbType() == QGis.WKBMultiPolygon:
                    continue   # no intersection found

                hazard_value = hazard_id[hazard_class_attribute]
                hazard_type = hazard_value_to_class.get(hazard_value)

                # write the impacted geometry
                f_impact = QgsFeature(impact_fields)
                f_impact.setGeometry(impact_geometry)
                f_impact.setAttributes(f.attributes() + [hazard_type])
                writer.addFeature(f_impact)

                impacted_geometries.append(impact_geometry)

            # TODO: uncomment if not affected polygons should be written
            # # Make sure the geometry we work with is valid, otherwise geom.
            # # processing operations (especially difference) may fail.
            # # Validity checking is a slow operation, it would be better if we
            # # could assume that all geometries are valid...
            # if not geometry.isGeosValid():
            #     geometry = geometry.buffer(0, 0)
            #
            # # write also not affected part of the exposure's feature
            # geometry_out = geometry.difference(
            #     QgsGeometry.unaryUnion(impacted_geometries))
            # if geometry_out and (geometry_out.wkbType() == QGis.WKBPolygon or
            #         geometry_out.wkbType() == QGis.WKBMultiPolygon):
            #     f_out = QgsFeature(impact_fields)
            #     f_out.setGeometry(geometry_out)
            #     f_out.setAttributes(f.attributes()+[self._not_affected_value])
            #     writer.addFeature(f_out)

        del writer
        impact_layer = QgsVectorLayer(filename, 'Impacted Land Cover', 'ogr')

        # from safe.test.debug_helper import show_qgis_layer
        # show_qgis_layer(impact_layer)

        if impact_layer.featureCount() == 0:
            raise ZeroImpactException()

        zone_field = None
        if self.aggregator:
            zone_field = self.aggregator.exposure_aggregation_field

        impact_data = LandCoverReportMixin(
            question=self.question,
            impact_layer=impact_layer,
            target_field=self.target_field,
            hazard_columns=self.hazard_classes,
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
                label=self.hazard_classes[1] + ': <0 - %.1f m' % low_max,
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
            'map_title': tr('Affected Land Cover'),
            'target_field': self.target_field
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create vector layer and return
        impact_layer = Vector(
            data=impact_layer,
            name=tr('Land cover affected by each hazard zone'),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
