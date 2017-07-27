# coding=utf-8

"""Definitions relating to exposure classifications."""

from safe.utilities.i18n import tr
from safe.definitions.constants import DO_NOT_REPORT

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

exposure_classification_type = tr('Exposure Classification'),

# We should include this somewhere in definitions:
# tr(
#     'An exposure classification is used to group exposure features '
#     'that have similar properties. For example a house and an apartment '
#     'building might be grouped into an exposure class called '
#     '"residential". Making groups in this way will make the reports '
#     'generated by InaSAFE easier to read and less verbose.'
# )

# Each classification should have an "other" group at the end of the
# classification. Each features without a classification will go in the last
# item of the list.

# Note from Etienne 25/10/16
# The osm_downloader is not used in InaSAFE itself. It is used in OSM-Reporter
# to generate the value_mapping. Please do not remove it.
# See https://github.com/kartoza/osm-reporter/wiki how to use this key.

do_not_report_class = {
    'key': DO_NOT_REPORT,
    'name': tr('Do Not Report'),
    'description': tr(
        'Land use types that will be excluded in the analysis.'),
    'osm_downloader': [],
    'string_defaults': [],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

generic_structure_classes = {
    'key': 'generic_structure_classes',
    'name': tr('Generic Structure Classification'),
    'description': tr(
        'Classification of structure based on OSM.'
    ),
    'type': exposure_classification_type,
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
                'church',
                'mosque',
                'temple',
                'synagogue',
                'worship',
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
                'public',
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
                'construction',
                'yes',
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

generic_road_classes = {
    'key': 'generic_road_classes',
    'name': tr('Generic Road Classification'),
    'description': tr(
        'Classification of roads based on OSM.'
    ),
    'type': exposure_classification_type,
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'classes': [
        {
            'key': 'motorway',
            'name': tr('Motorway'),
            'description': tr(
                'A road designed for fast moving traffic often with multiple '
                'lanes for each direction of traffic.'),
            'osm_downloader': [
                'Motorway link',
                'Motorway or highway',
            ],
            'string_defaults': [
                'motorway link',
                'motorway',
                'trunk link',
                'trunk',
            ],
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
                'A road that provides the main transportation link, often '
                'over a long distance travel characteristic and supporting a '
                'high average velocity.'),
            'string_defaults': [
                'primary link',
                'primary road',
                'primary',
            ],
            'osm_downloader': [
                'Primary link',
                'Primary road',
            ],
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
                'A road that provides a transportation link for medium '
                'distance travel and medium average velocity.'),
            'string_defaults': [
                'secondary link',
                'secondary',
            ],
            'osm_downloader': [
                'Secondary link',
                'Secondary',
            ],
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
                'A road that provides a transportation link for a short '
                'distance travel and low average velocity.'),
            'string_defaults': [
                'local',
                'tertiary link',
                'tertiary',
                'tertiary',
                'unclassified',
            ],
            'osm_downloader': [
                'Tertiary link',
                'Tertiary',
            ],
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
            'description': tr(
                'A route for pedestrian and non-motorised transport.'),
            'osm_downloader': [
                'Cycleway, footpath, etc.',
                'Track',
            ],
            'string_defaults': [
                'cycleway',
                'pedestrian',
                'footway',
                'path',
                'track',
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
                'A road that services residential or local traffic '
                'with low average velocity.'),
            'string_defaults': [
                'living street',
                'other',
                'residential',
                'road',
                'service',
            ],
            'osm_downloader': [
                'Road, residential, living street, etc.'
            ],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        }
    ]
}

generic_place_classes = {
    'key': 'generic_place_classes',
    'name': tr('Generic Place Classification'),
    'description': tr(
        'Classification of place based on OSM.'
    ),
    'type': exposure_classification_type,
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'classes': [
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
                'A second tier urban settlement of local importance, often '
                'with a population of at least 10,000 people and good range '
                'of local facilities including schools, medical facilities '
                'etc. and traditionally a market.'),
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
                'facilities available. People will typically travel to nearby '
                'towns to access facilities.'),
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
                'inhabitants and minimal infrastructure.'),
            'string_defaults': ['hamlet'],
            'osm_downloader': [],
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
                'A complex of runways and buildings for the takeoff, landing, '
                'and maintenance of civil aircraft, with facilities for '
                'passengers.'),
            'osm_downloader': [],
            'string_defaults': ['airport'],
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
            'description': tr('Other'),
            'osm_downloader': [],
            'string_defaults': ['other'],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        }
    ]
}

generic_landcover_classes = {
    'key': 'generic_landcover_classes',
    'name': tr('Generic Landcover Classification'),
    'description': tr(
        'Classification of landcover based on OSM.'
    ),
    'type': exposure_classification_type,
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
                'Predominantly houses or apartment buildings.'),
            'osm_downloader': [],
            'string_defaults': ['residential', 'population'],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'industrial',
            'name': tr('Industrial'),
            'description': tr(
                'Predominantly workshops, factories or warehouses.'),
            'string_defaults': ['industrial'],
            'osm_downloader': [],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'retail',
            'name': tr('Retail'),
            'description': tr(
                'Predominantly shops.'),
            'string_defaults': ['retail'],
            'osm_downloader': [],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'wood',
            'name': tr('Wood'),
            'description': tr(
                'A forested area.'),
            'string_defaults': ['wood', 'forest'],
            'osm_downloader': [],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'farm',
            'name': tr('Farm'),
            'description': tr(
                'An area of farmland used for tillage and pasture (animals, '
                'vegetables, flowers, fruit growing).'),
            'osm_downloader': [],
            'string_defaults': ['farm', 'meadow'],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'water',
            'name': tr('Water'),
            'description': tr(
                'Water bodies both natural and man-made.'),
            'osm_downloader': [],
            'string_defaults': ['water', 'lake'],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        do_not_report_class,
        # Need to put other class in the end
        {
            'key': 'other',
            'name': tr('Other'),
            'description': tr(
                'Any other land use type.'),
            'osm_downloader': [],
            'string_defaults': ['other'],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        }
    ]
}

badan_geologi_landcover_classes = {
    'key': 'badan_geologi_landcover_classes',
    'name': tr('Badan Geologi Landcover Classification'),
    'description': tr(
        'Classification of landcover based on Badan Geologi'),
    'type': exposure_classification_type,
    'citations': [
        {
            'text': tr('Badan Geologi'),
            'link': 'https://github.com/inasafe/inasafe/issues/3947'
        }
    ],
    'classes': [
        {
            'key': 'settlement',
            'name': tr('Settlement'),
            'description': tr('Settlement'),
            'osm_downloader': [],
            'string_defaults': ['Permukiman dan Tempat Kegiatan', '50102'],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'rice_field',
            'name': tr('Rice Field'),
            'description': tr('Rice Field'),
            'osm_downloader': [],
            'string_defaults': ['Sawah', '50306'],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'plantation',
            'name': tr('Plantation'),
            'description': tr('Plantation'),
            'osm_downloader': [],
            'string_defaults': ['Perkebunan / Kebun', '50304'],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'water_supply',
            'name': tr('Water'),
            'description': tr('Water bodies'),
            'osm_downloader': [],
            'string_defaults': [
                'Air Danau / Situ',
                'Air Empang',
                'Air Penggaraman',
                'Air Tambak',
                'Air Tawar Sungai',
                'Air Waduk',
                'Perairan Lainnya',
                '50404',
                '50420',
                '50418',
                '50416',
                '50408',
                '50406',
                '50400'],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'forest',
            'name': tr('Forest'),
            'description': tr('Forest'),
            'osm_downloader': [],
            'string_defaults': ['Hutan Rimba', '50202'],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        do_not_report_class,
        # Need to put other class in the end
        {
            'key': 'other',
            'name': tr('Other'),
            'description': tr(
                'Any other land use type.'),
            'osm_downloader': [],
            'string_defaults': ['other'],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        }
    ]
}


data_driven_classes = {
    'key': 'data_driven_classes',
    'name': tr('Generic Data-driven Classification'),
    'description': tr(
        'Classification based on the content of the exposure dataset.'
    ),
    'type': exposure_classification_type,
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'classes': []
}

exposure_classifications = [
    generic_structure_classes,
    generic_road_classes,
    generic_place_classes,
    generic_landcover_classes,
    badan_geologi_landcover_classes,
    data_driven_classes
]
