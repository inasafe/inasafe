import math
import numpy
from safe.metadata import hazard_earthquake, unit_mmi, layer_raster_numeric, \
    exposure_population, unit_people_per_pixel
from third_party.odict import OrderedDict

from safe.defaults import get_defaults
from safe.impact_functions.core import default_minimum_needs
from safe.impact_functions.earthquake.itb_earthquake_fatality_model import (
    ITBFatalityFunction)
from safe.common.utilities import ugettext as tr


class PAGFatalityFunction(ITBFatalityFunction):
    """
    Population Vulnerability Model Pager
    Loss ratio(MMI) = standard normal distrib( 1 / BETA * ln(MMI/THETA)).
    Reference:
    Jaiswal, K. S., Wald, D. J., and Hearne, M. (2009a).
    Estimating casualties for large worldwide earthquakes using an empirical
    approach. U.S. Geological Survey Open-File Report 2009-1136.

    :author Helen Crowley
    :rating 3

    :param requires category=='hazard' and \
                    subcategory=='earthquake' and \
                    layertype=='raster' and \
                    unit=='MMI'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster'
    """

    class Metadata(ITBFatalityFunction.Metadata):
        """Metadata for PAG Fatality Function.

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
                'id': 'PAGFatalityFunction.',
                'name': tr('PAG Fatality Function.'),
                'impact': tr('Die or be displaced'),
                'author': 'N/A',
                'date_implemented': 'N/A',
                'overview': tr(
                    'To assess the impact of earthquake on population based '
                    'on earthquake model developed by ITB')
            }
            dict_meta = {
                'id': values['id'],
                'name': values['name'],
                'impact': values['impact'],
                'author': 'Helen Crowley',
                'date_implemented': values['date_implemented'],
                'overview': values['overview'],
                'categories': {
                    'hazard': {
                        'subcategory': hazard_earthquake,
                        'units': [unit_mmi],
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
    synopsis = tr('To assess the impact of earthquake on population based on '
                  'Population Vulnerability Model Pager')
    citations = \
        tr(' * Jaiswal, K. S., Wald, D. J., and Hearne, M. (2009a). '
           '   Estimating casualties for large worldwide earthquakes using '
           '   an empirical approach. U.S. Geological Survey Open-File '
           '   Report 2009-1136.')
    limitation = ''
    detailed_description = ''
    title = tr('Die or be displaced according Pager model')
    defaults = get_defaults()

    # see https://github.com/AIFDR/inasafe/issues/628
    default_needs = default_minimum_needs()
    default_needs[tr('Water')] = 67

    parameters = OrderedDict([
        ('Theta', 11.067),
        ('Beta', 0.106),  # Model coefficients
        # Rates of people displaced for each MMI level
        ('displacement_rate', {
        1: 0, 1.5: 0, 2: 0, 2.5: 0, 3: 0,
        3.5: 0, 4: 0, 4.5: 0, 5: 0, 5.5: 0,
        6: 1.0, 6.5: 1.0, 7: 1.0, 7.5: 1.0,
        8: 1.0, 8.5: 1.0, 9: 1.0, 9.5: 1.0,
        10: 1.0}),
        ('mmi_range', list(numpy.arange(2, 10, 0.5))),
        ('step', 0.25),
        # Threshold below which layer should be transparent
        ('tolerance', 0.01),
        ('calculate_displaced_people', True),
        ('postprocessors', OrderedDict([
            ('Gender', {'on': True}),
            ('Age', {
                'on': True,
                'params': OrderedDict([
                    ('youth_ratio', defaults['YOUTH_RATIO']),
                    ('adult_ratio', defaults['ADULT_RATIO']),
                    ('elder_ratio', defaults['ELDER_RATIO'])])}),
            ('MinimumNeeds', {'on': True})])),
        ('minimum needs', default_needs)])

    def fatality_rate(self, mmi):
        """Pager method to compute fatality rate"""

        N = math.sqrt(2 * math.pi)
        THETA = self.parameters['Theta']
        BETA = self.parameters['Beta']

        x = math.log(mmi / THETA) / BETA
        return math.exp(-x * x / 2.0) / N
