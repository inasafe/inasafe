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

__author__ = 'lucernae'
__date__ = '24/03/15'
__revision__ = '$Format:%H$'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')

import numpy
import itertools

from safe.impact_functions.bases.classified_rh_continuous_re import \
    ClassifiedRHContinuousRE
from safe.impact_functions.core import (
    population_rounding,
    has_no_data)
from safe.storage.raster import Raster
from safe.common.utilities import (
    humanize_class,
    create_classes,
    create_label,
    get_thousand_separator)
from safe.utilities.i18n import tr
from safe.impact_functions.core import no_population_impact_message
from safe.impact_functions.generic.\
    classified_raster_population.metadata_definitions import \
    ClassifiedRasterHazardPopulationMetadata
from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters
from safe.common.exceptions import (
    FunctionParametersError, ZeroImpactException)
from safe.impact_reports.population_exposure_report_mixin import \
    PopulationExposureReportMixin
import safe.messaging as m
from safe.messaging import styles


class ClassifiedRasterHazardPopulationFunction(
        ClassifiedRHContinuousRE,
        PopulationExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Plugin for impact of population as derived by classified hazard."""

    _metadata = ClassifiedRasterHazardPopulationMetadata()

    def __init__(self):
        super(ClassifiedRasterHazardPopulationFunction, self).__init__()
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
        """Plugin for impact of population as derived by classified hazard.

        Counts number of people exposed to each class of the hazard

        Return
          Map of population exposed to high class
          Table with number of people in each class
        """
        self.validate()
        self.prepare()

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
            tr('Population in High hazard class areas')] = int(
                numpy.nansum(high_hazard_population))
        self.affected_population[
            tr('Population in Medium hazard class areas')] = int(
                numpy.nansum(medium_hazard_population))
        self.affected_population[
            tr('Population in Low hazard class areas')] = int(
                numpy.nansum(low_hazard_population))
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
        impact_table = impact_summary = self.html_report()

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
        map_title = tr('Number of people affected in each class')
        legend_title = tr('Number of People')
        legend_units = tr('(people per cell)')
        legend_notes = tr(
            'Thousand separator is represented by %s' %
            get_thousand_separator())

        # Create raster object and return
        raster_layer = Raster(
            data=affected_population,
            projection=self.exposure.layer.get_projection(),
            geotransform=self.exposure.layer.get_geotransform(),
            name=tr('People that might %s') % (
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
