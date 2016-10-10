# coding=utf-8

"""Definitions relating to hazards category.

See https://github.com/inasafe/inasafe/issues/2920#issuecomment-229874044
to have a table showing you classes of each kind of hazard.
"""
from safe.definitionsv4 import concepts, small_number
from safe.utilities.i18n import tr
from safe.definitionsv4.units import unit_centimetres

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# Missing Earthquakes, these IF are using damage curves.
# They are not represented in that file.

generic_hazard_classes = {
    'key': 'generic_hazard_classes',
    'name': tr('Generic classes'),
    'description': concepts['generic_hazard']['description'],
    'citations': concepts['generic_hazard']['citations'],
    'classes': [
        {
            'key': 'high',
            'name': tr('High Hazard Zone'),
            'affected': True,
            'description': tr('The location that has highest impact.'),
            'string_defaults': ['high'],
            'numeric_default_min': 3,
            'numeric_default_max': (4 - small_number),
            'optional': False,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ],
        },
        {
            'key': 'medium',
            'name': tr('Medium Hazard Zone'),
            'affected': True,
            'description': tr('The location that has medium impact.'),
            'string_defaults': ['medium'],
            'numeric_default_min': 2,
            'numeric_default_max': (3 - small_number),
            'optional': False,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ],
        },
        {
            'key': 'low',
            'name': tr('Low Hazard Zone'),
            'affected': True,
            'description': tr('The location that has lowest impact.'),
            'string_defaults': ['low'],
            'numeric_default_min': 0,
            'numeric_default_max': (2 - small_number),
            'optional': False,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ],
        }
    ]
}

volcano_hazard_classes = {
    'key': 'volcano_vector_hazard_classes',
    'name': tr('Volcano classes'),
    'description': tr(
        'Three classes are supported for volcano vector hazard data: '
        '<b>low</b>, <b>medium</b>, or <b>high</b>.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'classes': [
        {
            'key': 'high',
            'name': tr('High Hazard Zone'),
            'affected': True,
            'description': tr('The highest hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana III', 'high'],
            'numeric_default_min': 0,
            'numeric_default_max': (3 - small_number),
            'optional': False,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'medium',
            'name': tr('Medium Hazard Zone'),
            'affected': True,
            'description': tr('The medium hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana II', 'medium'],
            'numeric_default_min': 3,
            'numeric_default_max': (5 - small_number),
            'optional': False,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'low',
            'name': tr('Low Hazard Zone'),
            'affected': True,
            'description': tr('The lowest hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana I', 'low'],
            'numeric_default_min': 5,
            'numeric_default_max': 10,
            'optional': False,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        }
    ]
}

flood_hazard_classes = {
    'key': 'flood_hazard_classes',
    'name': tr('Flood classes'),
    'description': tr(
        'This is a binary description for an area. The area is either '
        '<b>wet</b> (affected by flood water) or <b>dry</b> (not affected '
        'by flood water). This unit does not describe how <b>wet</b> or '
        '<b>dry</b> an area is.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'classes': [
        {
            'key': 'wet',
            'name': tr('wet'),
            'affected': True,
            'description': tr('Water above ground height.'),
            'string_defaults': ['wet', '1', 'YES', 'y', 'yes'],
            'numeric_default_min': 1,
            'numeric_default_max': 9999999999,
            'optional': True,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'dry',
            'name': tr('dry'),
            'affected': False,
            'description': tr('No water above ground height.'),
            'string_defaults': ['dry', '0', 'No', 'n', 'no'],
            'numeric_default_min': 0,
            'numeric_default_max': (1 - small_number),
            'optional': True,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        }
    ]
}

ash_hazard_classes = {
    'key': 'ash_hazard_classes',
    'name': tr('Ash classes'),
    'description': tr(
        'Three four are supported for ash vector hazard data: '
        '<b>very low</b>, <b>low</b>, <b>medium</b>, <b>high</b> or '
        '<b>very high</b>.'),
    'unit': unit_centimetres,
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'classes': [
        {
            'key': 'very high',
            'name': tr('Very high'),
            'affected': True,
            'description': tr('Very High.'),
            'numeric_default_min': 10,
            'numeric_default_max': 9999999999,
            'optional': True,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'high',
            'name': tr('High'),
            'affected': True,
            'description': tr('High'),
            'numeric_default_min': 5,
            'numeric_default_max': 10,
            'optional': True,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'medium',
            'name': tr('Medium'),
            'affected': True,
            'description': tr('Medium'),
            'numeric_default_min': 2,
            'numeric_default_max': 5,
            'optional': True,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'low',
            'name': tr('Low'),
            'affected': False,
            'description': tr('Low'),
            'numeric_default_min': 0.1,
            'numeric_default_max': 2,
            'optional': True,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'very low',
            'name': tr('Very Low'),
            'affected': False,
            'description': tr('Very Low.'),
            'numeric_default_min': 0.01,
            'numeric_default_max': 0.1,
            'optional': True,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        }
    ]
}


tsunami_hazard_classes = {
    'key': 'tsunami_hazard_classes',
    'name': tr('Tsunami classes'),
    'description': tr(
        'This is a quinary description for an area. The area is either '
        '<b>dry</b>, <b>low</b>, <b>medium</b>, <b>high</b>, or '
        '<b>very high</b> for tsunami hazard classification. '
        'The following description for these classes is provided by Badan '
        'Geologi based on BNPB Perka 2/2012'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'classes': [
        {
            'key': 'very high',
            'name': tr('Very high hazard zone'),
            'affected': True,
            'description': tr('Water above 8.0m.'),
            'numeric_default_min': 8,
            'numeric_default_max': 9999999999,
            'optional': True,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'high',
            'name': tr('High hazard zone'),
            'affected': True,
            'description': tr(
                'Water above 3.1m and less than 8.0m. The area is potentially '
                'hit by a tsunami wave with an inundation depth > 3 m or '
                'reach a tsunami intensity scale of VII or even more '
                '(Papadoupulos and Imamura, 2001). Tsunami wave with 4 m '
                'inundation depth cause damage to small vessel, a few ships '
                'are drifted inland, severe damage on most wooden houses. '
                'Boulders are deposited on shore. If tsunami height reaches '
                '8 m, it will cause severe damage. Dykes, wave breaker, '
                'tsunami protection walls and green belts will be washed '
                'away.'),
            'numeric_default_min': 3,
            'numeric_default_max': 8,
            'optional': True,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'medium',
            'name': tr('Medium hazard zone'),
            'affected': True,
            'description': tr(
                'Water above 1.1m and less than 3.0m. The area is potentially '
                'hit by a tsunami wave with an inundation depth of 1 - 3 m or '
                'equal to V-VI tsunami intensity scale (Papadoupulos and '
                'Imamura, 2001). Tsunami wave with a 3m inundation depth '
                'causes most people frightened and to flee to higher ground. '
                'Small vessels drift and collide. Damage occurs to some '
                'wooden houses, while most of them are safe.'),
            'numeric_default_min': 1,
            'numeric_default_max': 3,
            'optional': True,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'low',
            'name': tr('Low hazard zone'),
            'affected': False,
            'description': tr(
                'Water above ground height and less than 1.0m. The area is '
                'potentially hit by a tsunami wave with an inundation depth '
                'less than 1 m or similar to tsunami intensity scale of V or '
                'less in (Papadoupulos and Imamura, 2001). Tsunami wave of 1m '
                'height causes few people to be frightened and flee to higher '
                'elevation. Felt by most people on large ship, observed from '
                'shore. Small vessels drift and collide and some turn over. '
                'Sand is deposited and there is flooding of areas close to '
                'the shore.'),
            'numeric_default_min': 0,
            'numeric_default_max': 1,
            'optional': True,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'dry',
            'name': tr('Dry zone'),
            'affected': False,
            'description': tr('No water above ground height.'),
            'numeric_default_min': 0,
            'numeric_default_max': (1 - small_number),
            'optional': True,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
    ]
}

hazard_classification = {
    'key': 'hazard_classification',
    'name': tr('Classes'),
    'description': tr(
        'Hazard classes are a way to group values.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'types': [
        generic_hazard_classes,
        flood_hazard_classes,
        tsunami_hazard_classes,
        volcano_hazard_classes,
        ash_hazard_classes,
    ]
}

all_hazard_classes = hazard_classification['types']
