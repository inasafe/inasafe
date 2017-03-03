# coding=utf-8

"""Definitions relating to hazards category."""
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

hazard_category_single_event = {
    'key': 'single_event',
    'name': tr('Single event'),
    # short name is used when concatenating map_title in IF
    'short_name': tr('event'),
    'description': tr(
        '<b>Single event</b> hazard data can be based on either a specific  '
        'event that has happened in the past, for example a flood like '
        'Jakarta 2013, or a possible event, such as the tsunami that results '
        'from an earthquake near Bima, that might happen in the future.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

hazard_category_multiple_event = {
    'key': 'multiple_event',
    'name': tr('Multiple event'),
    # short name is used when concatenating map_title in IF
    'short_name': tr('hazard'),
    'description': tr(
        '<b>Multiple event</b> hazard data can be based on historical '
        'observations such as a hazard map of all observed volcanic '
        'deposits around a volcano.'
        '<p>This type of hazard data shows those locations that might be '
        'impacted by a volcanic eruption in the future. Another example '
        'might be a probabilistic hazard model that shows the likelihood of a '
        'magnitude 7 earthquake happening in the next 50 years.</p>'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

hazard_category_all = [
    hazard_category_single_event,
    hazard_category_multiple_event
]

hazard_category = {
    'key': 'hazard_category',
    'name': tr('Scenario'),
    'description': tr(
        'This describes the type of hazard scenario that is represented by '
        'the layer. There are two possible values for this attribute, single '
        'event and multiple event.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'types': [
        hazard_category_single_event,
        hazard_category_multiple_event
    ]
}
