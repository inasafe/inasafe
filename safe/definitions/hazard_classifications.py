# coding=utf-8
"""Definitions relating to hazards classifications.

See https://github.com/inasafe/inasafe/issues/2920#issuecomment-229874044
to have a table showing you classes of each kind of hazard.
"""
from safe.definitions import concepts, small_number
from safe.utilities.i18n import tr
from safe.definitions.units import (
    unit_centimetres,
    unit_miles_per_hour,
    unit_kilometres_per_hour,
    unit_knots,
    unit_metres_per_second
)
from safe.definitions.styles import (
    grey,
    green,
    light_green,
    yellow,
    orange,
    red,
    dark_red,
    very_dark_red)
from safe.definitions.exposure import (
    exposure_land_cover,
    exposure_place,
    exposure_population,
    exposure_road,
    exposure_structure)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# This class will be automatically added to a hazard classification on runtime.
# We do not include it in the classes below because we do not want the user
# to be presented with not exposed in the keywords when setting up
# their classes.
# This class is not displayed if it's a polygon exposure (landcover and
# population) in the legend.
not_exposed_class = {
    'key': 'not exposed',
    'name': tr('Not exposed'),
    'description': tr('Not exposed'),
    'color': grey,
}

hazard_classification_type = tr('Hazard Classification')

generic_hazard_classes = {
    'key': 'generic_hazard_classes',
    'name': tr('Generic classes'),
    'description': concepts['generic_hazard']['description'],
    'type': hazard_classification_type,
    'citations': concepts['generic_hazard']['citations'],
    'classes': [
        {
            'key': 'high',
            'color': red,
            'value': 3,
            'name': tr('High hazard zone'),
            'affected': True,
            'description': tr('The locations having the highest impact.'),
            'string_defaults': ['high'],
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
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
            'name': tr('Medium hazard zone'),
            'affected': True,
            'description': tr('The locations where there is a medium impact.'),
            'string_defaults': ['medium'],
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
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
            'name': tr('Low hazard zone'),
            'affected': True,
            'description': tr(
                'The locations where the lowest impact occurred.'),
            'string_defaults': ['low'],
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': 0,
            'numeric_default_max': (2 - small_number),
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ],
        }
    ],
    'exposures': [
        exposure_land_cover,
        exposure_place,
        exposure_population,
        exposure_road,
        exposure_structure
    ]
}

earthquake_mmi_hazard_classes = {
    'key': 'earthquake_mmi_hazard_classes',
    'name': tr('Earthquake MMI classes'),
    'description': tr(
        'Three classes are supported for earthquake vector hazard data: '
        '<b>low</b>, <b>medium</b>, or <b>high</b>.'),
    'type': hazard_classification_type,
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'classes': [
        {
            'key': 'high',
            'value': 8,
            'color': red,
            'name': tr('High hazard zone'),
            'affected': True,
            'description': tr('The highest hazard class.'),
            'string_defaults': ['high'],
            # Not used because EQ algs take care of this
            # 'displacement_rate': 0.0,
            # Not used because EQ algs take care of this
            # 'fatality_rate': 0.0,
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
            'key': 'medium',
            'value': 2,
            'color': orange,
            'name': tr('Medium hazard zone'),
            'affected': True,
            'description': tr('The medium hazard class.'),
            'string_defaults': ['medium'],
            # Not used because EQ algs take care of this
            # 'displacement_rate': 0.0,
            # Not used because EQ algs take care of this
            # 'fatality_rate': 0.0,
            'numeric_default_min': 7,
            'numeric_default_max': (8 - small_number),
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
            'name': tr('Low hazard zone'),
            'affected': True,
            'description': tr('The lowest hazard class.'),
            'string_defaults': ['low'],
            # Not used because EQ algs take care of this
            # 'displacement_rate': 0.0,
            # Not used because EQ algs take care of this
            # 'fatality_rate': 0.0,
            'numeric_default_min': 6,
            'numeric_default_max': (7 - small_number),
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        }
    ],
    'exposures': [
        exposure_land_cover,
        exposure_place,
        exposure_population,
        exposure_road,
        exposure_structure
    ]
}

volcano_hazard_classes = {
    'key': 'volcano_hazard_classes',
    'name': tr('Volcano classes'),
    'description': tr(
        'Three classes are supported for volcano vector hazard data: '
        '<b>low</b>, <b>medium</b>, or <b>high</b>.'),
    'type': hazard_classification_type,
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
            'name': tr('High hazard zone'),
            'affected': True,
            'description': tr('The highest hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana III', 'high'],
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
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
            'name': tr('Medium hazard zone'),
            'affected': True,
            'description': tr('The medium hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana II', 'medium'],
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
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
            'name': tr('Low hazard zone'),
            'affected': True,
            'description': tr('The lowest hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana I', 'low'],
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': 5,
            'numeric_default_max': 10,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        }
    ],
    'exposures': [
        exposure_land_cover,
        exposure_place,
        exposure_population,
        exposure_road,
        exposure_structure
    ]
}

flood_hazard_classes = {
    'key': 'flood_hazard_classes',
    'name': tr('Flood classes'),
    'description': tr(
        'This is a binary classification for an area. The area is either '
        '<b>wet</b> (affected by flood water) or <b>dry</b> (not affected '
        'by flood water). This unit does not describe how <b>wet</b> or '
        '<b>dry</b> an area is.'),
    'type': hazard_classification_type,
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
            'description': tr('Water is present above ground height.'),
            'string_defaults': ['wet', '1', 'YES', 'y', 'yes'],
            'displacement_rate': 0.01,
            'fatality_rate': 0.0,
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
            'description': tr('No water encountered above ground height.'),
            'string_defaults': ['dry', '0', 'No', 'n', 'no'],
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': 0,
            'numeric_default_max': (1 - small_number),
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        }
    ],
    'exposures': [
        exposure_land_cover,
        exposure_place,
        exposure_population,
        exposure_road,
        exposure_structure
    ]
}

ash_hazard_classes = {
    'key': 'ash_hazard_classes',
    'name': tr('Ash classes'),
    'description': tr(
        'Three classes are supported for ash vector hazard data: '
        '<b>very low</b>, <b>low</b>, <b>medium</b>, <b>high</b> or '
        '<b>very high</b>.'),
    'type': hazard_classification_type,
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
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
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
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': 5,
            'numeric_default_max': 10 - small_number,
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
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': 2,
            'numeric_default_max': 5 - small_number,
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
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': 0.1,
            'numeric_default_max': 2 - small_number,
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
            'name': tr('Very low'),
            'affected': False,
            'description': tr('Very Low.'),
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': 0.01,
            'numeric_default_max': 0.1 - small_number,
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
        'Tsunami hazards can be classified into one of five classes for an '
        'area. The area is either <b>dry</b>, <b>low</b>, <b>medium</b>, '
        '<b>high</b>, or <b>very high</b> for tsunami hazard classification. '
        'The following description for these classes is provided by Badan '
        'Geologi based on BNPB Perka 2/2012'),
    'type': hazard_classification_type,
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
            'string_defaults': [],
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
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
                'Water above 3.1m and less than 8.0m. The area is '
                'potentially hit by a tsunami wave with an inundation '
                'depth > 3 m or reach a tsunami intensity scale of VII or '
                'even more (Papadoupulos and Imamura, 2001). Tsunami wave '
                'with 4 m inundation depth cause damage to small vessel, '
                'a few ships are drifted inland, severe damage on most wooden '
                'houses. Boulders are deposited on shore. If tsunami height '
                'reaches 8 m, it will cause severe damage. Dykes, wave '
                'breaker, tsunami protection walls and green belts will be '
                'washed away.'),
            'string_defaults': [],
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': 3,
            'numeric_default_max': 8 - small_number,
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
                'hit by a tsunami wave with an inundation depth of 1 - 3 '
                'm or equal to V-VI tsunami intensity scale (Papadoupulos and '
                'Imamura, 2001). Tsunami wave with a 3m inundation depth '
                'causes most people frightened and to flee to higher '
                'ground. Small vessels drift and collide. Damage occurs to '
                'some wooden houses, while most of them are safe.'),
            'string_defaults': [],
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': 1,
            'numeric_default_max': 3 - small_number,
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
                'potentially hit by a tsunami wave with an inundation '
                'depth less than 1 m or similar to tsunami intensity scale of '
                'V or less in (Papadoupulos and Imamura, 2001). Tsunami wave '
                'of 1m height causes few people to be frightened and flee to '
                'higher elevation. Felt by most people on large ship, '
                'observed from shore. Small vessels drift and collide and '
                'some turn over. Sand is deposited and there is flooding of '
                'areas close to the shore.'),
            'string_defaults': [],
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': 0.1,
            'numeric_default_max': 1 - small_number,
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
            'string_defaults': [],
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': 0,
            'numeric_default_max': 0.1 - small_number,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
    ],
    'exposures': [
        exposure_land_cover,
        exposure_place,
        exposure_population,
        exposure_road,
        exposure_structure
    ]
}

cyclone_au_bom_hazard_classes = {
    'key': 'cyclone_au_bom_hazard_classes',
    'name': tr('Cyclone classes (AU - BOM)'),
    'description': tr(
        '<b>Tropical cyclone</b> intensity is classified using five classes '
        'according to the Australian Bureau of Meteorology. Tropical Cyclone '
        'intensity is defined as the maximum mean wind speed over open flat '
        'land or water. This is sometimes referred to as the maximum '
        'sustained wind and will be experienced around the eye-wall of the '
        'cyclone.'),
    'type': hazard_classification_type,
    'citations': [
        {
            'text': tr(
                'Australian Bureau of Meteorology - Tropical Cyclone '
                'Intensity and Impacts'),
            'link':
                u'http://www.bom.gov.au/cyclone/about/intensity.shtml#WindC'
        },
        {
            'text': tr('Tropical cyclone scales - wikpedia'),
            'link': u'https://en.wikipedia.org/wiki/Tropical_cyclone_scales'
                    u'#Australia_and_Fiji'
        }
    ],
    'multiple_units': [
        unit_miles_per_hour, 
        unit_kilometres_per_hour, 
        unit_knots, 
        unit_metres_per_second],
    'classes': [
        {
            'key': 'category_5',
            'value': 5,
            'color': very_dark_red,
            'name': tr('Category 5 (severe tropical cyclone)'),
            'affected': True,
            'description': tr(
                'Extremely dangerous with widespread destruction. A Category '
                '5 cyclone\'s strongest winds are VERY DESTRUCTIVE winds with '
                'typical gusts over open flat land of more than 151 kt. '
                'These winds correspond to the highest category on the '
                'Beaufort scale, Beaufort 12 (Hurricane).'
            ),
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': {
                unit_knots['key']: 107,
                unit_metres_per_second['key']: 55,
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
                'caravans destroyed and blown away. Dangerous airborne debris '
                '. Widespread power failures. A Category 4 cyclone\'s '
                'strongest winds are VERY DESTRUCTIVE winds with typical '
                'gusts over open flat land of 122 - 151 kt. These winds '
                'correspond to the highest category on the Beaufort scale, '
                'Beaufort 12 (Hurricane).'
            ),
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': {
                unit_knots['key']: 85,
                unit_metres_per_second['key']: 44,
                unit_miles_per_hour['key']: 98,
                unit_kilometres_per_hour['key']: 157
            },
            'numeric_default_max': {
                unit_knots['key']: 107 - small_number,
                unit_metres_per_second['key']: 55 - small_number,
                unit_miles_per_hour['key']: 123 - small_number,
                unit_kilometres_per_hour['key']: 198 - small_number
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
                'Some roof and structural damage. Some caravans destroyed.'
                'Power failures likely. A Category 3 cyclone\'s strongest '
                'winds are VERY DESTRUCTIVE winds with typical gusts over '
                'open flat land of 90 - 121 kt. These winds correspond to the '
                'highest category on the Beaufort scale, Beaufort 12 ('
                'Hurricane).'),
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': {
                unit_knots['key']: 63,
                unit_metres_per_second['key']: 33,
                unit_miles_per_hour['key']: 72,
                unit_kilometres_per_hour['key']: 117
            },
            'numeric_default_max': {
                unit_knots['key']: 85 - small_number,
                unit_metres_per_second['key']: 44 - small_number,
                unit_miles_per_hour['key']: 98 - small_number,
                unit_kilometres_per_hour['key']: 157 - small_number
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
                'Minor house damage. Significant damage to signs, trees '
                'and caravans. Heavy damage to some crops. Risk of '
                'power failure. Small craft may break moorings. A Category 2 '
                'cyclone\'s strongest winds are DESTRUCTIVE winds with '
                'typical gusts over open flat land of 68 - 89 kt. '
                'These winds correspond to Beaufort 10 and 11 (Storm '
                'and violent storm).'),
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': {
                unit_knots['key']: 47,
                unit_metres_per_second['key']: 24,
                unit_miles_per_hour['key']: 54,
                unit_kilometres_per_hour['key']: 88
            },
            'numeric_default_max': {
                unit_knots['key']: 63 - small_number,
                unit_metres_per_second['key']: 33 - small_number,
                unit_miles_per_hour['key']: 72 - small_number,
                unit_kilometres_per_hour['key']: 117 - small_number
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
            'affected': True,
            'description': tr(
                'Negligible house damage. Damage to some crops, trees and '
                'caravans. Craft may drag moorings. A Category 1 cyclone\'s '
                'strongest winds are GALES with typical gusts over open '
                'flat land of 49 - 67 kt. These winds correspond to Beaufort '
                '8 and 9 (Gales and strong gales).'),
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': {
                unit_knots['key']: 34,
                unit_metres_per_second['key']: 17,
                unit_miles_per_hour['key']: 39,
                unit_kilometres_per_hour['key']: 63
            },
            'numeric_default_max': {
                unit_knots['key']: 47 - small_number,
                unit_metres_per_second['key']: 24 - small_number,
                unit_miles_per_hour['key']: 54 - small_number,
                unit_kilometres_per_hour['key']: 88 - small_number
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
            'description': tr(
                'A tropical depression is a tropical disturbance, that has a '
                'clearly defined surface circulation, which has maximum '
                'sustained winds of less than 34 kt.'),
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': 0,
            'numeric_default_max': {
                unit_knots['key']: 34 - small_number,
                unit_metres_per_second['key']: 17 - small_number,
                unit_miles_per_hour['key']: 39 - small_number,
                unit_kilometres_per_hour['key']: 63 - small_number
            },
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
    ],
    'exposures': [
        exposure_land_cover,
        exposure_place,
        exposure_population,
        exposure_road,
        exposure_structure
    ]
}

cyclone_sshws_hazard_classes = {
    'key': 'cyclone_sshws_hazard_classes',
    'name': tr('Hurricane classes (SSHWS)'),
    'description': tr(
        'The <b>Saffir-Simpson Hurricane Wind Scale</b> is a 1 to 5 rating '
        'based on a hurricane\'s sustained wind speed. This scale '
        'estimates potential property damage. Hurricanes reaching Category 3 '
        'and higher are considered major hurricanes because of their '
        'potential for significant loss of life and damage. Category 1 and 2 '
        'storms are still dangerous, however, and require preventative '
        'measures. In the western North Pacific, the term "super typhoon" is '
        'used for tropical cyclones with sustained winds exceeding 150 mph.'),
    'type': hazard_classification_type,
    'citations': [
        {
            'text': tr('NOAA - NHC'),
            'link': u'http://www.nhc.noaa.gov/aboutsshws.php'
        },
        {
            'text': tr('Saffir-Simpson scale - wikipedia'),
            'link':
                u'https://en.wikipedia.org/wiki/Saffir%E2%80%93Simpson_scale'
        }
    ],
    'multiple_units': [
        unit_miles_per_hour, unit_kilometres_per_hour, unit_knots],
    'classes': [
        {
            'key': 'category_5',
            'value': 5,
            'color': very_dark_red,
            'name': tr('Category 5 (major hurricane)'),
            'affected': True,
            'description': tr(
                'Catastrophic damage will occur: A high percentage of framed '
                'homes will be destroyed, with total roof failure and wall '
                'collapse. Fallen trees and power poles will isolate '
                'residential areas. Power outages will last for weeks to '
                'possibly months. Most of the area will be uninhabitable for '
                'weeks or months.'
            ),
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': {
                unit_knots['key']: 136,
                unit_metres_per_second['key']: 70,
                unit_miles_per_hour['key']: 156,
                unit_kilometres_per_hour['key']: 251
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
            'name': tr('Category 4 (major hurricane)'),
            'affected': True,
            'description': tr(
                'Catastrophic damage will occur: Well-built framed homes can '
                'sustain severe damage with loss of most of the roof '
                'structure and/or some exterior walls. Most trees will be '
                'snapped or uprooted and power poles downed. Fallen trees '
                'and power poles will isolate residential areas. Power '
                'outages will last weeks to possibly months. Most of the '
                'area will be uninhabitable for weeks or months.'
            ),
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': {
                unit_knots['key']: 112,
                unit_metres_per_second['key']: 58,
                unit_miles_per_hour['key']: 129,
                unit_kilometres_per_hour['key']: 208
            },
            'numeric_default_max': {
                unit_knots['key']: 136 - small_number,
                unit_metres_per_second['key']: 70 - small_number,
                unit_miles_per_hour['key']: 156 - small_number,
                unit_kilometres_per_hour['key']: 251 - small_number
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
            'name': tr('Category 3 (major hurricane)'),
            'affected': True,
            'description': tr(
                'Devastating damage will occur: Well-built framed homes '
                'may incur major damage or removal of roof decking and '
                'gable ends. Many trees will be snapped or uprooted, '
                'blocking numerous roads. Electricity and water will be '
                'unavailable for several days to weeks after the storm '
                'passes.'),
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': {
                unit_knots['key']: 95,
                unit_metres_per_second['key']: 50,
                unit_miles_per_hour['key']: 110,
                unit_kilometres_per_hour['key']: 177
            },
            'numeric_default_max': {
                unit_knots['key']: 112 - small_number,
                unit_metres_per_second['key']: 58 - small_number,
                unit_miles_per_hour['key']: 129 - small_number,
                unit_kilometres_per_hour['key']: 208 - small_number
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
            'name': tr('Category 2 (hurricane)'),
            'affected': True,
            'description': tr(
                'Extremely dangerous winds will cause extensive damage: '
                'Well-constructed frame homes could sustain major roof '
                'and siding damage. Many shallowly rooted trees will be '
                'snapped or uprooted and block numerous roads. Near-total '
                'power loss is expected with outages that could last from '
                'several days to weeks.'),
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': {
                unit_knots['key']: 82,
                unit_metres_per_second['key']: 42,
                unit_miles_per_hour['key']: 95,
                unit_kilometres_per_hour['key']: 153
            },
            'numeric_default_max': {
                unit_knots['key']: 95 - small_number,
                unit_metres_per_second['key']: 50 - small_number,
                unit_miles_per_hour['key']: 110 - small_number,
                unit_kilometres_per_hour['key']: 177 - small_number
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
            'name': tr('Category 1 (hurricane)'),
            'affected': True,
            'description': tr(
                'Very dangerous winds will produce some damage: Well-'
                'constructed frame homes could have damage to roof, shingles, '
                'vinyl siding and gutters. Large branches of trees will snap '
                'and shallowly rooted trees may be toppled. Extensive damage '
                'to power lines and poles likely will result in power outages '
                'that could last a few to several days.'),
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': {
                unit_knots['key']: 64,
                unit_metres_per_second['key']: 33,
                unit_miles_per_hour['key']: 74,
                unit_kilometres_per_hour['key']: 119
            },
            'numeric_default_max': {
                unit_knots['key']: 82 - small_number,
                unit_metres_per_second['key']: 42 - small_number,
                unit_miles_per_hour['key']: 95 - small_number,
                unit_kilometres_per_hour['key']: 153 - small_number
            },
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'no_hurricane',
            'value': 0,
            'color': green,
            'name': tr('No hurricane'),
            'affected': False,
            'description': tr('Winds less than Category 1 Hurricane'),
            'displacement_rate': 0.0,
            'fatality_rate': 0.0,
            'numeric_default_min': 0,
            'numeric_default_max': {
                unit_knots['key']: 64 - small_number,
                unit_metres_per_second['key']: 33 - small_number,
                unit_miles_per_hour['key']: 74 - small_number,
                unit_kilometres_per_hour['key']: 119 - small_number
            },
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
    ],
    'exposures': [
        exposure_land_cover,
        exposure_place,
        exposure_population,
        exposure_road,
        exposure_structure
    ]
}

hazard_classification = {
    'key': 'hazard_classification',
    'name': tr('Classes'),
    'description': tr(
        'A hazard classification is used to define a range of severity '
        'thresholds (classes) for a continuous hazard layer. The '
        'classification will be used to create zones of data that each '
        'present a similar hazard level. During the analysis, each exposure '
        'feature will be assessed to determine which hazard class it '
        'coincides with, and then a determination will be made as to '
        'whether and how the exposure feature is likely to be impacted by '
        'the hazard.'),
    'type': hazard_classification_type,
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'types': [
        generic_hazard_classes,
        flood_hazard_classes,
        earthquake_mmi_hazard_classes,
        tsunami_hazard_classes,
        volcano_hazard_classes,
        ash_hazard_classes,
        cyclone_au_bom_hazard_classes,
        cyclone_sshws_hazard_classes,
    ]
}

hazard_classes_all = hazard_classification['types']
