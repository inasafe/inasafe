# coding=utf-8
"""Definitions relating to API that used in Peta Bencana downloader."""
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

development_api = {
    'key': 'development_api',
    'name': tr('Development API'),
    'url': 'https://data-dev.petabencana.id/floods'
           '?city={city_code}&geoformat=geojson&format=json&minimum_state=1',
    'help_url': 'https://docs.petabencana.id/',
    'available_data': [
        {
            'code': 'jbd',
            'name': 'Jabodetabek'
        },
        {
            'code': 'bdg',
            'name': 'Bandung'
        },
        {
            'code': 'sby',
            'name': 'Surabaya'
        }
    ]
}

production_api = {
    'key': 'production_api',
    'name': tr('Production API'),
    'url': 'https://data.petabencana.id/floods'
           '?city={city_code}&geoformat=geojson&format=json&minimum_state=1',
    'help_url': 'https://docs.petabencana.id/',
    'available_data': [
        {
            'code': 'jbd',
            'name': 'Jabodetabek'
        },
        {
            'code': 'bdg',
            'name': 'Bandung'
        },
        {
            'code': 'sby',
            'name': 'Surabaya'
        }
    ]
}
