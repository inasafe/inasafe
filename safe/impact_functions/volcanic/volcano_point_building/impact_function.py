# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Volcano Point on Building
Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.volcanic.volcano_point_building\
    .metadata_definitions import VolcanoPointBuildingFunctionMetadata
from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.engine.utilities import buffer_points
from safe.common.utilities import (
    format_int,
    get_thousand_separator,
    get_non_conflicting_attribute_name,
    get_osm_building_usage)
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import (
    assign_hazard_values_to_exposure_data)


class VolcanoPointBuildingFunction(ImpactFunction):
    """Impact Function for Volcano Point on Building."""

    _metadata = VolcanoPointBuildingFunctionMetadata()

    def __init__(self):
        super(VolcanoPointBuildingFunction, self).__init__()

    def run(self, layers=None):
        """Counts number of building exposed to each volcano hazard zones.

        :param layers: List of layers expected to contain.
                * hazard_layer: Hazard layer of volcano
                * exposure_layer: Vector layer of structure data on
                the same grid as hazard_layer

        :returns: Map of building exposed to volcanic hazard zones.
                  Table with number of buildings affected
        :rtype: dict
        """
        self.validate()
        self.prepare(layers)
        # Target Field
        target_field = 'zone'
        # Hazard Zone Attribute
        hazard_zone_attribute = 'radius'
        # Not Affected Value
        not_affected_value = 'Not Affected'

        # Parameters
        radii = self.parameters['distances [km]']
        volcano_name_attribute = self.parameters['volcano name attribute']

        # Identify hazard and exposure layers
        hazard_layer = self.hazard  # Volcano hazard layer
        exposure_layer = self.exposure  # Building exposure layer

        # Input checks
        if not hazard_layer.is_point_data:
            message = (
                'Input hazard must be a vector point layer. I got %s '
                'with layer type %s' % (
                    hazard_layer.get_name(), hazard_layer.get_geometry_name()))
            raise Exception(message)

        # Make hazard layer by buffering the point
        centers = hazard_layer.get_geometry()
        features = hazard_layer.get_data()
        radii_meter = [x * 1000 for x in radii]  # Convert to meters
        hazard_layer = buffer_points(
            centers,
            radii_meter,
            hazard_zone_attribute,
            data_table=features)
        # Category names for the impact zone
        category_names = radii_meter
        category_names.append(not_affected_value)

        # Get names of volcanoes considered
        if volcano_name_attribute in hazard_layer.get_attribute_names():
            volcano_name_list = set()
            for row in hazard_layer.get_data():
                # Run through all polygons and get unique names
                volcano_name_list.add(row[volcano_name_attribute])
            volcano_names = ', '.join(volcano_name_list)
        else:
            volcano_names = tr('Not specified in data')

        # Find the target field name that has no conflict with the attribute
        # names in the hazard layer
        hazard_attribute_names = hazard_layer.get_attribute_names()
        target_field = get_non_conflicting_attribute_name(
            target_field, hazard_attribute_names)

        # Run interpolation function for polygon2polygon
        interpolated_layer = assign_hazard_values_to_exposure_data(
            hazard_layer, exposure_layer, attribute_name=None)

        # Extract relevant interpolated layer data
        attribute_names = interpolated_layer.get_attribute_names()
        features = interpolated_layer.get_data()

        # Initialize the container for the result
        building_per_category = {}
        other_sum = {}
        for category_name in category_names:
            building_per_category[category_name] = {}
            building_per_category[category_name]['total'] = 0
            other_sum[category_name] = 0

        building_usages = []
        # Iterate the interpolated building layer
        for i in range(len(features)):
            hazard_value = features[i][hazard_zone_attribute]
            if not hazard_value:
                hazard_value = not_affected_value
            features[i][target_field] = hazard_value

            if hazard_value in building_per_category.keys():
                building_per_category[hazard_value]['total'] += 1
            elif not hazard_value:
                building_per_category[not_affected_value]['total'] += 1
            else:
                building_per_category[hazard_value] = {}
                building_per_category[hazard_value]['total'] = 1

            # Count affected buildings by usage type if available
            usage = get_osm_building_usage(attribute_names, features[i])
            if usage is None:
                usage = tr('unknown')

            if usage not in building_usages:
                building_usages.append(usage)
                for building in building_per_category.values():
                    building[usage] = 0

            building_per_category[hazard_value][usage] += 1

        # Generate simple impact report
        blank_cell = ''
        table_body = [self.question,
                      TableRow([tr('Volcanoes considered'),
                                '%s' % volcano_names, blank_cell],
                               header=True)]

        table_headers = [tr('Building type')]
        table_headers += [tr(x) for x in category_names]
        table_headers += [tr('Total')]

        table_body += [TableRow(table_headers, header=True)]

        for building_usage in building_usages:
            building_usage_good = building_usage.replace('_', ' ')
            building_usage_good = building_usage_good.capitalize()

            building_sum = sum(
                [building_per_category[category_name][building_usage] for
                 category_name in category_names])

            # Filter building type that has no less than 25 items
            if building_sum >= 25:
                row = [tr(building_usage_good)]
                building_sum = 0
                for category_name in category_names:
                    building_sub_sum = building_per_category[category_name][
                        building_usage]
                    row.append(format_int(building_sub_sum))
                    building_sum += building_sub_sum

                row.append(format_int(building_sum))
                table_body.append(row)
            else:
                for category_name in category_names:
                    if category_name in other_sum.keys():
                        other_sum[category_name] += building_per_category[
                            category_name][building_usage]
                    else:
                        other_sum[category_name] = building_per_category[
                            category_name][building_usage]

        # Adding others building type to the report.
        other_row = [tr('Other')]
        other_building_total = 0
        for category_name in category_names:
            other_building_sum = other_sum[category_name]
            other_row.append(format_int(other_building_sum))
            other_building_total += other_building_sum

        other_row.append(format_int(other_building_total))
        table_body.append(other_row)

        all_row = [tr('Total')]
        all_row += [format_int(building_per_category[category_name]['total'])
                    for category_name in category_names]
        total = sum([building_per_category[category_name]['total'] for
                     category_name in category_names])
        all_row += [format_int(total)]

        table_body.append(TableRow(all_row, header=True))

        table_body += [TableRow(tr('Map shows buildings affected in each of '
                                   'the buffered zone.'))]

        impact_table = Table(table_body).toNewlineFreeString()
        impact_summary = impact_table

        # Extend impact report for on-screen display
        table_body.extend([TableRow(tr('Notes'), header=True),
                           tr('Total number of buildings %s in the viewable '
                              'area') % format_int(total),
                           tr('Only buildings available in OpenStreetMap '
                              'are considered.')])

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
        style_info = dict(target_field=target_field,
                          style_classes=style_classes,
                          style_type='categorizedSymbol')

        # For printing map purpose
        map_title = tr('Buildings affected by volcanic buffered point')
        legend_notes = tr('Thousand separator is represented by %s' %
                          get_thousand_separator())
        legend_units = tr('(building)')
        legend_title = tr('Building count')

        # Create vector layer and return
        impact_layer = Vector(
            data=features,
            projection=interpolated_layer.get_projection(),
            geometry=interpolated_layer.get_geometry(),
            name=tr('Buildings affected by volcanic buffered point'),
            keywords={'impact_summary': impact_summary,
                      'impact_table': impact_table,
                      'target_field': target_field,
                      'map_title': map_title,
                      'legend_notes': legend_notes,
                      'legend_units': legend_units,
                      'legend_title': legend_title},
            style_info=style_info)

        self._impact = impact_layer
        return impact_layer
