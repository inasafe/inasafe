# coding=utf-8

"""Definitions relating to hazards."""

from safe.definitionsv4.concepts import concepts
from safe.definitionsv4.constants import small_number
from safe.definitionsv4.units import unit_feet, unit_generic, \
    unit_kilogram_per_meter_square, unit_kilometres, unit_metres, \
    unit_millimetres, unit_centimetres, unit_mmi
from safe.definitionsv4.caveats import caveat_simulation, \
    caveat_local_conditions
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


layer_purpose_hazard = {
    'key': 'hazard',
    'name': tr('Hazard'),
    'description': concepts['hazard']['description'],
    'citations': concepts['hazard']['citations']
}
hazard_category_single_event = {
    'key': 'single_event',
    'name': tr('Single event'),
    # short name is used when concatenating map_title in IF
    'short_name': tr('event'),
    'description': tr(
        '<b>Single event</b> hazard data can be based on either a specific  '
        'event that has happened in the past, for example a flood like '
        'Jakarta 2013, or a possible event, such as the tsunami that results '
        'from an earthquake near Bima, that might happen in the future.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
hazard_category_multiple_event = {
    'key': 'multiple_event',
    'name': tr('Multiple event'),
    # short name is used when concatenating map_title in IF
    'short_name': tr('hazard'),
    'description': tr(
        '<b>Multiple event</b> hazard data can be based on historical '
        'observations such as a hazard map of all observed volcanic '
        'deposits around a volcano.'
        '<p>This type of hazard data shows those locations that might be '
        'impacted by a volcanic eruption in the future. Another example '
        'might be a probabilistic hazard model that shows the likelihood of a '
        'magnitude 7 earthquake happening in the next 50 years.</p>'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
hazard_category = {
    'key': 'hazard_category',
    'name': tr('Scenario'),
    'description': tr(
        'This describes the type of hazard scenario that is represented by '
        'the layer. There are two possible values for this attribute, single '
        'event and multiple event.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'types': [
        hazard_category_single_event,
        hazard_category_multiple_event
    ]
}
continuous_hazard_unit = {
    'key': 'continuous_hazard_unit',
    'name': tr('Units'),
    'description': tr(
        'Hazard units are used for continuous data. Examples of hazard units '
        'include metres and feet. '),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'types': [
        unit_feet,
        unit_generic,
        unit_kilogram_per_meter_square,
        unit_kilometres,
        unit_metres,
        unit_millimetres,
        unit_centimetres,
        unit_mmi
    ]
}
continuous_hazard_unit_all = continuous_hazard_unit['types']
generic_vector_hazard_classes = {
    'key': 'generic_vector_hazard_classes',
    'name': tr('Generic classes'),
    'description': concepts['generic_hazard']['description'],
    'citations': concepts['generic_hazard']['citations'],
    'default_attribute': 'affected',
    'classes': [
        {
            'key': 'high',
            'name': tr('High Hazard Zone'),
            'description': tr('The location that has highest impact.'),
            'string_defaults': ['high'],
            'numeric_default_min': 5,
            'numeric_default_max': 10,
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
            'numeric_default_min': 3,
            'numeric_default_max': (5 - small_number),
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
            'numeric_default_min': 0,
            'numeric_default_max': (3 - small_number),
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
flood_vector_hazard_classes = {
    'key': 'flood_vector_hazard_classes',
    'name': tr('Flood classes'),
    'description': tr(
        'This is a binary description for an area. The area is either '
        '<b>wet</b> (affected by flood water) or <b>dry</b> (not affected '
        'by flood water). This unit does not describe how <b>wet</b> or '
        '<b>dry</b> an area is.'),
    'default_attribute': 'affected',
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
        flood_vector_hazard_classes
    ]
}
all_vector_hazard_classes = vector_hazard_classification['types']
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
            'numeric_default_min': 3,
            'numeric_default_max': 3,
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
            'numeric_default_min': 2,
            'numeric_default_max': 2,
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
            'numeric_default_min': 1,
            'numeric_default_max': 1,
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
tsunami_raster_hazard_classes = {
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
            'key': 'very high',
            'name': tr('Very high hazard zone'),
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
        }

    ]
}
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
hazard_generic = {
    'key': 'generic',
    'name': tr('Generic'),
    'description': tr(
        'A <b>generic hazard</b> can be used for any type of hazard where the '
        'data have been classified or generalised. For example: earthquake, '
        'flood, volcano, tsunami, landslide, smoke haze or strong wind.'),
    'notes': [  # additional generic notes for generic - IF has more
        caveat_simulation,
        caveat_local_conditions,
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'single_event_notes': [  # notes specific to single event data
    ],
    'multi_event_notes': [  # notes specific to multi event data
    ],
    'actions': [  # these are additional generic actions - IF has more

    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'continuous_hazard_units': [],
    'vector_hazard_classifications': [generic_vector_hazard_classes],
    'raster_hazard_classifications': [generic_raster_hazard_classes],
}
hazard_earthquake = {
    'key': 'earthquake',
    'name': tr('Earthquake'),
    'description': tr(
        'An <b>earthquake</b> describes the sudden violent shaking of the '
        'ground that occurs as a result of volcanic activity or movement '
        'in the earth\'s crust.'),
    'notes': [  # additional generic notes for earthquake - IF has more
        caveat_simulation,
        caveat_local_conditions,
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'single_event_notes': [  # notes specific to single event data
    ],
    'multi_event_notes': [  # notes specific to multi event data
    ],
    'actions': [  # these are additional generic actions - IF has more

    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'continuous_hazard_units': [unit_mmi],
    'vector_hazard_classifications': [],
    'raster_hazard_classifications': [],
}
hazard_flood = {
    'key': 'flood',
    'name': tr('Flood'),
    'description': tr(
        'A <b>flood</b> describes the inundation of land that is '
        'normally dry by a large amount of water. '
        'For example: A <b>flood</b> can occur after heavy rainfall, '
        'when a river overflows its banks or when a dam breaks. '
        'The effect of a <b>flood</b> is for land that is normally dry '
        'to become wet.'),
    'notes': [  # additional generic notes for flood - IF has more
        caveat_simulation,
        caveat_local_conditions,
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'single_event_notes': [  # notes specific to single event data
    ],
    'multi_event_notes': [  # notes specific to multi event data
    ],
    'actions': [  # these are additional generic actions - IF has more

    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'continuous_hazard_units': [],
    'vector_hazard_classifications': [flood_vector_hazard_classes],
    'raster_hazard_classifications': [flood_raster_hazard_classes],
}
hazard_volcanic_ash = {
    'key': 'volcanic_ash',
    'name': tr('Volcanic ash'),
    'description': tr(
        '<b>Volcanic ash</b> describes fragments of pulverized rock, minerals '
        'and volcanic glass, created during volcanic eruptions, less than '
        '2 mm (0.079 inches) in diameter.'),
    'notes': [  # additional generic notes for volcanic ash - IF has more
        caveat_simulation,
        caveat_local_conditions,
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'single_event_notes': [  # notes specific to single event data
    ],
    'multi_event_notes': [  # notes specific to multi event data
    ],
    'actions': [  # these are additional generic actions - IF has more

    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'continuous_hazard_units': [unit_centimetres],
    'vector_hazard_classifications': [],
    'raster_hazard_classifications': [],
}
hazard_tsunami = {
    'key': 'tsunami',
    'name': tr('Tsunami'),
    'description': tr(
        'A <b>tsunami</b> describes a large ocean wave or series or '
        'waves usually caused by an underwater earthquake or volcano. '
        'A <b>tsunami</b> at sea may go unnoticed but a <b>tsunami</b> '
        'wave that strikes land may cause massive destruction and '
        'flooding.'),
    'notes': [  # additional generic notes for tsunami - IF has more
        caveat_simulation,
        caveat_local_conditions,
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'single_event_notes': [  # notes specific to single event data
    ],
    'multi_event_notes': [  # notes specific to multi event data
    ],
    'actions': [  # these are additional generic actions - IF has more

    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'continuous_hazard_units': [unit_feet, unit_metres],
    'vector_hazard_classifications': [],
    'raster_hazard_classifications': [tsunami_raster_hazard_classes],
}
hazard_volcano = {
    'key': 'volcano',
    'name': tr('Volcano'),
    'description': tr(
        'A <b>volcano</b> describes a mountain which has a vent through '
        'which rock fragments, ash, lava, steam and gases can be ejected '
        'from below the earth\'s surface. The type of material '
        'ejected depends on the type of <b>volcano</b>.'),
    'notes': [  # additional generic notes for volcano
        caveat_simulation,
        caveat_local_conditions,
    ],
    'actions': [  # these are additional generic actions - IF has more

    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'single_event_notes': [  # notes specific to single event data
    ],
    'multi_event_notes': [  # notes specific to multi event data
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'continuous_hazard_units': [],
    'vector_hazard_classifications': [volcano_vector_hazard_classes],
    'raster_hazard_classifications': [],
}
hazard_all = [
    hazard_flood,
    hazard_tsunami,
    hazard_earthquake,
    hazard_volcano,
    hazard_volcanic_ash,
    hazard_generic
]
hazards = {
    'key': 'hazards',
    'name': tr('Hazards'),
    'description': concepts['hazard']['description'],
    'types': hazard_all,
    'citations': concepts['hazard']['citations']
}
