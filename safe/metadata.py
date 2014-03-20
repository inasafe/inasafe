# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Metadata for SAFE.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'imajimatika@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '19/03/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from PyQt4.QtGui import QApplication

# Please group them and sort them alphabetical

# constants
small_number = 2 ** -53  # I think this is small enough

# categories
hazard_name = QApplication.translate(
    'Keyword Metadata',
    'hazard')
hazard_text = QApplication.translate(
    'Keyword Metadata',
    'A <b>hazard</b> layer represents '
    'something that will impact on the people or infrastructure '
    'in an area. For example; flood, earthquake, tsunami and  '
    'volcano are all examples of hazards.')

exposure_name = QApplication.translate(
    'Keyword Metadata',
    'exposure')
exposure_text = QApplication.translate(
    'Keyword Metadata',
    'An <b>exposure</b> layer represents '
    'people, property or infrastructure that may be affected '
    'in the event of a flood, earthquake, volcano etc.')

aggregation_name = QApplication.translate(
    'Keyword Metadata',
    'aggregation')
aggregation_text = QApplication.translate(
    'Keyword Metadata',
    'An <b>aggregation</b> layer represents '
    'regions you can use to summarise the results by. For '
    'example, we might summarise the affected people after'
    'a flood according to city districts.')


# subcategories
exposure_population = 'population'
exposure_population_name = QApplication.translate(
    'Keyword Metadata',
    'population')
exposure_population_text = QApplication.translate(
    'Keyword Metadata',
    'The <b>population</b> describes the people that might be '
    'exposed to a particular hazard.')

exposure_road = 'road'
exposure_road_name = QApplication.translate(
    'Keyword Metadata',
    'road')
exposure_road_text = QApplication.translate(
    'Keyword Metadata',
    'A <b>road</b> is a defined route used by a vehicle or people to '
    'travel between two or more points.')

exposure_structure = 'structure'
exposure_structure_name = QApplication.translate(
    'Keyword Metadata',
    'structure')
exposure_structure_text = QApplication.translate(
    'Keyword Metadata',
    'A <b>structure</b> can be any relatively permanent man '
    'made feature such as a building (an enclosed structure '
    'with walls and a roof) or a telecommunications facility or a '
    'bridge.')

hazard_all = 'all'

hazard_earthquake = 'earthquake'
hazard_earthquake_name = QApplication.translate(
    'Keyword Metadata',
    'earthquake')
hazard_earthquake_text = QApplication.translate(
    'Keyword Metadata',
    'An <b>earthquake</b> describes the sudden violent shaking of the '
    'ground that occurs as a result of volcanic activity or movement '
    'in the earth\'s crust.')

hazard_flood = 'flood'
hazard_flood_name = QApplication.translate(
    'Keyword Metadata',
    'flood')
hazard_flood_text = QApplication.translate(
    'Keyword Metadata',
    'A <b>flood</b> describes the inundation of land that is '
    'normally dry by a large amount of water. '
    'For example: A <b>flood</b> can occur after heavy rainfall, '
    'when a river overflows its banks or when a dam breaks. '
    'The effect of a <b>flood</b> is for land that is normally dry '
    'to become wet.')

hazard_tephra = 'tephra'
hazard_tephra_name = QApplication.translate(
    'Keyword Metadata',
    'tephra')
hazard_tephra_text = QApplication.translate(
    'Keyword Metadata',
    '<b>Tephra</b> describes the material, such as rock fragments and '
    'ash particles ejected by a volcanic eruption.')

hazard_tsunami = 'tsunami'
hazard_tsunami_name = QApplication.translate(
    'Keyword Metadata',
    'tsunami')
hazard_tsunami_text = QApplication.translate(
    'Keyword Metadata',
    'A <b>tsunami</b> describes a large ocean wave or series or '
    'waves usually caused by an under water earthquake or volcano.'
    'A <b>tsunami</b> at sea may go unnoticed but a <b>tsunami</b> '
    'wave that strikes land may cause massive destruction and '
    'flooding.')

hazard_volcano = 'volcano'
hazard_volcano_name = QApplication.translate(
    'Keyword Metadata',
    'volcano')
hazard_volcano_text = QApplication.translate(
    'Keyword Metadata',
    'A <b>volcano</b> describes a mountain which has a vent through '
    'which rock fragments, ash, lava, steam and gases can be ejected '
    'from below the earth\'s surface. The type of material '
    'ejected depends on the type of <b>volcano</b>.')


# layer_constraints
layer_raster_numeric = {
    'layer_type': 'raster',
    'data_type': 'numeric'
}
layer_vector_line = {
    'layer_type': 'vector',
    'data_type': 'line'
}
layer_vector_point = {
    'layer_type': 'vector',
    'data_type': 'point'
}
layer_vector_polygon = {
    'layer_type': 'vector',
    'data_type': 'polygon'
}


# units
unit_building_type_type = {
    'id': 'building_type',
    'name': QApplication.translate(
        'Keyword Metadata',
        'building type'),
    'description': QApplication.translate(
        'Keyword Metadata',
        ''),
    'constraint': 'unique values',
    'default_attribute': 'type'
}
unit_feet_depth = {
    'id': 'feet_depth',
    'name': QApplication.translate(
        'Keyword Metadata',
        'feet'),
    'description': QApplication.translate(
        'Keyword Metadata',
        '<b>Feet</b> are an imperial unit of measure. There are 12 '
        'inches in 1 foot and 3 feet in 1 yard. '
        'In this case <b>feet</b> are used to describe the water depth.'),
    'constraint': 'continuous',
    'default_attribute': 'depth'  # applies to vector only
}
unit_metres_depth = {
    'id': 'metres_depth',
    'name': QApplication.translate(
        'Keyword Metadata',
        'metres'),
    'description': QApplication.translate(
        'Keyword Metadata',
        '<b>metres</b> are a metric unit of measure. There are 100 '
        'centimetres in 1 metre. In this case <b>metres</b> are used to '
        'describe the water depth.'),
    'constraint': 'continuous',
    'default_attribute': 'depth'  # applies to vector only
}
unit_mmi = {
    'id': 'mmi',
    'name': QApplication.translate(
        'Keyword Metadata',
        'MMI'),
    'description': QApplication.translate(
        'Keyword Metadata',
        'The <b>Modified Mercalli Intensity (MMI)</b> scale describes '
        'the intensity of ground shaking from a earthquake based on the '
        'effects observed by people at the surface.'),
    'constraint': 'continuous'
}
unit_mmi_depth = {
    'id': 'mmi_depth',
    'name': QApplication.translate(
        'Keyword Metadata',
        'MMI'),
    'description': QApplication.translate(
        'Keyword Metadata',
        ''),
    'constraint': 'continuous',
    'default_attribute': 'depth'
}
unit_normalised = {
    'id': 'normalized',
    'name': QApplication.translate(
        'Keyword Metadata',
        'normalized'),
    'description': QApplication.translate(
        'Keyword Metadata',
        ''),
    'constraint': 'continuous'
}
unit_people_per_pixel = {
    'id': 'people_per_pixel',
    'name': QApplication.translate(
        'Keyword Metadata',
        'people per pixel'),
    'description': QApplication.translate(
        'Keyword Metadata',
        '<b>Density</b> is the number of features within a defined '
        'area. For example <b>population density</b> might be measured '
        'as the number of people per square kilometre.'),
    'constraint': 'continuous'
}
unit_road_type_type = {
    'id': 'road_type',
    'name': QApplication.translate(
        'Keyword Metadata',
        'Road Type'),
    'description': QApplication.translate(
        'Keyword Metadata',
        ''),
    'constraint': 'unique values',
    'default_attribute': 'type'
}
unit_volcano_categorical = {
    'id': 'volcano_categorical',
    'constraint': 'categorical',
    'default_attribute': 'affected',
    'default_category': 'high',
    'classes': [
        {
            'name': 'high',
            'description': 'Water above ground height.',
            'string_defaults': ['Kawasan Rawan Bencana I',
                                'high'],
            'numeric_default_min':  0,
            'numeric_default_max': 3,
            'optional': False
        },
        {
            'name': 'medium',
            'description': 'Water above ground height.',
            'string_defaults': ['Kawasan Rawan Bencana II',
                                'medium'],
            'numeric_default_min':  3,
            'numeric_default_max': 5,
            'optional': False
        },
        {
            'name': 'low',
            'description': 'Water above ground height.',
            'string_defaults': ['Kawasan Rawan Bencana III',
                                'low'],
            'numeric_default_min':  5,
            'numeric_default_max': 10,
            'optional': False
        }
    ],
    'name': QApplication.translate(
        'Keyword Metadata',
        'volcano categorical'),
    'description': QApplication.translate(
        'Keyword Metadata',
        '')
}
unit_wetdry = {
    'id': 'wetdry',
    'constraint': 'categorical',
    'default_attribute': 'affected',
    'default_category': 'wet',
    'classes': [
        {
            'name': 'wet',
            'description': 'Water above ground height.',
            'string_defaults': ['wet', '1', 'YES', 'y', 'yes'],
            'numeric_default_min':  1,
            'numeric_default_max': 9999999999,
            'optional': True,
            },
        {
            'name': 'dry',
            'description': 'No water above ground height.',
            'string_defaults': ['dry', '0', 'No', 'n', 'no'],
            'numeric_default_min':  0,
            'numeric_default_max': (1 - small_number),
            'optional': True
        }
    ],
    'name': QApplication.translate(
        'Keyword Metadata',
        'wet / dry'),
    'description': QApplication.translate(
        'Keyword Metadata',
        'This is a binary description for an area. The area is either '
        '<b>wet</b> (affected by flood water) or <b>dry</b> (not affected '
        'by flood water). This unit does not describe how <b>wet</b> or '
        '<b>dry</b> an area is.')
}


# Constants not used anywhere yet
notset_text = QApplication.translate(
    'Keyword Metadata',
    '<b>Not Set</b> is the default setting for when no units are '
    'selected.')
kgm2_text = QApplication.translate(
    'Keyword Metadata',
    '<b>Kilograms per square metre</b> describes the weight in '
    'kilograms by area in square metres.')
count_text = QApplication.translate(
    'Keyword Metadata',
    '<b>Count</b> is the number of features.')
