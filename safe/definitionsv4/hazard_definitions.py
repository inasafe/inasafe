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
# Please group them and sort them alphabetical
from safe.utilities.i18n import tr
from safe.definitionsv4.concepts import concepts
from safe.definitionsv4.hazard_classifications import (
    generic_vector_hazard_classes,
    flood_vector_hazard_classes,
    tsunami_vector_hazard_classes,
    volcano_vector_hazard_classes,
    ash_vector_hazard_classes
)

__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '13/04/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# Hazard
caveat_simulation = tr(
    'The extent and severity of the mapped scenario or hazard zones '
    'may not be consistent with future events.')
caveat_local_conditions = tr(
    'The impacts on roads, people, buildings and other exposure '
    'elements may differ from the analysis results due to local '
    'conditions such as terrain and infrastructure type.')

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
    # User will be able to override this at run time in future
    'default_hazard_classification':  generic_vector_hazard_classes

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
    # Not implemented for earthquake since it uses damage curves
    'default_hazard_classification': None
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
    # User will be able to override this at run time in future
    'default_hazard_classification': flood_vector_hazard_classes
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
    # User will be able to override this at run time in future
    'default_hazard_classification': ash_vector_hazard_classes
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
    # User will be able to override this at run time in future
    'default_hazard_classification': tsunami_vector_hazard_classes
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
    # User will be able to override this at run time in future
    'default_hazard_classification': volcano_vector_hazard_classes
}

hazard_all = [
    hazard_flood,
    hazard_tsunami,
    hazard_earthquake,
    hazard_volcano,
    hazard_volcanic_ash,
    hazard_generic
]

# Renamed key from hazard to hazards in 3.2 because key was not unique TS
hazards = {
    'key': 'hazards',
    'name': tr('Hazards'),
    'description': concepts['hazard']['description'],
    'types': hazard_all,
    'citations': concepts['hazard']['citations']
}

