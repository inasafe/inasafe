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

# Please group them and sort them alphabetical

# constants
small_number = 2 ** -143  # I think this is small enough

# subcategories
exposure_population = 'population'
exposure_road = 'road'
exposure_structure = 'structure'
hazard_all = 'all'
hazard_earthquake = 'earthquake'
hazard_flood = 'flood'
hazard_tsunami = 'tsunami'
hazard_volcano = 'volcano'

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
    'name': 'building type',
    'description': '',
    'constraint': 'unique values',
    'default_attribute': 'type'
}
unit_feet_depth = {
    'name': 'feet',
    'description': '',
    'constraint': 'continuous',
    'default_attribute': 'depth'  # applies to vector only
}
unit_metres_depth = {
    'name': 'metres',
    'description': '',
    'constraint': 'continuous',
    'default_attribute': 'depth'  # applies to vector only
}
unit_mmi = {
    'name': 'mmi',
    'description': '',
    'constraint': 'continuous'
}
unit_mmi_depth = {
    'name': 'mmi',
    'description': '',
    'constraint': 'continuous',
    'default_attribute': 'depth'
}
unit_normalised = {
    'name': 'normalized',
    'description': '',
    'constraint': 'continuous'
}
unit_people_per_pixel = {
    'name': 'people_per_pixel',
    'description': '',
    'constraint': 'continuous'
}
unit_road_type_type = {
    'name': 'road_type',
    'description': '',
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
    ]
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
    ]
}

mmi_name = ''
mmi_text = ''
road_type_name = ''
road_type_text = ''
building_type_name = ''
building_type_text = ''
people_per_pixel_name = ''
people_per_pixel_text = ''
normalized_name = ''
normalized_text = ''
wetdry_name = ''
wetdry_text = ''
depth_metres_name = ''
depth_metres_text = ''
depth_feet_name = ''
depth_feet_text = ''
volcano_category_name = ''
volcano_category_text = ''
