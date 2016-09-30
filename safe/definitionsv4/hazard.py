# coding=utf-8

"""Definitions relating to hazards."""
from safe.definitionsv4.hazard_classifications import generic_vector_hazard_classes, \
    volcano_vector_hazard_classes, flood_vector_hazard_classes, \
    flood_raster_hazard_classes, generic_raster_hazard_classes, \
    tsunami_raster_hazard_classes
from safe.definitionsv4.caveats import caveat_simulation, \
    caveat_local_conditions
from safe.definitionsv4.concepts import concepts
from safe.definitionsv4.units import unit_feet, unit_generic, \
    unit_kilogram_per_meter_square, unit_kilometres, unit_metres, \
    unit_millimetres, unit_centimetres, unit_mmi
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

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
