# coding=utf-8

"""Definitions relating to extra keywords."""

from datetime import datetime
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


extra_keyword_analysis_type = {
    'key': 'analysis_type',
    'name': tr('Analysis type'),
    'description': None
}

extra_keyword_latitude = {
    'key': 'latitude',
    'name': tr('Latitude'),
    'description': None
}

extra_keyword_longitude = {
    'key': 'longitude',
    'name': tr('Longitude'),
    'description': None
}

extra_keyword_magnitude = {
    'key': 'magnitude',
    'name': tr('Magnitude'),
    'description': None
}

extra_keyword_depth = {
    'key': 'depth',
    'name': tr('Depth'),
    'description': None
}

extra_keyword_description = {
    'key': 'description',
    'name': tr('Description'),
    'description': None
}

extra_keyword_location = {
    'key': 'location',
    'name': tr('Location'),
    'description': None
}

extra_keyword_time_zone = {
    'key': 'time_zone',
    'name': tr('Time zone'),
    'description': None
}

extra_keyword_x_minimum = {
    'key': 'x_minimum',
    'name': tr('X minimum'),
    'description': None
}

extra_keyword_x_maximum = {
    'key': 'x_maximum',
    'name': tr('X maximum'),
    'description': None
}

extra_keyword_y_minimum = {
    'key': 'y_minimum',
    'name': tr('Y minimum'),
    'description': None
}

extra_keyword_y_maximum = {
    'key': 'y_maximum',
    'name': tr('Y maximum'),
    'description': None
}

extra_keyword_volcano_name = {
    'key': 'volcano_name',
    'name': tr('Volcano name'),
    'description': tr('The name of the volcano.'),
    'type': unicode
}

extra_keyword_eruption_height = {
    'key': 'volcano_eruption_height',
    'name': tr('Eruption height'),
    'description': tr(
        'The ash column height. It is calculated from the vent of the volcano '
        'in metres.'),
    'type': float
}

extra_keyword_volcano_eruption_event_time = {
    'key': 'volcano_eruption_event_time',
    'name': tr('Eruption event time'),
    'description': tr(
        'The time of the eruption of the volcano.'),
    'type': datetime,
    'store_format': '%Y-%m-%dT%H:%M:%S',
    'show_format': '%H:%M:%S %d %b %Y'
}

volcano_alert_normal = {
    'key': 'volcano_alert_normal',
    'name': tr('Normal'),
    'description': tr(
        'Volcano is in typical background, noneruptive state'),
    'citations': [
        {
            'text': tr(
                'Volcanic alert-levels characterize conditions at U.S. '
                'volcanoes'),
            'link': 'https://volcanoes.usgs.gov/vhp/about_alerts.html'
        }
    ],
}
volcano_alert_advisory = {
    'key': 'volcano_alert_advisory',
    'name': tr('Advisory'),
    'description': tr(
        'Volcano is exhibiting signs of elevated unrest above known '
        'background level.'),
    'citations': [
        {
            'text': tr(
                'Volcanic alert-levels characterize conditions at U.S. '
                'volcanoes'),
            'link': 'https://volcanoes.usgs.gov/vhp/about_alerts.html'
        }
    ],
}
volcano_alert_watch = {
    'key': 'volcano_alert_watch',
    'name': tr('Watch'),
    'description': tr(
        'Volcano is exhibiting heightened or escalating unrest with increased '
        'potential of eruption, timeframe uncertain.'),
    'citations': [
        {
            'text': tr(
                'Volcanic alert-levels characterize conditions at U.S. '
                'volcanoes'),
            'link': 'https://volcanoes.usgs.gov/vhp/about_alerts.html'
        }
    ],
}
volcano_alert_warning = {
    'key': 'volcano_alert_warning',
    'name': tr('Warning'),
    'description': tr(
        'Hazardous eruption is imminent, underway, or suspected.'),
    'citations': [
        {
            'text': tr(
                'Volcanic alert-levels characterize conditions at U.S. '
                'volcanoes'),
            'link': 'https://volcanoes.usgs.gov/vhp/about_alerts.html'
        }
    ],
}

extra_keyword_volcano_alert_level = {
    'key': 'volcano_alert_level',
    'name': tr('Volcano alert level'),
    'description': tr(
        'This information shows the estimated severity level of the model. It '
        'is usually a choice between Normal, Advisory, Watch, or Warning.'),
    'type': unicode,
    'options': [
        volcano_alert_normal,
        volcano_alert_advisory,
        volcano_alert_watch,
        volcano_alert_warning,
    ]
}

ash_extra_keywords = [
    extra_keyword_volcano_name,
    extra_keyword_eruption_height,
    extra_keyword_volcano_eruption_event_time,
    extra_keyword_volcano_alert_level,
]

all_extra_keywords = [
    extra_keyword_analysis_type,
    extra_keyword_depth,
    extra_keyword_description,
    extra_keyword_latitude,
    extra_keyword_location,
    extra_keyword_longitude,
    extra_keyword_magnitude,
    extra_keyword_time_zone,
    extra_keyword_x_maximum,
    extra_keyword_x_minimum,
    extra_keyword_y_maximum,
    extra_keyword_y_minimum,
]

# map all extra keywords to a pair of key and name
all_extra_keywords_name = {}
for extra_keyword in all_extra_keywords:
    all_extra_keywords_name[extra_keyword['key']] = extra_keyword['name']

# map all extra keywords to a pair of key and description
all_extra_keywords_description = {}
for extra_keyword in all_extra_keywords:
    description = extra_keyword.get('description')
    if description:
        all_extra_keywords_description[extra_keyword['key']] = description
    else:
        all_extra_keywords_description[extra_keyword['key']] = (
            extra_keyword['name'])
