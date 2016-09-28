# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid - ** Generic Impact
Function on Population for Classified Hazard.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

import itertools

import numpy

from safe.definitionsv4.caveats import no_data_warning
from safe.common.exceptions import (
    FunctionParametersError, ZeroImpactException)
from safe.common.utilities import (
    format_int,
    humanize_class,
    create_classes,
    create_label)
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters
from safe.impact_functions.bases.classified_rh_continuous_re import \
    ClassifiedRHContinuousRE
from safe.impact_functions.core import (
    population_rounding, has_no_data, no_population_impact_message)
from safe.impact_functions.generic.\
    classified_raster_population.metadata_definitions import \
    ClassifiedRasterHazardPopulationMetadata
from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.impact_reports.population_exposure_report_mixin import \
    PopulationExposureReportMixin
from safe.storage.raster import Raster
from safe.utilities.i18n import tr

__author__ = 'lucernae'
__date__ = '24/03/15'
__revision__ = '$Format:%H$'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')


class ClassifiedRasterHazardPopulationFunction(
        ClassifiedRHContinuousRE,
        PopulationExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Plugin for impact of population as derived by classified hazard."""

    _metadata = ClassifiedRasterHazardPopulationMetadata()

    def __init__(self):
        super(ClassifiedRasterHazardPopulationFunction, self).__init__()
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
               'zone.')
        ]

        if self.no_data_warning:
            fields = fields + no_data_warning
        # include any generic exposure specific notes from definitions_v3.py
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions_v3.py
        fields = fields + self.hazard_notes()
        return fields

    def run(self):
        """Plugin for impact of population as derived by classified hazard.

        Counts number of people exposed to each class of the hazard

        :returns: Map of population exposed to high class
            Table with number of people in each class
        """

        # The 3 classes
        # TODO (3.2): shouldnt these be defined in keywords rather? TS
        categorical_hazards = self.parameters['Categorical hazards'].value
        low_class = categorical_hazards[0].value
        medium_class = categorical_hazards[1].value
        high_class = categorical_hazards[2].value

        # The classes must be different to each other
        unique_classes_flag = all(
            x != y for x, y in list(
                itertools.combinations(
                    [low_class, medium_class, high_class], 2)))
        if not unique_classes_flag:
            raise FunctionParametersError(
                'There is hazard class that has the same value with other '
                'class. Please check the parameters.')

        # Extract data as numeric arrays
        hazard_data = self.hazard.layer.get_data(nan=True)  # Class
        if has_no_data(hazard_data):
            self.no_data_warning = True

        # Calculate impact as population exposed to each class
        population = self.exposure.layer.get_data(scaling=True)

        # Get all population data that falls in each hazard class
        high_hazard_population = numpy.where(
            hazard_data == high_class, population, 0)
        medium_hazard_population = numpy.where(
            hazard_data == medium_class, population, 0)
        low_hazard_population = numpy.where(
            hazard_data == low_class, population, 0)
        affected_population = (
            high_hazard_population + medium_hazard_population +
            low_hazard_population)

        # Carry the no data values forward to the impact layer.
        affected_population = numpy.where(
            numpy.isnan(population),
            numpy.nan,
            affected_population)
        affected_population = numpy.where(
            numpy.isnan(hazard_data),
            numpy.nan,
            affected_population)

        # Count totals
        self.total_population = int(numpy.nansum(population))
        self.affected_population[
            tr('Population in low hazard zone')] = int(
                numpy.nansum(low_hazard_population))
        self.affected_population[
            tr('Population in medium hazard zone')] = int(
                numpy.nansum(medium_hazard_population))
        self.affected_population[
            tr('Population in high hazard zone')] = int(
                numpy.nansum(high_hazard_population))
        self.unaffected_population = (
            self.total_population - self.total_affected_population)

        # check for zero impact
        if self.total_affected_population == 0:
            message = no_population_impact_message(self.question)
            raise ZeroImpactException(message)

        self.minimum_needs = [
            parameter.serialize() for parameter in
            self.parameters['minimum needs']
        ]

        total_needs = self.total_needs

        # Create style
        colours = [
            '#FFFFFF', '#38A800', '#79C900', '#CEED00',
            '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        classes = create_classes(affected_population.flat[:], len(colours))
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
            data=affected_population,
            projection=self.exposure.layer.get_projection(),
            geotransform=self.exposure.layer.get_geotransform(),
            name=self.map_title(),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
