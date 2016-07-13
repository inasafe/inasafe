# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Ash Raster on Population
Impact Function

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import numpy

from safe.common.exceptions import ZeroImpactException

from safe.impact_functions.bases.continuous_rh_continuous_re import \
    ContinuousRHContinuousRE

from safe.impact_functions.core import (
    has_no_data,
    no_population_impact_message
)
from safe.storage.raster import Raster
from safe.utilities.i18n import tr
from safe.common.utilities import (
    humanize_class,
    create_classes,
    create_label)

from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    filter_needs_parameters
from safe.impact_reports.population_exposure_report_mixin import \
    PopulationExposureReportMixin

from safe.impact_functions.ash.ash_raster_population.metadata_definitions \
    import AshRasterHazardPopulationFunctionMetadata


__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'impact_function.py'
__date__ = '7/13/16'
__copyright__ = 'imajimatika@gmail.com'


class AshRasterPopulationFunction(
        ContinuousRHContinuousRE,
        PopulationExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Simple impact function for ash raster on people."""
    _metadata = AshRasterHazardPopulationFunctionMetadata()

    def __init__(self):
        """Constructor."""
        super(AshRasterPopulationFunction, self).__init__()
        PopulationExposureReportMixin.__init__(self)

        self.hazard_classes = [
            tr('Very Low'),
            tr('Low'),
            tr('Moderate'),
            tr('High'),
            tr('Very High'),
        ]

        self.parameters = add_needs_parameters(self.parameters)
        self.no_data_warning = False

    def run(self):
        """Run the impact function.
        """
        # Range for ash hazard
        group_parameters = self.parameters['group_threshold']
        unaffected_max = group_parameters.value_map[
            'unaffected_threshold'].value
        very_low_max = group_parameters.value_map['very_low_threshold'].value
        low_max = group_parameters.value_map['low_threshold'].value
        medium_max = group_parameters.value_map['moderate_threshold'].value
        high_max = group_parameters.value_map['high_threshold'].value

        # Extract hazard data as numeric arrays
        ash = self.hazard.layer.get_data(nan=True)  # Thickness
        if has_no_data(ash):
            self.no_data_warning = True

        # Extract exposure data as numeric arrays
        population = self.exposure.layer.get_data(nan=True, scaling=True)
        if has_no_data(population):
            self.no_data_warning = True

        # Create 5 data for each hazard level. Get the value of the exposure
        # if the exposure is in the hazard zone, else just assign 0
        unaffected_exposure = numpy.where(ash < unaffected_max, population, 0)
        very_low_exposure = numpy.where(
            (ash >= unaffected_max) & (ash < very_low_max), population, 0)
        low_exposure = numpy.where(
            (ash >= very_low_max) & (ash < low_max), population, 0)
        medium_exposure = numpy.where(
            (ash >= low_max) & (ash < medium_max), population, 0)
        high_exposure = numpy.where(
            (ash >= medium_max) & (ash < high_max), population, 0)
        very_high_exposure = numpy.where(ash >= high_max, population, 0)

        impacted_exposure = (
            very_low_exposure +
            low_exposure +
            medium_exposure +
            high_exposure +
            very_high_exposure
        )

        # Count totals
        self.total_population = int(numpy.nansum(population))
        self.affected_population[
            tr('Population in very low hazard zone')] = int(
            numpy.nansum(very_low_exposure))
        self.affected_population[
            tr('Population in low hazard zone')] = int(
            numpy.nansum(low_exposure))
        self.affected_population[
            tr('Population in medium hazard zone')] = int(
            numpy.nansum(medium_exposure))
        self.affected_population[
            tr('Population in high hazard zone')] = int(
            numpy.nansum(high_exposure))
        self.affected_population[
            tr('Population in very high hazard zone')] = int(
            numpy.nansum(very_high_exposure))
        self.unaffected_population = int(
            numpy.nansum(unaffected_exposure))

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
            'map_title': self.metadata().key('map_title'),
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
            name=self.metadata().key('layer_name'),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
