# coding=utf-8

"""Definitions relating to value maps.

Value maps are used to map concepts in user data to concepts in InaSAFE.
"""


from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

value_map = {
    'key': 'value_map',
    'name': tr('Attribute value map'),
    'description': tr(
        'Attribute value maps are used to group related attribute '
        'values. For example flooded polygons with attribute values of "yes" '
        ', "YES", "1" and "Flooded" might all be grouped together as '
        '"FLOODPRONE".'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
road_class_mapping = [
    {
        'key': 'motorway',
        'name': tr('Motorway'),
        'description': tr('A road to solve the traffic and have a fare.'),
        'osm_downloader': ['Motorway or highway', 'Motorway link'],
        'string_defaults': [
            'motorway', 'trunk', 'motorway link', 'trunk link'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'primary',
        'name': tr('Primary'),
        'description': tr(
            'A road that service the main transportation with a long distance '
            'travel characteristic and high average velocity.'),
        'string_defaults': ['primary', 'primary link', 'primary road'],
        'osm_downloader': ['Primary road', 'Primary link'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'secondary',
        'name': tr('Secondary'),
        'description': tr(
            'A road that service the transportation with a medium distance '
            'travel characteristic and medium average velocity.'),
        'string_defaults': ['secondary', 'secondary link'],
        'osm_downloader': ['Secondary', 'Secondary link'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'local',
        'name': tr('Local'),
        'description': tr(
            'A road that service the transportation with short distance '
            'travel and low average velocity.'),
        'string_defaults': [
            'local', 'tertiary', 'tertiary', 'tertiary link', 'unclassified'
        ],
        'osm_downloader': ['Tertiary', 'Tertiary link'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'path',
        'name': tr('Path'),
        'description': tr('A road to walk on foot aim.'),
        'osm_downloader': ['Track', 'Cycleway, footpath, etc.'],
        'string_defaults': [
            'path',
            'track',
            'footway',
            'cycleway',
            'cycleway, footpath, etc.'
        ],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'other',
        'name': tr('Other'),
        'description': tr(
            'A road that service the transportation with short travel and '
            'low average velocity.'),
        'string_defaults': [
            'other', 'residential', 'service', 'living street', 'pedestrian',
            'road', 'road, residential, living street, etc.'
        ],
        'osm_downloader': ['Road, residential, living street, etc.'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    }
]
road_class_order = [item['key'] for item in road_class_mapping]

place_class_mapping = [
    {
        'key': 'city',
        'name': tr('City'),
        'description': tr(
            'The largest urban settlements in the territory, normally '
            'including the national, state and provincial capitals.'),
        'osm_downloader': [],
        'string_defaults': ['city'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'Town',
        'name': tr('Town'),
        'description': tr(
            'A second tier urban settlement of local importance, often with a '
            'population of 10,000 people and good range of local facilities '
            'including schools, medical facilities etc and traditionally a '
            'market.'),
        'string_defaults': ['town'],
        'osm_downloader': [],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'Village',
        'name': tr('Village'),
        'description': tr(
            'A smaller distinct settlement, smaller than a town with few '
            'facilities available with people traveling to nearby towns to '
            'access these.'),
        'string_defaults': ['village'],
        'osm_downloader': [],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'hamlet',
        'name': tr('Hamlet'),
        'description': tr(
            'A smaller rural community typically with fewer than 100-200 '
            'inhabitants, few infrastructure.'),
        'string_defaults': ['hamlet'],
        'osm_downloader': ['Tertiary', 'Tertiary link'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'airport',
        'name': tr('Airport'),
        'description': tr(
            'A complex of runways and buildings for the takeoff, landing, and '
            'maintenance of civil aircraft, with facilities for passengers.'),
        'osm_downloader': [],
        'string_defaults': ['airport'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    }
]
place_class_order = [item['key'] for item in place_class_mapping]
