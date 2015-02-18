# coding=utf-8
"""**Pager Earthquake fatality model**

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__revision__ = '$Format:%H$'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import math
import numpy
from collections import OrderedDict

from safe.definitions import (
    hazard_earthquake,
    unit_mmi,
    layer_raster_continuous,
    exposure_population,
    unit_people_per_pixel,
    hazard_definition,
    exposure_definition
)
from safe.defaults import (
    get_defaults,
    default_minimum_needs,
    default_provenance
)
from safe.impact_functions.earthquake.itb_earthquake_fatality_model import (
    ITBFatalityFunction)
from safe.utilities.i18n import tr
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters


class PAGFatalityFunction(ITBFatalityFunction):
    # noinspection PyUnresolvedReferences
    """Population Vulnerability Model Pager.

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

        .. versionadded:: 2.1

        We only need to re-implement get_metadata(), all other behaviours
        are inherited from the abstract base class.
        """

        @staticmethod
        def get_metadata():
            """Return metadata as a dictionary.

            This is a static method. You can use it to get the metadata in
            dictionary format for an impact function.

            :returns: A dictionary representing all the metadata for the
                concrete impact function.
            :rtype: dict
            """
            dict_meta = {
                'id': 'PAGFatalityFunction',
                'name': tr('PAG Fatality Function'),
                'impact': tr('Die or be displaced according Pager model'),
                'title': tr('Die or be displaced according Pager model'),
                'author': 'Helen Crowley',
                'date_implemented': 'N/A',
                'overview': tr(
                    'To assess the impact of earthquake on population based '
                    'on Population Vulnerability Model Pager'),
                'detailed_description': '',
                'hazard_input': '',
                'exposure_input': '',
                'output': '',
                'actions': '',
                'limitations': [],
                'citations': [
                    tr('Jaiswal, K. S., Wald, D. J., and Hearne, M. (2009a). '
                       'Estimating casualties for large worldwide earthquakes '
                       'using an empirical approach. U.S. Geological Survey '
                       'Open-File Report 2009-1136.')
                ],
                'categories': {
                    'hazard': {
                        'definition': hazard_definition,
                        'subcategories': [hazard_earthquake],
                        'units': [unit_mmi],
                        'layer_constraints': [layer_raster_continuous]
                    },
                    'exposure': {
                        'definition': exposure_definition,
                        'subcategories': [exposure_population],
                        'units': [unit_people_per_pixel],
                        'layer_constraints': [layer_raster_continuous]
                    }
                }
            }
            return dict_meta

    defaults = get_defaults()

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
                    ('elderly_ratio', defaults['ELDERLY_RATIO'])])}),
            ('MinimumNeeds', {'on': True})])),
        ('minimum needs', default_minimum_needs()),
        ('provenance', default_provenance())])
    parameters = add_needs_parameters(parameters)

    # noinspection PyPep8Naming
    def fatality_rate(self, mmi):
        """Pager method to compute fatality rate.

        :param mmi: MMI

        :returns: Fatality rate
        """

        N = math.sqrt(2 * math.pi)
        THETA = self.parameters['Theta']
        BETA = self.parameters['Beta']

        x = math.log(mmi / THETA) / BETA
        return math.exp(-x * x / 2.0) / N
