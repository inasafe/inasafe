# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid / DFAT -
**New Metadata for SAFE.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from safe.utilities.i18n import tr
from safe.definitionsv4.concepts import concepts
from safe.definitionsv4.definitions_v3 import small_number
from safe.definitionsv4.definitions_v3 import (
    unit_centimetres, unit_metres, unit_kilometres)

# TODO : Add unit to each of these hazard classification

# Vector Hazard Classification
generic_vector_hazard_classes = {
    'key': 'generic_vector_hazard_classes',
    'name': tr('Generic classes'),
    'description': concepts['generic_hazard']['description'],
    'citations': concepts['generic_hazard']['citations'],
    'default_attribute': 'affected',
    'unit': None,
    'classes': [
        {
            'key': 'high',
            'name': tr('High Hazard Zone'),
            'description': tr('The location that has highest impact.'),
            'string_defaults': ['high'],
            'class_value': 3,
            'numeric_min': 3,
            'numeric_max': (4 - small_number),
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
            'description': tr('The location that has medium impact.'),
            'string_defaults': ['medium'],
            'class_value': 2,
            'numeric_min': 2,
            'numeric_max': (3 - small_number),
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
            'description': tr('The location that has lowest impact.'),
            'string_defaults': ['low'],
            'class_value': 1,
            'numeric_min': 1,
            'numeric_max': (2 - small_number),
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

volcano_vector_hazard_classes = {
    'key': 'volcano_vector_hazard_classes',
    'name': tr('Volcano classes'),
    'description': tr(
        'Three classes are supported for volcano vector hazard data: '
        '<b>low</b>, <b>medium</b>, or <b>high</b>.'),
    'default_attribute': 'affected',
    'unit': unit_kilometres,
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
            'description': tr('The highest hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana III', 'high'],
            'class_value': 3,
            'numeric_min': 0,
            'numeric_max': (3 - small_number),
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
            'description': tr('The medium hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana II', 'medium'],
            'class_value': 2,
            'numeric_min': 3,
            'numeric_max': (5 - small_number),
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
            'description': tr('The lowest hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana I', 'low'],
            'class_value': 1,
            'numeric_min': 5,
            'numeric_max': 10,
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

flood_vector_hazard_classes = {
    'key': 'flood_vector_hazard_classes',
    'name': tr('Flood classes'),
    'description': tr(
        'This is a binary description for an area. The area is either '
        '<b>wet</b> (affected by flood water) or <b>dry</b> (not affected '
        'by flood water). This unit does not describe how <b>wet</b> or '
        '<b>dry</b> an area is.'),
    'default_attribute': 'affected',
    'unit': unit_metres,
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
            'description': tr('Water above ground height.'),
            'string_defaults': ['wet', '1', 'YES', 'y', 'yes'],
            'class_value': 2,
            'numeric_min': 1,
            'numeric_max': 9999999999,
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
            'description': tr('No water above ground height.'),
            'string_defaults': ['dry', '0', 'No', 'n', 'no'],
            'class_value': 1,
            'numeric_min': 0,
            'numeric_max': (1 - small_number),
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

ash_vector_hazard_classes = {
    'key': 'ash_vector_hazard_classes',
    'name': tr('Ash classes'),
    'description': tr(
        'Three four are supported for ash vector hazard data: '
        '<b>very low</b>, <b>low</b>, <b>medium</b>, <b>high</b> or '
        '<b>very high</b>.'),
    'default_attribute': 'affected',
    'unit': unit_centimetres,
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'classes': [
        {
            'key': 'very low',
            'name': tr('Very Low'),
            'description': tr('Very Low.'),
            'class_value': 1,
            'numeric_min': 0.01,
            'numeric_max': 0.1,
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
            'description': tr('Low'),
            'class_value': 2,
            'numeric_min': 0.1,
            'numeric_max': 2,
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
            'description': tr('Medium'),
            'class_value': 3,
            'numeric_min': 2,
            'numeric_max': 5,
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
            'description': tr('High'),
            'class_value': 4,
            'numeric_min': 5,
            'numeric_max': 10,
            'optional': True,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'very high',
            'name': tr('Very high'),
            'description': tr('Very High.'),
            'numeric_min': 10,
            'numeric_max': 9999999999,
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

# Raster Hazard Classification
flood_raster_hazard_classes = {
    'key': 'flood_raster_hazard_classes',
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
            'description': tr('Water above ground height.'),
            'numeric_min': 1,
            'numeric_max': 9999999999,
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
            'description': tr('No water above ground height.'),
            'numeric_min': 0,
            'numeric_max': (1 - small_number),
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

generic_raster_hazard_classes = {
    'key': 'generic_raster_hazard_classes',
    'name': tr('Generic classes'),
    'description': concepts['generic_hazard']['description'],
    'citations': concepts['generic_hazard']['citations'],
    'classes': [
        {
            'key': 'high',
            'name': tr('High hazard zone'),
            'description': tr('The highest hazard classification.'),
            'numeric_min': 3,
            'numeric_max': 3,
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
            'name': tr('Medium hazard zone'),
            'description': tr('The middle hazard classification.'),
            'numeric_min': 2,
            'numeric_max': 2,
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
            'name': tr('Low hazard zone'),
            'description': tr('The lowest hazard classification.'),
            'numeric_min': 1,
            'numeric_max': 1,
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

tsunami_vector_hazard_classes = {
    'key': 'tsunami_raster_hazard_classes',
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
            'key': 'dry',
            'name': tr('Dry zone'),
            'description': tr('No water above ground height.'),
            'numeric_min': 0,
            'numeric_max': (1 - small_number),
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
            'numeric_min': 0,
            'numeric_max': 1,
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
            'description': tr(
                'Water above 1.1m and less than 3.0m. The area is potentially '
                'hit by a tsunami wave with an inundation depth of 1 - 3 m or '
                'equal to V-VI tsunami intensity scale (Papadoupulos and '
                'Imamura, 2001). Tsunami wave with a 3m inundation depth '
                'causes most people frightened and to flee to higher ground. '
                'Small vessels drift and collide. Damage occurs to some '
                'wooden houses, while most of them are safe.'),
            'numeric_min': 1,
            'numeric_max': 3,
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
            'numeric_min': 3,
            'numeric_max': 8,
            'optional': True,
            'citations': [
                {
                    'text': None,
                    'link': None
                }
            ]
        },
        {
            'key': 'very high',
            'name': tr('Very high hazard zone'),
            'description': tr('Water above 8.0m.'),
            'numeric_min': 8,
            'numeric_max': 9999999999,
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

# Todo, we need to remove this raster classes for the V4.
tsunami_raster_hazard_classes = tsunami_vector_hazard_classes

# Todo, we need to remove this raster classes for the V4.
raster_hazard_classification = {
    'key': 'raster_hazard_classification',
    'name': tr('Classes'),
    'description': tr(
        'Hazard classes are a way to classify the cell values '
        'in a raster layer.'),
    'types': [
        flood_raster_hazard_classes,
        generic_raster_hazard_classes,
        tsunami_raster_hazard_classes
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

all_raster_hazard_classes = raster_hazard_classification['types']

vector_hazard_classification = {
    'key': 'vector_hazard_classification',
    'name': tr('Classes'),
    'description': tr(
        'Hazard classes are a way to group the values in one of '
        'the attributes or fields in a vector layer.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'types': [
        generic_vector_hazard_classes,
        volcano_vector_hazard_classes,
        ash_vector_hazard_classes,
        tsunami_vector_hazard_classes,
        flood_vector_hazard_classes
    ]
}

all_vector_hazard_classes = vector_hazard_classification['types']
