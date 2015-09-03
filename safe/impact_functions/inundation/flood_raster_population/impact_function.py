# coding=utf-8
"""Flood Evacuation Impact Function."""
__author__ = 'Rizky Maulana Nugraha'

import logging
import numpy

from safe.impact_functions.core import (
    population_rounding,
    has_no_data)
from safe.impact_functions.impact_function_manager \
    import ImpactFunctionManager
from safe.impact_functions.inundation.flood_raster_population\
    .metadata_definitions import FloodEvacuationRasterHazardMetadata
from safe.impact_functions.bases.continuous_rh_continuous_re import \
    ContinuousRHContinuousRE
from safe.utilities.i18n import tr
from safe.common.tables import Table, TableRow
from safe.common.exceptions import ZeroImpactException
from safe.storage.raster import Raster
from safe.common.utilities import (
    format_int,
    create_classes,
    humanize_class,
    create_label,
    verify,
    get_thousand_separator)
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    get_needs_provenance_value
from safe.impact_reports.population_exposure_report_mixin import \
    PopulationExposureReportMixin

LOGGER = logging.getLogger('InaSAFE')


class FloodEvacuationRasterHazardFunction(
        ContinuousRHContinuousRE,
        PopulationExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Risk plugin for flood population evacuation."""
    _metadata = FloodEvacuationRasterHazardMetadata()

    def __init__(self):
        """Constructor."""
        super(FloodEvacuationRasterHazardFunction, self).__init__()
        self.impact_function_manager = ImpactFunctionManager()

        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)

        # Initialize instance attributes for readability (pylint)
        self.no_data_warning = False

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: list
        """
        thresholds = self.parameters['thresholds'].value
        notes = [
            {
                'content': tr('Notes'),
                'header': True
            },
            {
                'content': tr('Total population: %s') % population_rounding(
                    self.total_population)
            },
            {
                'content': tr(
                    '<sup>1</sup>People need evacuation if flood levels '
                    'exceed %(eps).1f m.') % {'eps': thresholds[-1]},
            },
            {
                'content': tr(get_needs_provenance_value(self.parameters)),
            },
            {
                'content': tr(
                    'The layers contained `no data`. This missing data was '
                    'carried through to the impact layer.'),
                'condition': self.no_data_warning
            },
            {
                'content': tr(
                    '`No data` values in the impact layer were treated as 0 '
                    'when counting the affected or total population.'),
                'condition': self.no_data_warning
            },
            {
                'content': tr(
                    'All values are rounded up to the nearest integer in '
                    'order to avoid representing human lives as fractions.'),
            },
            {
                'content': tr(
                    'Population rounding is applied to all population '
                    'values, which may cause discrepancies when adding '
                    'values.')
            }
        ]
        return notes

    def _tabulate_zero_impact(self):
        thresholds = self.parameters['thresholds'].value
        table_body = [
            self.question,
            TableRow([(tr('People in %.1f m of water') % thresholds[-1]),
                      '%s' % format_int(self.total_evacuated)],
                     header=True)]
        return table_body

    def run(self):
        """Risk plugin for flood population evacuation.

        Counts number of people exposed to flood levels exceeding
        specified threshold.

        :returns: Map of population exposed to flood levels exceeding the
            threshold. Table with number of people evacuated and supplies
            required.
        :rtype: tuple
        """
        self.validate()
        self.prepare()

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
        total = int(numpy.nansum(population))
        if has_no_data(population):
            self.no_data_warning = True

        # merely initialize
        impact = None

        for i, lo in enumerate(thresholds):
            if i == len(thresholds) - 1:
                # The last threshold
                thresholds_name = tr(
                    'People in >= %.1f m of water') % lo
                self.impact_category_ordering.append(thresholds_name)
                self._evacuation_category = thresholds_name
                impact = medium = numpy.where(data >= lo, population, 0)
            else:
                # Intermediate thresholds
                hi = thresholds[i + 1]
                thresholds_name = tr(
                    'People in %.1f m to %.1f m of water' % (lo, hi))
                self.impact_category_ordering.append(thresholds_name)
                medium = numpy.where((data >= lo) * (data < hi), population, 0)

            # Count
            val = int(numpy.nansum(medium))
            self.affected_population[thresholds_name] = val

        self.total_population = total
        self.unaffected_population = total - self.total_affected_population

        # Carry the no data values forward to the impact layer.
        impact = numpy.where(numpy.isnan(population), numpy.nan, impact)
        impact = numpy.where(numpy.isnan(data), numpy.nan, impact)

        # Count totals
        evacuated = self.total_evacuated

        self.minimum_needs = [
            parameter.serialize() for parameter in
            self.parameters['minimum needs']
        ]

        # Result
        impact_summary = self.generate_html_report()
        impact_table = impact_summary

        total_needs = self.total_needs

        # check for zero impact
        if numpy.nanmax(impact) == 0 == numpy.nanmin(impact):
            table_body = self._tabulate_zero_impact()
            my_message = Table(table_body).toNewlineFreeString()
            raise ZeroImpactException(my_message)

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
        map_title = tr('People in need of evacuation')
        legend_notes = tr(
            'Thousand separator is represented by %s' %
            get_thousand_separator())
        legend_units = tr('(people per cell)')
        legend_title = tr('Population Count')

        # Create raster object and return
        raster = Raster(
            impact,
            projection=self.hazard.layer.get_projection(),
            geotransform=self.hazard.layer.get_geotransform(),
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
                'evacuated': evacuated,
                'total_needs': total_needs},
            style_info=style_info)
        self._impact = raster
        return raster
