# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Volcano Polygon on
Population Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import numpy

from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.volcanic.volcano_polygon_population\
    .metadata_definitions import VolcanoPolygonPopulationFunctionMetadata
from safe.impact_functions.core import (
    evacuated_population_needs,
    population_rounding)
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.storage.vector import Vector
from safe.utilities.i18n import tr
from safe.common.utilities import (
    format_int,
    humanize_class,
    create_classes,
    create_label,
    get_thousand_separator,
    get_non_conflicting_attribute_name)
from safe.common.tables import Table, TableRow
from safe.common.exceptions import InaSAFEError, ZeroImpactException
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters


class VolcanoPolygonPopulationFunction(ImpactFunction):
    """Impact Function for Volcano Point on Building."""

    _metadata = VolcanoPolygonPopulationFunctionMetadata()

    def __init__(self):
        super(VolcanoPolygonPopulationFunction, self).__init__()
        self.target_field = 'population'
        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)

    def run(self, layers=None):
        """Run volcano population evacuation Impact Function.

        :param layers: List of layers expected to contain where two layers
            should be present.

            * hazard_layer: Vector polygon layer of volcano impact zones
            * exposure_layer: Raster layer of population data on the same grid
                as hazard_layer

        Counts number of people exposed to volcano event.

        :returns: Map of population exposed to the volcano hazard zone.
            The returned dict will include a table with number of people
            evacuated and supplies required.
        :rtype: dict

        :raises:
            * Exception - When hazard layer is not vector layer
            * RadiiException - When radii are not valid (they need to be
                monotonically increasing)
        """
        self.validate()
        self.prepare(layers)

        # Parameters
        hazard_zone_attribute = self.parameters['hazard zone attribute']
        name_attribute = self.parameters['volcano name attribute']

        # Identify hazard and exposure layers
        hazard_layer = self.hazard
        exposure_layer = self.exposure

        # Input checks
        if not hazard_layer.is_polygon_data:
            msg = ('Input hazard must be a polygon layer. I got %s with '
                   'layer type %s' % (hazard_layer.get_name(),
                                      hazard_layer.get_geometry_name()))
            raise Exception(msg)

        # Check if hazard_zone_attribute exists in hazard_layer
        if hazard_zone_attribute not in hazard_layer.get_attribute_names():
            msg = ('Hazard data %s did not contain expected attribute %s ' % (
                hazard_layer.get_name(), hazard_zone_attribute))
            # noinspection PyExceptionInherit
            raise InaSAFEError(msg)

        features = hazard_layer.get_data()
        category_header = tr('Category')
        hazard_zone_categories = list(
            set(hazard_layer.get_data(hazard_zone_attribute)))

        # Get names of volcanoes considered
        if name_attribute in hazard_layer.get_attribute_names():
            volcano_name_list = []
            # Run through all polygons and get unique names
            for row in features:
                volcano_name_list.append(row[name_attribute])

            volcano_names = ''
            for name in volcano_name_list:
                volcano_names += '%s, ' % name
            volcano_names = volcano_names[:-2]  # Strip trailing ', '
        else:
            volcano_names = tr('Not specified in data')

        # Find the target field name that has no conflict with default target
        attribute_names = hazard_layer.get_attribute_names()
        new_target_field = get_non_conflicting_attribute_name(
            self.target_field, attribute_names)
        self.target_field = new_target_field

        # Run interpolation function for polygon2raster
        interpolated_layer = assign_hazard_values_to_exposure_data(
            hazard_layer, exposure_layer, attribute_name=self.target_field)

        # Initialise data_table of output dataset with all data_table
        # from input polygon and a population count of zero
        new_data_table = hazard_layer.get_data()
        categories = {}
        for row in new_data_table:
            row[self.target_field] = 0
            category = row[hazard_zone_attribute]
            categories[category] = 0

        # Count affected population per polygon and total
        for row in interpolated_layer.get_data():
            # Get population at this location
            population = float(row[self.target_field])

            # Update population count for associated polygon
            poly_id = row['polygon_id']
            new_data_table[poly_id][self.target_field] += population

            # Update population count for each category
            category = new_data_table[poly_id][hazard_zone_attribute]
            categories[category] += population

        # Count totals
        total_population = population_rounding(
            int(numpy.sum(exposure_layer.get_data(nan=0))))

        # Count number and cumulative for each zone
        cumulative = 0
        all_categories_population = {}
        all_categories_cumulative = {}
        for name in hazard_zone_categories:
            key = name
            # prevent key error
            population = int(categories.get(key, 0))

            cumulative += population

            # I'm not sure whether this is the best place to apply rounding?
            all_categories_population[name] = population_rounding(population)
            all_categories_cumulative[name] = population_rounding(cumulative)

        # Use final accumulation as total number needing evacuation
        evacuated = population_rounding(cumulative)

        minimum_needs = [
            parameter.serialize() for parameter in
            self.parameters['minimum needs']
        ]

        # Generate impact report for the pdf map
        blank_cell = ''
        table_body = [self.question,
                      TableRow([tr('Volcanoes considered'),
                                '%s' % volcano_names, blank_cell],
                               header=True),
                      TableRow([tr('People needing evacuation'),
                                '%s' % format_int(evacuated),
                                blank_cell],
                               header=True),
                      TableRow([category_header,
                                tr('Total'), tr('Cumulative')],
                               header=True)]

        for name in hazard_zone_categories:
            table_body.append(
                TableRow([name,
                          format_int(all_categories_population[name]),
                          format_int(all_categories_cumulative[name])]))

        table_body.extend([
            TableRow(tr(
                'Map shows the number of people affected in each of volcano '
                'hazard polygons.'))])

        total_needs = evacuated_population_needs(
            evacuated, minimum_needs)
        for frequency, needs in total_needs.items():
            table_body.append(TableRow(
                [
                    tr('Needs should be provided %s' % frequency),
                    tr('Total')
                ],
                header=True))
            for resource in needs:
                table_body.append(TableRow([
                    tr(resource['table name']),
                    format_int(resource['amount'])]))
        impact_table = Table(table_body).toNewlineFreeString()

        # Extend impact report for on-screen display
        table_body.extend(
            [TableRow(tr('Notes'), header=True),
             tr('Total population %s in the exposure layer') % format_int(
                 total_population),
             tr('People need evacuation if they are within the '
                'volcanic hazard zones.')])

        population_counts = [x[self.target_field] for x in new_data_table]
        impact_summary = Table(table_body).toNewlineFreeString()

        # check for zero impact
        if numpy.nanmax(population_counts) == 0 == numpy.nanmin(
                population_counts):
            table_body = [
                self.question,
                TableRow([tr('People needing evacuation'),
                          '%s' % format_int(evacuated),
                          blank_cell], header=True)]
            my_message = Table(table_body).toNewlineFreeString()
            raise ZeroImpactException(my_message)

        # Create style
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        classes = create_classes(population_counts, len(colours))
        interval_classes = humanize_class(classes)
        # Define style info for output polygons showing population counts
        style_classes = []
        for i in xrange(len(colours)):
            style_class = dict()
            style_class['label'] = create_label(interval_classes[i])
            if i == 0:
                transparency = 100
                style_class['min'] = 0
            else:
                transparency = 30
                style_class['min'] = classes[i - 1]
            style_class['transparency'] = transparency
            style_class['colour'] = colours[i]
            style_class['max'] = classes[i]
            style_classes.append(style_class)

        # Override style info with new classes and name
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='graduatedSymbol')

        # For printing map purpose
        map_title = tr('People affected by volcanic hazard zone')
        legend_notes = tr('Thousand separator is represented by  %s' %
                          get_thousand_separator())
        legend_units = tr('(people per cell)')
        legend_title = tr('Population')

        # Create vector layer and return
        impact_layer = Vector(
            data=new_data_table,
            projection=hazard_layer.get_projection(),
            geometry=hazard_layer.get_geometry(as_geometry_objects=True),
            name=tr('People affected by volcanic hazard zone'),
            keywords={'impact_summary': impact_summary,
                      'impact_table': impact_table,
                      'target_field': self.target_field,
                      'map_title': map_title,
                      'legend_notes': legend_notes,
                      'legend_units': legend_units,
                      'legend_title': legend_title,
                      'total_needs': total_needs},
            style_info=style_info)

        self._impact = impact_layer
        return impact_layer
