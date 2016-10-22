# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Generic Impact function on
Land Cover for Classified Hazard.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import logging
LOGGER = logging.getLogger('InaSAFE')

from qgis.core import (
    QGis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsGeometry,
    QgsRectangle,
    QgsSpatialIndex,
    QgsVectorFileWriter,
    QgsVectorLayer,
)
from PyQt4.QtCore import QVariant
from collections import OrderedDict

from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.common.exceptions import ZeroImpactException
from safe.common.utilities import unique_filename
from safe.impact_functions.bases.classified_vh_classified_ve import \
    ClassifiedVHClassifiedVE
from safe.impact_functions.generic.classified_polygon_landcover\
    .metadata_definitions \
    import ClassifiedPolygonHazardLandCoverFunctionMetadata
from safe.impact_reports.land_cover_report_mixin import LandCoverReportMixin


def _calculate_landcover_impact(
        exposure, extent_exposure, extent_exposure_geom,
        hazard_class_attribute, hazard_features, hazard_index,
        hazard_value_to_class, impact_fields, writer):
    """This function is used by GenericOnLandcover, TsunamiOnLandcover and
    AshOnLandcover.
    """

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
            if not impact_geometry:
                LOGGER.warning(
                    'Impact geometry is None for hazard_id %s' % hazard_id)
                continue
            if not impact_geometry.wkbType() == QGis.WKBPolygon and \
                    not impact_geometry.wkbType() == QGis.WKBMultiPolygon:
                continue  # no intersection found

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


class ClassifiedPolygonHazardLandCoverFunction(
        ClassifiedVHClassifiedVE):

    _metadata = ClassifiedPolygonHazardLandCoverFunctionMetadata()

    def __init__(self):
        super(ClassifiedPolygonHazardLandCoverFunction, self).__init__()

        # Set the question of the IF (as the hazard data is not an event)
        self.question = (
            'In each of the hazard zones which land cover types might be '
            'affected?')
        # Don't put capital letters as the value in the attribute should match.
        self.hazard_columns = OrderedDict()
        self.hazard_columns['low'] = tr('Low Hazard Zone')
        self.hazard_columns['medium'] = tr('Medium Hazard Zone')
        self.hazard_columns['high'] = tr('High Hazard Zone')
        self.affected_hazard_columns = []

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        fields = [
            tr('The classes used for low, medium, high hazard are specific '
               'to the hazard dataset used.'),
            tr('Please consult the original hazard dataset creator for more '
               'details.')
        ]

        # include any generic exposure specific notes from definitions
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions
        fields = fields + self.hazard_notes()
        return fields

    def run(self):
        """Risk plugin for classified polygon hazard on land cover.

        Counts area of land cover types exposed to hazard zones.

        :returns: Impact layer
        :rtype: Vector
        """

        # Identify hazard and exposure layers
        hazard = self.hazard.layer
        exposure = self.exposure.layer

        type_attr = self.exposure.keyword('field')

        self.hazard_class_attribute = self.hazard.keyword('field')
        hazard_value_to_class = {}
        self.hazard_class_mapping = self.hazard.keyword('value_map')
        for key, values in self.hazard_class_mapping.items():
            for value in values:
                hazard_value_to_class[value] = self.hazard_columns[key]

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

        # Iterate over all exposure polygons and calculate the impact.
        _calculate_landcover_impact(
            exposure, extent_exposure, extent_exposure_geom,
            self.hazard_class_attribute, hazard_features, hazard_index,
            hazard_value_to_class, impact_fields, writer)

        del writer
        impact_layer = QgsVectorLayer(filename, 'Impacted Land Cover', 'ogr')

        if impact_layer.featureCount() == 0:
            raise ZeroImpactException()

        zone_field = None
        if self.aggregator:
            zone_field = self.aggregator.exposure_aggregation_field

        # This is not the standard way to use mixins
        # Martin preferred to call it directly - normally it is called with
        # multiple inheritance. Thats ok but we need to monkey patch the
        # notes function as it is not overloaded by this class
        mixin = LandCoverReportMixin(
            question=self.question,
            impact_layer=impact_layer,
            target_field=self.target_field,
            ordered_columns=self.hazard_columns.values(),
            affected_columns=self.affected_hazard_columns,
            land_cover_field=type_attr,
            zone_field=zone_field
        )

        mixin.notes = self.notes
        impact_data = mixin.generate_data()

        # Define style for the impact layer
        style_classes = [
            dict(
                label=self.hazard_columns['low'],
                value=self.hazard_columns['low'],
                colour='#acffb6',
                border_color='#000000',
                transparency=0,
                size=0.5),
            dict(
                label=self.hazard_columns['medium'],
                value=self.hazard_columns['medium'],
                colour='#ffe691',
                border_color='#000000',
                transparency=0,
                size=0.5),
            dict(
                label=self.hazard_columns['high'],
                value=self.hazard_columns['high'],
                colour='#F31A1C',
                border_color='#000000',
                transparency=0,
                size=0.5),
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
