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

from safe.common.utilities import ugettext as tr

# Please group them and sort them alphabetical

# constants
small_number = 2 ** -53  # I think this is small enough

# categories
hazard_definition = {
    'id': 'hazard',
    'name': tr('hazard'),
    'description': tr(
        'A <b>hazard</b> layer represents '
        'something that will impact on the people or infrastructure '
        'in an area. For example; flood, earthquake, tsunami and  '
        'volcano are all examples of hazards.')
}
exposure_definition = {
    'id': 'exposure',
    'name': tr('exposure'),
    'description': tr(
        'An <b>exposure</b> layer represents '
        'people, property or infrastructure that may be affected '
        'in the event of a flood, earthquake, volcano etc.')
}
aggregation_definition = {
    'id': 'aggregation',
    'name': tr('aggregation'),
    'description': tr(
        'An <b>aggregation</b> layer represents '
        'regions you can use to summarise the results by. For '
        'example, we might summarise the affected people after'
        'a flood according to city districts.')
}

# subcategories
exposure_population = {
    'id': 'population',
    'name': tr('population'),
    'description': tr(
        'The <b>population</b> describes the people that might be '
        'exposed to a particular hazard.')
}
exposure_road = {
    'id': 'road',
    'name': tr('road'),
    'description': tr(
        'A <b>road</b> is a defined route used by a vehicle or people to '
        'travel between two or more points.')
}
exposure_structure = {
    'id': 'structure',
    'name': tr('structure'),
    'description': tr(
        'A <b>structure</b> can be any relatively permanent man '
        'made feature such as a building (an enclosed structure '
        'with walls and a roof) or a telecommunications facility or a '
        'bridge.')
}

hazard_all = {
    'id': 'all',
    'name': tr('all'),
    'description': tr(
        'An <b>all</b> hazard can be used to all types of hazard. For '
        'example: earthquake, flood, volcano, or tsunami.')
}
hazard_earthquake = {
    'id': 'earthquake',
    'name': tr('earthquake'),
    'description': tr(
        'An <b>earthquake</b> describes the sudden violent shaking of the '
        'ground that occurs as a result of volcanic activity or movement '
        'in the earth\'s crust.')
}
hazard_flood = {
    'id': 'flood',
    'name': tr('flood'),
    'description': tr(
        'A <b>flood</b> describes the inundation of land that is '
        'normally dry by a large amount of water. '
        'For example: A <b>flood</b> can occur after heavy rainfall, '
        'when a river overflows its banks or when a dam breaks. '
        'The effect of a <b>flood</b> is for land that is normally dry '
        'to become wet.')
}
hazard_tephra = {
    'id': 'tephra',
    'name': tr('tephra'),
    'description': tr(
        '<b>Tephra</b> describes the material, such as rock fragments and '
        'ash particles ejected by a volcanic eruption.')
}
hazard_tsunami = {
    'id': 'tsunami',
    'name': tr('tsunami'),
    'description': tr(
        'A <b>tsunami</b> describes a large ocean wave or series or '
        'waves usually caused by an under water earthquake or volcano.'
        'A <b>tsunami</b> at sea may go unnoticed but a <b>tsunami</b> '
        'wave that strikes land may cause massive destruction and '
        'flooding.')
}
hazard_volcano = {
    'id': 'volcano',
    'name': tr('volcano'),
    'description': tr(
        'A <b>volcano</b> describes a mountain which has a vent through '
        'which rock fragments, ash, lava, steam and gases can be ejected '
        'from below the earth\'s surface. The type of material '
        'ejected depends on the type of <b>volcano</b>.')
}

# units
unit_building_type_type = {
    'id': 'building_type',
    'name': tr('building type'),
    'description': tr(''),
    'constraint': 'unique values',
    'default_attribute': 'type'
}
unit_feet_depth = {
    'id': 'feet_depth',
    'name': tr('feet'),
    'description': tr(
        '<b>Feet</b> are an imperial unit of measure. There are 12 '
        'inches in 1 foot and 3 feet in 1 yard. '
        'In this case <b>feet</b> are used to describe the water depth.'),
    'constraint': 'continuous',
    'default_attribute': 'depth'  # applies to vector only
}
unit_metres_depth = {
    'id': 'metres_depth',
    'name': tr('metres'),
    'description': tr(
        '<b>metres</b> are a metric unit of measure. There are 100 '
        'centimetres in 1 metre. In this case <b>metres</b> are used to '
        'describe the water depth.'),
    'constraint': 'continuous',
    'default_attribute': 'depth'  # applies to vector only
}
unit_mmi = {
    'id': 'mmi',
    'name': tr('MMI'),
    'description': tr(
        'The <b>Modified Mercalli Intensity (MMI)</b> scale describes '
        'the intensity of ground shaking from a earthquake based on the '
        'effects observed by people at the surface.'),
    'constraint': 'continuous'
}
unit_mmi_depth = {
    'id': 'mmi_depth',
    'name': tr('MMI Depth'),
    'description': tr(
        'The <b>Modified Mercalli Intensity (MMI)</b> scale describes '
        'the intensity of ground shaking from a earthquake based on the '
        'effects observed by people at the surface. It will use <i>depth</> '
        'as default attribute in vector layer.'),
    'constraint': 'continuous',
    'default_attribute': 'depth'
}
unit_normalised = {
    'id': 'normalized',
    'name': tr('normalized'),
    'description': tr(''),
    'constraint': 'continuous'
}
unit_people_per_pixel = {
    'id': 'people_per_pixel',
    'name': tr('people per pixel'),
    'description': tr(
        '<b>Count</b> is the number of people in each cell. For example <b>'
        'population count</b> might be measured as the number of people per '
        'pixel in a raster data set. This unit is relevant for population '
        'rasters in geographic coordinates.'),
    'constraint': 'continuous'
}
unit_road_type_type = {
    'id': 'road_type',
    'name': tr('Road Type'),
    'description': tr(''),
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
            'description': tr('Water above ground height.'),
            'string_defaults': ['Kawasan Rawan Bencana I',
                                'high'],
            'numeric_default_min': 0,
            'numeric_default_max': 3,
            'optional': False
        },
        {
            'name': 'medium',
            'description': tr('Water above ground height.'),
            'string_defaults': ['Kawasan Rawan Bencana II',
                                'medium'],
            'numeric_default_min': 3,
            'numeric_default_max': 5,
            'optional': False
        },
        {
            'name': 'low',
            'description': tr('Water above ground height.'),
            'string_defaults': ['Kawasan Rawan Bencana III',
                                'low'],
            'numeric_default_min': 5,
            'numeric_default_max': 10,
            'optional': False
        }
    ],
    'name': tr('volcano categorical'),
    'description': tr('')
}
unit_wetdry = {
    'id': 'wetdry',
    'constraint': 'categorical',
    'default_attribute': 'affected',
    'default_category': 'wet',
    'classes': [
        {
            'name': 'wet',
            'description': tr('Water above ground height.'),
            'string_defaults': ['wet', '1', 'YES', 'y', 'yes'],
            'numeric_default_min': 1,
            'numeric_default_max': 9999999999,
            'optional': True
        },
        {
            'name': 'dry',
            'description': tr('No water above ground height.'),
            'string_defaults': ['dry', '0', 'No', 'n', 'no'],
            'numeric_default_min': 0,
            'numeric_default_max': (1 - small_number),
            'optional': True
        }
    ],
    'name': tr('wet / dry'),
    'description': tr(
        'This is a binary description for an area. The area is either '
        '<b>wet</b> (affected by flood water) or <b>dry</b> (not affected '
        'by flood water). This unit does not describe how <b>wet</b> or '
        '<b>dry</b> an area is.')
}


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
