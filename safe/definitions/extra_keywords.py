# coding=utf-8

"""Definitions relating to extra keywords."""

from datetime import datetime
import pytz
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


extra_keyword_analysis_type = {
    'key': 'analysis_type',
    'name': tr('Analysis type'),
    'description': tr('')
}

timezones_dicts = [
    {'key': k, 'name': k} for k in pytz.common_timezones
]

# Generic Extra Keywords
extra_keyword_time_zone = {
    'key': 'time_zone',
    'name': tr('Time zone'),
    'description': tr('Time zone'),
    'type': unicode,
    'options': timezones_dicts
}
extra_keyword_region = {
    'key': 'region',
    'name': tr('Region'),
    'description': tr('Region of the event.'),
    'type': unicode
}

# Earthquake Extra Keywords
extra_keyword_earthquake_latitude = {
    'key': 'earthquake_latitude',
    'name': tr('Latitude'),
    'description': tr('The latitude of the earthquake epicentre.')
}

extra_keyword_earthquake_longitude = {
    'key': 'earthquake_longitude',
    'name': tr('Longitude'),
    'description': tr('The longitude of the earthquake epicentre.')
}

extra_keyword_earthquake_magnitude = {
    'key': 'earthquake_magnitude',
    'name': tr('Magnitude'),
    'description': tr('The magnitude of the earthquake in Richter scale.')
}

extra_keyword_earthquake_depth = {
    'key': 'earthquake_depth',
    'name': tr('Depth'),
    'description': tr('The depth of earthquake epicentre in kilometre unit.')
}

extra_keyword_earthquake_description = {
    'key': 'earthquake_description',
    'name': tr('Description'),
    'description': tr('Additional description of the earthquake event.')
}

extra_keyword_earthquake_location = {
    'key': 'earthquake_location',
    'name': tr('Location'),
    'description': tr(
        'The location information of the earthquake event. It usually refers '
        'to the nearest city in the location.')
}

extra_keyword_earthquake_event_time = {
    'key': 'earthquake_event_time',
    'name': tr('Earthquake event time'),
    'description': tr(
        'The time of the earthquake happen.'),
    'type': datetime,
    'store_format': '%Y-%m-%dT%H:%M:%S.%f',
    'store_format2': '%Y-%m-%dT%H:%M:%S',
    'show_format': '%H:%M:%S %d %b %Y'
}

extra_keyword_earthquake_x_minimum = {
    'key': 'earthquake_x_minimum',
    'name': tr('X minimum'),
    'description': tr(
        'The minimum value of x coordinate of the shakemaps. It indicates the '
        'extent of the event.')
}

extra_keyword_earthquake_x_maximum = {
    'key': 'earthquake_x_maximum',
    'name': tr('X maximum'),
    'description': tr(
        'The maximum value of x coordinate of the shakemaps. It indicates the '
        'extent of the event.')
}

extra_keyword_earthquake_y_minimum = {
    'key': 'earthquake_y_minimum',
    'name': tr('Y minimum'),
    'description': tr(
        'The minimum value of y coordinate of the shakemaps. It indicates the '
        'extent of the event.')
}

extra_keyword_earthquake_y_maximum = {
    'key': 'earthquake_y_maximum',
    'name': tr('Y maximum'),
    'description': tr(
        'The maximum value of y coordinate of the shakemaps. It indicates the '
        'extent of the event.')
}


# Volcano Extra Keywords
extra_keyword_volcano_event_id = {
    'key': 'volcano_event_id',
    'name': tr('Volcano event ID'),
    'description': tr(
        'The ID of the volcano eruption. It is constructed from '
        'YYYYMMDDHHmm[zoneoffset]_[volcano_name]. YYYYMMDDHHmm is the format '
        'of the eruption event time. [zone offset] is the of set of its time '
        'zoen. [volcano_name] is the name of the volcano. For example: '
        '201712012200+0800_Agung'),
    'type': unicode
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
    'store_format': '%Y-%m-%dT%H:%M:%S.%f',
    'store_format2': '%Y-%m-%dT%H:%M:%S',
    'show_format': '%H:%M:%S %d %b %Y'
}

extra_keyword_volcano_latitude = {
    'key': 'volcano_latitude',
    'name': tr('Latitude'),
    'description': tr('The latitude of the volcano.'),
    'type': float
}

extra_keyword_volcano_longitude = {
    'key': 'volcano_longitude',
    'name': tr('Longitude'),
    'description': tr('The longitude of the volcano.'),
    'type': float
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

extra_keyword_volcano_height = {
    'key': 'volcano_height',
    'name': tr('Volcano height'),
    'description': tr(
        'The height of the vent of a volcano. It is calculated from the sea '
        'level in metres.'),
    'type': float,
}

earthquake_extra_keywords = [
    extra_keyword_earthquake_latitude,
    extra_keyword_earthquake_longitude,
    extra_keyword_earthquake_magnitude,
    extra_keyword_earthquake_depth,
    extra_keyword_earthquake_description,
    extra_keyword_earthquake_location,
    extra_keyword_earthquake_event_time,
    extra_keyword_time_zone,
    extra_keyword_earthquake_x_maximum,
    extra_keyword_earthquake_x_minimum,
    extra_keyword_earthquake_y_maximum,
    extra_keyword_earthquake_y_minimum,
]

ash_extra_keywords = [
    extra_keyword_volcano_name,
    extra_keyword_region,
    extra_keyword_eruption_height,
    extra_keyword_volcano_eruption_event_time,
    extra_keyword_volcano_alert_level,
    extra_keyword_time_zone,
    extra_keyword_volcano_latitude,
    extra_keyword_volcano_longitude,
    extra_keyword_volcano_height
]

all_extra_keywords = [
    extra_keyword_analysis_type,
    extra_keyword_time_zone,

    extra_keyword_earthquake_depth,
    extra_keyword_earthquake_description,
    extra_keyword_earthquake_event_time,
    extra_keyword_earthquake_latitude,
    extra_keyword_earthquake_location,
    extra_keyword_earthquake_longitude,
    extra_keyword_earthquake_magnitude,
    extra_keyword_earthquake_x_maximum,
    extra_keyword_earthquake_x_minimum,
    extra_keyword_earthquake_y_maximum,
    extra_keyword_earthquake_y_minimum,

    extra_keyword_volcano_name,
    extra_keyword_eruption_height,
    extra_keyword_volcano_eruption_event_time,
    extra_keyword_volcano_alert_level,
    extra_keyword_volcano_latitude,
    extra_keyword_volcano_longitude,
    extra_keyword_volcano_height
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
    del extra_keyword  # Make sure there is no duplicate dictionary
