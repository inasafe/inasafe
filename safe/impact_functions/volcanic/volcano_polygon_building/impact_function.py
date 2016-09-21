# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Volcano Point on Building
Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from safe.impact_functions.bases.classified_vh_classified_ve import \
    ClassifiedVHClassifiedVE
from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.impact_functions.volcanic.volcano_polygon_building\
    .metadata_definitions import VolcanoPolygonBuildingFunctionMetadata
from safe.common.exceptions import InaSAFEError
from safe.engine.interpolation import (
    assign_hazard_values_to_exposure_data)
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)
from safe.utilities.keyword_io import definition
from safe.utilities.utilities import main_type
from safe.impact_functions.core import get_key_for_value
from safe.utilities.unicode import get_string


class VolcanoPolygonBuildingFunction(
        ClassifiedVHClassifiedVE,
        BuildingExposureReportMixin):
    """Impact Function for Volcano Point on Building."""

    _metadata = VolcanoPolygonBuildingFunctionMetadata()

    def __init__(self):
        super(VolcanoPolygonBuildingFunction, self).__init__()
        BuildingExposureReportMixin.__init__(self)
        # A set of volcano names
        self.volcano_names = set()
        self._target_field = 'Hazard'

    def notes(self):
        """Return the notes section of the report as dict.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        if self.volcano_names:
            sorted_volcano_names = ', '.join(sorted(self.volcano_names))
        else:
            sorted_volcano_names = tr('Not specified in data')
        fields = [
            tr('Map shows buildings affected in each of the volcano hazard '
               'polygons.'),
            tr('Volcanoes considered: %s.') % sorted_volcano_names
        ]
        # include any generic exposure specific notes from definitions_v3.py
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions_v3.py
        fields = fields + self.hazard_notes()
        return fields

    def run(self):
        """Risk plugin for volcano hazard on building/structure.

        Counts number of building exposed to each volcano hazard zones.

        :returns: Map of building exposed to volcanic hazard zones.
                  Table with number of buildings affected
        :rtype: dict
        """

        # Get parameters from layer's keywords
        self.hazard_class_attribute = self.hazard.keyword('field')
        self.name_attribute = self.hazard.keyword('volcano_name_field')
        self.hazard_class_mapping = self.hazard.keyword('value_map')
        self.exposure_class_attribute = self.exposure.keyword(
            'structure_class_field')
        exposure_value_mapping = self.exposure.keyword('value_mapping')

        # Input checks
        if not self.hazard.layer.is_polygon_data:
            message = (
                'Input hazard must be a polygon. I got %s with '
                'layer type %s' %
                (self.hazard.name, self.hazard.layer.get_geometry_name()))
            raise Exception(message)

        # Check if hazard_zone_attribute exists in hazard_layer
        if (self.hazard_class_attribute not in
                self.hazard.layer.get_attribute_names()):
            message = (
                'Hazard data %s did not contain expected attribute %s ' %
                (self.hazard.name, self.hazard_class_attribute))
            # noinspection PyExceptionInherit
            raise InaSAFEError(message)

        # Get names of volcanoes considered
        if self.name_attribute in self.hazard.layer.get_attribute_names():
            for row in self.hazard.layer.get_data():
                # Run through all polygons and get unique names
                self.volcano_names.add(row[self.name_attribute])

        # Retrieve the classification that is used by the hazard layer.
        vector_hazard_classification = self.hazard.keyword(
            'vector_hazard_classification')
        # Get the dictionary that contains the definition of the classification
        vector_hazard_classification = definition(vector_hazard_classification)
        # Get the list classes in the classification
        vector_hazard_classes = vector_hazard_classification['classes']
        # Initialize OrderedDict of affected buildings
        hazard_class = []
        # Iterate over vector hazard classes
        for vector_hazard_class in vector_hazard_classes:
            # Check if the key of class exist in hazard_class_mapping
            if vector_hazard_class['key'] in self.hazard_class_mapping.keys():
                # Replace the key with the name as we need to show the human
                # friendly name in the report.
                self.hazard_class_mapping[vector_hazard_class['name']] = \
                    self.hazard_class_mapping.pop(vector_hazard_class['key'])
                # Adding the class name as a key in affected_building
                hazard_class.append(vector_hazard_class['name'])

        # Run interpolation function for polygon2raster
        interpolated_layer = assign_hazard_values_to_exposure_data(
            self.hazard.layer, self.exposure.layer)

        # Extract relevant exposure data
        features = interpolated_layer.get_data()

        self.init_report_var(hazard_class)

        for i in range(len(features)):
            # Get the hazard value based on the value mapping in keyword
            hazard_value = get_key_for_value(
                    features[i][self.hazard_class_attribute],
                    self.hazard_class_mapping)
            if not hazard_value:
                hazard_value = self._not_affected_value
            features[i][self.target_field] = get_string(hazard_value)

            usage = features[i][self.exposure_class_attribute]
            usage = main_type(usage, exposure_value_mapping)

            affected = False
            if hazard_value in self.affected_buildings.keys():
                affected = True

            self.classify_feature(hazard_value, usage, affected)

        self.reorder_dictionaries()

        # Create style
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        colours = colours[::-1]  # flip

        colours = colours[:len(self.affected_buildings.keys())]

        style_classes = []

        for i, category_name in enumerate(self.affected_buildings.keys()):
            style_class = dict()
            style_class['label'] = tr(category_name)
            style_class['transparency'] = 0
            style_class['value'] = category_name
            style_class['size'] = 1

            if i >= len(self.affected_buildings.keys()):
                i = len(self.affected_buildings.keys()) - 1
            style_class['colour'] = colours[i]

            style_classes.append(style_class)

        # Override style info with new classes and name
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='categorizedSymbol')

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
            data=features,
            projection=interpolated_layer.get_projection(),
            geometry=interpolated_layer.get_geometry(),
            name=self.map_title(),
            keywords=impact_layer_keywords,
            style_info=style_info
        )

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
