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
import numpy

from definitionsv4.definitions_v3 import no_data_warning
from safe.common.exceptions import (
    FunctionParametersError, ZeroImpactException)
from safe.common.utilities import (
    format_int,
    create_classes,
    create_label,
    humanize_class)
from safe.gui.tools.minimum_needs.needs_profile import (
    add_needs_parameters, filter_needs_parameters)
from safe.impact_functions.bases.continuous_rh_continuous_re import \
    ContinuousRHContinuousRE
from safe.impact_functions.core import (
    population_rounding,
    has_no_data,
    no_population_impact_message
)
from safe.impact_functions.generic\
    .continuous_hazard_population.metadata_definitions import \
    ContinuousHazardPopulationMetadata
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_reports.population_exposure_report_mixin import \
    PopulationExposureReportMixin
from safe.storage.raster import Raster
from safe.utilities.i18n import tr

__author__ = 'lucernae'
__date__ = '24/03/15'
__revision__ = '$Format:%H$'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')


class ContinuousHazardPopulationFunction(
        ContinuousRHContinuousRE,
        PopulationExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Plugin for impact of population as derived by continuous hazard."""
    _metadata = ContinuousHazardPopulationMetadata()

    def __init__(self):
        super(ContinuousHazardPopulationFunction, self).__init__()
        PopulationExposureReportMixin.__init__(self)
        self.impact_function_manager = ImpactFunctionManager()

        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)
        self.no_data_warning = False

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        fields = [
            tr('Total population in the analysis area: %s') %
            format_int(population_rounding(self.total_population)),
            tr('<sup>1</sup>People need evacuation if they are in a hazard '
               'zone.'),
            tr('Map shows the numbers of people in high, medium, and low '
               'hazard zones.')
        ]

        if self.no_data_warning:
            fields = fields + no_data_warning

        # include any generic exposure specific notes from definitions_v3.py
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions_v3.py
        fields = fields + self.hazard_notes()
        return fields

    def run(self):
        """Plugin for impact of population as derived by continuous hazard.

        Hazard is reclassified into 3 classes based on the extrema provided
        as impact function parameters.

        Counts number of people exposed to each category of the hazard

        :returns:
          Map of population exposed to high category
          Table with number of people in each category
        """

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
            tr('Population in high hazard zones')] = int(
                numpy.nansum(high_exposure))
        self.affected_population[
            tr('Population in medium hazard zones')] = int(
                numpy.nansum(medium_exposure))
        self.affected_population[
            tr('Population in low hazard zones')] = int(
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
            style_class['transparency'] = 0
            style_class['colour'] = colours[i]
            style_classes.append(style_class)

        style_info = dict(
            target_field=None,
            style_classes=style_classes,
            style_type='rasterStyle')

        impact_data = self.generate_data()

        extra_keywords = {
            'map_title': self.map_title(),
            'legend_notes': self.metadata().key('legend_notes'),
            'legend_units': self.metadata().key('legend_units'),
            'legend_title': self.metadata().key('legend_title'),
            'total_needs': total_needs
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create raster object and return
        impact_layer = Raster(
            data=impacted_exposure,
            projection=self.hazard.layer.get_projection(),
            geotransform=self.hazard.layer.get_geotransform(),
            name=self.map_title(),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
