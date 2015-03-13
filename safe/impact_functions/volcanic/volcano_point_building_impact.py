# coding=utf-8
"""
InaSAFE Disaster risk tool by Australian Aid - Volcano Point impact on
buildings.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from collections import OrderedDict

from safe.impact_functions.core import (
    FunctionProvider, get_hazard_layer, get_exposure_layer, get_question)
from safe.impact_functions.impact_function_metadata import (
    ImpactFunctionMetadata)
from safe.definitions import (
    hazard_volcano,
    unit_volcano_categorical,
    layer_vector_polygon,
    layer_vector_point,
    exposure_structure,
    unit_building_type_type,
    exposure_definition,
    hazard_definition,
    unit_building_generic)
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


class VolcanoPointBuildingImpact(FunctionProvider):
    """Risk plugin for volcano point building impact.

    :author AIFDR
    :rating 4
    :param requires category=='hazard' and \
                    subcategory in ['volcano'] and \
                    layertype=='vector' and \
                    data_type=='point'

    :param requires category=='exposure' and \
                    subcategory=='structure' and \
                    layertype=='vector'
    """

    class Metadata(ImpactFunctionMetadata):
        """Metadata for Volcano Point Building Impact.

        .. versionadded:: 2.1

        We only need to re-implement get_metadata(), all other behaviours
        are inherited from the abstract base class.
        """

        @staticmethod
        def get_metadata():
            """Return metadata as a dictionary.

            This is a static method. You can use it to get the metadata in
            dictionary format for an impact function.

            :returns: A dictionary representing all the metadata for the
                concrete impact function.
            :rtype: dict
            """
            dict_meta = {
                'id': 'VolcanoPointBuildingImpact',
                'name': tr('Volcano Point On Building Impact'),
                'impact': tr('Be affected'),
                'title': tr('Be affected'),
                'author': 'AIFDR',
                'date_implemented': 'N/A',
                'overview': tr(
                    'To assess the impacts of volcano point on building.'),
                'detailed_description': '',
                'hazard_input': tr(
                    'The hazard layer must be a point layer. '
                    'This point will be buffered with the radii specified in '
                    'the parameters as the hazard zone. If you want to see '
                    'the name of the volcano in the result, you need to '
                    'specify the volcano name attribute in the Impact Function '
                    'option.'),
                'exposure_input': tr(
                    'Vector polygon layer extracted from OSM where each '
                    'polygon represents the footprint of a building.'),
                'output': tr(
                    'Vector layer contains Map of building exposed to '
                    'volcanic hazard zones for each  radius.'),
                'actions': tr(
                    'Provide details about how many building would likely be '
                    'affected by each hazard zones.'),
                'limitations': [],
                'citations': [],
                'categories': {
                    'hazard': {
                        'definition': hazard_definition,
                        'subcategories': [hazard_volcano],
                        'units': [unit_volcano_categorical],
                        'layer_constraints': [
                            layer_vector_point
                        ]
                    },
                    'exposure': {
                        'definition': exposure_definition,
                        'subcategories': [exposure_structure],
                        'units': [
                            unit_building_type_type,
                            unit_building_generic],
                        'layer_constraints': [
                            layer_vector_polygon,
                            layer_vector_point]
                    }
                }
            }
            return dict_meta

    parameters = OrderedDict([
        # The list of radii in km for volcano point hazard
        ('distances [km]', [3, 5, 10]),

        # The attribute for name of the volcano in hazard layer
        ('volcano name attribute', 'NAME')])

    def run(self, layers):
        """Risk plugin for volcano hazard on building/structure.

        Counts number of building exposed to each volcano hazard zones.

        :param layers: List of layers expected to contain.
                * hazard_layer: Hazard layer of volcano
                * exposure_layer: Vector layer of structure data on
                the same grid as hazard_layer

        :returns: Map of building exposed to volcanic hazard zones.
                  Table with number of buildings affected
        :rtype: dict
        """
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
        hazard_layer = get_hazard_layer(layers)  # Volcano hazard layer
        exposure_layer = get_exposure_layer(layers)  # Building exposure layer

        # Get question
        question = get_question(
            hazard_layer.get_name(), exposure_layer.get_name(), self)

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
        table_body = [question,
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
            geometry=interpolated_layer.get_geometry(as_geometry_objects=True),
            name=tr('Buildings affected by volcanic buffered point'),
            keywords={'impact_summary': impact_summary,
                      'impact_table': impact_table,
                      'target_field': target_field,
                      'map_title': map_title,
                      'legend_notes': legend_notes,
                      'legend_units': legend_units,
                      'legend_title': legend_title},
            style_info=style_info)
        return impact_layer
