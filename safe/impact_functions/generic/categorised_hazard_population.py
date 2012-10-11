import numpy
from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question, get_function_title
from safe.impact_functions.styles import flood_population_style as style_info
from safe.storage.raster import Raster
from safe.common.utilities import ugettext as tr
from safe.common.tables import Table, TableRow


class CategorisedHazardPopulationImpactFunction(FunctionProvider):
    """Plugin for impact of population as derived by categorised hazard

    :author AIFDR
    :rating 2
    :param requires category=='hazard' and \
                    subcategory=='normalised' and \
                    layertype=='raster'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster'
    :citation citation1
    :citation citation2 \
                next citation2
    :detail The Detail
    """

    title = tr('Be impacted')

    def run(self, layers):
        """Plugin for impact of population as derived by categorised hazard

        Input
          layers: List of layers expected to contain
              H: Raster layer of categorised hazard
              P: Raster layer of population data

        Counts number of people exposed to each category of the hazard

        Return
          Map of population exposed to high category
          Table with number of people in each category
        """

        # The 3 category
        high_t = 1
        medium_t = 0.66
        low_t = 0.34

        # Identify hazard and exposure layers
        inundation = get_hazard_layer(layers)    # Categorised Hazard
        population = get_exposure_layer(layers)  # Population Raster

        question = get_question(inundation.get_name(),
                                population.get_name(),
                                self)

        # Extract data as numeric arrays
        C = inundation.get_data(nan=0.0)  # Category

        # Calculate impact as population exposed to each category
        P = population.get_data(nan=0.0, scaling=True)
        H = numpy.where(C == high_t, P, 0)
        M = numpy.where(C > medium_t, P, 0)
        L = numpy.where(C < low_t, P, 0)

        # Count totals
        total = int(numpy.sum(P))
        high = int(numpy.sum(H))
        medium = int(numpy.sum(M)) - int(numpy.sum(H))
        low = int(numpy.sum(L)) - int(numpy.sum(M))
        total_impact = high + medium + low

        # Don't show digits less than a 1000
        if total > 1000:
            total = total // 1000 * 1000
        if total_impact > 1000:
            total_impact = total_impact // 1000 * 1000
        if high > 1000:
            high = high // 1000 * 1000
        if medium > 1000:
            medium = medium // 1000 * 1000
        if low > 1000:
            low = low // 1000 * 1000

        # Calculate estimated needs based on BNPB Perka 7/2008 minimum bantuan
##        rice = evacuated * 2.8
##        drinking_water = evacuated * 17.5
##        water = evacuated * 67
##        family_kits = evacuated / 5
##        toilets = evacuated / 20

        # Generate impact report for the pdf map
        table_body = [question,
                      TableRow([tr('People impacted '),
                                '%i' % total_impact],
                               header=True),
                      TableRow([tr('People in high hazard area '),
                                '%i' % high],
                               header=True),
                      TableRow([tr('People in medium hazard area '),
                                '%i' % medium],
                               header=True),
                      TableRow([tr('People in low hazard area'),
                                '%i' % low],
                               header=True)]

##                    TableRow([tr('Needs per week'), tr('Total')],
##                               header=True),
##                      [tr('Rice [kg]'), int(rice)],
##                      [tr('Drinking Water [l]'), int(drinking_water)],
##                      [tr('Clean Water [l]'), int(water)],
##                      [tr('Family Kits'), int(family_kits)],
##                      [tr('Toilets'), int(toilets)]]
        impact_table = Table(table_body).toNewlineFreeString()

        # Extend impact report for on-screen display
        table_body.extend([TableRow(tr('Notes'), header=True),
                           tr('Map shows population density in high or medium '
                             'hazard area'),
                           tr('Total population: %i') % total])
##                           tr('Minimum needs are defined in BNPB '
##                             'regulation 7/2008')])
        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('People in high hazard areas')

        # Generare 8 equidistant classes across the range of flooded population
        # 8 is the number of classes in the predefined flood population style
        # as imported
        classes = numpy.linspace(numpy.nanmin(M.flat[:]),
                                 numpy.nanmax(M.flat[:]), 8)

        # Modify labels in existing flood style to show quantities
        style_classes = style_info['style_classes']

        style_classes[1]['label'] = tr('Low [%i people/cell]') % classes[1]
        style_classes[4]['label'] = tr('Medium [%i people/cell]') % classes[4]
        style_classes[7]['label'] = tr('High [%i people/cell]') % classes[7]

        style_info['legend_title'] = tr('Population Density')

        # Create raster object and return
        R = Raster(M,
                   projection=inundation.get_projection(),
                   geotransform=inundation.get_geotransform(),
                   name=tr('Population which %s') % get_function_title(self),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title},
                   style_info=style_info)
        return R
