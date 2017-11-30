# coding=utf-8

"""Definitions relating to extra keywords."""

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
