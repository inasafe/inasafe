# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Generic Polygon on Building
Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from qgis.core import QgsField, QgsRectangle
from PyQt4.QtCore import QVariant

from safe.impact_functions.bases.classified_vh_classified_ve import \
    ClassifiedVHClassifiedVE
from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.impact_functions.generic.classified_polygon_building \
    .metadata_definitions \
    import ClassifiedPolygonHazardBuildingFunctionMetadata
from safe.common.exceptions import (
    InaSAFEError, ZeroImpactException, KeywordNotFoundError)
from safe.common.utilities import color_ramp
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)
from safe.engine.interpolation_qgis import interpolate_polygon_polygon
from safe.impact_functions.core import get_key_for_value
from safe.utilities.keyword_io import definition
from safe.utilities.unicode import get_unicode
from safe.utilities.utilities import main_type


class ClassifiedPolygonHazardBuildingFunction(
    ClassifiedVHClassifiedVE,
    BuildingExposureReportMixin):
    """Impact Function for Generic Polygon on Building."""

    _metadata = ClassifiedPolygonHazardBuildingFunctionMetadata()

    def __init__(self):
        super(ClassifiedPolygonHazardBuildingFunction, self).__init__()
        BuildingExposureReportMixin.__init__(self)

        # Hazard zones are all unique values from the hazard zone attribute
        self.hazard_zones = []
        # Set the question of the IF (as the hazard data is not an event)
        self.question = tr(
            'In each of the hazard zones how many buildings might be '
            'affected?')

    def notes(self):
        """Return the notes section of the report as dict.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        fields = [
            tr('Map shows buildings affected in each of these hazard zones: '
               '%s') % ', '.join(self.hazard_zones)
        ]

        # include any generic exposure specific notes from definitions
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions
        fields = fields + self.hazard_notes()
        return fields

    def run(self):
        """Risk plugin for classified polygon hazard on building/structure.

        Counts number of building exposed to each hazard zones.

        :returns: Impact vector layer building exposed to each hazard zones.
            Table with number of buildings affected
        :rtype: Vector
        """

        # Value from layer's keywords
        self.hazard_class_attribute = self.hazard.keyword('field')
        self.hazard_class_mapping = self.hazard.keyword('value_map')
        self.exposure_class_attribute = self.exposure.keyword(
            'structure_class_field')
        try:
            exposure_value_mapping = self.exposure.keyword('value_mapping')
        except KeywordNotFoundError:
            # Generic IF, the keyword might not be defined base.py
            exposure_value_mapping = {}

        # Retrieve the classification that is used by the hazard layer.
        vector_hazard_classification = self.hazard.keyword(
            'vector_hazard_classification')
        # Get the dictionary that contains the definition of the classification
        vector_hazard_classification = definition(vector_hazard_classification)
        # Get the list classes in the classification
        vector_hazard_classes = vector_hazard_classification['classes']
        # Iterate over vector hazard classes
        hazard_classes = []
        for vector_hazard_class in vector_hazard_classes:
            # Check if the key of class exist in hazard_class_mapping
            if vector_hazard_class['key'] in self.hazard_class_mapping.keys():
                # Replace the key with the name as we need to show the human
                # friendly name in the report.
                self.hazard_class_mapping[vector_hazard_class['name']] = \
                    self.hazard_class_mapping.pop(vector_hazard_class['key'])
                # Adding the class name as a key in affected_building
                hazard_classes.append(vector_hazard_class['name'])

        hazard_zone_attribute_index = self.hazard.layer.fieldNameIndex(
            self.hazard_class_attribute)

        # Check if hazard_zone_attribute exists in hazard_layer
        if hazard_zone_attribute_index < 0:
            message = (
                'Hazard data %s does not contain expected attribute %s ' %
                (self.hazard.layer.name(), self.hazard_class_attribute))
            # noinspection PyExceptionInherit
            raise InaSAFEError(message)

        # Hazard zone categories from hazard layer
        unique_values = self.hazard.layer.uniqueValues(
            hazard_zone_attribute_index)
        # Values might be integer or float, we should have unicode. #2626
        self.hazard_zones = [get_unicode(val) for val in unique_values]

        self.init_report_var(hazard_classes)

        wgs84_extent = QgsRectangle(
            self.requested_extent[0], self.requested_extent[1],
            self.requested_extent[2], self.requested_extent[3])

        # Run interpolation function for polygon2polygon
        interpolated_layer = interpolate_polygon_polygon(
            self.hazard.layer, self.exposure.layer, wgs84_extent)

        new_field = QgsField(self.target_field, QVariant.String)
        interpolated_layer.dataProvider().addAttributes([new_field])
        interpolated_layer.updateFields()

        target_field_index = interpolated_layer.fieldNameIndex(
            self.target_field)
        changed_values = {}

        if interpolated_layer.featureCount() < 1:
            raise ZeroImpactException()

        # Extract relevant interpolated data
        for feature in interpolated_layer.getFeatures():
            # Get the hazard value based on the value mapping in keyword
            hazard_value = get_key_for_value(
                    feature[self.hazard_class_attribute],
                    self.hazard_class_mapping)
            if not hazard_value:
                hazard_value = self._not_affected_value
            changed_values[feature.id()] = {target_field_index: hazard_value}

            usage = feature[self.exposure_class_attribute]
            usage = main_type(usage, exposure_value_mapping)

            affected = False
            if hazard_value in self.hazard_class_mapping.keys():
                affected = True

            self.classify_feature(hazard_value, usage, affected)

        interpolated_layer.dataProvider().changeAttributeValues(changed_values)

        self.reorder_dictionaries()

        # Create style
        categories = self.affected_buildings.keys()
        categories.append(self._not_affected_value)
        colours = color_ramp(len(categories))
        style_classes = []

        for i, hazard_zone in enumerate(self.affected_buildings.keys()):
            style_class = dict()
            style_class['label'] = tr(hazard_zone)
            style_class['transparency'] = 0
            style_class['value'] = hazard_zone
            style_class['size'] = 1
            style_class['colour'] = colours[i]
            style_classes.append(style_class)

        # Override style info with new classes and name
        style_info = dict(
            target_field=self.target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol'
        )

        impact_data = self.generate_data()

        extra_keywords = {
            'target_field': self.target_field,
            'map_title': self.map_title(),
            'legend_notes': self.metadata().key('legend_notes'),
            'legend_units': self.metadata().key('legend_units'),
            'legend_title': self.metadata().key('legend_title')
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create vector layer and return
        impact_layer = Vector(
            data=interpolated_layer,
            name=self.map_title(),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
