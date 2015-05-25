# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - Metadata for ITB Earthquake
Impact Function on Population.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.common.utilities import OrderedDict
from safe.defaults import default_minimum_needs, default_provenance
from safe.definitions import hazard_definition, hazard_earthquake, unit_mmi, \
    layer_raster_continuous, exposure_definition, exposure_population, \
    unit_people_per_pixel
from safe.defaults import (
    default_gender_postprocessor,
    age_postprocessor,
    minimum_needs_selector)
from safe.utilities.i18n import tr
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.impact_functions.earthquake.\
    itb_earthquake_fatality_model.parameter_definitions import (
        mmi_range,
        displacement_rate,
        x_coefficient,
        y_coefficient,
        step,
        tolerance,
        displaced_people,
        default_provenance)

__author__ = 'lucernae'
__project_name__ = 'inasafe'
__filename__ = 'metadata_definitions'
__date__ = '24/03/15'
__copyright__ = 'lana.pcfre@gmail.com'


class ITBFatalityMetadata(ImpactFunctionMetadata):
    """Metadata for ITB Fatality function.

    .. versionadded:: 2.1

    We only need to re-implement as_dict(), all other behaviours
    are inherited from the abstract base class.
    """

    @staticmethod
    def as_dict():
        """Return metadata as a dictionary

        This is a static method. You can use it to get the metadata in
        dictionary format for an impact function.

        :returns: A dictionary representing all the metadata for the
            concrete impact function.
        :rtype: dict
        """
        dict_meta = {
            'id': 'ITBFatalityFunction',
            'name': tr('Earthquake ITB fatality function'),
            'impact': tr('Die or be displaced'),
            'title': tr('Die or be displaced'),
            'function_type': 'old-style',
            'author': 'Hadi Ghasemi',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impact of earthquake on population based '
                'on the earthquake model for Indonesia developed by ITB.'),
            'detailed_description': tr(
                'This model was developed by Institut Teknologi Bandung '
                '(ITB) and implemented by Dr. Hadi Ghasemi, Geoscience '
                'Australia\n'
                'Algorithm:\n'
                'In this study, the same functional form as Allen (2009) '
                'is adopted o express fatality rate as a function of '
                'intensity (see Eq. 10 in the report). The Matlab '
                'built-in function (fminsearch) for Nelder-Mead algorithm '
                'was used to estimate the model parameters. The objective '
                'function (L2G norm) that is minimized during the '
                'optimisation is the same as the one used by Jaiswal '
                'et al. (2010).\n'
                'The coefficients used in the indonesian model are '
                'x=0.62275231, y=8.03314466, zeta=2.15'),
            'hazard_input': '',
            'exposure_input': '',
            'output': '',
            'actions': tr(
                'Provide details about the population including '
                'estimates for mortalities and displaced persons.'),
            'limitations': [
                tr('The model is based on a limited number of observed '
                   'fatality rates during four previous fatal events.'),
                tr('The model clearly over-predicts the fatality rates at '
                   'intensities higher than VIII.'),
                tr('The model only estimates the expected fatality rate '
                   'for a given intensity level. The associated '
                   'uncertainty for the proposed model is not addressed.'),
                tr('There are few known issues in the  current model:\n\n'
                   '* rounding MMI values to the nearest 0.5,\n'
                   '* Implemention of Finite-Fault models of candidate '
                   '  events, and\n'
                   '* consistency between selected GMPEs with those in '
                   '  use by BMKG.\n')
            ],
            'citations': [
                tr('Indonesian Earthquake Building-Damage and Fatality '
                   'Models and Post Disaster Survey Guidelines '
                   'Development Bali, 27-28 February 2012, 54pp.'),
                tr('Allen, T. I., Wald, D. J., Earle, P. S., Marano, K. '
                   'D., Hotovec, A. J., Lin, K., and Hearne, M., 2009. An '
                   'Atlas of ShakeMaps and population exposure catalog '
                   'for earthquake loss modeling, Bull. Earthq. Eng. 7, '
                   '701-718.'),
                tr('Jaiswal, K., and Wald, D., 2010. An empirical model '
                   'for global earthquake fatality estimation, Earthq. '
                   'Spectra 26, 1017-1037.')
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
            },
            'parameters': OrderedDict([
                # Model coefficients
                ('x', x_coefficient()),
                ('y', y_coefficient()),
                # Rates of people displaced for each MMI level
                ('displacement_rate', displacement_rate()),
                ('mmi_range', mmi_range()),
                ('step', step()),
                # Threshold below which layer should be transparent
                ('tolerance', tolerance()),
                ('calculate_displaced_people', displaced_people()),
                ('postprocessors', OrderedDict([
                    ('Gender', default_gender_postprocessor()),
                    ('Age', age_postprocessor()),
                    ('MinimumNeeds', minimum_needs_selector()),
                    ])),
                ('minimum needs', default_minimum_needs()),
                ('provenance', default_provenance())
            ])
        }
        return dict_meta
