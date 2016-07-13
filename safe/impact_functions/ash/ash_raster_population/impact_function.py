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
from safe.utilities.utilities import ranges_according_thresholds_list
import safe.messaging as m

from safe.impact_functions.core import (
    population_rounding,
    has_no_data
)
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.storage.raster import Raster
from safe.utilities.i18n import tr
from safe.common.utilities import (
    verify,
    humanize_class,
    create_classes,
    create_label)

from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    filter_needs_parameters, get_needs_provenance_value
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

        :returns: A vector layer with affected areas marked.
        :type: safe_layer
        """
        # Range for ash hazard
        group_parameters = self.parameters['group_threshold']
        ver_low_unit = group_parameters.value_map['very_low_threshold'].unit
        unaffected_threshold = group_parameters.value_map[
            'unaffected_threshold']
        unaffected_max = unaffected_threshold.value
        very_low_max = group_parameters.value_map['very_low_threshold'].value
        low_max = group_parameters.value_map['low_threshold'].value
        medium_max = group_parameters.value_map['moderate_threshold'].value
        high_max = group_parameters.value_map['high_threshold'].value
        unit_abbrev = ver_low_unit.abbreviation

        hazard_level_range = [
            unaffected_max,
            very_low_max,
            low_max,
            medium_max,
            high_max,
        ]

        # Extract hazard data as numeric arrays
        ash = self.hazard.layer.get_data(nan=True)  # Thickness
        if has_no_data(ash):
            self.no_data_warning = True

        # Extract exposure data as numeric arrays
        population = self.exposure.layer.get_data(nan=True, scaling=True)
        if has_no_data(population):
            self.no_data_warning = True

        # merely initialize
        impact = None
        for i, lo in enumerate(hazard_level_range):
            thresholds_name = self.hazard_classes[i]
            if i == len(hazard_level_range) - 1:
                # The last threshold
                impact = medium = numpy.where(ash >= hazard_level_range[0], population, 0)
                self.impact_category_ordering.append(thresholds_name)
                self._evacuation_category = thresholds_name
            else:
                # Intermediate thresholds
                hi = hazard_level_range[i + 1]
                medium = numpy.where(
                    (ash >= lo) * (ash < hi), population, 0)

            # Count
            val = int(numpy.nansum(medium))
            self.affected_population[thresholds_name] = val

        self.impact_category_ordering.reverse()

        # Carry the no data values forward to the impact layer.
        impact = numpy.where(numpy.isnan(population), numpy.nan, impact)
        impact = numpy.where(numpy.isnan(ash), numpy.nan, impact)

        # Count totals
        self.total_population = int(numpy.nansum(population))
        self.unaffected_population = (
            self.total_population - self.total_affected_population)

        self.minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
            ]

        # check for zero impact
        if sum(self.affected_population.values()) == 0:
            message = m.Message()
            message.add(self.question)
            message.add(
                tr('No people in %.1f m of water') % hazard_level_range[-1])
            message = message.to_html(suppress_newlines=True)
            raise ZeroImpactException(message)

        # Create style
        colours = [
            '#2C6BA4', '#00A4D8', '#FFEF36', '#EFA951',
            '#D62631']
        classes = create_classes(impact.flat[:], len(colours))
        interval_classes = humanize_class(classes)
        style_classes = []

        for i in xrange(len(colours)):
            style_class = dict()
            label = self.hazard_classes[i]
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
            'evacuated': self.total_evacuated,
            'total_needs': self.total_needs
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create raster object and return
        impact_layer = Raster(
            impact,
            projection=self.hazard.layer.get_projection(),
            geotransform=self.hazard.layer.get_geotransform(),
            name=self.metadata().key('layer_name'),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
