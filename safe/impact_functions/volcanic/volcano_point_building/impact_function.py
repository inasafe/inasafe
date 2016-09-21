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
from safe.impact_functions.volcanic.volcano_point_building\
    .metadata_definitions import VolcanoPointBuildingFunctionMetadata
from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.utilities.utilities import main_type
from safe.common.utilities import get_non_conflicting_attribute_name
from safe.engine.interpolation import (
    assign_hazard_values_to_exposure_data)
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)


class VolcanoPointBuildingFunction(
        ClassifiedVHClassifiedVE,
        BuildingExposureReportMixin):
    """Impact Function for Volcano Point on Building."""

    _metadata = VolcanoPointBuildingFunctionMetadata()

    def __init__(self):
        super(VolcanoPointBuildingFunction, self).__init__()
        BuildingExposureReportMixin.__init__(self)
        # A set of volcano names
        self.volcano_names = set()
        self._affected_categories_volcano = []
        self.hazard_zone_attribute = 'radius'

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
            tr('Map shows buildings affected in each of the volcano buffered '
               'zones.'),
            tr('Volcanoes considered: %s.') % sorted_volcano_names
        ]
        # include any generic exposure specific notes from definitions_v3.py
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions_v3.py
        fields = fields + self.hazard_notes()
        return fields

    @property
    def _affected_categories(self):
        """Overwriting the affected categories, since 'unaffected' are counted.

        :returns: The categories that equal effected.
        :rtype: list
        """
        return self._affected_categories_volcano

    def run(self):
        """Counts number of building exposed to each volcano hazard zones.

        :returns: Map of building exposed to volcanic hazard zones.
                  Table with number of buildings affected
        :rtype: dict
        """
        # Parameters
        radii = self.parameters['distances'].value

        # Get parameters from layer's keywords
        volcano_name_attribute = self.hazard.keyword('volcano_name_field')
        self.exposure_class_attribute = self.exposure.keyword(
            'structure_class_field')
        exposure_value_mapping = self.exposure.keyword('value_mapping')

        # Category names for the impact zone
        category_names = radii
        # In kilometers
        self._affected_categories_volcano = [
            tr('Radius %.1f km') % key for key in radii[::]]

        # Get names of volcanoes considered
        if volcano_name_attribute in self.hazard.layer.get_attribute_names():
            for row in self.hazard.layer.get_data():
                # Run through all polygons and get unique names
                self.volcano_names.add(row[volcano_name_attribute])

        # Find the target field name that has no conflict with the attribute
        # names in the hazard layer
        hazard_attribute_names = self.hazard.layer.get_attribute_names()
        target_field = get_non_conflicting_attribute_name(
            self.target_field, hazard_attribute_names)

        # Run interpolation function for polygon2polygon
        interpolated_layer = assign_hazard_values_to_exposure_data(
            self.hazard.layer, self.exposure.layer)

        # Extract relevant interpolated layer data
        features = interpolated_layer.get_data()

        self.init_report_var(radii)

        # Iterate the interpolated building layer
        for i in range(len(features)):
            hazard_value = features[i][self.hazard_zone_attribute]
            if not hazard_value:
                hazard_value = self._not_affected_value
            features[i][target_field] = hazard_value

            # Count affected buildings by usage type if available
            usage = features[i][self.exposure_class_attribute]
            usage = main_type(usage, exposure_value_mapping)

            affected = False
            if hazard_value in self.affected_buildings.keys():
                affected = True

            self.classify_feature(hazard_value, usage, affected)

        self.reorder_dictionaries()

        # Adding 'km'.
        affected_building_keys = self.affected_buildings.keys()
        for key in affected_building_keys:
            self.affected_buildings[tr('Radius %.1f km' % key)] = \
                self.affected_buildings.pop(key)

        # Create style
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        colours = colours[::-1]  # flip
        colours = colours[:len(category_names)]
        style_classes = []

        for i, category_name in enumerate(category_names):
            style_class = dict()
            style_class['label'] = tr('Radius %s km') % tr(category_name)
            style_class['transparency'] = 0
            style_class['value'] = category_name
            style_class['size'] = 1

            if i >= len(category_names):
                i = len(category_names) - 1
            style_class['colour'] = colours[i]

            style_classes.append(style_class)

        # Override style info with new classes and name
        style_info = dict(
            target_field=target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        impact_data = self.generate_data()

        extra_keywords = {
            'target_field': target_field,
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
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
