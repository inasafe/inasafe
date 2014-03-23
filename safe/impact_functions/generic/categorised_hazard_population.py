import numpy
from safe.common.utilities import OrderedDict
from safe.defaults import get_defaults
from safe.impact_functions.core import (FunctionProvider,
                                        get_hazard_layer,
                                        get_exposure_layer,
                                        get_question,
                                        get_function_title)
from safe.impact_functions.styles import flood_population_style as style_info
from safe.metadata import hazard_all, unit_normalised, layer_raster_numeric, \
    exposure_population, unit_people_per_pixel
from safe.storage.raster import Raster
from safe.common.utilities import (ugettext as tr,
                                   format_int,
                                   round_thousand)
from safe.common.tables import Table, TableRow
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata


class CategorisedHazardPopulationImpactFunction(FunctionProvider):
    """Plugin for impact of population as derived by categorised hazard

    :author AIFDR
    :rating 2
    :param requires category=='hazard' and \
                    unit=='normalised' and \
                    layertype=='raster'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster'
    """

    class Metadata(ImpactFunctionMetadata):
        """Metadata for Categorised Hazard Population Impact Function

           We only need to re-implement get_metadata(), all other behaviours
           are inherited from the abstract base class.
           """

        @staticmethod
        def get_metadata():
            """
            Return metadata as a dictionary

            This is a static method. You can use it to get the metadata in
            dictionary format for an impact function.

            :returns: A dictionary representing all the metadata for the
                concrete impact function.
            :rtype: dict
            """
            values = {
                'name': tr('Categorised Hazard Population Impact Function'),
                'overview': tr(
                    'To assess the impacts of categorized hazards in raster '
                    'format on population raster layer.')
            }
            values = {
                'id': 'CategorisedHazardPopulationImpactFunction',
                'name': tr('Categorised Hazard Population Impact Function'),
                'impact': tr('Be impacted'),
                'author': 'AIFDR',
                'date_implemented': 'N/A',
                'overview': tr(
                    'To assess the impacts of categorized hazards in raster '
                    'format on population raster layer.')
            }
            dict_meta = {
                'id': values['id'],
                'name': values['name'],
                'impact': values['impact'],
                'author': values['author'],
                'date_implemented': values['date_implemented'],
                'overview': values['overview'],
                'categories': {
                    'hazard': {
                        'subcategory': hazard_all,
                        'units': [unit_normalised],
                        'layer_constraints': [layer_raster_numeric]
                    },
                    'exposure': {
                        'subcategory': exposure_population,
                        'units': [unit_people_per_pixel],
                        'layer_constraints': [layer_raster_numeric]
                    }
                }
            }
            return dict_meta

    # Function documentation
    title = tr('Be impacted')
    synopsis = tr('To assess the impacts of categorized hazards in raster '
                  'format on population raster layer.')
    actions = tr('Provide details about how many people would likely need '
                 'to be impacted for each category.')
    hazard_input = tr('A hazard raster layer where each cell represents '
                      'the category of the hazard. There should be 3 '
                      'categories: 1, 2, and 3.')
    exposure_input = tr('An exposure raster layer where each cell represent '
                        'population count.')
    output = tr('Map of population exposed to high category and a table with '
                'number of people in each category')
    detailed_description = \
        tr('This function will calculate how many people will be impacted '
           'per each category for all categories in the hazard layer. '
           'Currently there should be 3 categories in the hazard layer. After '
           'that it will show the result and the total amount of people that '
           'will be impacted for the hazard given.')
    limitation = tr('The number of categories is three.')

    # Configurable parameters
    defaults = get_defaults()
    parameters = OrderedDict([
        ('Categorical thresholds', [0.34, 0.67, 1]),
        ('postprocessors', OrderedDict([
            ('Gender', {'on': True}),
            ('Age', {
                'on': True,
                'params': OrderedDict([
                    ('youth_ratio', defaults['YOUTH_RATIO']),
                    ('adult_ratio', defaults['ADULT_RATIO']),
                    ('elder_ratio', defaults['ELDER_RATIO'])])})]))])

    def run(self, layers):
        """Plugin for impact of population as derived by categorised hazard

        Input
          layers: List of layers expected to contain
              my_hazard: Raster layer of categorised hazard
              my_exposure: Raster layer of population data

        Counts number of people exposed to each category of the hazard

        Return
          Map of population exposed to high category
          Table with number of people in each category
        """

        # The 3 category
        high_t = self.parameters['Categorical thresholds'][2]
        medium_t = self.parameters['Categorical thresholds'][1]
        low_t = self.parameters['Categorical thresholds'][0]

        # Identify hazard and exposure layers
        my_hazard = get_hazard_layer(layers)    # Categorised Hazard
        my_exposure = get_exposure_layer(layers)  # Population Raster

        question = get_question(my_hazard.get_name(),
                                my_exposure.get_name(),
                                self)

        # Extract data as numeric arrays
        C = my_hazard.get_data(nan=0.0)  # Category

        # Calculate impact as population exposed to each category
        P = my_exposure.get_data(nan=0.0, scaling=True)
        H = numpy.where(C <= high_t, P, 0)
        M = numpy.where(C < medium_t, P, 0)
        L = numpy.where(C < low_t, P, 0)

        # Count totals
        total = int(numpy.sum(P))
        high = int(numpy.sum(H)) - int(numpy.sum(M))
        medium = int(numpy.sum(M)) - int(numpy.sum(L))
        low = int(numpy.sum(L))
        total_impact = high + medium + low

        # Don't show digits less than a 1000
        total = round_thousand(total)
        total_impact = round_thousand(total_impact)
        high = round_thousand(high)
        medium = round_thousand(medium)
        low = round_thousand(low)

        # Generate impact report for the pdf map
        table_body = [question,
                      TableRow([tr('People impacted '),
                                '%s' % format_int(total_impact)],
                               header=True),
                      TableRow([tr('People in high hazard area '),
                                '%s' % format_int(high)],
                               header=True),
                      TableRow([tr('People in medium hazard area '),
                                '%s' % format_int(medium)],
                               header=True),
                      TableRow([tr('People in low hazard area'),
                                '%s' % format_int(low)],
                               header=True)]

        impact_table = Table(table_body).toNewlineFreeString()

        # Extend impact report for on-screen display
        table_body.extend([TableRow(tr('Notes'), header=True),
                           tr('Map shows population density in high or medium '
                              'hazard area'),
                           tr('Total population: %s') % format_int(total)])
        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('People in high hazard areas')

        # Generate 8 equidistant classes across the range of flooded population
        # 8 is the number of classes in the predefined flood population style
        # as imported
        # noinspection PyTypeChecker
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
                   projection=my_hazard.get_projection(),
                   geotransform=my_hazard.get_geotransform(),
                   name=tr('Population which %s') % (
                       get_function_title(self).lower()),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title},
                   style_info=style_info)
        return R
