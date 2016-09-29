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
structure_class_mapping = [
    {
        'key': 'residential',
        'name': tr('Residential'),
        'description': tr(
            'A structure used to provide shelter for people.'),
        'string_defaults': ['house', 'dorm', 'residential' 'residence'],
        'osm_downloader': ['Residential'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'education',
        'name': tr('Education'),
        'description': tr('A structure that provides a service in the '
                          'education sector.'),
        'string_defaults': [
            'kindergarten', 'college', 'school', 'university', 'education',
            'university/college'
        ],
        'osm_downloader': ['School', 'University/College'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'health',
        'name': tr('Health'),
        'description': tr(
            'A structure that provides a service or facility in the '
            'health sector.'),
        'string_defaults': [
            'clinic', 'doctor', 'hospital', 'dentist', 'pharmacy', 'health',
            'clinic/doctor'
        ],
        'osm_downloader': ['Clinic/Doctor', 'Hospital'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'transport',
        'name': tr('Transport'),
        'description': tr(
            'A structure that provides a service or facility in the '
            'transport sector.'),
        'string_defaults': [
            'bus stop', 'bus station', 'station', 'ferry terminal',
            'aerodrome', 'airport', 'terminal', 'transportation'],
        'osm_downloader': [],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'place of worship',
        'name': tr('Place of Worship'),
        'description': tr(
            'A structure or facility that is used for prayer or related '
            'religion activity.'),
        'string_defaults': [
            'place of worship - islam',
            'place of worship - buddhist',
            'place of worship - christian',
            'place of worship - hindu',
            'place of worship'
        ],
        'osm_downloader': [
            'Place of Worship - Islam', 'Place of Worship - Unitarian',
            'Place of Worship - Buddhist', 'Place of Worship'
        ],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'government',
        'name': tr('Government'),
        'description': tr(
            'A structure or facility that is used to provide a public service '
            'or other government activity.'),
        'string_defaults': ['government'],
        'osm_downloader': ['Government'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'commercial',
        'name': tr('Commercial'),
        'description': tr(
            'A structure or facility that is used for commercial or '
            'industrial purposes.'),
        'string_defaults': [
            'supermarket', 'shop', 'market', 'tailor', 'warehouse', 'works',
            'convenience', 'seafood', 'atm', 'mall', 'clothes', 'shoes',
            'commercial', 'industrial', 'economy', 'restaurant', 'cafe',
            'fast food', 'hotel', 'accommodation'
        ],
        'osm_downloader': ['Supermarket', 'Commercial', 'Industrial'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'recreation',
        'name': tr('Recreation'),
        'description': tr(
            'A structure or facility that is used for entertainment, sporting '
            'or recreation purposes.'),
        'string_defaults': [
            'amusement arcade', 'cinema', 'zoo', 'museum', 'theatre',
            'recreation and entertainment' 'stadium', 'sport centre', 'pitch',
            'sports facility', 'sport'
        ],
        'osm_downloader': ['Sports Facility'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    },
    {
        'key': 'public facility',
        'name': tr('Public Facility'),
        'description': tr(
            'A structure or facility that provides a service or facility to '
            'the public including emergency services.'),
        'string_defaults': [
            'library', 'toilet', 'convention hall', 'prison', 'police station',
            'public facility', 'public building', 'fire station'
        ],
        'osm_downloader': [
            'Fire Station',
            'Police Station',
            'Public Building'
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
            'Any other structure frequently mapped.'),
        'string_defaults': [
            'animal boarding', 'water well', 'lighthouse', 'utility', 'other'
        ],
        'osm_downloader': ['Utility'],
        'citations': [
            {
                'text': None,
                'link': None
            }
        ]
    }
]
structure_class_order = [item['key'] for item in structure_class_mapping]
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
