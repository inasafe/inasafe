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
    population_rounding)
from safe.impact_functions.styles import flood_population_style as style_info
from safe.storage.raster import Raster
from safe.utilities.i18n import tr
from safe.common.utilities import format_int
from safe.common.tables import Table, TableRow


class ContinuousHazardPopulationFunction(ImpactFunction):
    # noinspection PyUnresolvedReferences
    """Plugin for impact of population as derived by continuous hazard."""
    _metadata = ContinuousHazardPopulationMetadata()

    def __init__(self):
        super(ContinuousHazardPopulationFunction, self).__init__()
        self.impact_function_manager = ImpactFunctionManager()

    def _tabulate(self, high, low, medium, question, total_impact):
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

    def _tabulate_notes(self, minimum_needs, table_body, total, total_impact):
        # Extend impact report for on-screen display
        table_body.extend([
            TableRow(tr('Notes'), header=True),
            tr('Map shows population count in high or medium hazard area'),
            tr('Total population: %s') % format_int(total),
            TableRow(tr(
                'Table below shows the minimum needs for all '
                'affected people'))])
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

        # The 3 category
        high_t = self.parameters['Categorical thresholds'][2]
        medium_t = self.parameters['Categorical thresholds'][1]
        low_t = self.parameters['Categorical thresholds'][0]

        # Identify hazard and exposure layers
        hazard_layer = self.hazard    # Categorised Hazard
        exposure_layer = self.exposure  # Population Raster

        question = self.question()

        # Extract data as numeric arrays
        C = hazard_layer.get_data(nan=0.0)  # Category

        # Calculate impact as population exposed to each category
        P = exposure_layer.get_data(nan=0.0, scaling=True)
        H = numpy.where(C <= high_t, P, 0)
        M = numpy.where(C < medium_t, P, 0)
        L = numpy.where(C < low_t, P, 0)

        # Count totals
        total = int(numpy.sum(P))
        high = int(numpy.sum(H)) - int(numpy.sum(M))
        medium = int(numpy.sum(M)) - int(numpy.sum(L))
        low = int(numpy.sum(L))
        total_impact = high + medium + low

        # Don't show digits less than a 1000
        total = population_rounding(total)
        total_impact = population_rounding(total_impact)
        high = population_rounding(high)
        medium = population_rounding(medium)
        low = population_rounding(low)

        minimum_needs = [
            parameter.serialize() for parameter in
            self.parameters['minimum needs']
        ]

        table_body = self._tabulate(high, low, medium, question, total_impact)

        impact_table = Table(table_body).toNewlineFreeString()

        table_body, total_needs = self._tabulate_notes(
            minimum_needs, table_body, total, total_impact)

        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('People in high hazard areas')

        # Generate 8 equidistant classes across the range of flooded population
        # 8 is the number of classes in the predefined flood population style
        # as imported
        # noinspection PyTypeChecker
        classes = numpy.linspace(
            numpy.nanmin(M.flat[:]), numpy.nanmax(M.flat[:]), 8)

        # Modify labels in existing flood style to show quantities
        style_classes = style_info['style_classes']

        style_classes[1]['label'] = tr('Low [%i people/cell]') % classes[1]
        style_classes[4]['label'] = tr('Medium [%i people/cell]') % classes[4]
        style_classes[7]['label'] = tr('High [%i people/cell]') % classes[7]

        style_info['legend_title'] = tr('Population Count')

        # Create raster object and return
        raster_layer = Raster(
            M,
            projection=hazard_layer.get_projection(),
            geotransform=hazard_layer.get_geotransform(),
            name=tr('Population which %s') % (
                self.impact_function_manager
                .get_function_title(self).lower()),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'map_title': map_title,
                'total_needs': total_needs},
            style_info=style_info)
        self._impact = raster_layer
        return raster_layer
