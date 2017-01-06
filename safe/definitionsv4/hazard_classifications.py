# coding=utf-8

"""Definitions relating to hazards classifications.

See https://github.com/inasafe/inasafe/issues/2920#issuecomment-229874044
to have a table showing you classes of each kind of hazard.
"""
from safe.definitionsv4 import concepts, small_number
from safe.utilities.i18n import tr
from safe.definitionsv4.units import unit_centimetres, unit_miles_per_hour, \
    unit_kilometres_per_hour, unit_knots
from safe.definitionsv4.colors import (
    green,
    light_green,
    yellow,
    orange,
    red,
    dark_red,
    very_dark_red)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# Missing Earthquakes, these IF are using damage curves.
# They are not represented in that file.

null_hazard_value = 'null'
null_hazard_legend = tr('No hazard')

generic_hazard_classes = {
    'key': 'generic_hazard_classes',
    'name': tr('Generic classes'),
    'description': concepts['generic_hazard']['description'],
    'citations': concepts['generic_hazard']['citations'],
    'classes': [
        {
            'key': 'high',
            'color': red,
            'value': 3,
            'name': tr('High Hazard Zone'),
            'affected': True,
            'description': tr('The location that has highest impact.'),
            'string_defaults': ['high'],
            'numeric_default_min': 3,
            'numeric_default_max': (4 - small_number),
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ],
        },
        {
            'key': 'medium',
            'color': orange,
            'value': 2,
            'name': tr('Medium Hazard Zone'),
            'affected': True,
            'description': tr('The location that has medium impact.'),
            'string_defaults': ['medium'],
            'numeric_default_min': 2,
            'numeric_default_max': (3 - small_number),
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ],
        },
        {
            'key': 'low',
            'value': 1,
            'color': yellow,
            'name': tr('Low Hazard Zone'),
            'affected': True,
            'description': tr('The location that has lowest impact.'),
            'string_defaults': ['low'],
            'numeric_default_min': 0,
            'numeric_default_max': (2 - small_number),
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
    'key': 'volcano_hazard_classes',
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
            'value': 3,
            'color': red,
            'name': tr('High Hazard Zone'),
            'affected': True,
            'description': tr('The highest hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana III', 'high'],
            'numeric_default_min': 0,
            'numeric_default_max': (3 - small_number),
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'medium',
            'value': 2,
            'color': orange,
            'name': tr('Medium Hazard Zone'),
            'affected': True,
            'description': tr('The medium hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana II', 'medium'],
            'numeric_default_min': 3,
            'numeric_default_max': (5 - small_number),
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'low',
            'value': 1,
            'color': yellow,
            'name': tr('Low Hazard Zone'),
            'affected': True,
            'description': tr('The lowest hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana I', 'low'],
            'numeric_default_min': 5,
            'numeric_default_max': 10,
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
            'value': 2,
            'color': red,
            'name': tr('Wet'),
            'affected': True,
            'description': tr('Water above ground height.'),
            'string_defaults': ['wet', '1', 'YES', 'y', 'yes'],
            'numeric_default_min': 1,
            'numeric_default_max': 9999999999,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'dry',
            'value': 1,
            'color': yellow,
            'name': tr('Dry'),
            'affected': False,
            'description': tr('No water above ground height.'),
            'string_defaults': ['dry', '0', 'No', 'n', 'no'],
            'numeric_default_min': 0,
            'numeric_default_max': (1 - small_number),
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
            'value': 5,
            'color': dark_red,
            'name': tr('Very high'),
            'affected': True,
            'description': tr('Very High.'),
            'numeric_default_min': 10,
            'numeric_default_max': 9999999999,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'high',
            'value': 4,
            'color': red,
            'name': tr('High'),
            'affected': True,
            'description': tr('High'),
            'numeric_default_min': 5,
            'numeric_default_max': 10,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'medium',
            'value': 3,
            'color': orange,
            'name': tr('Medium'),
            'affected': True,
            'description': tr('Medium'),
            'numeric_default_min': 2,
            'numeric_default_max': 5,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'low',
            'value': 2,
            'color': yellow,
            'name': tr('Low'),
            'affected': False,
            'description': tr('Low'),
            'numeric_default_min': 0.1,
            'numeric_default_max': 2,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'very low',
            'value': 1,
            'color': light_green,
            'name': tr('Very Low'),
            'affected': False,
            'description': tr('Very Low.'),
            'numeric_default_min': 0.01,
            'numeric_default_max': 0.1,
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
            'value': 5,
            'color': dark_red,
            'name': tr('Very high hazard zone'),
            'affected': True,
            'description': tr('Water above 8.0m.'),
            'numeric_default_min': 8,
            'numeric_default_max': 9999999999,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'high',
            'value': 4,
            'color': red,
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
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'medium',
            'value': 3,
            'color': orange,
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
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'low',
            'value': 2,
            'color': yellow,
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
            'numeric_default_min': 0.1,
            'numeric_default_max': 1,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'dry',
            'value': 1,
            'color': green,
            'name': tr('Dry zone'),
            'affected': False,
            'description': tr('No water above ground height.'),
            'numeric_default_min': 0,
            'numeric_default_max': 0.1,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
    ]
}


cyclone_au_bom_hazard_classes = {
    'key': 'cyclone_au_bom_hazard_classes',
    'name': tr('Cyclone classes (AU - BOM)'),
    'description': tr(
        'The quinary <b>tropical cyclone</b> intensity classification '
        'according to the Australian Bureau of Metereology is defined by the '
        'maximum mean wind speed over open flat land or water. '
        'This is sometimes referred to as the maximum sustained wind and will'
        'be experienced around the eye-wall of the cyclone.'),
    'citations': [
        {
            'text': 'Australian Bureau of Metereology - Tropical Cyclone '
                    'Intensity and Impacts',
            'link': 'http://www.bom.gov.au/cyclone/about/intensity.shtml#WindC'
        },
        {
            'text': 'Tropical cyclone scales - wikpedia',
            'link': 'https://en.wikipedia.org/wiki/Tropical_cyclone_scales#Australia_and_Fiji'
        }
    ],
    'multiple_units': [unit_miles_per_hour, unit_kilometres_per_hour,
                       unit_knots],
    'classes': [
        {
            'key': 'category_5',
            'value': 5,
            'color': very_dark_red,
            'name': tr('Category 5 (severe tropical cyclone)'),
            'affected': True,
            'description': tr(
                    'Extremely dangerous with widespread destruction. A '
                    'Category '
                    '5 cyclone\'s strongest winds are VERY DESTRUCTIVE winds '
                    'with '
                    'typical gusts over open flat land of more than 151 kn. '
                    'These winds correspond to the highest category on the '
                    'Beaufort scale, Beaufort 12 (Hurricane).'
            ),
            'numeric_default_min': {
                unit_knots['key']: 107,
                unit_miles_per_hour['key']: 123,
                unit_kilometres_per_hour['key']: 198
                },
            'numeric_default_max': 9999999999,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'category_4',
            'value': 4,
            'color': dark_red,
            'name': tr('Category 4 (severe tropical cyclone)'),
            'affected': True,
            'description': tr(
                    'Significant roofing loss and structural damage. Many '
                    'caravans destroyed and blown away. Dangerous airborne '
                    'debris. Widespread power failures. A Category 4 cyclone\'s'
                    'strongest winds are VERY DESTRUCTIVE winds with typical '
                    'gusts over open flat land of 122 - 151 kn. These winds '
                    'correspond to the highest category on the Beaufort scale, '
                    'Beaufort 12 (Hurricane).'
            ),
            'numeric_default_min': {
                unit_knots['key']: 85,
                unit_miles_per_hour['key']: 98,
                unit_kilometres_per_hour['key']: 157
                },
            'numeric_default_max': {
                unit_knots['key']: 107,
                unit_miles_per_hour['key']: 123,
                unit_kilometres_per_hour['key']: 198
                },
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'category_3',
            'value': 3,
            'color': red,
            'name': tr('Category 3 (severe tropical cyclone)'),
            'affected': True,
            'description': tr(
                    'Some roof and structural damage. Some caravans destroyed. '
                    'Power failures likely. A Category 3 cyclone\'s strongest '
                    'winds are VERY DESTRUCTIVE winds with typical gusts over '
                    'open flat land of 90 - 121 kn. These winds correspond to '
                    'the highest category on the Beaufort scale, Beaufort 12 ('
                    'Hurricane).'),
            'numeric_default_min': {
                unit_knots['key']: 63,
                unit_miles_per_hour['key']: 72,
                unit_kilometres_per_hour['key']: 117
                },
            'numeric_default_max': {
                unit_knots['key']: 85,
                unit_miles_per_hour['key']: 98,
                unit_kilometres_per_hour['key']: 157
                },
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'category_2',
            'value': 2,
            'color': orange,
            'name': tr('Category 2 (tropical cyclone)'),
            'affected': True,
            'description': tr(
                    'Minor house damage. Significant damage to signs, '
                    'trees and '
                    'caravans. Heavy damage to some crops. Risk of power '
                    'failure. '
                    'Small craft may break moorings. A Category 2 cyclone\'s '
                    'strongest winds are DESTRUCTIVE winds with typical gusts '
                    'over open flat land of 68 - 89 kn. These winds '
                    'correspond to Beaufort 10 and 11 (Storm and violent '
                    'storm).'),
            'numeric_default_min': {
                unit_knots['key']: 47,
                unit_miles_per_hour['key']: 54,
                unit_kilometres_per_hour['key']: 88
                },
            'numeric_default_max': {
                unit_knots['key']: 63,
                unit_miles_per_hour['key']: 72,
                unit_kilometres_per_hour['key']: 117
                },
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'category_1',
            'value': 1,
            'color': yellow,
            'name': tr('Category 1 (tropical cyclone)'),
            'affected': False,
            'description': tr(
                    'Negligible house damage. Damage to some crops, trees and '
                    'caravans. Craft may drag moorings. A Category 1 '
                    'cyclone\'s '
                    'strongest winds are GALES with typical gusts over open '
                    'flat '
                    'land of 49 - 67 kn. These winds correspond to Beaufort 8 '
                    'and 9 (Gales and strong gales).'),
            'numeric_default_min': {
                unit_knots['key']: 34,
                unit_miles_per_hour['key']: 39,
                unit_kilometres_per_hour['key']: 63
                },
            'numeric_default_max': {
                unit_knots['key']: 47,
                unit_miles_per_hour['key']: 54,
                unit_kilometres_per_hour['key']: 88
                },
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'tropical_depression',
            'value': 0,
            'color': green,
            'name': tr('Tropical Depression'),
            'affected': False,
            'description': tr('A tropical depression is a tropical '
                              'disturbance, that has a clearly defined '
                              'surface circulation, which has maximum '
                              'sustained winds of less than 34 kn.'),
            'numeric_default_min': 0,
            'numeric_default_max': {
                unit_knots['key']: 34,
                unit_miles_per_hour['key']: 39,
                unit_kilometres_per_hour['key']: 63
                },
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
    ]
}

cyclone_hazard_classes = [cyclone_au_bom_hazard_classes]

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
        ash_hazard_classes
    ]
}
hazard_classification['types'].extend(cyclone_hazard_classes)

all_hazard_classes = hazard_classification['types']
