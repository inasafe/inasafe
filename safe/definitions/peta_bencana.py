from safe.utilities.i18n import tr

development_api = {
    'key': 'development_api',
    'name': tr('Development API'),
    'url': 'https://data-dev.petabencana.id/floods'
           '?city={city_code}&geoformat=geojson&format=json&minimum_state=1',
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
    'key': 'development_api',
    'name': tr('Development API'),
    'url': 'https://data.petabencana.id/floods'
           '?city={city_code}&geoformat=geojson&format=json&minimum_state=1',
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