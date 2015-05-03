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

__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '19/03/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# Please group them and sort them alphabetical
from safe.utilities.i18n import tr

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
        'regions you can use when summarise analysis results. For '
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

hazard_generic = {
    'id': 'generic',
    'name': tr('generic'),
    'description': tr(
        'A generic hazard can be used for any type of hazard where the data '
        'have been classified or generalised. For example: earthquake, flood, '
        'volcano, or tsunami.')
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
hazard_volcanic_ash = {
    'id': 'volcanic_ash',
    'name': tr('volcanic ash'),
    'description': tr(
        '<b>Volcanic ash</b> describes fragments of pulverized rock, minerals '
        'and volcanic glass, created during volcanic eruptions, less than '
        '2 mm (0.079 inches) in diameter')
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

hazard_all = [
    hazard_earthquake,
    hazard_flood,
    hazard_volcanic_ash,
    hazard_tsunami,
    hazard_volcano,
    hazard_generic
]

# units
unit_building_generic = {
    'id': 'building_generic',
    'name': tr('building generic'),
    'description': tr(
        '<b>Building generic</b> unit means that there is no building type '
        'attribute in the exposure data.')
}
unit_building_type_type = {
    'id': 'building_type',
    'name': tr('building type'),
    'description': tr(
        '<b>Building type</b> is a unit that represent the type of the '
        'building. In this case, building type will be used to group the '
        'result of impact function.'),
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
    'constraint': 'continuous',
    'default_attribute': 'mmi'  # applies to vector only
}
unit_continuous = {
    'id': 'continuous',
    'name': tr('continuous'),
    'description': tr(
        '<b>Continuous</b> data can be hazard or exposure data '
        'where the values are are either integers or decimal numbers '
        'resulting a continuously varying phenomenon. For example flood depth '
        'is a continuous value from 0 to the maximum reported depth during a '
        'flood. Raster data is considered to be continuous by default and you '
        'should explicitly indicate that it is classified if each cell in the '
        'raster represents a discrete class (e.g. low depth = 1, medium depth '
        '= 2, high depth = 3).'),
    'constraint': 'continuous'
}
unit_classified = {
    'id': 'classes',
    'name': tr('classes'),
    'description': tr(
        '<b>Classified</b> data can be hazard data where the '
        'values have been classified or coded such that each raster cell '
        'represents a discrete class. For example if the raster represents '
        'a flood layer, permissible cell values may be 1, 2, 3 where 1 '
        'represents low water, 2 represents medium inundation and 3 '
        'represents high inundation.'
    ),
    'constraint': 'classified'
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
    'description': tr(
        '<b>Road type</b> is a unit that represent the type of the road. '
        'In this case, road type will be used to group the result of impact '
        'function.'),
    'constraint': 'unique values',
    'default_attribute': 'type'
}
unit_volcano_categorical = {
    'id': 'volcano_categorical',
    'name': tr('volcano categorical'),
    'description': tr(
        'This is a ternary description for an area. The area is either '
        'has <b>low</b>, <b>medium</b>, or <b>high</b> impact from the '
        'volcano.'),
    'constraint': 'categorical',
    'default_attribute': 'affected',
    'default_category': 'high',
    'classes': [
        {
            'name': 'high',
            'description': tr('Distance from the volcano.'),
            'string_defaults': ['Kawasan Rawan Bencana III',
                                'high'],
            'numeric_default_min': 0,
            'numeric_default_max': 3,
            'optional': False
        },
        {
            'name': 'medium',
            'description': tr('Distance from the volcano.'),
            'string_defaults': ['Kawasan Rawan Bencana II',
                                'medium'],
            'numeric_default_min': 3,
            'numeric_default_max': 5,
            'optional': False
        },
        {
            'name': 'low',
            'description': tr('Distance from the volcano.'),
            'string_defaults': ['Kawasan Rawan Bencana I',
                                'low'],
            'numeric_default_min': 5,
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
    'name': tr('wet / dry'),
    'description': tr(
        'This is a binary description for an area. The area is either '
        '<b>wet</b> (affected by flood water) or <b>dry</b> (not affected '
        'by flood water). This unit does not describe how <b>wet</b> or '
        '<b>dry</b> an area is.'),
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
    ]
}

# layer_constraints
layer_raster_continuous = {
    'layer_type': 'raster',
    'data_type': 'continuous',
    'description': unit_continuous['description']
}

layer_raster_classified = {
    'layer_type': 'raster',
    'data_type': 'classified',
    'description': unit_classified['description']
}

layer_vector_point = {
    'layer_type': 'vector',
    'data_type': 'point',
    'description': tr(
        'A layer composed of points which each represent a feature on the '
        'earth. Currently the only point data supported by InaSAFE are '
        '<b>volcano hazard</b> layers.')
}

layer_vector_line = {
    'layer_type': 'vector',
    'data_type': 'line',
    'description': tr(
        'A layer composed of linear features. Currently only <b>road exposure'
        '</b>line layers are supported by InaSAFE.')
}

layer_vector_polygon = {
    'layer_type': 'vector',
    'data_type': 'polygon',
    'description': tr(
        'A layer composed on polygon features that represent areas of hazard '
        'or exposure. For example areas of flood represented as polygons '
        '(for a hazard) or building footprints represented as polygons ( '
        'for an exposure). The polygon layer will often need the presence '
        'of specific layer attributes too - these will vary from impact '
        'function to impact function and whether the layer represents '
        'a hazard or an exposure layer. Polygon layers can also be used '
        'for aggregation - where impact analysis results per boundary '
        'such as village or district boundaries.')
}


# aggregation keywords
global_default_attribute = {
    'id': 'Global default',
    'name': tr('Global default')
}

do_not_use_attribute = {
    'id': 'Don\'t use',
    'name': tr('Don\'t use')
}


# Converter new keywords to old keywords
converter_dict = {
    'subcategory': {
        'all': [],
        'earthquake': [],
        'flood': [],
        'population': [],
        'road': [],
        'structure': [],
        'tephra': [],
        'tsunami': [],
        'volcano': []
    },
    'layertype': {
        'raster': [],
        'vector': []
    },
    'data_type': {
    },
    'unit': {
        'm': ['metres_depth'],  # FIXME(Ismail): Please check for feet_depth
        'MMI': ['mmi'],
    }
}


def old_to_new_unit_id(old_unit_id):
    """Convert old unit id to new unit id in keyword system.

    :param old_unit_id: Unit id in old keyword system.
    :type old_unit_id: str

    :returns: Unit id in new keyword system.
    :rtype: str
    """

    # These converter is used for wizard only, converting old keywords to new
    # keywords as default value when run the wizard.
    old_to_new_keywords = {
        'm': 'metres_depth',
        'mmi': 'MMI'
    }

    return old_to_new_keywords.get(old_unit_id, old_unit_id)
