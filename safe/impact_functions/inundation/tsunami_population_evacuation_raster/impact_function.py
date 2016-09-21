# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Tsunami Impact Function
on Population.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import numpy

import safe.messaging as m
from definitionsv4.definitions_v3 import no_data_warning
from safe.common.exceptions import ZeroImpactException
from safe.common.utilities import (
    format_int,
    verify,
    humanize_class,
    create_classes,
    create_label)
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    filter_needs_parameters, get_needs_provenance_value
from safe.impact_functions.bases.continuous_rh_continuous_re import \
    ContinuousRHContinuousRE
from safe.impact_functions.core import (
    population_rounding,
    has_no_data
)
from safe.impact_functions.inundation\
    .tsunami_population_evacuation_raster.metadata_definitions import \
    TsunamiEvacuationMetadata
from safe.impact_reports.population_exposure_report_mixin import \
    PopulationExposureReportMixin
from safe.storage.raster import Raster
from safe.utilities.i18n import tr


# noinspection PyClassHasNoInit
class TsunamiEvacuationFunction(
        ContinuousRHContinuousRE,
        PopulationExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Impact function for tsunami evacuation."""
    _metadata = TsunamiEvacuationMetadata()

    def __init__(self):
        super(TsunamiEvacuationFunction, self).__init__()
        PopulationExposureReportMixin.__init__(self)

        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)
        self.no_data_warning = False

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """

        thresholds = self.parameters['thresholds'].value
        if get_needs_provenance_value(self.parameters) is None:
            needs_provenance = ''
        else:
            needs_provenance = tr(get_needs_provenance_value(self.parameters))

        fields = [
            tr('Total population in the analysis area: %s') %
            format_int(population_rounding(self.total_population)),
            tr('<sup>1</sup>People need evacuation if flood levels exceed '
               '%(eps).1f m.') % {'eps': thresholds[-1]},
            needs_provenance
        ]

        if self.no_data_warning:
            fields = fields + no_data_warning
        # include any generic exposure specific notes from definitions_v3.py
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions_v3.py
        fields = fields + self.hazard_notes()
        return fields

    def run(self):
        """Risk plugin for tsunami population evacuation.

        Counts number of people exposed to tsunami levels exceeding
        specified threshold.

        :returns: Map of population exposed to tsunami levels exceeding the
            threshold. Table with number of people evacuated and supplies
            required.
        :rtype: tuple
        """

        # Determine depths above which people are regarded affected [m]
        # Use thresholds from inundation layer if specified
        thresholds = self.parameters['thresholds'].value

        verify(
            isinstance(thresholds, list),
            'Expected thresholds to be a list. Got %s' % str(thresholds))

        # Extract data as numeric arrays
        data = self.hazard.layer.get_data(nan=True)  # Depth
        if has_no_data(data):
            self.no_data_warning = True

        # Calculate impact as population exposed to depths > max threshold
        population = self.exposure.layer.get_data(nan=True, scaling=True)
        if has_no_data(population):
            self.no_data_warning = True

        # merely initialize
        impact = None
        for i, lo in enumerate(thresholds):
            if i == len(thresholds) - 1:
                # The last threshold
                thresholds_name = tr(
                    'People in >= %.1f m of water') % lo
                impact = medium = numpy.where(data >= lo, population, 0)
                self.impact_category_ordering.append(thresholds_name)
                self._evacuation_category = thresholds_name
            else:
                # Intermediate thresholds
                hi = thresholds[i + 1]
                thresholds_name = tr(
                    'People in %.1f m to %.1f m of water' % (lo, hi))
                medium = numpy.where((data >= lo) * (data < hi), population, 0)

            # Count
            val = int(numpy.nansum(medium))
            self.affected_population[thresholds_name] = val

        # Put the deepest area in top #2385
        self.impact_category_ordering.reverse()

        # Carry the no data values forward to the impact layer.
        impact = numpy.where(numpy.isnan(population), numpy.nan, impact)
        impact = numpy.where(numpy.isnan(data), numpy.nan, impact)

        # Count totals
        self.total_population = int(numpy.nansum(population))
        self.unaffected_population = (
            self.total_population - self.total_affected_population)

        self.minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
        ]

        # check for zero impact
        if numpy.nanmax(impact) == 0 == numpy.nanmin(impact):
            message = m.Message()
            message.add(self.question)
            message.add(tr('No people in %.1f m of water') % thresholds[-1])
            message = message.to_html(suppress_newlines=True)
            raise ZeroImpactException(message)

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
            'evacuated': self.total_evacuated,
            'total_needs': self.total_needs
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create raster object and return
        impact_layer = Raster(
            impact,
            projection=self.hazard.layer.get_projection(),
            geotransform=self.hazard.layer.get_geotransform(),
            name=self.map_title(),
            keywords=impact_layer_keywords,
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
