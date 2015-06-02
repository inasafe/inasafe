# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Generic Polygon on Building
Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from collections import OrderedDict

from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.generic.classified_polygon_building\
    .metadata_definitions \
    import ClassifiedPolygonHazardBuildingFunctionMetadata
from safe.common.exceptions import InaSAFEError
from safe.common.utilities import (
    get_thousand_separator,
    get_osm_building_usage,
    color_ramp)
from safe.engine.interpolation import (
    assign_hazard_values_to_exposure_data)
from safe.impact_reports.building_exposure_report_mixin import (
    BuildingExposureReportMixin)


class ClassifiedPolygonHazardBuildingFunction(
        ImpactFunction,
        BuildingExposureReportMixin):
    """Impact Function for Generic Polygon on Building."""

    _metadata = ClassifiedPolygonHazardBuildingFunctionMetadata()

    def __init__(self):
        super(ClassifiedPolygonHazardBuildingFunction, self).__init__()

        # Hazard zones are all unique values from the hazard zone attribute
        self.hazard_zones = []
        # Set the question of the IF (as the hazard data is not an event)
        self.question = ('In each of the hazard zones how many buildings '
                         'might be affected.')

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        return [
            {
                'content': tr('Notes'),
                'header': True
            },
            {
                'content': tr(
                    'Map shows buildings affected in each of these hazard '
                    'zones: %s') % ', '.join(self.hazard_zones)
            }
        ]

    def run(self, layers=None):
        """Risk plugin for classified polygon hazard on building/structure.

        Counts number of building exposed to each hazard zones.

        :param layers: List of layers expected to contain.
                * hazard_layer: Hazard layer
                * exposure_layer: Vector layer of structure data on
                the same grid as hazard_layer

        :returns: Map of building exposed to each hazard zones.
                  Table with number of buildings affected
        :rtype: dict
        """
        self.validate()
        self.prepare(layers)

        # Parameters
        hazard_zone_attribute = self.parameters['hazard zone attribute']

        # Identify hazard and exposure layers
        hazard_layer = self.hazard
        exposure_layer = self.exposure

        # Input checks
        if not hazard_layer.is_polygon_data:
            message = (
                'Input hazard must be a polygon. I got %s with '
                'layer type %s' %
                (hazard_layer.get_name(), hazard_layer.get_geometry_name()))
            raise Exception(message)

        # Check if hazard_zone_attribute exists in hazard_layer
        if hazard_zone_attribute not in hazard_layer.get_attribute_names():
            message = (
                'Hazard data %s does not contain expected attribute %s ' %
                (hazard_layer.get_name(), hazard_zone_attribute))
            # noinspection PyExceptionInherit
            raise InaSAFEError(message)

        # Hazard zone categories from hazard layer
        self.hazard_zones = list(
            set(hazard_layer.get_data(hazard_zone_attribute)))

        self.buildings = {}
        self.affected_buildings = OrderedDict()
        for hazard_zone in self.hazard_zones:
            self.affected_buildings[hazard_zone] = {}

        # Run interpolation function for polygon2polygon
        interpolated_layer = assign_hazard_values_to_exposure_data(
            hazard_layer, exposure_layer, attribute_name=None)

        # Extract relevant interpolated data
        attribute_names = interpolated_layer.get_attribute_names()
        features = interpolated_layer.get_data()

        for i in range(len(features)):
            hazard_value = features[i][hazard_zone_attribute]
            if not hazard_value:
                hazard_value = self._not_affected_value
            features[i][self.target_field] = hazard_value
            usage = get_osm_building_usage(attribute_names, features[i])
            if usage is None:
                usage = tr('Unknown')
            if usage not in self.buildings:
                self.buildings[usage] = 0
                for category in self.affected_buildings.keys():
                    self.affected_buildings[category][usage] = OrderedDict(
                        [(tr('Buildings Affected'), 0)])
            self.buildings[usage] += 1
            if hazard_value in self.affected_buildings.keys():
                self.affected_buildings[hazard_value][usage][
                    tr('Buildings Affected')] += 1

        # Lump small entries and 'unknown' into 'other' category
        self._consolidate_to_other()

        # Generate simple impact report
        impact_summary = impact_table = self.generate_html_report()

        # Create style
        categories = self.hazard_zones
        categories.append(self._not_affected_value)
        colours = color_ramp(len(categories))
        style_classes = []

        i = 0
        for hazard_zone in self.hazard_zones:
            style_class = dict()
            style_class['label'] = tr(hazard_zone)
            style_class['transparency'] = 0
            style_class['value'] = hazard_zone
            style_class['size'] = 1
            style_class['colour'] = colours[i]
            style_classes.append(style_class)
            i += 1

        # Override style info with new classes and name
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='categorizedSymbol')

        # For printing map purpose
        map_title = tr('Buildings affected by each hazard zone')
        legend_notes = tr('Thousand separator is represented by %s' %
                          get_thousand_separator())
        legend_units = tr('(building)')
        legend_title = tr('Building count')

        # Create vector layer and return
        impact_layer = Vector(
            data=features,
            projection=interpolated_layer.get_projection(),
            geometry=interpolated_layer.get_geometry(),
            name=tr('Buildings affected by each hazard zone'),
            keywords={'impact_summary': impact_summary,
                      'impact_table': impact_table,
                      'target_field': self.target_field,
                      'map_title': map_title,
                      'legend_notes': legend_notes,
                      'legend_units': legend_units,
                      'legend_title': legend_title},
            style_info=style_info)

        self._impact = impact_layer
        return impact_layer
