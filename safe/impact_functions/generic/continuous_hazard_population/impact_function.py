# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid - **Generic Impact Function
on Population for Continuous Hazard.**

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

from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.generic\
    .continuous_hazard_population.metadata_definitions import \
    ContinuousHazardPopulationMetadata
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.core import (
    evacuated_population_needs,
    population_rounding,
    has_no_data)
from safe.storage.raster import Raster
from safe.utilities.i18n import tr
from safe.common.utilities import format_int
from safe.common.tables import Table, TableRow
from safe.common.utilities import create_classes, create_label, humanize_class
from safe.common.exceptions import (
    FunctionParametersError, ZeroImpactException)
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    filter_needs_parameters


class ContinuousHazardPopulationFunction(ImpactFunction):
    # noinspection PyUnresolvedReferences
    """Plugin for impact of population as derived by continuous hazard."""
    _metadata = ContinuousHazardPopulationMetadata()

    def __init__(self):
        super(ContinuousHazardPopulationFunction, self).__init__()
        self.impact_function_manager = ImpactFunctionManager()

        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)

    def _tabulate(
            self,
            high,
            low,
            medium,
            question,
            total_impact):
        # Generate impact report for the pdf map
        table_body = [
            question,
            TableRow([tr('People impacted '),
                      '%s' % format_int(total_impact)],
                     header=True),
            TableRow([tr('People in high hazard area '),
                      '%s' % format_int(high)],
                     header=True),
            TableRow([tr('People in medium hazard area '),
                      '%s' % format_int(medium)],
                     header=True),
            TableRow([tr('People in low hazard area'),
                      '%s' % format_int(low)],
                     header=True)]
        return table_body

    def _tabulate_notes(
            self,
            minimum_needs,
            table_body,
            total,
            total_impact,
            no_data_warning):
        # Extend impact report for on-screen display
        table_body.extend([
            TableRow(tr('Notes'), header=True),
            tr('Map shows population count in high, medium, and low hazard '
               'area.'),
            tr('Total population: %s') % format_int(total),
            TableRow(tr(
                'Table below shows the minimum needs for all '
                'affected people'))])
        if no_data_warning:
            table_body.extend([
                tr('The layers contained `no data`. This missing data was '
                   'carried through to the impact layer.'),
                tr('`No data` values in the impact layer were treated as 0 '
                   'when counting the affected or total population.')
            ])

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

    def run(self, layers=None):
        """Plugin for impact of population as derived by categorised hazard.

        :param layers: List of layers expected to contain

            * hazard_layer: Raster layer of categorised hazard
            * exposure_layer: Raster layer of population data

        Counts number of people exposed to each category of the hazard

        :returns:
          Map of population exposed to high category
          Table with number of people in each category
        """
        self.validate()
        self.prepare(layers)

        thresholds = self.parameters['Categorical thresholds']

        # Thresholds must contain 3 thresholds
        if len(thresholds) != 3:
            raise FunctionParametersError(
                'The thresholds must consist of 3 values.')

        # Thresholds must monotonically increasing
        monotonically_increasing_flag = all(
            x < y for x, y in zip(thresholds, thresholds[1:]))
        if not monotonically_increasing_flag:
            raise FunctionParametersError(
                'Each threshold should be larger than the previous.')

        # The 3 categories
        low_t = thresholds[0]
        medium_t = thresholds[1]
        high_t = thresholds[2]

        # Identify hazard and exposure layers
        hazard_layer = self.hazard    # Categorised Hazard
        exposure_layer = self.exposure  # Population Raster

        # Extract data as numeric arrays
        hazard_data = hazard_layer.get_data(nan=True)  # Category
        no_data_warning = False
        if has_no_data(hazard_data):
            no_data_warning = True

        # Calculate impact as population exposed to each category
        exposure_data = exposure_layer.get_data(nan=True, scaling=True)
        if has_no_data(exposure_data):
            no_data_warning = True

        # Make 3 data for each zone. Get the value of the exposure if the
        # exposure is in the hazard zone, else just assign 0
        low_exposure = numpy.where(hazard_data < low_t, exposure_data, 0)
        medium_exposure = numpy.where(
            (hazard_data >= low_t) & (hazard_data < medium_t),
            exposure_data, 0)
        high_exposure = numpy.where(
            (hazard_data >= medium_t) & (hazard_data <= high_t),
            exposure_data, 0)
        impacted_exposure = low_exposure + medium_exposure + high_exposure

        # Count totals
        total = int(numpy.nansum(exposure_data))
        low_total = int(numpy.nansum(low_exposure))
        medium_total = int(numpy.nansum(medium_exposure))
        high_total = int(numpy.nansum(high_exposure))
        total_impact = high_total + medium_total + low_total

        # Check for zero impact
        if total_impact == 0:
            table_body = [
                self.question,
                TableRow(
                    [tr('People impacted'),
                     '%s' % format_int(total_impact)], header=True)]
            message = Table(table_body).toNewlineFreeString()
            raise ZeroImpactException(message)

        # Don't show digits less than a 1000
        total = population_rounding(total)
        total_impact = population_rounding(total_impact)
        low_total = population_rounding(low_total)
        medium_total = population_rounding(medium_total)
        high_total = population_rounding(high_total)

        minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
        ]

        table_body = self._tabulate(
            high_total, low_total, medium_total, self.question, total_impact)

        impact_table = Table(table_body).toNewlineFreeString()

        table_body, total_needs = self._tabulate_notes(
            minimum_needs, table_body, total, total_impact, no_data_warning)

        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('People in each hazard areas (low, medium, high)')

        # Style for impact layer
        colours = [
            '#FFFFFF', '#38A800', '#79C900', '#CEED00',
            '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        classes = create_classes(impacted_exposure.flat[:], len(colours))
        interval_classes = humanize_class(classes)
        style_classes = []

        for i in xrange(len(colours)):
            style_class = dict()
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
            style_class['label'] = label
            style_class['quantity'] = classes[i]
            if i == 0:
                transparency = 100
            else:
                transparency = 0
            style_class['transparency'] = transparency
            style_class['colour'] = colours[i]
            style_classes.append(style_class)

        style_info = dict(
            target_field=None,
            style_classes=style_classes,
            style_type='rasterStyle')

        # Create raster object and return
        raster_layer = Raster(
            data=impacted_exposure,
            projection=hazard_layer.get_projection(),
            geotransform=hazard_layer.get_geotransform(),
            name=tr('Population might %s') % (
                self.impact_function_manager.
                get_function_title(self).lower()),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'map_title': map_title,
                'total_needs': total_needs},
            style_info=style_info)
        self._impact = raster_layer
        return raster_layer
