# coding=utf-8
"""Tsunami Evacuation Impact Function."""
import numpy

from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.core import (
    evacuated_population_needs,
    population_rounding_full,
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
    format_int,
    verify,
    humanize_class,
    create_classes,
    create_label,
    get_thousand_separator
)
from safe.common.tables import Table, TableRow
from safe.common.exceptions import ZeroImpactException
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    filter_needs_parameters


# noinspection PyClassHasNoInit
class TsunamiEvacuationFunction(ImpactFunction):
    # noinspection PyUnresolvedReferences
    """Impact function for tsunami evacuation."""
    _metadata = TsunamiEvacuationMetadata()

    def __init__(self):
        super(TsunamiEvacuationFunction, self).__init__()
        self.impact_function_manager = ImpactFunctionManager()

        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)

    def _tabulate(self, counts, evacuated, minimum_needs, question, rounding,
                  thresholds, total, no_data_warning):
        # noinspection PyListCreation
        table_body = [
            question,
            TableRow([(tr('People in %.1f m of water') % thresholds[-1]),
                      '%s*' % format_int(evacuated)],
                     header=True),
            TableRow(
                tr('* Number is rounded up to the nearest %s') % rounding),
            TableRow(tr('Map shows the numbers of people needing evacuation'))]
        total_needs = evacuated_population_needs(
            evacuated, minimum_needs)
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
        table_body.append(TableRow(tr('Action Checklist:'), header=True))
        table_body.append(TableRow(tr('How will warnings be disseminated?')))
        table_body.append(TableRow(tr('How will we reach stranded people?')))
        table_body.append(TableRow(tr('Do we have enough relief items?')))
        table_body.append(TableRow(tr('If yes, where are they located and how '
                                      'will we distribute them?')))
        table_body.append(TableRow(tr(
            'If no, where can we obtain additional relief items from and how '
            'will we transport them to here?')))
        # Extend impact report for on-screen display
        table_body.extend([
            TableRow(tr('Notes'), header=True),
            tr('Total population: %s') % format_int(total),
            tr('People need evacuation if tsunami levels exceed %(eps).1f m') %
            {'eps': thresholds[-1]},
            tr('Minimum needs are defined in BNPB regulation 7/2008'),
            tr('All values are rounded up to the nearest integer in order to '
               'avoid representing human lives as fractions.')])
        if len(counts) > 1:
            table_body.append(TableRow(tr('Detailed breakdown'), header=True))

            for i, val in enumerate(counts[:-1]):
                s = (tr('People in %(lo).1f m to %(hi).1f m of water: %(val)i')
                     % {'lo': thresholds[i],
                        'hi': thresholds[i + 1],
                        'val': format_int(val[0])})
                table_body.append(TableRow(s))
        if no_data_warning:
            table_body.extend([
                tr('The layers contained `no data`. This missing data was '
                   'carried through to the impact layer.'),
                tr('`No data` values in the impact layer were treated as 0 '
                   'when counting the affected or total population.')
            ])

        return table_body, total_needs

    def run(self, layers=None):
        """Risk plugin for tsunami population evacuation.

        :param layers: List of layers expected to contain
              hazard_layer: Raster layer of tsunami depth
              exposure_layer: Raster layer of population data on the same grid
              as hazard_layer

        Counts number of people exposed to tsunami levels exceeding
        specified threshold.

        :returns: Map of population exposed to tsunami levels exceeding the
            threshold. Table with number of people evacuated and supplies
            required.
        :rtype: tuple
        """
        self.validate()
        self.prepare(layers)

        # Identify hazard and exposure layers
        hazard_layer = self.hazard  # Tsunami inundation [m]
        exposure_layer = self.exposure

        # Determine depths above which people are regarded affected [m]
        # Use thresholds from inundation layer if specified
        thresholds = self.parameters['thresholds [m]']

        verify(
            isinstance(thresholds, list),
            'Expected thresholds to be a list. Got %s' % str(thresholds))

        # Extract data as numeric arrays
        data = hazard_layer.get_data(nan=True)  # Depth
        no_data_warning = False
        if has_no_data(data):
            no_data_warning = True

        # Calculate impact as population exposed to depths > max threshold
        population = exposure_layer.get_data(nan=True, scaling=True)
        if has_no_data(population):
            no_data_warning = True

        # Calculate impact to intermediate thresholds
        counts = []
        # merely initialize
        impact = None
        for i, lo in enumerate(thresholds):
            if i == len(thresholds) - 1:
                # The last threshold
                impact = medium = numpy.where(data >= lo, population, 0)
            else:
                # Intermediate thresholds
                hi = thresholds[i + 1]
                medium = numpy.where((data >= lo) * (data < hi), population, 0)

            # Count
            val = int(numpy.nansum(medium))

            # Sensible rounding
            val, rounding = population_rounding_full(val)
            counts.append([val, rounding])

        # Carry the no data values forward to the impact layer.
        impact = numpy.where(numpy.isnan(population), numpy.nan, impact)
        impact = numpy.where(numpy.isnan(data), numpy.nan, impact)

        # Count totals
        evacuated, rounding = counts[-1]
        total = int(numpy.nansum(population))
        # Don't show digits less than a 1000
        total = population_rounding(total)

        minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
        ]

        # Generate impact report for the pdf map
        table_body, total_needs = self._tabulate(
            counts,
            evacuated,
            minimum_needs,
            self.question,
            rounding,
            thresholds,
            total,
            no_data_warning)

        # Result
        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary

        # check for zero impact
        if numpy.nanmax(impact) == 0 == numpy.nanmin(impact):
            table_body = [
                self.question,
                TableRow([(tr('People in %.1f m of water') % thresholds[-1]),
                          '%s' % format_int(evacuated)],
                         header=True)]
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
        legend_title = tr('Population')

        # Create raster object and return
        raster = Raster(
            impact,
            projection=hazard_layer.get_projection(),
            geotransform=hazard_layer.get_geotransform(),
            name=tr('Population which %s') % (
                self.impact_function_manager.get_function_title(self).lower()),
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
