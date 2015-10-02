# coding=utf-8
"""Tsunami Evacuation Impact Function."""
import numpy

from safe.impact_functions.bases.continuous_rh_continuous_re import \
    ContinuousRHContinuousRE
from safe.impact_functions.core import (
    population_rounding,
    has_no_data
)
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.inundation\
    .tsunami_population_evacuation_raster.metadata_definitions import \
    TsunamiEvacuationMetadata
from safe.storage.raster import Raster
from safe.utilities.i18n import tr
from safe.common.utilities import (
    verify,
    humanize_class,
    create_classes,
    create_label,
    get_thousand_separator)

from safe.common.exceptions import ZeroImpactException
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    filter_needs_parameters, get_needs_provenance_value
from safe.impact_reports.population_exposure_report_mixin import \
    PopulationExposureReportMixin
import safe.messaging as m
from safe.messaging import styles


# noinspection PyClassHasNoInit
class TsunamiEvacuationFunction(
        ContinuousRHContinuousRE,
        PopulationExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Impact function for tsunami evacuation."""
    _metadata = TsunamiEvacuationMetadata()

    def __init__(self):
        super(TsunamiEvacuationFunction, self).__init__()
        self.impact_function_manager = ImpactFunctionManager()

        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)
        self.no_data_warning = False

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: safe.messaging.Message
        """
        thresholds = self.parameters['thresholds'].value
        if get_needs_provenance_value(self.parameters) is None:
            needs_provenance = ''
        else:
            needs_provenance = tr(get_needs_provenance_value(self.parameters))

        message = m.Message(style_class='container')

        message.add(
            m.Heading(tr('Notes and assumptions'), **styles.INFO_STYLE))
        checklist = m.BulletedList()
        checklist.add(tr(
            'Total population in the analysis area: %s'
            ) % population_rounding(self.total_population))
        checklist.add(tr(
            '<sup>1</sup>People need evacuation if flood levels '
            'exceed %(eps).1f m.') % {'eps': thresholds[-1]})
        checklist.add(needs_provenance)
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
            'values, which may cause discrepancies when adding values.'))

        message.add(checklist)
        return message

    def run(self):
        """Risk plugin for tsunami population evacuation.

        Counts number of people exposed to tsunami levels exceeding
        specified threshold.

        :returns: Map of population exposed to tsunami levels exceeding the
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

        impact_table = impact_summary = self.html_report()

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

        # For printing map purpose
        map_title = tr('People in need of evacuation')
        legend_title = tr('Population')
        legend_units = tr('(people per cell)')
        legend_notes = tr(
            'Thousand separator is represented by %s' %
            get_thousand_separator())

        # Create raster object and return
        raster = Raster(
            impact,
            projection=self.hazard.layer.get_projection(),
            geotransform=self.hazard.layer.get_geotransform(),
            name=tr('Population which %s') % (
                self.impact_function_manager.get_function_title(self).lower()),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'map_title': map_title,
                'legend_notes': legend_notes,
                'legend_units': legend_units,
                'legend_title': legend_title,
                'evacuated': self.total_evacuated,
                'total_needs': self.total_needs},
            style_info=style_info)
        self._impact = raster
        return raster
