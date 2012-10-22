import numpy
from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question, get_function_title
from safe.impact_functions.styles import flood_population_style as style_info
from safe.storage.raster import Raster
from safe.common.utilities import (ugettext as tr,
                                   get_defaults)
from safe.common.utilities import verify
from safe.common.tables import Table, TableRow


class FloodEvacuationFunction(FunctionProvider):
    """Risk plugin for flood evacuation

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
    parameters = {
        'thresholds': [1.0],
        'postprocessors':
            {'Gender': {'on': True},
             'Age': {'on': True,
                     'params': {
                    'youth_ratio': defaults['YOUTH_RATIO'],
                    'adult_ratio': defaults['ADULT_RATIO'],
                    'elder_ratio': defaults['ELDER_RATIO']}}}}

    def run(self, layers):
        """Risk plugin for flood population evacuation

        Input
          layers: List of layers expected to contain
              H: Raster layer of flood depth
              P: Raster layer of population data on the same grid as H

        Counts number of people exposed to flood levels exceeding
        specified threshold.

        Return
          Map of population exposed to flood levels exceeding the threshold
          Table with number of people evacuated and supplies required
        """

        # Identify hazard and exposure layers
        inundation = get_hazard_layer(layers)  # Flood inundation [m]
        population = get_exposure_layer(layers)

        question = get_question(inundation.get_name(),
                                population.get_name(),
                                self)

        # Determine depths above which people are regarded affected [m]
        # Use thresholds from inundation layer if specified
        thresholds = self.parameters['thresholds']

        verify(isinstance(thresholds, list),
               'Expected thresholds to be a list. Got %s' % str(thresholds))

        # Extract data as numeric arrays
        D = inundation.get_data(nan=0.0)  # Depth

        # Calculate impact as population exposed to depths > max threshold
        P = population.get_data(nan=0.0, scaling=True)

        # Calculate impact to intermediate thresholds
        counts = []
        for i, lo in enumerate(thresholds):
            if i == len(thresholds) - 1:
                # The last threshold
                I = M = numpy.where(D >= lo, P, 0)
            else:
                # Intermediate thresholds
                hi = thresholds[i + 1]
                M = numpy.where((D >= lo) * (D < hi), P, 0)

            # Count
            val = int(numpy.sum(M))

            # Don't show digits less than a 1000
            if val > 1000:
                val = val // 1000 * 1000
            counts.append(val)

        # Count totals
        evacuated = counts[-1]
        total = int(numpy.sum(P))
        # Don't show digits less than a 1000
        if total > 1000:
            total = total // 1000 * 1000

        # Calculate estimated needs based on BNPB Perka 7/2008 minimum bantuan
        rice = evacuated * 2.8
        drinking_water = evacuated * 17.5
        water = evacuated * 67
        family_kits = evacuated / 5
        toilets = evacuated / 20

        # Generate impact report for the pdf map
        table_body = [question,
                      TableRow([tr('People needing evacuation'),
                                '%i' % evacuated],
                               header=True),
                      TableRow(tr('Map shows population density needing '
                                 'evacuation')),
                      TableRow([tr('Needs per week'), tr('Total')],
                               header=True),
            [tr('Rice [kg]'), int(rice)],
            [tr('Drinking Water [l]'), int(drinking_water)],
            [tr('Clean Water [l]'), int(water)],
            [tr('Family Kits'), int(family_kits)],
            [tr('Toilets'), int(toilets)]]
        impact_table = Table(table_body).toNewlineFreeString()

        table_body.append(TableRow(tr('Action Checklist:'), header=True))
        table_body.append(TableRow(tr('How will warnings be disseminated?')))
        table_body.append(TableRow(tr('How will we reach stranded people?')))
        table_body.append(TableRow(tr('Do we have enough relief items?')))
        table_body.append(TableRow(tr('If yes, where are they located and how '
                                     'will we distribute them?')))
        table_body.append(TableRow(tr('If no, where can we obtain additional '
                                     'relief items from and how will we '
                                     'transport them to here?')))

        # Extend impact report for on-screen display
        table_body.extend([TableRow(tr('Notes'), header=True),
                           tr('Total population: %i') % total,
                           tr('People need evacuation if flood levels '
                             'exceed %(eps).1f m') % {'eps': thresholds[-1]},
                           tr('Minimum needs are defined in BNPB '
                             'regulation 7/2008')])

        if len(counts) > 1:
            table_body.append(TableRow(tr('Detailed breakdown'), header=True))

            for i, val in enumerate(counts[:-1]):
                s = (tr('People in %(lo).1f m to %(hi).1f m of water: %(val)i')
                     % {'lo': thresholds[i],
                        'hi': thresholds[i + 1],
                        'val': val})
                table_body.append(TableRow(s, header=False))

        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('People in need of evacuation')

        # Generate 8 equidistant classes across the range of flooded population
        # 8 is the number of classes in the predefined flood population style
        # as imported
        classes = numpy.linspace(numpy.nanmin(I.flat[:]),
                                 numpy.nanmax(I.flat[:]), 8)

        # Modify labels in existing flood style to show quantities
        style_classes = style_info['style_classes']
        style_classes[1]['label'] = tr('Low [%i people/cell]') % classes[1]
        style_classes[4]['label'] = tr('Medium [%i people/cell]') % classes[4]
        style_classes[7]['label'] = tr('High [%i people/cell]') % classes[7]

        # Override associated quantities in colour style
        for i in range(len(classes)):
            if i == 0:
                transparency = 100
            else:
                transparency = 0

            style_classes[i]['quantity'] = classes[i]
            style_classes[i]['transparency'] = transparency

        # Title
        style_info['legend_title'] = tr('Population Density')

        # Create raster object and return
        R = Raster(I,
                   projection=inundation.get_projection(),
                   geotransform=inundation.get_geotransform(),
                   name=tr('Population which %s') % get_function_title(self),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title},
                   style_info=style_info)
        return R
