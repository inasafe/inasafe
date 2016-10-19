# coding=utf-8
"""Definitions relating to exposure classifications.

"""
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


generic_structure_classes = {
    'key': 'generic_exposure_classes',
    'name': tr('Generic Structure'),
    'description': tr(
        'Classification of structure based on OSM.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'classes': [
        {
            'key': 'residential',
            'name': tr('Residential'),
            'description': tr(
                'A structure used to provide shelter for people.'),
            'string_defaults': [
                'dorm',
                'house',
                'residence',
                'residential',
            ],
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
            'description': tr(
                'A structure that provides a service in the education '
                'sector.'),
            'string_defaults': [
                'college',
                'education',
                'kindergarten',
                'school',
                'university',
                'university/college',
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
                'clinic',
                'clinic/doctor',
                'dentist',
                'doctor',
                'health',
                'hospital',
                'pharmacy',
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
                'aerodrome',
                'airport',
                'bus station',
                'bus stop',
                'ferry terminal',
                'station',
                'terminal',
                'transportation',
            ],
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
                'place of worship - buddhist',
                'place of worship - christian',
                'place of worship - hindu',
                'place of worship - islam',
                'place of worship',
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
                'A structure or facility that is used to provide a public '
                'service or other government activity.'),
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
                'accommodation',
                'atm',
                'cafe',
                'clothes',
                'commercial',
                'convenience',
                'economy',
                'fast food',
                'hotel',
                'industrial',
                'mall',
                'market',
                'restaurant',
                'seafood',
                'shoes',
                'shop',
                'supermarket',
                'tailor',
                'warehouse',
                'works',
            ],
            'osm_downloader': [
                'Commercial',
                'Industrial',
                'Supermarket'
            ],
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
                'A structure or facility that is used for entertainment, '
                'sporting or recreation purposes.'),
            'string_defaults': [
                'amusement arcade',
                'cinema',
                'museum',
                'pitch',
                'recreation and entertainment',
                'sport centre',
                'sport',
                'sports facility',
                'stadium',
                'theatre',
                'zoo',
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
                'A structure or facility that provides a service or facility '
                'to the public including emergency services.'),
            'string_defaults': [
                'convention hall',
                'fire station',
                'library',
                'police station',
                'prison',
                'public building',
                'public facility',
                'toilet',
            ],
            'osm_downloader': [
                'Fire Station',
                'Police Station',
                'Public Building',
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
                'animal boarding',
                'lighthouse',
                'other',
                'utility',
                'water well',
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
}

# CLasses order
structure_class_order = [
    item['key'] for item in generic_structure_classes['classes']]