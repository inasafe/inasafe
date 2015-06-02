# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Volcano Point on
Population Impact Function.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import numpy

from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.volcanic.volcano_point_population\
    .metadata_definitions import VolcanoPointPopulationFunctionMetadata
from safe.impact_functions.core import (
    evacuated_population_needs,
    population_rounding,
    has_no_data)
from safe.engine.utilities import buffer_points
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.storage.raster import Raster
from safe.utilities.i18n import tr
from safe.common.utilities import (
    format_int,
    humanize_class,
    create_classes,
    create_label,
    get_thousand_separator)
from safe.common.tables import Table, TableRow
from safe.common.exceptions import ZeroImpactException
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    filter_needs_parameters


class VolcanoPointPopulationFunction(ImpactFunction):
    """Impact Function for Volcano Point on Population."""

    _metadata = VolcanoPointPopulationFunctionMetadata()

    def __init__(self):
        super(VolcanoPointPopulationFunction, self).__init__()
        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)
        # TODO: alternatively to specifying the question here we should
        # TODO: consider changing the 'population' metadata concept to 'people'
        self.question = (
            'In the event of a volcano point how many people might be impacted'
        )

    def run(self, layers=None):
        """Run volcano point population evacuation Impact Function.

        :param layers: List of layers expected to contain where two layers
            should be present.

            * hazard_layer: Vector point layer.
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
        radii = self.parameters['distance [km]']
        name_attribute = self.parameters['volcano name attribute']

        # Identify hazard and exposure layers
        hazard_layer = self.hazard
        exposure_layer = self.exposure

        # Input checks
        if not hazard_layer.is_point_data:
            msg = (
                'Input hazard must be a polygon or point layer. I got %s with '
                'layer type %s' % (hazard_layer.get_name(),
                                   hazard_layer.get_geometry_name()))
            raise Exception(msg)

        data_table = hazard_layer.get_data()

        # Use concentric circles
        category_title = 'Radius'
        category_header = tr('Distance [km]')

        centers = hazard_layer.get_geometry()
        rad_m = [x * 1000 for x in radii]  # Convert to meters
        hazard_layer = buffer_points(
            centers, rad_m, category_title, data_table=data_table)

        # Get names of volcanoes considered
        if name_attribute in hazard_layer.get_attribute_names():
            volcano_name_list = []
            # Run through all polygons and get unique names
            for row in data_table:
                volcano_name_list.append(row[name_attribute])

            volcano_names = ''
            for radius in volcano_name_list:
                volcano_names += '%s, ' % radius
            volcano_names = volcano_names[:-2]  # Strip trailing ', '
        else:
            volcano_names = tr('Not specified in data')

        # Run interpolation function for polygon2raster
        interpolated_layer, covered_exposure_layer = \
            assign_hazard_values_to_exposure_data(
                hazard_layer,
                exposure_layer,
                attribute_name=self.target_field
            )

        # Initialise affected population per categories
        affected_population = {}
        for radius in rad_m:
            affected_population[radius] = 0

        nan_warning = False
        if has_no_data(exposure_layer.get_data(nan=True)):
            nan_warning = True
        # Count affected population per polygon and total
        for row in interpolated_layer.get_data():
            # Get population at this location
            population = row[self.target_field]
            if not numpy.isnan(population):
                population = float(population)
                # Update population count for this category
                category = row[category_title]
                affected_population[category] += population

        # Count totals
        total_population = population_rounding(
            int(numpy.nansum(exposure_layer.get_data())))

        # Count cumulative for each zone
        total_affected_population = 0
        cumulative_affected_population = {}
        for radius in rad_m:
            population = int(affected_population.get(radius, 0))
            total_affected_population += population
            cumulative_affected_population[radius] = total_affected_population

        minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
        ]

        # Generate impact report for the pdf map
        blank_cell = ''
        table_body = [
            self.question,
            TableRow(
                [tr('Volcanoes considered'),
                 '%s' % volcano_names,
                 blank_cell],
                header=True),
            TableRow(
                [tr('People needing evacuation'),
                 '%s' % format_int(
                     population_rounding(total_affected_population)),
                 blank_cell],
                header=True),
            TableRow(
                [category_header,
                 tr('Total'),
                 tr('Cumulative')],
                header=True)]

        for radius in rad_m:
            table_body.append(
                TableRow(
                    [radius,
                     format_int(
                         population_rounding(
                             affected_population[radius])),
                     format_int(
                         population_rounding(
                             cumulative_affected_population[radius]))]))

        table_body.extend([
            TableRow(tr(
                'Map shows the number of people affected in each of volcano '
                'hazard polygons.'))])

        total_needs = evacuated_population_needs(
            total_affected_population, minimum_needs)
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

        if nan_warning:
            table_body.extend([
                tr('The population layer contained `no data`. This missing '
                   'data was carried through to the impact layer.'),
                tr('`No data` values in the impact layer were treated as 0 '
                   'when counting the affected or total population.')
            ])

        impact_summary = Table(table_body).toNewlineFreeString()

        # check for zero impact
        if total_affected_population == 0:
            table_body = [
                self.question,
                TableRow(
                    [tr('People needing evacuation'),
                     '%s' % format_int(total_affected_population),
                     blank_cell],
                    header=True)]
            message = Table(table_body).toNewlineFreeString()
            raise ZeroImpactException(message)

        # Create style
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        classes = create_classes(
            covered_exposure_layer.get_data().flat[:], len(colours))
        interval_classes = humanize_class(classes)
        # Define style info for output polygons showing population counts
        style_classes = []
        for i in xrange(len(colours)):
            style_class = dict()
            style_class['label'] = create_label(interval_classes[i])
            if i == 1:
                label = create_label(
                    interval_classes[i],
                    tr('Low Population [%i people/cell]' % classes[i]))
            elif i == 4:
                label = create_label(
                    interval_classes[i],
                    tr('Medium Population [%i people/cell]' % classes[i]))
            elif i == 7:
                label = create_label(
                    interval_classes[i],
                    tr('High Population [%i people/cell]' % classes[i]))
            else:
                label = create_label(interval_classes[i])

            if i == 0:
                transparency = 100
            else:
                transparency = 0

            style_class['label'] = label
            style_class['quantity'] = classes[i]
            style_class['colour'] = colours[i]
            style_class['transparency'] = transparency
            style_classes.append(style_class)

        # Override style info with new classes and name
        style_info = dict(
            target_field=None,
            style_classes=style_classes,
            style_type='rasterStyle')

        # For printing map purpose
        map_title = tr('People affected by the buffered point volcano')
        legend_notes = tr('Thousand separator is represented by  %s' %
                          get_thousand_separator())
        legend_units = tr('(people per cell)')
        legend_title = tr('Population')

        # Create vector layer and return
        impact_layer = Raster(
            data=covered_exposure_layer.get_data(),
            projection=covered_exposure_layer.get_projection(),
            geotransform=covered_exposure_layer.get_geotransform(),
            name=tr('People affected by the buffered point volcano'),
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
