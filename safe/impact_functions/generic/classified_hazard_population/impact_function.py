# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid - **Flood classified raster
evacuation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'lucernae'
__date__ = '24/03/15'
__revision__ = '$Format:%H$'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')

import numpy

from safe.impact_functions.core import (
    evacuated_population_needs,
    population_rounding
)
from safe.storage.raster import Raster
from safe.common.utilities import (
    format_int,
    humanize_class,
    create_classes,
    create_label,
    get_thousand_separator)
from safe.utilities.i18n import tr
from safe.common.tables import Table, TableRow
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.generic.\
    classified_hazard_population.metadata_definitions import \
    ClassifiedHazardPopulationMetadata
from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager


class ClassifiedHazardPopulationFunction(ImpactFunction):
    # noinspection PyUnresolvedReferences
    """Plugin for impact of population as derived by classified hazard."""
    
    _metadata = ClassifiedHazardPopulationMetadata()

    def __init__(self):
        super(ClassifiedHazardPopulationFunction, self).__init__()
        self.impact_function_manager = ImpactFunctionManager()

    def _tabulate(self, high, low, medium, minimum_needs, no_impact, question,
                  total_impact):
        # Generate impact report for the pdf map
        table_body = [question,
                      TableRow([tr('Total Population Affected '),
                                '%s' % format_int(total_impact)],
                               header=True),
                      TableRow([tr('Population in High hazard class areas '),
                                '%s' % format_int(high)]),
                      TableRow([tr('Population in Medium hazard class areas '),
                                '%s' % format_int(medium)]),
                      TableRow([tr('Population in Low hazard class areas '),
                                '%s' % format_int(low)]),
                      TableRow([tr('Population Not Affected'),
                                '%s' % format_int(no_impact)]),
                      TableRow(
                          tr('Table below shows the minimum needs for all '
                             'evacuated people'))]
        total_needs = evacuated_population_needs(
            total_impact, minimum_needs)
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

    def _tabulate_action_checklist(self, table_body, total):
        table_body.append(
            TableRow(tr('Action Checklist:'), header=True))
        table_body.append(
            TableRow(tr('How will warnings be disseminated?')))
        table_body.append(
            TableRow(tr('How will we reach stranded people?')))
        table_body.append(
            TableRow(tr('Do we have enough relief items?')))
        table_body.append(
            TableRow(
                tr('If yes, where are they located and how will we distribute '
                   'them?')))
        table_body.append(
            TableRow(
                tr('If no, where can we obtain additional relief items from '
                   'and how will we transport them to here?')))
        # Extend impact report for on-screen display
        table_body.extend([
            TableRow(tr('Notes'), header=True),
            tr('Map shows the numbers of people in high, medium, and low '
               'hazard class areas'),
            tr('Total population: %s') % format_int(total)
        ])
        return table_body

    def run(self, layers=None):
        """Plugin for impact of population as derived by classified hazard.

        Input
        :param layers: List of layers expected to contain

              * hazard_layer: Raster layer of classified hazard
              * exposure_layer: Raster layer of population data

        Counts number of people exposed to each class of the hazard

        Return
          Map of population exposed to high class
          Table with number of people in each class
        """
        self.validate()
        self.prepare(layers)

        # The 3 classes
        low_t = self.parameters['low_hazard_class']
        medium_t = self.parameters['medium_hazard_class']
        high_t = self.parameters['high_hazard_class']

        # Identify hazard and exposure layers
        hazard_layer = self.hazard  # Classified Hazard
        exposure_layer = self.exposure  # Population Raster

        question = self.question()

        # Extract data as numeric arrays
        data = hazard_layer.get_data(nan=0.0)  # Class

        # Calculate impact as population exposed to each class
        population = exposure_layer.get_data(nan=0.0, scaling=True)
        if high_t == 0:
            hi = numpy.where(0, population, 0)
        else:
            hi = numpy.where(data == high_t, population, 0)
        if medium_t == 0:
            med = numpy.where(0, population, 0)
        else:
            med = numpy.where(data == medium_t, population, 0)
        if low_t == 0:
            lo = numpy.where(0, population, 0)
        else:
            lo = numpy.where(data == low_t, population, 0)
        if high_t == 0:
            impact = numpy.where(
                (data == low_t) +
                (data == medium_t),
                population, 0)
        elif medium_t == 0:
            impact = numpy.where(
                (data == low_t) +
                (data == high_t),
                population, 0)
        elif low_t == 0:
            impact = numpy.where(
                (data == medium_t) +
                (data == high_t),
                population, 0)
        else:
            impact = numpy.where(
                (data == low_t) +
                (data == medium_t) +
                (data == high_t),
                population, 0)

        # Count totals
        total = int(numpy.sum(population))
        high = int(numpy.sum(hi))
        medium = int(numpy.sum(med))
        low = int(numpy.sum(lo))
        total_impact = int(numpy.sum(impact))

        # Perform population rounding based on number of people
        no_impact = population_rounding(total - total_impact)
        total = population_rounding(total)
        total_impact = population_rounding(total_impact)
        high = population_rounding(high)
        medium = population_rounding(medium)
        low = population_rounding(low)

        minimum_needs = [
            parameter.serialize() for parameter in
            self.parameters['minimum needs']
        ]

        table_body, total_needs = self._tabulate(high, low, medium,
                                                 minimum_needs, no_impact,
                                                 question, total_impact)

        impact_table = Table(table_body).toNewlineFreeString()

        table_body = self._tabulate_action_checklist(table_body, total)
        impact_summary = Table(table_body).toNewlineFreeString()

        # Create style
        colours = [
            '#FFFFFF', '#38A800', '#79C900', '#CEED00',
            '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        classes = create_classes(impact.flat[:], len(colours))
        interval_classes = humanize_class(classes)
        style_classes = []

        for i in xrange(len(colours)):
            style_class = dict()
            if i == 1:
                label = create_label(interval_classes[i], 'Low')
            elif i == 4:
                label = create_label(interval_classes[i], 'Medium')
            elif i == 7:
                label = create_label(interval_classes[i], 'High')
            else:
                label = create_label(interval_classes[i])
            style_class['label'] = label
            style_class['quantity'] = classes[i]
            if i == 0:
                transparency = 30
            else:
                transparency = 30
            style_class['transparency'] = transparency
            style_class['colour'] = colours[i]
            style_classes.append(style_class)

        style_info = dict(
            target_field=None,
            style_classes=style_classes,
            style_type='rasterStyle')

        # For printing map purpose
        map_title = tr('Population affected by each class')
        legend_notes = tr(
            'Thousand separator is represented by %s' %
            get_thousand_separator())
        legend_units = tr('(people per cell)')
        legend_title = tr('Number of People')

        # Create raster object and return
        raster_layer = Raster(
            impact,
            projection=hazard_layer.get_projection(),
            geotransform=hazard_layer.get_geotransform(),
            name=tr('Population which %s') % (
                self.impact_function_manager
                .get_function_title(self).lower()),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'map_title': map_title,
                'legend_notes': legend_notes,
                'legend_units': legend_units,
                'legend_title': legend_title,
                'total_needs': total_needs},
            style_info=style_info)
        self._impact = raster_layer
        return raster_layer
