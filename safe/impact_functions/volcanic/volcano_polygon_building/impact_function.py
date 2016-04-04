# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Volcano Point on Building
Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from collections import OrderedDict

from safe.impact_functions.bases.classified_vh_classified_ve import \
    ClassifiedVHClassifiedVE
from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.impact_functions.volcanic.volcano_polygon_building\
    .metadata_definitions import VolcanoPolygonBuildingFunctionMetadata
from safe.common.exceptions import InaSAFEError, KeywordNotFoundError
from safe.common.utilities import (
    get_thousand_separator,
    get_osm_building_usage)
from safe.engine.interpolation import (
    assign_hazard_values_to_exposure_data)
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)
import safe.messaging as m
from safe.messaging import styles
from safe.utilities.keyword_io import definition
from safe.impact_functions.core import get_key_for_value
from safe.utilities.unicode import get_string


class VolcanoPolygonBuildingFunction(
        ClassifiedVHClassifiedVE,
        BuildingExposureReportMixin):
    """Impact Function for Volcano Point on Building."""

    _metadata = VolcanoPolygonBuildingFunctionMetadata()

    def __init__(self):
        super(VolcanoPolygonBuildingFunction, self).__init__()
        self.volcano_names = tr('Not specified in data')
        self._target_field = 'Hazard'

        # From BuildingExposureReportMixin
        self.building_report_threshold = 25

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        message.add(m.Heading(
            tr('Notes and assumptions'), **styles.INFO_STYLE))
        checklist = m.BulletedList()
        checklist.add(tr(
            'Map shows buildings affected in each of the volcano hazard '
            'polygons.'))
        names = tr('Volcanoes considered: %s.') % self.volcano_names
        checklist.add(names)
        message.add(checklist)
        return message

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
        # Try to get the value from keyword, if not exist, it will not fail,
        # but use the old get_osm_building_usage
        try:
            self.exposure_class_attribute = self.exposure.keyword(
                'structure_class_field')
        except KeywordNotFoundError:
            self.exposure_class_attribute = None

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
            volcano_name_list = set()
            for row in self.hazard.layer.get_data():
                # Run through all polygons and get unique names
                volcano_name_list.add(row[self.name_attribute])
            self.volcano_names = ', '.join(volcano_name_list)
        else:
            self.volcano_names = tr('Not specified in data')

        # Retrieve the classification that is used by the hazard layer.
        vector_hazard_classification = self.hazard.keyword(
            'vector_hazard_classification')
        # Get the dictionary that contains the definition of the classification
        vector_hazard_classification = definition(vector_hazard_classification)
        # Get the list classes in the classification
        vector_hazard_classes = vector_hazard_classification['classes']
        # Initialize OrderedDict of affected buildings
        self.affected_buildings = OrderedDict()
        # Iterate over vector hazard classes
        for vector_hazard_class in vector_hazard_classes:
            # Check if the key of class exist in hazard_class_mapping
            if vector_hazard_class['key'] in self.hazard_class_mapping.keys():
                # Replace the key with the name as we need to show the human
                # friendly name in the report.
                self.hazard_class_mapping[vector_hazard_class['name']] = \
                    self.hazard_class_mapping.pop(vector_hazard_class['key'])
                # Adding the class name as a key in affected_building
                self.affected_buildings[vector_hazard_class['name']] = {}

        # Run interpolation function for polygon2raster
        interpolated_layer = assign_hazard_values_to_exposure_data(
            self.hazard.layer, self.exposure.layer)

        # Extract relevant exposure data
        attribute_names = interpolated_layer.get_attribute_names()
        features = interpolated_layer.get_data()

        self.buildings = {}

        for i in range(len(features)):
            # Get the hazard value based on the value mapping in keyword
            hazard_value = get_key_for_value(
                    features[i][self.hazard_class_attribute],
                    self.hazard_class_mapping)
            if not hazard_value:
                hazard_value = self._not_affected_value
            features[i][self.target_field] = get_string(hazard_value)

            if (self.exposure_class_attribute and
                    self.exposure_class_attribute in attribute_names):
                usage = features[i][self.exposure_class_attribute]
            else:
                usage = get_osm_building_usage(attribute_names, features[i])

            if usage in [None, 'NULL', 'null', 'Null', 0]:
                usage = tr('Unknown')

            if usage not in self.buildings:
                self.buildings[usage] = 0
                for category in self.affected_buildings.keys():
                    self.affected_buildings[category][
                        usage] = OrderedDict([
                            (tr('Buildings Affected'), 0)])

            self.buildings[usage] += 1
            if hazard_value in self.affected_buildings.keys():
                self.affected_buildings[hazard_value][usage][
                    tr('Buildings Affected')] += 1

        # Lump small entries and 'unknown' into 'other' category
        # Building threshold #2468
        postprocessors = self.parameters['postprocessors']
        building_postprocessors = postprocessors['BuildingType'][0]
        self.building_report_threshold = building_postprocessors.value[0].value
        self._consolidate_to_other()

        # Generate simple impact report
        impact_summary = impact_table = self.html_report()

        # Create style
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        colours = colours[::-1]  # flip

        colours = colours[:len(self.affected_buildings.keys())]

        style_classes = []

        i = 0
        for category_name in self.affected_buildings.keys():
            style_class = dict()
            style_class['label'] = tr(category_name)
            style_class['transparency'] = 0
            style_class['value'] = category_name
            style_class['size'] = 1

            if i >= len(self.affected_buildings.keys()):
                i = len(self.affected_buildings.keys()) - 1
            style_class['colour'] = colours[i]
            i += 1

            style_classes.append(style_class)

        # Override style info with new classes and name
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='categorizedSymbol')

        # For printing map purpose
        map_title = tr('Buildings affected by volcanic hazard zone')
        legend_title = tr('Building count')
        legend_units = tr('(building)')
        legend_notes = tr('Thousand separator is represented by %s' %
                          get_thousand_separator())

        extra_keywords = {
            'impact_summary': impact_summary,
            'impact_table': impact_table,
            'target_field': self.target_field,
            'map_title': map_title,
            'legend_notes': legend_notes,
            'legend_units': legend_units,
            'legend_title': legend_title
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create vector layer and return
        impact_layer = Vector(
            data=features,
            projection=interpolated_layer.get_projection(),
            geometry=interpolated_layer.get_geometry(),
            name=tr('Buildings affected by volcanic hazard zone'),
            keywords=impact_layer_keywords,
            style_info=style_info
        )

        self._impact = impact_layer
        return impact_layer
