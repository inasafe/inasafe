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

from safe.impact_functions.generic\
    .continuous_hazard_population.metadata_definitions import \
    ContinuousHazardPopulationMetadata
from safe.impact_functions.bases.continuous_rh_continuous_re import \
    ContinuousRHContinuousRE
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.core import (
    population_rounding,
    has_no_data)
from safe.storage.raster import Raster
from safe.utilities.i18n import tr
from safe.common.utilities import get_thousand_separator
from safe.impact_functions.core import no_population_impact_message
from safe.common.utilities import create_classes, create_label, humanize_class
from safe.common.exceptions import (
    FunctionParametersError, ZeroImpactException)
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    filter_needs_parameters
from safe.impact_reports.population_exposure_report_mixin import \
    PopulationExposureReportMixin
import safe.messaging as m
from safe.messaging import styles


class ContinuousHazardPopulationFunction(
        ContinuousRHContinuousRE,
        PopulationExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Plugin for impact of population as derived by continuous hazard."""
    _metadata = ContinuousHazardPopulationMetadata()

    def __init__(self):
        super(ContinuousHazardPopulationFunction, self).__init__()
        self.impact_function_manager = ImpactFunctionManager()

        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)
        self.no_data_warning = False

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        message.add(
            m.Heading(tr('Notes and assumptions'), **styles.INFO_STYLE))
        checklist = m.BulletedList()
        checklist.add(tr(
            'Total population in the analysis area: %s'
            ) % population_rounding(self.total_population))
        checklist.add(tr(
            '<sup>1</sup>People need evacuation if they are in a '
            'hazard zone.'))
        checklist.add(tr(
            'Map shows the numbers of people in high, medium, '
            'and low hazard class areas.'))
        if self.no_data_warning:
            checklist.add(tr(
                'The layers contained "no data" values. This missing data '
                'was carried through to the impact layer.'))
            checklist.add(tr(
                '"No data" values in the impact layer were treated as 0 '
                'when counting the affected or total population.'))
        checklist.add(tr(
            'All values are rounded up to the nearest integer in '
            'order to avoid representing human lives as fractions.'))
        checklist.add(tr(
            'Population rounding is applied to all population '
            'values, which may cause discrepancies when adding value.'))
        message.add(checklist)
        return message

    def run(self):
        """Plugin for impact of population as derived by continuous hazard.

        Hazard is reclassified into 3 classes based on the extrema provided
        as impact function parameters.

        Counts number of people exposed to each category of the hazard

        :returns:
          Map of population exposed to high category
          Table with number of people in each category
        """
        self.validate()
        self.prepare()

        thresholds = [
            p.value for p in self.parameters['Categorical thresholds'].value]

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

        # Extract data as numeric arrays
        hazard_data = self.hazard.layer.get_data(nan=True)  # Category
        if has_no_data(hazard_data):
            self.no_data_warning = True

        # Calculate impact as population exposed to each category
        exposure_data = self.exposure.layer.get_data(nan=True, scaling=True)
        if has_no_data(exposure_data):
            self.no_data_warning = True

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
        self.total_population = int(numpy.nansum(exposure_data))
        self.affected_population[
            tr('Population in high hazard areas')] = int(
                numpy.nansum(high_exposure))
        self.affected_population[
            tr('Population in medium hazard areas')] = int(
                numpy.nansum(medium_exposure))
        self.affected_population[
            tr('Population in low hazard areas')] = int(
                numpy.nansum(low_exposure))
        self.unaffected_population = (
            self.total_population - self.total_affected_population)

        # check for zero impact
        if self.total_affected_population == 0:
            message = no_population_impact_message(self.question)
            raise ZeroImpactException(message)

        # Don't show digits less than a 1000
        self.minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
        ]
        total_needs = self.total_needs

        impact_table = impact_summary = self.html_report()

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

        # For printing map purpose
        map_title = tr('People in each hazard areas (low, medium, high)')
        legend_title = tr('Number of People')
        legend_units = tr('(people per cell)')
        legend_notes = tr(
            'Thousand separator is represented by %s' %
            get_thousand_separator())

        # Create raster object and return
        raster_layer = Raster(
            data=impacted_exposure,
            projection=self.hazard.layer.get_projection(),
            geotransform=self.hazard.layer.get_geotransform(),
            name=tr('Population might %s') % (
                self.impact_function_manager.
                get_function_title(self).lower()),
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
