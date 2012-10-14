import numpy
from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question, get_function_title
from safe.impact_functions.styles import flood_population_style as style_info
from safe.storage.raster import Raster
from safe.common.utilities import ugettext as tr
from safe.common.tables import Table, TableRow


class WBFloodEvacuationFunction(FunctionProvider):
    """Risk plugin for flood evacuation

    :author AIFDR
    :rating 4
    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype=='raster' and \
                    unit=='m'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster' and \
                    datatype=='density'
    """

    title = tr('Need evacuation')

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

        # Depth above which people are regarded affected [m]
        threshold = 1.0  # Threshold [m]

        # Identify hazard and exposure layers
        inundation = get_hazard_layer(layers)  # Flood inundation [m]
        population = get_exposure_layer(layers)

        question = get_question(inundation.get_name(),
                                population.get_name(),
                                self)

        # Extract data as numeric arrays
        D = inundation.get_data(nan=0.0)  # Depth

        # Calculate impact as population exposed to depths > threshold
        P = population.get_data(nan=0.0, scaling=True)
        I = numpy.where(D > threshold, P, 0)
        M = numpy.where(D > 0.5, P, 0)
        L = numpy.where(D > 0.3, P, 0)

        # Count totals
        total = int(numpy.sum(P))
        evacuated = int(numpy.sum(I))
        medium = int(numpy.sum(M)) - int(numpy.sum(I))
        low = int(numpy.sum(L)) - int(numpy.sum(M))

        # Don't show digits less than a 1000
        if total > 1000:
            total = total // 1000 * 1000
        if evacuated > 1000:
            evacuated = evacuated // 1000 * 1000
        if medium > 1000:
            medium = medium // 1000 * 1000
        if low > 1000:
            low = low // 1000 * 1000

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
                                 'evacuation'))]
                      #,
##                      TableRow([tr('People in 50cm to 1m of water '),
##                                '%i' % medium],
##                               header=True),
##                      TableRow([tr('People in 30cm to 50cm of water'),
##                                '%i' % low],
##                               header=True)]
##                      TableRow([tr('Needs per week'), tr('Total')],
##                               header=True),
##                      [tr('Rice [kg]'), int(rice)],
##                      [tr('Drinking Water [l]'), int(drinking_water)],
##                      [tr('Clean Water [l]'), int(water)],
##                      [tr('Family Kits'), int(family_kits)],
##                      [tr('Toilets'), int(toilets)]]
        impact_table = Table(table_body).toNewlineFreeString()

        # Extend impact report for on-screen display
        table_body.extend([TableRow(tr('Notes:'), header=True),
                           tr('Total population: %i') % total,
                           tr('People need evacuation if flood levels '
                             'exceed %(eps)i m') % {'eps': threshold},
                           tr('People in 50cm to 1m of water: %i') % medium,
                           tr('People in 30cm to 50cm of water: %i') % low])
##                           tr('Minimum needs are defined in BNPB '
##                             'regulation 7/2008')])
        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('People in need of evacuation')
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
