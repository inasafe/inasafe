# coding=utf-8

"""Actions, notes, questions which are specials for a given hazard/exposure."""

from safe.definitions.exposure import (
    exposure_population,
    exposure_road,
)
from safe.definitions.hazard import (
    hazard_volcanic_ash,
    hazard_earthquake,
    hazard_flood,
)
from safe.utilities.i18n import tr, locale

# Notes, for the analysis question, this is specific for French. I put the
# singular and masculine sentence on transifex.
# I put here when it's plural and/or feminine.

ITEMS = (
    {
        'hazard': hazard_volcanic_ash,
        'exposure': exposure_population,
        'actions': [
            {
                'item_category': 'additional_volcanic_ash_on_population',
                'item_header': tr('volcanic ash on population specific'),
                'item_list': [
                    tr('Do you have enough masks for people in '
                       'the affected area?')
                ]
            },
        ],
        'notes': [
        ]
    },
    {
        'hazard': hazard_earthquake,
        'exposure': exposure_population,
        'actions': [],
        'notes': [
            {
                'item_category': 'additional_earthquake_on_population',
                'item_header': tr('earthquake on population specific notes'),
                'item_list': [
                    tr('Map shows the estimated displaced population. '
                       'People are displaced if they experience and survive '
                       'a shake level of more than V on the MMI scale.'),
                    tr('Exposed population varies by the time (day or night, '
                       'weekends, holidays etc.). Such variations are not '
                       'considered in the estimates in the InaSAFE.'),
                    # notes updated to match fatality reporting as ranges
                    tr('The fatality calculation assumes that no fatalities '
                       'occur for shake levels of less than or equal to V on '
                       'the MMI scale.'),
                    tr('Estimated fatality counts are reported as ranges. The '
                       'following ranges are used: 0 - 100, 100 - 1,000, '
                       '1,000 - 10,000, 10,000 - 100,000.'),
                    # notes provided by Hadi Ghasemi
                    tr('Earthquake fatalities are due to a number of factors, '
                       'such as destructive level of ground shaking, tsunami, '
                       'landsliding and fire. The implemented fatality models '
                       'only consider the number of fatalities due to '
                       'the earthquake ground shaking and do not include '
                       'losses due to the other secondary hazards.'),
                    tr('The fatality models do not estimate number of '
                       'injuries or displaced people. '),
                    tr('Empirical fatality models provide an estimate of '
                       'the number of fatalities. There are several sources '
                       'of uncertainty contributing to the overall '
                       'uncertainty of any estimate, such as uncertainties '
                       'in shaking intensity, and population estimates.'),
                    tr('Care should be taken when applying empirical '
                       'earthquake fatality models for ground-motion '
                       'estimation methods that are inconsistent with '
                       'the methods used to calibrate the model.'),
                    # end notes provided by Hadi Ghasemi
                ]
            },
        ]
    },
    {
        'hazard': hazard_flood,
        'exposure': exposure_road,
        'analysis_question': {
            'fr': "Dans l'événement d'une inondation, quelle longueur de "
                  "routes peut-être affectée?"
        }
    },
)


def specific_notes(hazard, exposure):
    """Return notes which are specific for a given hazard and exposure.

    :param hazard: The hazard definition.
    :type hazard: safe.definition.hazard

    :param exposure: The exposure definition.
    :type hazard: safe.definition.exposure

    :return: List of notes specific.
    :rtype: list
    """
    for item in ITEMS:
        if item['hazard'] == hazard and item['exposure'] == exposure:
            return item.get('notes', [])
    return []


def specific_actions(hazard, exposure):
    """Return actions which are specific for a given hazard and exposure.

    :param hazard: The hazard definition.
    :type hazard: safe.definition.hazard

    :param exposure: The exposure definition.
    :type hazard: safe.definition.exposure

    :return: List of actions specific.
    :rtype: list
    """
    for item in ITEMS:
        if item['hazard'] == hazard and item['exposure'] == exposure:
            return item.get('actions', [])
    return []


def specific_analysis_question(hazard, exposure):
    """Return a translated hardcoded analysis question a given hazard/exposure.

    :param hazard: The hazard definition.
    :type hazard: safe.definition.hazard

    :param exposure: The exposure definition.
    :type hazard: safe.definition.exposure

    :return: The analysis question or None if it's not hardcoded.
    :rtype: basestring
    """
    lang = locale()
    for item in ITEMS:
        if item['hazard'] == hazard and item['exposure'] == exposure:
            analysis_questions = item.get('analysis_question', None)
            if not analysis_questions:
                return None
            return analysis_questions.get(lang, None)
    return None
