# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Flood Vector Impact on
Buildings using QGIS.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from collections import OrderedDict

from PyQt4.QtCore import QVariant
from qgis.core import (
    QgsField,
    QgsSpatialIndex,
    QgsVectorLayer,
    QgsFeature,
    QgsCoordinateTransform,
    QgsGeometry)

import safe.messaging as m
from safe.common.exceptions import \
    GetDataError, ZeroImpactException
from safe.impact_functions.bases.classified_vh_classified_ve import \
    ClassifiedVHClassifiedVE
from safe.impact_functions.inundation.flood_vector_building_impact.\
    metadata_definitions import FloodPolygonBuildingFunctionMetadata
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)
from safe.messaging import styles
from safe.storage.vector import Vector
from safe.utilities.gis import is_point_layer
from safe.utilities.i18n import tr


class FloodPolygonBuildingFunction(
        ClassifiedVHClassifiedVE,
        BuildingExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Impact function for inundation (polygon-polygon)."""

    _metadata = FloodPolygonBuildingFunctionMetadata()

    def __init__(self):
        super(FloodPolygonBuildingFunction, self).__init__()
        # The 'wet' variable
        self.wet = 'wet'

        # From BuildingExposureReportMixin
        self.building_report_threshold = 25

    def notes(self):
        """Return the notes section of the report as dict.

        :return: The notes that should be attached to this impact report.
        :rtype: dict
        """
        title = tr('Notes and assumptions')
        hazard_classes_string = ', '.join(
            [unicode(hazard_class) for hazard_class in
             self.hazard_class_mapping[self.wet]])
        fields = [
            tr('Buildings are flooded when in a region with field "%s" in '
               '"%s".') % (self.hazard_class_attribute, hazard_classes_string)
        ]

        return {
            'title': title,
            'fields': fields
        }

    def run(self):
        """Experimental impact function."""

        # Get parameters from layer's keywords
        self.hazard_class_attribute = self.hazard.keyword('field')
        self.hazard_class_mapping = self.hazard.keyword('value_map')
        self.exposure_class_attribute = self.exposure.keyword(
            'structure_class_field')

        # Prepare Hazard Layer
        hazard_provider = self.hazard.layer.dataProvider()

        # Check affected field exists in the hazard layer
        affected_field_index = hazard_provider.fieldNameIndex(
            self.hazard_class_attribute)
        if affected_field_index == -1:
            message = tr(
                'Field "%s" is not present in the attribute table of the '
                'hazard layer. Please change the Affected Field parameter in '
                'the IF Option.') % self.hazard_class_attribute
            raise GetDataError(message)

        srs = self.exposure.layer.crs().toWkt()
        exposure_provider = self.exposure.layer.dataProvider()
        exposure_fields = exposure_provider.fields()

        # Check self.exposure_class_attribute exists in exposure layer
        building_type_field_index = exposure_provider.fieldNameIndex(
            self.exposure_class_attribute)
        if building_type_field_index == -1:
            message = tr(
                'Field "%s" is not present in the attribute table of '
                'the exposure layer. Please change the Building Type '
                'Field parameter in the IF Option.'
            ) % self.exposure_class_attribute
            raise GetDataError(message)

        # If target_field does not exist, add it:
        if exposure_fields.indexFromName(self.target_field) == -1:
            exposure_provider.addAttributes(
                [QgsField(self.target_field, QVariant.Int)])
        target_field_index = exposure_provider.fieldNameIndex(
            self.target_field)
        exposure_fields = exposure_provider.fields()

        # Create layer to store the buildings from E and extent
        buildings_are_points = is_point_layer(self.exposure.layer)
        if buildings_are_points:
            building_layer = QgsVectorLayer(
                'Point?crs=' + srs, 'impact_buildings', 'memory')
        else:
            building_layer = QgsVectorLayer(
                'Polygon?crs=' + srs, 'impact_buildings', 'memory')
        building_provider = building_layer.dataProvider()

        # Set attributes
        building_provider.addAttributes(exposure_fields.toList())
        building_layer.startEditing()
        building_layer.commitChanges()

        # Split building_layer by H and save as result:
        #   1) Filter from H inundated features
        #   2) Mark buildings as inundated (1) or not inundated (0)

        # make spatial index of affected polygons
        hazard_index = QgsSpatialIndex()
        hazard_geometries = {}  # key = feature id, value = geometry
        has_hazard_objects = False
        for feature in self.hazard.layer.getFeatures():
            value = feature[affected_field_index]
            if value not in self.hazard_class_mapping[self.wet]:
                continue
            hazard_index.insertFeature(feature)
            hazard_geometries[feature.id()] = QgsGeometry(feature.geometry())
            has_hazard_objects = True

        if not has_hazard_objects:
            message = tr(
                'There are no objects in the hazard layer with %s '
                'value in %s. Please check your data or use another '
                'attribute.') % (
                    self.hazard_class_attribute,
                    ', '.join(self.hazard_class_mapping[self.wet]))
            raise GetDataError(message)

        # We will use this transform to project each exposure feature into
        # the CRS of the Hazard.
        transform = QgsCoordinateTransform(
            self.exposure.crs(), self.hazard.crs())
        features = []
        for feature in self.exposure.layer.getFeatures():
            # Make a deep copy as the geometry is passed by reference
            # If we don't do this, subsequent operations will affect the
            # original feature geometry as well as the copy TS
            building_geom = QgsGeometry(feature.geometry())
            # Project the building geometry to hazard CRS
            building_bounds = transform.transform(building_geom.boundingBox())
            affected = False
            # get tentative list of intersecting hazard features
            # only based on intersection of bounding boxes
            ids = hazard_index.intersects(building_bounds)
            for fid in ids:
                # run (slow) exact intersection test
                building_geom.transform(transform)
                if hazard_geometries[fid].intersects(building_geom):
                    affected = True
                    break
            new_feature = QgsFeature()
            # We write out the original feature geom, not the projected one
            new_feature.setGeometry(feature.geometry())
            new_feature.setAttributes(feature.attributes())
            new_feature[target_field_index] = 1 if affected else 0
            features.append(new_feature)

            # every once in a while commit the created features
            # to the output layer
            if len(features) == 1000:
                (_, __) = building_provider.addFeatures(features)
                features = []

        (_, __) = building_provider.addFeatures(features)
        building_layer.updateExtents()

        # Generate simple impact report
        self.buildings = {}
        self.affected_buildings = OrderedDict([
            (tr('Flooded'), {})
        ])
        buildings_data = building_layer.getFeatures()
        building_type_field_index = building_layer.fieldNameIndex(
            self.exposure_class_attribute)
        for building in buildings_data:
            record = building.attributes()
            building_type = record[building_type_field_index]
            if building_type in [None, 'NULL', 'null', 'Null']:
                building_type = 'Unknown type'
            if building_type not in self.buildings:
                self.buildings[building_type] = 0
                for category in self.affected_buildings.keys():
                    self.affected_buildings[category][
                        building_type] = OrderedDict([
                            (tr('Buildings Affected'), 0)])
            self.buildings[building_type] += 1

            if record[target_field_index] == 1:
                self.affected_buildings[tr('Flooded')][building_type][
                    tr('Buildings Affected')] += 1

        # Lump small entries and 'unknown' into 'other' category
        # Building threshold #2468
        postprocessors = self.parameters['postprocessors']
        building_postprocessors = postprocessors['BuildingType'][0]
        self.building_report_threshold = building_postprocessors.value[0].value
        self._consolidate_to_other()

        # For printing map purpose
        map_title = tr('Buildings inundated')
        legend_title = tr('Structure inundated status')

        style_classes = [
            dict(label=tr('Not Inundated'), value=0, colour='#1EFC7C',
                 transparency=0, size=0.5),
            dict(label=tr('Inundated'), value=1, colour='#F31A1C',
                 transparency=0, size=0.5)]
        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        # Convert QgsVectorLayer to inasafe layer and return it.
        if building_layer.featureCount() < 1:
            raise ZeroImpactException(tr(
                'No buildings were impacted by this flood.'))

        impact_data = self.generate_data()

        extra_keywords = {
            'map_title': map_title,
            'legend_title': legend_title,
            'target_field': self.target_field,
            'buildings_total': self.total_buildings,
            'buildings_affected': self.total_affected_buildings
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        impact_layer = Vector(
            data=building_layer,
            name=tr('Flooded buildings'),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
