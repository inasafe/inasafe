# coding=utf-8
"""Definitions relating to hazards classifications.

See https://github.com/inasafe/inasafe/issues/2920#issuecomment-229874044
to have a table showing you classes of each kind of hazard.

Rule of using the thresholds:
Minimum value IS NOT included, but maximum value IS included to the range.
Mathematical expression:
minimum_value < x <= maximum_value
"""
from safe.definitions import concepts
from safe.definitions.constants import big_number
from safe.definitions.earthquake import (
    earthquake_fatality_rate, current_earthquake_model_name)
from safe.definitions.exposure import (
    exposure_land_cover,
    exposure_place,
    exposure_population,
    exposure_road,
    exposure_structure)
from safe.definitions.styles import (
    grey,
    green,
    light_green,
    yellow,
    orange,
    red,
    dark_red,
    very_dark_red,
    MMI_10,
    MMI_9,
    MMI_8,
    MMI_7,
    MMI_6,
    MMI_5,
    MMI_4,
    MMI_3,
    MMI_2,
    MMI_1)
from safe.definitions.units import (
    unit_centimetres,
    unit_miles_per_hour,
    unit_kilometres_per_hour,
    unit_knots,
    unit_metres_per_second
)
from safe.utilities.i18n import tr

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
            'name': tr('High'),
            'affected': True,
            'description': tr('The area with the highest hazard.'),
            'string_defaults': ['high'],
            'fatality_rate': None,
            'displacement_rate': 1.0,
            'numeric_default_min': 3,
            'numeric_default_max': 4,
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
            'name': tr('Medium'),
            'affected': True,
            'description': tr('The area with the medium hazard.'),
            'string_defaults': ['medium'],
            'fatality_rate': None,
            'displacement_rate': 1.0,
            'numeric_default_min': 2,
            'numeric_default_max': 3,
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
            'name': tr('Low'),
            'affected': False,
            'description': tr(
                'The area with the lowest hazard.'),
            'string_defaults': ['low'],
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': 0,
            'numeric_default_max': 2,
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
    ],
    'classification_unit': tr('hazard zone')
}

earthquake_mmi_scale = {
    'key': 'earthquake_mmi_scale',
    'name': tr('Earthquake MMI scale'),
    'description': tr(
        'This scale, composed of increasing levels of intensity that range '
        'from imperceptible shaking to catastrophic destruction, is '
        'designated by Roman numerals. It does not have a mathematical '
        'basis; instead it is an arbitrary ranking based on observed '
        'effects. Note that fatality rates listed here are based on the '
        'active earthquake fatality model (currently set to %s). Users '
        'can select the active earthquake fatality model in InaSAFE '
        'Options.' % current_earthquake_model_name()),
    'type': hazard_classification_type,
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'classes': [
        {
            'key': 'X',
            'value': 10,
            'color': MMI_10,
            'name': tr('X'),
            'affected': True,
            'description':
                tr('Some well-built wooden structures destroyed; most masonry '
                   'and frame structures destroyed with foundations. '
                   'Rails bent.'),
            'string_defaults': ['extreme'],
            'fatality_rate': earthquake_fatality_rate(10),
            'displacement_rate': 1.0,
            'numeric_default_min': 9.5,
            'numeric_default_max': 10.5,
            'citations': [
                {
                    'text': None,
                    'link': 'https://earthquake.usgs.gov/learn/topics/'
                            'mercalli.php'
                }
            ]
        },
        {
            'key': 'IX',
            'value': 9,
            'color': MMI_9,
            'name': tr('IX'),
            'affected': True,
            'description':
                tr('Damage considerable in specially designed structures; '
                   'well-designed frame structures thrown out of plumb. '
                   'Damage great in substantial buildings, with partial '
                   'collapse. Buildings shifted off foundations.'),
            'string_defaults': ['violent'],
            'fatality_rate': earthquake_fatality_rate(9),
            'displacement_rate': 1.0,
            'numeric_default_min': 8.5,
            'numeric_default_max': 9.5,
            'citations': [
                {
                    'text': None,
                    'link': 'https://earthquake.usgs.gov/learn/topics/'
                            'mercalli.php'
                }
            ]
        },
        {
            'key': 'VIII',
            'value': 8,
            'color': MMI_8,
            'name': tr('VIII'),
            'affected': True,
            'description':
                tr('Damage slight in specially designed structures; '
                   'considerable damage in ordinary substantial buildings '
                   'with partial collapse. Damage great in poorly built '
                   'structures. Fall of chimneys, factory stacks, columns, '
                   'monuments, walls. Heavy furniture overturned.'),
            'string_defaults': ['severe'],
            'fatality_rate': earthquake_fatality_rate(8),
            'displacement_rate': 1.0,
            'numeric_default_min': 7.5,
            'numeric_default_max': 8.5,
            'citations': [
                {
                    'text': None,
                    'link': 'https://earthquake.usgs.gov/learn/topics/'
                            'mercalli.php'
                }
            ]
        },
        {
            'key': 'VII',
            'value': 7,
            'color': MMI_7,
            'name': tr('VII'),
            'affected': True,
            'description':
                tr('Damage negligible in buildings of good design and '
                   'construction; slight to moderate in well-built ordinary '
                   'structures; considerable damage in poorly built or badly '
                   'designed structures; some chimneys broken.'),
            'string_defaults': ['very strong'],
            'fatality_rate': earthquake_fatality_rate(7),
            'displacement_rate': 1.0,
            'numeric_default_min': 6.5,
            'numeric_default_max': 7.5,
            'citations': [
                {
                    'text': None,
                    'link': 'https://earthquake.usgs.gov/learn/topics/'
                            'mercalli.php'
                }
            ]
        },
        {
            'key': 'VI',
            'value': 6,
            'color': MMI_6,
            'name': tr('VI'),
            'affected': True,
            'description':
                tr('Felt by all, many frightened. Some heavy furniture moved; '
                   'a few instances of fallen plaster. Damage slight.'),
            'string_defaults': ['strong'],
            'fatality_rate': earthquake_fatality_rate(6),
            'displacement_rate': 1.0,
            'numeric_default_min': 5.5,
            'numeric_default_max': 6.5,
            'citations': [
                {
                    'text': None,
                    'link': 'https://earthquake.usgs.gov/learn/topics/'
                            'mercalli.php'
                }
            ]
        },
        {
            'key': 'V',
            'value': 5,
            'color': MMI_5,
            'name': tr('V'),
            'affected': True,
            'description':
                tr('Felt by nearly everyone; many awakened. Some dishes, '
                   'windows broken. Unstable objects overturned. Pendulum '
                   'clocks may stop.'),
            'string_defaults': ['moderate'],
            'fatality_rate': earthquake_fatality_rate(5),
            'displacement_rate': 0.0,
            'numeric_default_min': 4.5,
            'numeric_default_max': 5.5,
            'citations': [
                {
                    'text': None,
                    'link': 'https://earthquake.usgs.gov/learn/topics/'
                            'mercalli.php'
                }
            ]
        },
        {
            'key': 'IV',
            'value': 4,
            'color': MMI_4,
            'name': tr('IV'),
            'affected': True,
            'description':
                tr('Felt indoors by many, outdoors by few during the day. '
                   'At night, some awakened. Dishes, windows, doors '
                   'disturbed; walls make cracking sound. Sensation like '
                   'heavy truck striking building. Standing motor cars rocked '
                   'noticeably.'),
            'string_defaults': ['light'],
            'fatality_rate': earthquake_fatality_rate(4),
            'displacement_rate': 0.0,
            'numeric_default_min': 3.5,
            'numeric_default_max': 4.5,
            'citations': [
                {
                    'text': None,
                    'link': 'https://earthquake.usgs.gov/learn/topics/'
                            'mercalli.php'
                }
            ]
        },
        {
            'key': 'III',
            'value': 3,
            'color': MMI_3,
            'name': tr('III'),
            'affected': True,
            'description':
                tr('Felt quite noticeably by persons indoors, especially on '
                   'upper floors of buildings. Many people do not recognize  '
                   'it as an earthquake. Standing motor cars may rock '
                   'slightly. Vibrations similar to the passing of a truck. '
                   'Duration estimated.'),
            'string_defaults': ['weak'],
            'fatality_rate': earthquake_fatality_rate(3),
            'displacement_rate': 0.0,
            'numeric_default_min': 2.5,
            'numeric_default_max': 3.5,
            'citations': [
                {
                    'text': None,
                    'link': 'https://earthquake.usgs.gov/learn/topics/'
                            'mercalli.php'
                }
            ]
        },
        {
            'key': 'II',
            'value': 2,
            'color': MMI_2,
            'name': tr('II'),
            'affected': True,
            'description':
                tr('Felt only by a few persons at rest, especially on upper '
                   'floors of buildings.'),
            'string_defaults': [],
            'fatality_rate': earthquake_fatality_rate(2),
            'displacement_rate': 0.0,
            'numeric_default_min': 1.5,
            'numeric_default_max': 2.5,
            'citations': [
                {
                    'text': None,
                    'link': 'https://earthquake.usgs.gov/learn/topics/'
                            'mercalli.php'
                }
            ]
        },
        {
            'key': 'I',
            'value': 1,
            'color': MMI_1,
            'name': tr('I'),
            'affected': False,
            'description':
                tr('Not felt except by a very few under especially favorable '
                   'conditions.'),
            'string_defaults': ['not felt'],
            'fatality_rate': earthquake_fatality_rate(1),
            'displacement_rate': 0.0,
            'numeric_default_min': 0.5,
            'numeric_default_max': 1.5,
            'citations': [
                {
                    'text': None,
                    'link': 'https://earthquake.usgs.gov/learn/topics/'
                            'mercalli.php'
                }
            ]
        }
    ],
    'exposures': [
        exposure_place,
        exposure_population,
        exposure_road,
        exposure_structure
    ],
    'classification_unit': tr('MMI intensity')
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
            'name': tr('High'),
            'affected': True,
            'description': tr('The highest hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana III', 'high'],
            'displacement_rate': 1.0,
            'numeric_default_min': 0,
            'numeric_default_max': 3,
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
            'name': tr('Medium'),
            'affected': True,
            'description': tr('The medium hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana II', 'medium'],
            'displacement_rate': 1.0,
            'numeric_default_min': 3,
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
            'value': 1,
            'color': yellow,
            'name': tr('Low'),
            'affected': False,
            'description': tr('The lowest hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana I', 'low'],
            'displacement_rate': 0.0,
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
    ],
    'classification_unit': tr('hazard zone')
}

flood_hazard_classes = {
    'key': 'flood_hazard_classes',
    'name': tr('Flood wet/dry classes'),
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
            'string_defaults': ['wet', '1', 'YES', 'y', 'true'],
            'fatality_rate': None,
            'displacement_rate': 0.01,
            'numeric_default_min': 1,
            'numeric_default_max': big_number,
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
            'string_defaults': ['dry', '0', 'No', 'n', 'false'],
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': 0,
            'numeric_default_max': 1,
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
    ],
    'classification_unit': tr('hazard zone')
}

flood_petabencana_hazard_classes = {
    'key': 'flood_petabencana_hazard_classes',
    'name': tr('Flood classes'),
    'type': hazard_classification_type,
    'description': tr(
        'This is a flood classification for an area. The area is broken '
        'down into a number of flood classes of increasing severity based '
        'on the water depth.'),
    'citations': [
        {
            'text': tr('PetaBencana.id'),
            'link': 'https://petabencana.id'
        }
    ],
    'classes': [
        {
            'key': 'high',
            'value': 4,
            'color': red,
            'name': tr('High'),
            'affected': True,
            'description': tr('Flooding is over 150 centimetres.'),
            'fatality_rate': None,
            # displacement rate estimated from DMI analysis of historical
            # flood data and IDP numbers
            'displacement_rate': 0.05,
            'numeric_default_min': 1.5,
            'numeric_default_max': big_number,
            'string_defaults': ['high', 'severe'],
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
            'description': tr(
                'Flooding between 71 and 150 centimetres.'),
            'fatality_rate': None,
            # displacement rate estimated from DMI analysis of historical
            # flood data and IDP numbers
            'displacement_rate': 0.03,
            'numeric_default_min': 0.7,
            'numeric_default_max': 1.5,
            'string_defaults': ['medium', 'moderate'],
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
            'affected': True,
            'description': tr(
                'Flooding of between 10 and 70 centimetres.'),
            'fatality_rate': None,
            # displacement rate estimated from DMI analysis of historical
            # flood data and IDP numbers
            'displacement_rate': 0.01,
            'numeric_default_min': 0.1,
            'numeric_default_max': 0.7,
            'string_defaults': ['low', 'minor'],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'use_caution',
            'value': 0,
            'color': light_green,
            'name': tr('Use caution'),
            'affected': False,
            'description': tr(
                'An unknown level of flooding - use caution - '),
            'fatality_rate': None,
            # displacement rate estimated from DMI analysis of historical
            # flood data and IDP numbers
            'displacement_rate': 0.0,
            'numeric_default_min': 0,
            'numeric_default_max': 0.1,
            'string_defaults': ['caution', 'unknown'],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        }
    ],
    'classification_unit': tr('hazard zone')
}

flood_pcrafi_hazard_classes = {
    'key': 'flood_pcrafi_hazard_classes',
    'name': tr('Flood classes PCRAFI'),
    'type': hazard_classification_type,
    'description': tr(
        'This is a flood classification for an area. The area is broken '
        'down into a number of flood classes of increasing severity based '
        'on the water depth according to the PCRAFI project.'),
    'citations': [
        {
            'text': 'PCRAFI',
            'link': 'https://pcrafi.spc.int'
        }
    ],
    'classes': [
        {
            'key': 'very high',
            'value': 5,
            'color': dark_red,
            'name': tr('Very high'),
            'affected': True,
            'description': tr('Flooding is over 300 centimetres.'),
            'fatality_rate': None,
            'displacement_rate': 0.05,
            'numeric_default_min': 3.0,
            'numeric_default_max': big_number,
            'string_defaults': ['very high', 'very severe'],
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
            'description': tr('Flooding between 110 and 300 centimetres.'),
            'fatality_rate': None,
            'displacement_rate': 0.05,
            'numeric_default_min': 1.1,
            'numeric_default_max': 3.0,
            'string_defaults': ['high', 'severe'],
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
            'description': tr(
                'Flooding between 40 and 110 centimetres.'),
            'fatality_rate': None,
            'displacement_rate': 0.03,
            'numeric_default_min': 0.4,
            'numeric_default_max': 1.1,
            'string_defaults': ['medium', 'moderate'],
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
            'affected': True,
            'description': tr(
                'Flooding of between 20 and 40 centimetres.'),
            'fatality_rate': None,
            'displacement_rate': 0.01,
            'numeric_default_min': 0.2,
            'numeric_default_max': 0.4,
            'string_defaults': ['low', 'minor'],
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
            'description': tr(
                'Flooding of between 0 and 20 centimetres. '),
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': 0,
            'numeric_default_max': 0.2,
            'string_defaults': ['very low', 'very minor'],
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        }
    ],
    'classification_unit': tr('hazard zone')
}

inundation_dam_class = {
    'key': 'inundation_dam_class',
    'name': tr('Inundation classes'),
    'description': tr(
        'This type of classification refers to the division of flood areas '
        'based on the range of water levels. This area is divided into 3 '
        'areas of inundation including <b>Inundation 1</b>, '
        '<b>Inundation 2</b>, and <b>Inundation 3</b>.'),
    'type': hazard_classification_type,
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'classes': [
        {
            'key': 'inundation_3',
            'value': 3,
            'color': red,
            'name': tr('Inundation Class 3'),
            'affected': True,
            'description': tr('High water level above ground surface.'),
            'string_defaults': ['Inundation 3'],
            'fatality_rate': None,
            'displacement_rate': 0.01,
            'numeric_default_min': 1.5,
            'numeric_default_max': big_number,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'inundation_2',
            'value': 2,
            'color': orange,
            'name': tr('Inundation Class 2'),
            'affected': False,
            'description': tr('Medium water level above ground surface.'),
            'string_defaults': ['Inundation 2'],
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': 0.6,
            'numeric_default_max': 1.5,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'inundation_1',
            'value': 1,
            'color': yellow,
            'name': tr('Inundation Class 1'),
            'affected': False,
            'description': tr('Low water level above ground surface.'),
            'string_defaults': ['Inundation 1'],
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': 0,
            'numeric_default_max': 0.6,
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
    ],
    'classification_unit': tr('hazard zone')
}

ash_hazard_classes = {
    'key': 'ash_hazard_classes',
    'name': tr('Ash classes'),
    'description': tr(
        'Five classes are supported for volcanic ash hazard data: '
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
            'description': tr(
                'Dry loading on buildings causing structural collapse.'),
            'fatality_rate': None,
            # Displacement rate of 100% advised by Ibu Estu - BG Feb 2017
            'displacement_rate': 1.0,
            'numeric_default_min': 10,
            'numeric_default_max': big_number,
            'string_defaults': ['very high'],
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
            'description': tr(
                'Dry loading on buildings causing structural damage but not '
                'collapse; wet loading on buildings (i.e. ash loading + heavy '
                'rainfall) causing structural collapse.'),
            'fatality_rate': None,
            # Displacement rate of 100% advised by Ibu Estu - PVMBG Feb 2017
            'displacement_rate': 1.0,
            'numeric_default_min': 5,
            'numeric_default_max': 10,
            'string_defaults': ['high'],
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
            'description': tr(
                'Damage to less vulnerable agricultural crops (e.g. tea '
                'plantations) and destruction of more vulnerable crops; '
                'destruction of critical infrastructure; cosmetic '
                '(non-structural) damage to buildings'),
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': 2,
            'numeric_default_max': 5,
            'string_defaults': ['medium'],
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
            # affected is true for roads; driving becomes dangerous
            # Advice from Pak Nugi - PVMBG - Feb 2017
            'affected': True,
            'description': tr(
                'Damage to transportation routes (e.g. airports, roads, '
                'railways); damage to critical infrastructure '
                '(e.g. electricity supply); damage to more vulnerable '
                'agricultural crops (e.g. rice fields)'),
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': 0.1,
            'numeric_default_max': 2,
            'string_defaults': ['low'],
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
            'affected': True,
            'description': tr(
                'Impact on health (respiration), livestock, and contamination '
                'of water supply.'),
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': 0.01,
            'numeric_default_max': 0.1,
            'string_defaults': ['very low'],
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
    ],
    'classification_unit': tr('hazard zone')
}

# Original tsunami hazard classes with displacement rates added
tsunami_hazard_classes = {
    'key': 'tsunami_hazard_classes',
    'name': tr('Tsunami classes'),
    # note: these are default tsunami classes for everything except population
    'description': tr(
        'Tsunami hazards can be classified into one of four classes for an '
        'area. The area is either <b>dry</b>, <b>low</b>, <b>medium</b>, or '
        '<b>high</b>, for tsunami hazard classification. '
        'The following description for these classes is provided by Badan '
        'Geologi based on BNPB Perka 2/2012'),
    'type': hazard_classification_type,
    'citations': [
        {
            'text': tr('BNPB Perka 2/2012'),
            'link': 'http://bpbd.kendalkab.go.id/docs/publikasi/'
                    'perka_bnpb_no_2_tahun_2012_0.pdf'
        }
    ],
    'classes': [

        {
            'key': 'high',
            'value': 4,
            'color': red,
            'name': tr('High'),
            'affected': True,
            'description': tr(
                'The area is potentially hit by a tsunami wave with an '
                'inundation depth > 3 m or reach a tsunami intensity scale of '
                'VII or more (Papadopoulos and Imamura, 2001). Tsunami wave '
                'with 4 m inundation depth cause damage to small vessel, '
                'a few ships are drifted inland, severe damage on most wooden '
                'houses. Boulders are deposited on shore. If tsunami height '
                'reaches 8 m, it will cause severe damage. Dykes, wave '
                'breaker, tsunami protection walls and green belts will be '
                'washed away.'),
            'string_defaults': ['high'],
            'fatality_rate': None,
            'displacement_rate': 1.0,
            'numeric_default_min': 3,
            'numeric_default_max': big_number,
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
            'description': tr(
                'Water above 1.1m and less than 3.0m. The area is potentially '
                'hit by a tsunami wave with an inundation depth of 1 - 3 '
                'm or equal to V-VI tsunami intensity scale (Papadopoulos and '
                'Imamura, 2001). Tsunami wave with a 3m inundation depth '
                'causes most people frightened and to flee to higher '
                'ground. Small vessels drift and collide. Damage occurs to '
                'some wooden houses, while most of them are safe.'),
            'string_defaults': ['medium'],
            'fatality_rate': None,
            'displacement_rate': 1.0,
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
            'name': tr('Low'),
            'affected': False,
            'description': tr(
                'Water above ground height and less than 1.0m. The area is '
                'potentially hit by a tsunami wave with an inundation '
                'depth less than 1 m or similar to tsunami intensity scale of '
                'V or less in (Papadopoulos and Imamura, 2001). Tsunami wave '
                'of 1m height causes few people to be frightened and flee to '
                'higher elevation. Felt by most people on large ship, '
                'observed from shore. Small vessels drift and collide and '
                'some turn over. Sand is deposited and there is flooding of '
                'areas close to the shore.'),
            'string_defaults': ['low'],
            'fatality_rate': None,
            'displacement_rate': 0.0,
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
            'name': tr('Dry'),
            'affected': False,
            'description': tr('No water above ground height.'),
            'string_defaults': ['dry'],
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': 0,
            'numeric_default_max': 0.1,
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
        exposure_road,
        exposure_structure
    ],
    'classification_unit': tr('hazard zone')
}

# Duplicate classes for tsunami hazard; modified for population exposure
tsunami_hazard_population_classes = {
    'key': 'tsunami_hazard_population_classes',
    'name': tr('Tsunami population classes'),
    # note: these are default tsunami classes for population
    'description': tr(
        'Tsunami hazards can be classified into one of three classes for an '
        'area. The area is either <b>low</b>, <b>medium</b>, or '
        '<b>high</b>, for tsunami hazard classification. '
        'The following description for these classes is provided by Badan '
        'Geologi based on BNPB Perka 2/2012, and modified for population by '
        'Pak Hamza'),
    'type': hazard_classification_type,
    'citations': [
        {
            'text': tr('BNPB Perka 2/2012'),
            'link': 'http://bpbd.kendalkab.go.id/docs/publikasi/'
                    'perka_bnpb_no_2_tahun_2012_0.pdf'
        }
    ],
    'classes': [
        {
            'key': 'high',
            'value': 4,
            'color': red,
            'name': tr('High'),
            'affected': True,
            'description': tr(
                'The area is potentially hit by a tsunami wave with an '
                'inundation depth > 3 m or reach a tsunami intensity scale of '
                'VII or more (Papadopoulos and Imamura, 2001). Tsunami wave '
                'with 4 m inundation depth cause damage to small vessel, '
                'a few ships are drifted inland, severe damage on most wooden '
                'houses. Boulders are deposited on shore. If tsunami height '
                'reaches 8 m, it will cause severe damage. Dykes, wave '
                'breaker, tsunami protection walls and green belts will be '
                'washed away.'),
            'string_defaults': ['high'],
            'fatality_rate': None,
            'displacement_rate': 1.0,
            'numeric_default_min': 3,
            'numeric_default_max': big_number,
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
            'description': tr(
                'Water above 0.7m and less than 3.0m. The area is potentially '
                'hit by a tsunami wave with an inundation depth of 1 - 3 '
                'm or equal to V-VI tsunami intensity scale (Papadopoulos and '
                'Imamura, 2001). Tsunami wave with a 3m inundation depth '
                'causes most people frightened and to flee to higher '
                'ground. Small vessels drift and collide. Damage occurs to '
                'some wooden houses, while most of them are safe.'),
            'string_defaults': ['medium'],
            'fatality_rate': None,
            'displacement_rate': 1.0,
            'numeric_default_min': 0.7,
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
            'name': tr('Low'),
            'affected': True,
            'description': tr(
                'Water above ground height and less than 1.0m. The area is '
                'potentially hit by a tsunami wave with an inundation '
                'depth less than 1 m or similar to tsunami intensity scale of '
                'V or less in (Papadopoulos and Imamura, 2001). Tsunami wave '
                'of 1m height causes few people to be frightened and flee to '
                'higher elevation. Felt by most people on large ship, '
                'observed from shore. Small vessels drift and collide and '
                'some turn over. Sand is deposited and there is flooding of '
                'areas close to the shore.'),
            'string_defaults': ['low'],
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': 0.1,
            'numeric_default_max': 0.7,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },

    ],
    'exposures': [
        exposure_population
    ],
    'classification_unit': tr('hazard zone')
}
# duplicate classes for tsunami hazard based on advice from Pak Hamza
tsunami_hazard_classes_ITB = {
    'key': 'tsunami_hazard_classes_ITB',
    'name': tr('Tsunami classes ITB'),
    'description': tr(
        'Tsunami hazards can be classified into one of five classes for an '
        'area. The area is either <b>dry</b>, <b>low</b>, <b>medium</b>, '
        '<b>high</b>, or <b>very high</b> for tsunami hazard classification. '
        'The following description for these classes is provided by Pak '
        'Hamza ITB based on Papadopoulos and Imamura, 2001.'),
    'type': hazard_classification_type,
    'citations': [
        {
            'text': 'Papadopoulos and Imamura, 2001',
            'link': 'http://geology.about.com/od/tsunamis/a/'
                    'Tsunami-Intensity-Scale-2001.htm'
        }
    ],
    'classes': [
        {
            'key': 'very high',
            'value': 5,
            'color': dark_red,
            'name': tr('Very high'),
            'affected': True,
            'description': tr('Water above 8.0m.'),
            'string_defaults': ['very high'],
            'fatality_rate': None,
            'displacement_rate': 1.0,
            'numeric_default_min': 8,
            'numeric_default_max': big_number,
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
            'description': tr(
                'Water above 3.1m and less than 8.0m. The area is '
                'potentially hit by a tsunami wave with an inundation '
                'depth > 3 m or reach a tsunami intensity scale of VII or '
                'even more (Papadopoulos and Imamura, 2001). Tsunami wave '
                'with 4 m inundation depth cause damage to small vessel, '
                'a few ships are drifted inland, severe damage on most wooden '
                'houses. Boulders are deposited on shore. If tsunami height '
                'reaches 8 m, it will cause severe damage. Dykes, wave '
                'breaker, tsunami protection walls and green belts will be '
                'washed away.'),
            'string_defaults': ['high'],
            'fatality_rate': None,
            'displacement_rate': 1.0,
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
            'name': tr('Medium'),
            'affected': True,
            'description': tr(
                'Water above 1.1m and less than 3.0m. The area is potentially '
                'hit by a tsunami wave with an inundation depth of 1 - 3 '
                'm or equal to V-VI tsunami intensity scale (Papadopoulos and '
                'Imamura, 2001). Tsunami wave with a 3m inundation depth '
                'causes most people frightened and to flee to higher '
                'ground. Small vessels drift and collide. Damage occurs to '
                'some wooden houses, while most of them are safe.'),
            'string_defaults': ['medium'],
            'fatality_rate': None,
            'displacement_rate': 1.0,
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
            'name': tr('Low'),
            'affected': False,
            'description': tr(
                'Water above ground height and less than 1.0m. The area is '
                'potentially hit by a tsunami wave with an inundation '
                'depth less than 1 m or similar to tsunami intensity scale of '
                'V or less in (Papadopoulos and Imamura, 2001). Tsunami wave '
                'of 1m height causes few people to be frightened and flee to '
                'higher elevation. Felt by most people on large ship, '
                'observed from shore. Small vessels drift and collide and '
                'some turn over. Sand is deposited and there is flooding of '
                'areas close to the shore.'),
            'string_defaults': ['low'],
            'fatality_rate': None,
            'displacement_rate': 0.0,
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
            'string_defaults': ['dry'],
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': 0,
            'numeric_default_max': 0.1,
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
        exposure_road,
        exposure_structure
    ],
    'classification_unit': tr('hazard zone')
}

# duplicate classes for tsunami hazard based on advice from Pak Hamza and
# modified for population
tsunami_hazard_population_classes_ITB = {
    'key': 'tsunami_hazard_population_classes_ITB',
    'name': tr('Tsunami population classes ITB'),
    'description': tr(
        'Tsunami hazards can be classified into one of five classes for an '
        'area. The area is either <b>dry</b>, <b>low</b>, <b>medium</b>, '
        '<b>high</b>, or <b>very high</b> for tsunami hazard classification. '
        'The following description for these classes is provided by Pak '
        'Hamza ITB based on Papadopoulos and Imamura, 2001.'),
    'type': hazard_classification_type,
    'citations': [
        {
            'text': 'Papadopoulos and Imamura, 2001',
            'link': 'http://geology.about.com/od/tsunamis/a/'
                    'Tsunami-Intensity-Scale-2001.htm'
        }
    ],
    'classes': [
        {
            'key': 'very high',
            'value': 5,
            'color': dark_red,
            'name': tr('Very high'),
            'affected': True,
            'description': tr('Water above 8.0m.'),
            'string_defaults': ['very high'],
            'fatality_rate': None,
            'displacement_rate': 1.0,
            'numeric_default_min': 8,
            'numeric_default_max': big_number,
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
            'description': tr(
                'Water above 3.1m and less than 8.0m. The area is '
                'potentially hit by a tsunami wave with an inundation '
                'depth > 3 m or reach a tsunami intensity scale of VII or '
                'even more (Papadopoulos and Imamura, 2001). Tsunami wave '
                'with 4 m inundation depth cause damage to small vessel, '
                'a few ships are drifted inland, severe damage on most wooden '
                'houses. Boulders are deposited on shore. If tsunami height '
                'reaches 8 m, it will cause severe damage. Dykes, wave '
                'breaker, tsunami protection walls and green belts will be '
                'washed away.'),
            'string_defaults': ['high'],
            'fatality_rate': None,
            'displacement_rate': 1.0,
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
            'name': tr('Medium'),
            'affected': True,
            'description': tr(
                'Water above 1.1m and less than 3.0m. The area is potentially '
                'hit by a tsunami wave with an inundation depth of 1 - 3 '
                'm or equal to V-VI tsunami intensity scale (Papadopoulos and '
                'Imamura, 2001). Tsunami wave with a 3m inundation depth '
                'causes most people frightened and to flee to higher '
                'ground. Small vessels drift and collide. Damage occurs to '
                'some wooden houses, while most of them are safe.'),
            'string_defaults': ['medium'],
            'fatality_rate': None,
            'displacement_rate': 1.0,
            'numeric_default_min': 0.7,
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
            'name': tr('Low'),
            'affected': True,
            'description': tr(
                'Water above ground height and less than 1.0m. The area is '
                'potentially hit by a tsunami wave with an inundation '
                'depth less than 1 m or similar to tsunami intensity scale of '
                'V or less in (Papadopoulos and Imamura, 2001). Tsunami wave '
                'of 1m height causes few people to be frightened and flee to '
                'higher elevation. Felt by most people on large ship, '
                'observed from shore. Small vessels drift and collide and '
                'some turn over. Sand is deposited and there is flooding of '
                'areas close to the shore.'),
            'string_defaults': ['low'],
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': 0.1,
            'numeric_default_max': 0.7,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },

    ],
    'exposures': [
        exposure_population
    ],
    'classification_unit': tr('hazard zone')
}

cyclone_au_bom_hazard_classes = {
    'key': 'cyclone_au_bom_hazard_classes',
    'name': tr('Cyclone classes (AU - BOM)'),
    'description': tr(
        '<b>Tropical cyclone</b> intensity is classified using five classes '
        'according to the Australian Bureau of Meteorology. Tropical Cyclone '
        'intensity is defined as the maximum mean wind speed over open flat '
        'land or water, averaged over a 10-minute period. This is sometimes '
        'referred to as the maximum sustained wind and will be experienced '
        'around the eye-wall of the cyclone.'),
    'type': hazard_classification_type,
    'citations': [
        {
            'text': tr(
                'Australian Bureau of Meteorology - Tropical Cyclone '
                'Intensity and Impacts'),
            'link':
                'http://www.bom.gov.au/cyclone/about/intensity.shtml#WindC'
        },
        {
            'text': tr('Tropical cyclone scales - wikpedia'),
            'link': 'https://en.wikipedia.org/wiki/Tropical_cyclone_scales'
                    '#Australia_and_Fiji'
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
            ),
            'fatality_rate': None,
            'displacement_rate': 1.0,
            'numeric_default_min': {
                unit_knots['key']: 153,
                unit_metres_per_second['key']: 79,
                unit_miles_per_hour['key']: 176,
                unit_kilometres_per_hour['key']: 283
            },
            'numeric_default_max': big_number,
            'string_defaults': ['cat 5', 'category 5'],
            'citations': [
                {
                    'text': tr(
                        'Displacement rate is a generalized estimate ('
                        'personal communication Craig Arthur)'),
                    'link': 'https://github.com/inasafe/inasafe/issues/3762'
                            '#issuecomment-283839365'
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
                'gusts over open flat land of 122 - 151 kt. '
            ),
            'fatality_rate': None,
            'displacement_rate': 0.97,
            'numeric_default_min': {
                unit_knots['key']: 121,
                unit_metres_per_second['key']: 63,
                unit_miles_per_hour['key']: 140,
                unit_kilometres_per_hour['key']: 224
            },
            'numeric_default_max': {
                unit_knots['key']: 153,
                unit_metres_per_second['key']: 79,
                unit_miles_per_hour['key']: 176,
                unit_kilometres_per_hour['key']: 283
            },
            'string_defaults': ['cat 4', 'category 4'],
            'citations': [
                {
                    'text': tr(
                        'Displacement rate is a generalized estimate ('
                        'personal communication Craig Arthur)'),
                    'link': 'https://github.com/inasafe/inasafe/issues/3762'
                            '#issuecomment-283839365'
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
                'open flat land of 90 - 121 kt. '
            ),
            'fatality_rate': None,
            'displacement_rate': 0.55,
            'numeric_default_min': {
                unit_knots['key']: 90,
                unit_metres_per_second['key']: 47,
                unit_miles_per_hour['key']: 103,
                unit_kilometres_per_hour['key']: 167
            },
            'numeric_default_max': {
                unit_knots['key']: 121,
                unit_metres_per_second['key']: 63,
                unit_miles_per_hour['key']: 140,
                unit_kilometres_per_hour['key']: 224
            },
            'string_defaults': ['cat 3', 'category 3'],
            'citations': [
                {
                    'text': tr(
                        'Displacement rate is a generalized estimate ('
                        'personal communication Craig Arthur)'),
                    'link': 'https://github.com/inasafe/inasafe/issues/3762'
                            '#issuecomment-283839365'
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
            ),
            'fatality_rate': None,
            'displacement_rate': 0.06,
            'numeric_default_min': {
                unit_knots['key']: 67,
                unit_metres_per_second['key']: 34,
                unit_miles_per_hour['key']: 77,
                unit_kilometres_per_hour['key']: 126
            },
            'numeric_default_max': {
                unit_knots['key']: 90,
                unit_metres_per_second['key']: 47,
                unit_miles_per_hour['key']: 103,
                unit_kilometres_per_hour['key']: 167
            },
            'string_defaults': ['cat 2', 'category 2'],
            'citations': [
                {
                    'text': tr(
                        'Displacement rate is a generalized estimate ('
                        'personal communication Craig Arthur)'),
                    'link': 'https://github.com/inasafe/inasafe/issues/3762'
                            '#issuecomment-283839365'
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
                'flat land of 49 - 67 kt. '
            ),
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': {
                unit_knots['key']: 49,
                unit_metres_per_second['key']: 24,
                unit_miles_per_hour['key']: 56,
                unit_kilometres_per_hour['key']: 90
            },
            'numeric_default_max': {
                unit_knots['key']: 67,
                unit_metres_per_second['key']: 34,
                unit_miles_per_hour['key']: 77,
                unit_kilometres_per_hour['key']: 126
            },
            'string_defaults': ['cat 1', 'category 1'],
            'citations': [
                {
                    'text': tr(
                        'Displacement rate is a generalized estimate ('
                        'personal communication Craig Arthur)'),
                    'link': 'https://github.com/inasafe/inasafe/issues/3762'
                            '#issuecomment-283839365'
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
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': 0,
            'numeric_default_max': {
                unit_knots['key']: 49,
                unit_metres_per_second['key']: 24,
                unit_miles_per_hour['key']: 56,
                unit_kilometres_per_hour['key']: 90
            },
            'string_defaults': ['tropical depression', 'no', 'false'],
            'citations': [
                {
                    'text': tr(
                        'Displacement rate is a generalized estimate ('
                        'personal communication Craig Arthur)'),
                    'link': 'https://github.com/inasafe/inasafe/issues/3762'
                            '#issuecomment-283839365'
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
    ],
    'classification_unit': tr('cyclone category')
}

cyclone_sshws_hazard_classes = {
    'key': 'cyclone_sshws_hazard_classes',
    'name': tr('Hurricane classes (SSHWS)'),
    'description': tr(
        'The <b>Saffir-Simpson Hurricane Wind Scale</b> is a 1 to 5 rating '
        'based on a hurricane\'s sustained wind speed, measured over a '
        '1-minute period. This scale estimates potential property damage. '
        'Hurricanes reaching Category 3 and higher are considered major '
        'hurricanes because of their potential for significant loss of '
        'life and damage. Category 1 and 2 storms are still dangerous, '
        'however, and require preventative measures. In the western '
        'North Pacific, the term "super typhoon" is used for tropical '
        'cyclones with sustained winds exceeding 150 mph.'),
    'type': hazard_classification_type,
    'citations': [
        {
            'text': tr('NOAA - NHC'),
            'link': 'http://www.nhc.noaa.gov/aboutsshws.php'
        },
        {
            'text': tr('Saffir-Simpson scale - wikipedia'),
            'link':
                'https://en.wikipedia.org/wiki/Saffir%E2%80%93Simpson_scale'
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
            'fatality_rate': None,
            'displacement_rate': 1.0,
            'numeric_default_min': {
                unit_knots['key']: 183,
                unit_metres_per_second['key']: 94,
                unit_miles_per_hour['key']: 210,
                unit_kilometres_per_hour['key']: 337
            },
            'numeric_default_max': big_number,
            'string_defaults': ['cat 5', 'category 5'],
            'citations': [
                {
                    'text': tr(
                        'Displacement rate is a generalized estimate ('
                        'personal communication Craig Arthur)'),
                    'link': 'https://github.com/inasafe/inasafe/issues/3762'
                            '#issuecomment-283839365'
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
            'fatality_rate': None,
            'displacement_rate': 0.99,
            'numeric_default_min': {
                unit_knots['key']: 151,
                unit_metres_per_second['key']: 77,
                unit_miles_per_hour['key']: 174,
                unit_kilometres_per_hour['key']: 279
            },
            'numeric_default_max': {
                unit_knots['key']: 183,
                unit_metres_per_second['key']: 94,
                unit_miles_per_hour['key']: 210,
                unit_kilometres_per_hour['key']: 337
            },
            'string_defaults': ['cat 4', 'category 4'],
            'citations': [
                {
                    'text': tr(
                        'Displacement rate is a generalized estimate ('
                        'personal communication Craig Arthur)'),
                    'link': 'https://github.com/inasafe/inasafe/issues/3762'
                            '#issuecomment-283839365'
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
            'fatality_rate': None,
            'displacement_rate': 0.9,
            'numeric_default_min': {
                unit_knots['key']: 128,
                unit_metres_per_second['key']: 65,
                unit_miles_per_hour['key']: 148,
                unit_kilometres_per_hour['key']: 238
            },
            'numeric_default_max': {
                unit_knots['key']: 151,
                unit_metres_per_second['key']: 77,
                unit_miles_per_hour['key']: 174,
                unit_kilometres_per_hour['key']: 279
            },
            'string_defaults': ['cat 3', 'category 3'],
            'citations': [
                {
                    'text': tr(
                        'Displacement rate is a generalized estimate ('
                        'personal communication Craig Arthur)'),
                    'link': 'https://github.com/inasafe/inasafe/issues/3762'
                            '#issuecomment-283839365'
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
            'fatality_rate': None,
            'displacement_rate': 0.65,
            'numeric_default_min': {
                unit_knots['key']: 111,
                unit_metres_per_second['key']: 57,
                unit_miles_per_hour['key']: 128,
                unit_kilometres_per_hour['key']: 206
            },
            'numeric_default_max': {
                unit_knots['key']: 128,
                unit_metres_per_second['key']: 65,
                unit_miles_per_hour['key']: 148,
                unit_kilometres_per_hour['key']: 238
            },
            'string_defaults': ['cat 2', 'category 2'],
            'citations': [
                {
                    'text': tr(
                        'Displacement rate is a generalized estimate ('
                        'personal communication Craig Arthur)'),
                    'link': 'https://github.com/inasafe/inasafe/issues/3762'
                            '#issuecomment-283839365'
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
            'fatality_rate': None,
            'displacement_rate': 0.15,
            'numeric_default_min': {
                unit_knots['key']: 85,
                unit_metres_per_second['key']: 44,
                unit_miles_per_hour['key']: 99,
                unit_kilometres_per_hour['key']: 160
            },
            'numeric_default_max': {
                unit_knots['key']: 111,
                unit_metres_per_second['key']: 57,
                unit_miles_per_hour['key']: 128,
                unit_kilometres_per_hour['key']: 238
            },
            'string_defaults': ['cat 1', 'category 1'],
            'citations': [
                {
                    'text': tr(
                        'Displacement rate is a generalized estimate ('
                        'personal communication Craig Arthur)'),
                    'link': 'https://github.com/inasafe/inasafe/issues/3762'
                            '#issuecomment-283839365'
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
            'fatality_rate': None,
            'displacement_rate': 0.0,
            'numeric_default_min': 0,
            'numeric_default_max': {
                unit_knots['key']: 85,
                unit_metres_per_second['key']: 44,
                unit_miles_per_hour['key']: 199,
                unit_kilometres_per_hour['key']: 160
            },
            'string_defaults': ['no', 'false'],
            'citations': [
                {
                    'text': tr(
                        'Displacement rate is a generalized estimate ('
                        'personal communication Craig Arthur)'),
                    'link': 'https://github.com/inasafe/inasafe/issues/3762'
                            '#issuecomment-283839365'
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
    ],
    'classification_unit': tr('cyclone category')
}

hazard_classification = {
    'key': 'hazard_classification',
    'name': tr('Classes'),
    'description': tr(
        'A hazard classification is used to define a range of severity '
        'thresholds (classes) for a hazard layer. '
        'The classification will be used to create zones of data that each '
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
        flood_petabencana_hazard_classes,
        flood_pcrafi_hazard_classes,
        inundation_dam_class,
        earthquake_mmi_scale,
        tsunami_hazard_classes,
        tsunami_hazard_population_classes,
        tsunami_hazard_classes_ITB,
        tsunami_hazard_population_classes_ITB,
        volcano_hazard_classes,
        ash_hazard_classes,
        cyclone_au_bom_hazard_classes,
        cyclone_sshws_hazard_classes,
    ]
}

hazard_classes_all = hazard_classification['types']
