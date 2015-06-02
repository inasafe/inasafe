# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid - **Flood polygon evacuation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""
__author__ = 'Rizky Maulana Nugraha'

import logging
from numbers import Number
import numpy

from safe.utilities.i18n import tr
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.core import (
    population_rounding_full,
    population_rounding,
    evacuated_population_needs,
    has_no_data)
from safe.impact_functions.inundation.flood_polygon_population \
    .metadata_definitions import FloodEvacuationVectorHazardMetadata
from safe.common.tables import Table, TableRow, TableCell
from safe.storage.raster import Raster
from safe.common.utilities import (
    format_int,
    create_classes,
    humanize_class,
    create_label)
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    get_needs_provenance_value, filter_needs_parameters
from safe.utilities.unicode import get_unicode
from safe.common.exceptions import ZeroImpactException

LOGGER = logging.getLogger('InaSAFE')


class FloodEvacuationVectorHazardFunction(ImpactFunction):
    # noinspection PyUnresolvedReferences
    """Impact function for vector flood evacuation."""
    _metadata = FloodEvacuationVectorHazardMetadata()

    def __init__(self):
        """Constructor."""
        super(FloodEvacuationVectorHazardFunction, self).__init__()

        # Use affected field flag (if False, all polygon will be considered as
        # affected)
        self.use_affected_field = False

        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)

    def _tabulate(self, affected_population, evacuated, minimum_needs,
                  question, rounding, rounding_evacuated):
        # People Affected
        table_body = [
            question,
            TableRow(
                [tr('People affected'), '%s*' % (
                    format_int(int(affected_population)))],
                header=True)]
        if self.use_affected_field:
            table_body.append(
                TableRow(
                    tr('* People are considered to be affected if they are '
                       'within the area where the value of the hazard field ('
                       '"%s") is "%s"') %
                    (self.parameters['affected_field'],
                     self.parameters['affected_value'])))
        else:
            table_body.append(
                TableRow(
                    tr('* People are considered to be affected if they are '
                       'within any polygons.')))
        table_body.append(
            TableRow([TableCell(
                tr('* Number is rounded up to the nearest %s') % rounding,
                col_span=2)]))

        # People Needing Evacuation
        table_body.append(
            TableRow([tr('People needing evacuation'), '%s*' % (
                format_int(int(evacuated)))], header=True))
        table_body.append(TableRow(
            [TableCell(
                tr('* Number is rounded up to the nearest %s') %
                rounding_evacuated, col_span=2)]))
        table_body.append(
            TableRow(
                [tr('Evacuation threshold'), '%s%%' % format_int(
                    self.parameters['evacuation_percentage'])], header=True))
        table_body.append(
            TableRow(tr('Table below shows the weekly minimum needs for all '
                        'evacuated people')))

        total_needs = evacuated_population_needs(evacuated, minimum_needs)
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
        return table_body, total_needs

    def _tabulate_action_checklist(self, table_body, total, nan_warning):
        # Action Checklist
        table_body.append(TableRow(tr('Action Checklist:'), header=True))
        table_body.append(TableRow(tr('How will warnings be disseminated?')))
        table_body.append(TableRow(tr('How will we reach stranded people?')))
        table_body.append(TableRow(tr('Do we have enough relief items?')))
        table_body.append(TableRow(
            'If yes, where are they located and how will we distribute '
            'them?'))
        table_body.append(TableRow(
            'If no, where can we obtain additional relief items from and '
            'how will we transport them to here?'))

        # Notes
        table_body.append(TableRow(tr('Notes'), header=True))
        table_body.append(
            TableRow(tr('Total population: %s') % format_int(total)))
        table_body.append(TableRow(get_needs_provenance_value(
            self.parameters)))
        if nan_warning:
            table_body.extend([
                tr('The population layer contained `no data`. This missing '
                   'data was carried through to the impact layer.'),
                tr('`No data` values in the impact layer were treated as 0 '
                   'when counting the affected or total population.')
            ])

    def run(self, layers=None):
        """Risk plugin for flood population evacuation.

        :param layers: List of layers expected to contain

            * hazard_layer : Vector polygon layer of flood depth
            * exposure_layer : Raster layer of population data on the same grid
                as hazard_layer

        Counts number of people exposed to areas identified as flood prone

        :returns: Map of population exposed to flooding Table with number of
            people evacuated and supplies required.
        :rtype: tuple
        """
        self.validate()
        self.prepare(layers)

        # Get the IF parameters
        affected_field = self.parameters['affected_field']
        affected_value = self.parameters['affected_value']
        evacuation_percentage = self.parameters['evacuation_percentage']

        # Identify hazard and exposure layers
        hazard_layer = self.hazard
        exposure_layer = self.exposure

        # Check that hazard is polygon type
        if not hazard_layer.is_polygon_data:
            message = (
                'Input hazard must be a polygon layer. I got %s with layer '
                'type %s' % (
                    hazard_layer.get_name(),
                    hazard_layer.get_geometry_name()))
            raise Exception(message)

        nan_warning = False
        if has_no_data(exposure_layer.get_data(nan=True)):
            nan_warning = True

        # Check that affected field exists in hazard layer
        if affected_field in hazard_layer.get_attribute_names():
            self.use_affected_field = True

        # Run interpolation function for polygon2raster
        interpolated_layer, covered_exposure = \
            assign_hazard_values_to_exposure_data(
                hazard_layer,
                exposure_layer,
                attribute_name=self.target_field)

        # Data for manipulating the covered_exposure layer
        new_covered_exposure_data = covered_exposure.get_data()
        covered_exposure_top_left = numpy.array([
            covered_exposure.get_geotransform()[0],
            covered_exposure.get_geotransform()[3]])
        covered_exposure_dimension = numpy.array([
            covered_exposure.get_geotransform()[1],
            covered_exposure.get_geotransform()[5]])

        # Count affected population per polygon, per category and total
        total_affected_population = 0
        for attr in interpolated_layer.get_data():
            affected = False
            if self.use_affected_field:
                row_affected_value = attr[affected_field]
                if row_affected_value is not None:
                    if isinstance(row_affected_value, Number):
                        type_func = type(row_affected_value)
                        affected = row_affected_value == type_func(
                            affected_value)
                    else:
                        affected =\
                            get_unicode(affected_value).lower() == \
                            get_unicode(row_affected_value).lower()
            else:
                # assume that every polygon is affected (see #816)
                affected = True

            if affected:
                # Get population at this location
                population = attr[self.target_field]
                if not numpy.isnan(population):
                    population = float(population)
                    total_affected_population += population
            else:
                # If it's not affected, set the value of the impact layer to 0
                grid_point = attr['grid_point']
                index = numpy.floor(
                    (grid_point - covered_exposure_top_left) / (
                        covered_exposure_dimension)).astype(int)
                new_covered_exposure_data[index[1]][index[0]] = 0

        # Estimate number of people in need of evacuation
        evacuated = (
            total_affected_population * evacuation_percentage / 100.0)

        total_population = int(
            numpy.nansum(exposure_layer.get_data(scaling=False)))

        minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
        ]

        # Rounding
        total_affected_population, rounding = population_rounding_full(
            total_affected_population)
        total_population = population_rounding(total_population)
        evacuated, rounding_evacuated = population_rounding_full(evacuated)

        # Generate impact report for the pdf map
        table_body, total_needs = self._tabulate(
            total_affected_population,
            evacuated,
            minimum_needs,
            self.question,
            rounding,
            rounding_evacuated)

        impact_table = Table(table_body).toNewlineFreeString()

        self._tabulate_action_checklist(
            table_body,
            total_population,
            nan_warning)
        impact_summary = Table(table_body).toNewlineFreeString()

        # Create style
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        classes = create_classes(
            new_covered_exposure_data.flat[:], len(colours))

        # check for zero impact
        if min(classes) == 0 == max(classes):
            table_body = [
                self.question,
                TableRow(
                    [tr('People affected'),
                     '%s' % format_int(total_affected_population)],
                    header=True)]
            message = Table(table_body).toNewlineFreeString()
            raise ZeroImpactException(message)

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
        map_title = tr('People affected by flood prone areas')
        legend_notes = tr('Thousand separator is represented by \'.\'')
        legend_units = tr('(people per polygon)')
        legend_title = tr('Population Count')

        # Create vector layer and return
        impact_layer = Raster(
            data=new_covered_exposure_data,
            projection=covered_exposure.get_projection(),
            geotransform=covered_exposure.get_geotransform(),
            name=tr('People affected by flood prone areas'),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'target_field': self.target_field,
                'map_title': map_title,
                'legend_notes': legend_notes,
                'legend_units': legend_units,
                'legend_title': legend_title,
                'affected_population': total_affected_population,
                'total_population': total_population,
                'total_needs': total_needs},
            style_info=style_info)
        self._impact = impact_layer
        return impact_layer
