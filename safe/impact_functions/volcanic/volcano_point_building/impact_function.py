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
from safe.impact_functions.volcanic.volcano_point_building\
    .metadata_definitions import VolcanoPointBuildingFunctionMetadata
from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.engine.core import buffer_points
from safe.common.utilities import (
    get_thousand_separator,
    get_non_conflicting_attribute_name,
    get_osm_building_usage)
from safe.engine.interpolation import (
    assign_hazard_values_to_exposure_data)
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)
from safe.common.exceptions import KeywordNotFoundError
import safe.messaging as m
from safe.messaging import styles


class VolcanoPointBuildingFunction(
        ClassifiedVHClassifiedVE,
        BuildingExposureReportMixin):
    """Impact Function for Volcano Point on Building."""

    _metadata = VolcanoPointBuildingFunctionMetadata()

    def __init__(self):
        super(VolcanoPointBuildingFunction, self).__init__()
        self.volcano_names = tr('Not specified in data')
        self._affected_categories_volcano = []

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
            'Map shows buildings affected in each of the volcano buffered '
            'zones.'))
        names = tr('Volcanoes considered: %s.') % self.volcano_names
        checklist.add(names)
        message.add(checklist)
        return message

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
        self.validate()
        self.prepare()

        # Hazard Zone Attribute
        hazard_zone_attribute = 'radius'

        # Parameters
        radii = self.parameters['distances'].value

        # Get parameters from layer's keywords
        volcano_name_attribute = self.hazard.keyword('volcano_name_field')
        # Try to get the value from keyword, if not exist, it will not fail,
        # but use the old get_osm_building_usage
        try:
            self.exposure_class_attribute = self.exposure.keyword(
                'structure_class_field')
        except KeywordNotFoundError:
            self.exposure_class_attribute = None

        # Input checks
        if not self.hazard.layer.is_point_data:
            message = (
                'Input hazard must be a vector point layer. I got %s '
                'with layer type %s' % (
                    self.hazard.name, self.hazard.layer.get_geometry_name()))
            raise Exception(message)

        # Make hazard layer by buffering the point
        centers = self.hazard.layer.get_geometry()
        features = self.hazard.layer.get_data()
        radii_meter = [x * 1000 for x in radii]  # Convert to meters
        hazard_layer = buffer_points(
            centers,
            radii_meter,
            hazard_zone_attribute,
            data_table=features)
        # Category names for the impact zone
        category_names = radii_meter
        self._affected_categories_volcano = radii_meter[:]
        category_names.append(self._not_affected_value)

        # Get names of volcanoes considered
        if volcano_name_attribute in hazard_layer.get_attribute_names():
            volcano_name_list = set()
            for row in hazard_layer.get_data():
                # Run through all polygons and get unique names
                volcano_name_list.add(row[volcano_name_attribute])
            self.volcano_names = ', '.join(volcano_name_list)

        # Find the target field name that has no conflict with the attribute
        # names in the hazard layer
        hazard_attribute_names = hazard_layer.get_attribute_names()
        target_field = get_non_conflicting_attribute_name(
            self.target_field, hazard_attribute_names)

        # Run interpolation function for polygon2polygon
        interpolated_layer = assign_hazard_values_to_exposure_data(
            hazard_layer, self.exposure.layer)

        # Extract relevant interpolated layer data
        attribute_names = interpolated_layer.get_attribute_names()
        features = interpolated_layer.get_data()

        self.buildings = {}
        self.affected_buildings = OrderedDict()
        for category in radii_meter:
            self.affected_buildings[category] = {}

        # Iterate the interpolated building layer
        for i in range(len(features)):
            hazard_value = features[i][hazard_zone_attribute]
            if not hazard_value:
                hazard_value = self._not_affected_value
            features[i][target_field] = hazard_value

            # Count affected buildings by usage type if available
            if (self.exposure_class_attribute and
                    self.exposure_class_attribute in attribute_names):
                usage = features[i][self.exposure_class_attribute]
            else:
                usage = get_osm_building_usage(attribute_names, features[i])

            if usage is [None, 'NULL', 'null', 'Null', 0]:
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
        self._consolidate_to_other()

        # Generate simple impact report
        impact_summary = impact_table = self.html_report()

        # Create style
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        colours = colours[::-1]  # flip
        colours = colours[:len(category_names)]
        style_classes = []

        i = 0
        for category_name in category_names:
            style_class = dict()
            style_class['label'] = tr(category_name)
            style_class['transparency'] = 0
            style_class['value'] = category_name
            style_class['size'] = 1

            if i >= len(category_names):
                i = len(category_names) - 1
            style_class['colour'] = colours[i]
            i += 1

            style_classes.append(style_class)

        # Override style info with new classes and name
        style_info = dict(
            target_field=target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        # For printing map purpose
        map_title = tr('Buildings affected by volcanic buffered point')
        legend_title = tr('Building count')
        legend_units = tr('(building)')
        legend_notes = tr(
            'Thousand separator is represented by %s' %
            get_thousand_separator())

        # Create vector layer and return
        impact_layer = Vector(
            data=features,
            projection=interpolated_layer.get_projection(),
            geometry=interpolated_layer.get_geometry(),
            name=tr('Buildings affected by volcanic buffered point'),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'target_field': target_field,
                'map_title': map_title,
                'legend_notes': legend_notes,
                'legend_units': legend_units,
                'legend_title': legend_title},
            style_info=style_info)

        self._impact = impact_layer
        return impact_layer
