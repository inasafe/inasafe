# coding=utf-8

"""Notes which are specific for an exposure and a hazard."""

from safe.utilities.i18n import tr
from safe.definitions.hazard import hazard_volcanic_ash
from safe.definitions.exposure import exposure_population

ITEMS = (
    {
        'hazard': hazard_volcanic_ash,
        'exposure': exposure_population,
        'actions': [
            tr('Do you have enough masks for people in the affected area?'),
        ],
        'notes': [
        ]
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
            return item['notes']
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
            return item['actions']
    return []
