import numpy
from safe.common.utilities import OrderedDict
from safe.impact_functions.core import (
    FunctionProvider,
    get_hazard_layer,
    get_exposure_layer,
    get_question,
    get_function_title)
from safe.storage.raster import Raster
from safe.common.utilities import (
    ugettext as tr,
    get_defaults,
    format_int,
    verify,
    round_thousand,
    humanize_class,
    create_classes,
    create_label)
from safe.common.tables import Table, TableRow


class FloodEvacuationFunction(FunctionProvider):
    """Impact function for flood evacuation

    :author AIFDR
    :rating 4
    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype=='raster' and \
                    unit=='m'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster'
    """

    title = tr('Need evacuation')
    defaults = get_defaults()

    # Function documentation
    synopsis = tr(
        'To assess the impacts of (flood or tsunami) inundation in raster '
        'format on population.')
    actions = tr(
        'Provide details about how many people would likely need to be '
        'evacuated, where they are located and what resources would be '
        'required to support them.')
    detailed_description = tr(
        'The population subject to inundation exceeding a threshold '
        '(default 1m) is calculated and returned as a raster layer. In '
        'addition the total number and the required needs in terms of the '
        'BNPB (Perka 7) are reported. The threshold can be changed and even '
        'contain multiple numbers in which case evacuation and needs are '
        'calculated using the largest number with population breakdowns '
        'provided for the smaller numbers. The population raster is resampled '
        'to the resolution of the hazard raster and is rescaled so that the '
        'resampled population counts reflect estimates of population count '
        'per resampled cell. The resulting impact layer has the same '
        'resolution and reflects population count per cell which are affected '
        'by inundation.')
    hazard_input = tr(
        'A hazard raster layer where each cell represents flood depth '
        '(in meters).')
    exposure_input = tr(
        'An exposure raster layer where each cell represent population count.')
    output = tr(
        'Raster layer contains population affected and the minimum needs '
        'based on the population affected.')
    limitation = tr(
        'The default threshold of 1 meter was selected based on consensus, '
        'not hard evidence.')

    # Configurable parameters
    parameters = OrderedDict([
        ('thresholds [m]', [1.0]),
        ('postprocessors', OrderedDict([
            ('Gender', {'on': True}),
            ('Age', {
                'on': True,
                'params': OrderedDict([
                    ('youth_ratio', defaults['YOUTH_RATIO']),
                    ('adult_ratio', defaults['ADULT_RATIO']),
                    ('elder_ratio', defaults['ELDER_RATIO'])])})]))])

    def run(self, layers):
        """Risk plugin for flood population evacuation

        Input
          layers: List of layers expected to contain
              my_hazard: Raster layer of flood depth
              my_exposure: Raster layer of population data on the same grid
              as my_hazard

        Counts number of people exposed to flood levels exceeding
        specified threshold.

        Return
          Map of population exposed to flood levels exceeding the threshold
          Table with number of people evacuated and supplies required
        """

        # Identify hazard and exposure layers
        my_hazard = get_hazard_layer(layers)  # Flood inundation [m]
        my_exposure = get_exposure_layer(layers)

        question = get_question(my_hazard.get_name(),
                                my_exposure.get_name(),
                                self)

        # Determine depths above which people are regarded affected [m]
        # Use thresholds from inundation layer if specified
        thresholds = self.parameters['thresholds [m]']

        verify(isinstance(thresholds, list),
               'Expected thresholds to be a list. Got %s' % str(thresholds))

        # Extract data as numeric arrays
        D = my_hazard.get_data(nan=0.0)  # Depth

        # Calculate impact as population exposed to depths > max threshold
        P = my_exposure.get_data(nan=0.0, scaling=True)

        # Calculate impact to intermediate thresholds
        counts = []
        for i, lo in enumerate(thresholds):
            if i == len(thresholds) - 1:
                # The last threshold
                my_impact = M = numpy.where(D >= lo, P, 0)
            else:
                # Intermediate thresholds
                hi = thresholds[i + 1]
                M = numpy.where((D >= lo) * (D < hi), P, 0)

            # Count
            val = int(numpy.sum(M))

            # Don't show digits less than a 1000
            val = round_thousand(val)
            counts.append(val)

        # Count totals
        evacuated = counts[-1]
        total = int(numpy.sum(P))
        # Don't show digits less than a 1000
        total = round_thousand(total)

        # Calculate estimated needs based on BNPB Perka 7/2008 minimum bantuan

        # FIXME: Refactor and share
        # 400g per person per day
        rice = int(evacuated * 2.8)
        # 2.5L per person per day
        drinking_water = int(evacuated * 17.5)
        # 15L per person per day
        water = int(evacuated * 105)
        # assume 5 people per family (not in perka)
        family_kits = int(evacuated / 5)
        # 20 people per toilet
        toilets = int(evacuated / 20)

        # Generate impact report for the pdf map
        table_body = [
            question,
            TableRow([(tr('People in %.1f m of water') % thresholds[-1]),
                      '%s*' % format_int(evacuated)],
                     header=True),
            TableRow(tr('* Number is rounded to the nearest 1000'),
                     header=False),
            TableRow(tr('Map shows population density needing evacuation')),
            TableRow([tr('Needs per week'), tr('Total')], header=True),
            [tr('Rice [kg]'), format_int(rice)],
            [tr('Drinking Water [l]'), format_int(drinking_water)],
            [tr('Clean Water [l]'), format_int(water)],
            [tr('Family Kits'), format_int(family_kits)],
            [tr('Toilets'), format_int(toilets)]]

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
            tr('People need evacuation if flood levels exceed %(eps).1f m') %
            {'eps': thresholds[-1]},
            tr('Minimum needs are defined in BNPB regulation 7/2008'),
            tr('All values are rounded up to the nearest integer in order to '
               'avoid representing human lives as fractionals.')])

        if len(counts) > 1:
            table_body.append(TableRow(tr('Detailed breakdown'), header=True))

            for i, val in enumerate(counts[:-1]):
                s = (tr('People in %(lo).1f m to %(hi).1f m of water: %(val)i')
                     % {'lo': thresholds[i],
                        'hi': thresholds[i + 1],
                        'val': format_int(val)})
                table_body.append(TableRow(s, header=False))

        # Result
        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary

        # Create style
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        classes = create_classes(my_impact.flat[:], len(colours))
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
                label = create_label(interval_classes[i], 'High')
            style_class['label'] = label
            style_class['quantity'] = classes[i]
            if i == 0:
                transparency = 100
            else:
                transparency = 0
            style_class['transparency'] = transparency
            style_class['colour'] = colours[i]
            style_classes.append(style_class)

        style_info = dict(target_field=None,
                          style_classes=style_classes,
                          style_type='rasterStyle')

        # For printing map purpose
        map_title = tr('People in need of evacuation')
        legend_notes = tr('Thousand separator is represented by \'.\'')
        legend_units = tr('(people per cell)')
        legend_title = tr('Population density')

        # Create raster object and return
        R = Raster(my_impact,
                   projection=my_hazard.get_projection(),
                   geotransform=my_hazard.get_geotransform(),
                   name=tr('Population which %s') % get_function_title(self),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title,
                             'legend_notes': legend_notes,
                             'legend_units': legend_units,
                             'legend_title': legend_title},
                   style_info=style_info)
        return R
