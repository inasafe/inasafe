# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**New Metadata for SAFE.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '13/04/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# Please group them and sort them alphabetical
from safe.utilities.i18n import tr

# constants
small_number = 2 ** -53  # I think this is small enough

# Aggregation keywords
global_default_attribute = {
    'id': 'Global default',
    'name': tr('Global default')
}

do_not_use_attribute = {
    'id': 'Don\'t use',
    'name': tr('Don\'t use')
}

# Layer Purpose
layer_purpose_hazard = {
    'key': 'hazard',
    'name': tr('hazard'),
    'description': tr(
        'A <b>hazard</b> layer represents '
        'something that will impact on the people or infrastructure '
        'in an area. For example; flood, earthquake, tsunami and  '
        'volcano are all examples of hazards.')
}
layer_purpose_exposure = {
    'key': 'exposure',
    'name': tr('exposure'),
    'description': tr(
        'An <b>exposure</b> layer represents '
        'people, property or infrastructure that may be affected '
        'in the event of a flood, earthquake, volcano etc.')
}
layer_purpose_aggregation = {
    'key': 'aggregation',
    'name': tr('aggregation'),
    'description': tr(
        'An <b>aggregation</b> layer represents '
        'regions you can use when summarise analysis results. For '
        'example, we might summarise the affected people after'
        'a flood according to city districts.')
}

layer_purpose = {
    'key': 'layer_purpose',
    'name': tr('Layer Purpose'),
    'description': tr(
        'The purpose of the layer can be hazard layer, exposure layer, or '
        'aggregation layer'),
    'types': [
        layer_purpose_hazard,
        layer_purpose_exposure,
        layer_purpose_aggregation
    ]
}

# Layer mode
layer_mode_continuous = {
    'key': 'continuous',
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
}
layer_mode_classified = {
    'key': 'classified',
    'name': tr('classified'),
    'description': tr(
        '<b>Classified</b> data can be hazard data where the '
        'values have been classified or coded such that each raster cell '
        'represents a discrete class. For example if the raster represents '
        'a flood layer, permissible cell values may be 1, 2, 3 where 1 '
        'represents low water, 2 represents medium inundation and 3 '
        'represents high inundation.'
    ),
}

layer_mode_none = {
    'key': 'none',
    'name': tr('none'),
    'description': tr(
        'Layer mode <b>None</b> means that the layer is not continuous or '
        'classified. All vector features regardless of their attributes or '
        'all raster non-null cells regardess of their values have the '
        'same meaning.'
    )
}

layer_mode = {
    'key': 'layer_mode',
    'name': tr('Layer Mode'),
    'description': tr(
        'The mode of the layer describe the type of the value of the layer '
        'data. It can be continuous or classified'),
    'types': [
        layer_mode_continuous,
        layer_mode_classified
    ]
}

# Layer Geometry
layer_geometry_point = {
    'key': 'point',
    'name': tr('Point'),
    'description': tr(
        'A layer composed of points which each represent a feature on the '
        'earth. Currently the only point data supported by InaSAFE are '
        '<b>volcano hazard</b> layers.')
}

layer_geometry_line = {
    'key': 'line',
    'name': tr('Line'),
    'description': tr(
        'A layer composed of linear features. Currently only <b>road exposure'
        '</b>line layers are supported by InaSAFE.')
}

layer_geometry_polygon = {
    'key': 'polygon',
    'name': tr('Polygon'),
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

layer_geometry_raster = {
    'key': 'raster',
    'name': tr('Raster'),
    'description': tr(
        'A raster data type is, in essence, any type of digital image '
        'represented by reducible and enlargeable grids.')
}

layer_geometry = {
    'key': 'layer_geometry',
    'name': tr('Layer Geometry'),
    'description': tr(
        'This describes which format of the layer, and the type of it. There '
        'are four possible values : raster, point, line, and polygon. The '
        'last three values are implicitly included in vector format.'),
    'types': [
        layer_geometry_raster,
        layer_geometry_point,
        layer_geometry_line,
        layer_geometry_polygon
    ]
}

# Hazard Category
hazard_category_single_event = {
    'key': 'single_event',
    'name': tr('Single Event'),
    'description': tr(
        'TBA')
}

hazard_category_multiple_event = {
    'key': 'multiple_event',
    'name': tr('Multiple Event'),
    'description': tr(
        'TBA')
}

hazard_category = {
    'key': 'hazard_category',
    'name': tr('Hazard Category'),
    'description': tr(
        'This describes which category of the hazard that represented by the '
        'layer. There are two possible values for this attribute, hazard '
        'scenario and hazard zone.'),
    'types': [
        hazard_category_single_event,
        hazard_category_multiple_event
    ]
}

# Hazard
hazard_generic = {
    'key': 'generic',
    'name': tr('generic'),
    'description': tr(
        'A generic hazard can be used for any type of hazard where the data '
        'have been classified or generalised. For example: earthquake, flood, '
        'volcano, or tsunami.')
}

hazard_earthquake = {
    'key': 'earthquake',
    'name': tr('earthquake'),
    'description': tr(
        'An <b>earthquake</b> describes the sudden violent shaking of the '
        'ground that occurs as a result of volcanic activity or movement '
        'in the earth\'s crust.')
}

hazard_flood = {
    'key': 'flood',
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
    'key': 'volcanic_ash',
    'name': tr('volcanic ash'),
    'description': tr(
        '<b>Volcanic ash</b> describes fragments of pulverized rock, minerals '
        'and volcanic glass, created during volcanic eruptions, less than '
        '2 mm (0.079 inches) in diameter')
}

hazard_tsunami = {
    'key': 'tsunami',
    'name': tr('tsunami'),
    'description': tr(
        'A <b>tsunami</b> describes a large ocean wave or series or '
        'waves usually caused by an under water earthquake or volcano.'
        'A <b>tsunami</b> at sea may go unnoticed but a <b>tsunami</b> '
        'wave that strikes land may cause massive destruction and '
        'flooding.')
}

hazard_volcano = {
    'key': 'volcano',
    'name': tr('volcano'),
    'description': tr(
        'A <b>volcano</b> describes a mountain which has a vent through '
        'which rock fragments, ash, lava, steam and gases can be ejected '
        'from below the earth\'s surface. The type of material '
        'ejected depends on the type of <b>volcano</b>.')
}

hazard_all = [
    hazard_flood,
    hazard_tsunami,
    hazard_earthquake,
    hazard_volcano,
    hazard_volcanic_ash,
    hazard_generic
]

hazard = {
    'key': 'hazard',
    'name': tr('Hazard'),
    'description': tr(
        '<b>Hazards</b> (also called disasters) are what we call the data '
        'layers that describe the extent and magnitude of natural events '
        '(such as earthquakes, tsunamis and volcanic eruptions) that could '
        'potentially cause an event or series of events that threaten and '
        'disrupt the lives and livelihoods of people.'),
    'types': [
        hazard_flood,
        hazard_tsunami,
        hazard_earthquake,
        hazard_volcano,
        hazard_volcanic_ash,
        hazard_generic
    ]
}

# Exposure
exposure_land_cover = {
    'key': 'land_cover',
    'name': tr('land_cover'),
    'description': tr(
        'TBA')
}

exposure_people_in_building = {
    'key': 'people_in_building',
    'name': tr('people_in_building'),
    'description': tr(
        'TBA')
}

exposure_population = {
    'key': 'population',
    'name': tr('population'),
    'description': tr(
        'The <b>population</b> describes the people that might be '
        'exposed to a particular hazard.')
}

exposure_road = {
    'key': 'road',
    'name': tr('road'),
    'description': tr(
        'A <b>road</b> is a defined route used by a vehicle or people to '
        'travel between two or more points.')
}

exposure_structure = {
    'key': 'structure',
    'name': tr('structure'),
    'description': tr(
        'A <b>structure</b> can be any relatively permanent man '
        'made feature such as a building (an enclosed structure '
        'with walls and a roof) or a telecommunications facility or a '
        'bridge.')
}

exposure_all = [
    exposure_land_cover,
    exposure_people_in_building,
    exposure_population,
    exposure_road,
    exposure_structure
]

exposure = {
    'key': 'exposure',
    'name': tr('Exposure'),
    'description': tr(
        '<b>Exposure</b> data represents things that are at risk when faced '
        'with a potential hazard. '),
    'types': [
        exposure_land_cover,
        exposure_people_in_building,
        exposure_population,
        exposure_road,
        exposure_structure
    ]
}

# Continuous Hazard Unit
unit_feet = {
    'key': 'feet',
    'name': tr('feet'),
    'description': tr(
        '<b>Feet</b> are an imperial unit of measure. There are 12 '
        'inches in 1 foot and 3 feet in 1 yard.'),
}

unit_generic = {
    'key': 'generic',
    'name': tr('generic'),
    'description': tr(
        'A generic unit for value that does not have unit or we do not know '
        'about the unit. It also can be used for normalised values.'),
    }

unit_kilogram_per_meter_square = {
    'key': 'kilogram_per_meter_square',
    'name': tr('kg/m2'),
    'description': tr(
        'TBA'),
    }

unit_kilometres = {
    'key': 'kilometres',
    'name': tr('kilometres'),
    'description': tr(
        '<b>kilometres</b> are a metric unit of measure. There are 1000 '
        'metres in 1 kilometer (km).'),
    }

unit_metres = {
    'key': 'metres',
    'name': tr('metres'),
    'description': tr(
        '<b>metres</b> are a metric unit of measure. There are 100 '
        'centimetres in 1 meter.'),
}

unit_millimetres = {
    'key': 'millimetres',
    'name': tr('millimetres'),
    'description': tr(
        '<b>metres</b> are a metric unit of measure. There are 1000 '
        'millimetres in 1 meter.'),
    }

unit_mmi = {
    'key': 'mmi',
    'name': tr('MMI'),
    'description': tr(
        'The <b>Modified Mercalli Intensity (MMI)</b> scale describes '
        'the intensity of ground shaking from a earthquake based on the '
        'effects observed by people at the surface.'),
}

continuous_hazard_unit = {
    'key': 'continuous_hazard_unit',
    'name': tr('Continuous Hazard Unit'),
    'description': tr(
        'Continuous hazard unit represent unit for continuous layer mode.'),
    'types': [
        unit_feet,
        unit_generic,
        unit_kilogram_per_meter_square,
        unit_kilometres,
        unit_metres,
        unit_millimetres,
        unit_mmi
    ]
}

continuous_hazard_unit_all = continuous_hazard_unit['types']

# Vector Hazard Classification
generic_vector_hazard_classes = {
    'key': 'generic_vector_hazard_classes',
    'name': tr('generic vector hazard classes'),
    'description': tr(
        'This is a ternary description for an area. The area is either '
        'has <b>low</b>, <b>medium</b>, or <b>high</b> impact from the '
        'hazard.'),
    'default_attribute': 'affected',
    'default_class': 'high',  # unclassified value will go to this class
    'classes': [
        {
            'key': 'high',
            'name': tr('high'),
            'description': tr('The location that has highest impact.'),
            'string_defaults': ['high'],
            'numeric_default_min': 5,
            'numeric_default_max': 10,
            'optional': False
        },
        {
            'key': 'medium',
            'name': tr('medium'),
            'description': tr('The location that has medium impact.'),
            'string_defaults': ['medium'],
            'numeric_default_min': 3,
            'numeric_default_max': (5 - small_number),
            'optional': False
        },
        {
            'key': 'low',
            'name': tr('low'),
            'description': tr('The location that has lowest impact.'),
            'string_defaults': ['low'],
            'numeric_default_min': 0,
            'numeric_default_max': (3 - small_number),
            'optional': False
        }
    ]
}

volcano_vector_hazard_classes = {
    'key': 'volcano_vector_hazard_classes',
    'name': tr('volcano vector hazard classes'),
    'description': tr(
        'This is a ternary description for an area. The area is either '
        'has <b>low</b>, <b>medium</b>, or <b>high</b> impact from the '
        'volcano.'),
    'default_attribute': 'affected',
    'default_class': 'high',  # unclassified value will go to this class
    'classes': [
        {
            'key': 'high',
            'name': tr('high'),
            'description': tr('The location that has highest impact.'),
            'string_defaults': ['Kawasan Rawan Bencana III', 'high'],
            'numeric_default_min': 0,
            'numeric_default_max': (3 - small_number),
            'optional': False
        },
        {
            'key': 'medium',
            'name': tr('medium'),
            'description': tr('The location that has medium impact.'),
            'string_defaults': ['Kawasan Rawan Bencana II', 'medium'],
            'numeric_default_min': 3,
            'numeric_default_max': (5 - small_number),
            'optional': False
        },
        {
            'key': 'low',
            'name': tr('low'),
            'description': tr('The location that has lowest impact.'),
            'string_defaults': ['Kawasan Rawan Bencana I', 'low'],
            'numeric_default_min': 5,
            'numeric_default_max': 10,
            'optional': False
        }
    ]
}

flood_vector_hazard_classes = {
    'key': 'flood_vector_hazard_classes',
    'name': tr('flood vector hazard classes'),
    'description': tr(
        'This is a binary description for an area. The area is either '
        '<b>wet</b> (affected by flood water) or <b>dry</b> (not affected '
        'by flood water). This unit does not describe how <b>wet</b> or '
        '<b>dry</b> an area is.'),
    'default_attribute': 'affected',
    'default_class': 'wet',
    'classes': [
        {
            'key': 'wet',
            'name': tr('wet'),
            'description': tr('Water above ground height.'),
            'string_defaults': ['wet', '1', 'YES', 'y', 'yes'],
            'numeric_default_min': 1,
            'numeric_default_max': 9999999999,
            'optional': True
        },
        {
            'key': 'dry',
            'name': tr('dry'),
            'description': tr('No water above ground height.'),
            'string_defaults': ['dry', '0', 'No', 'n', 'no'],
            'numeric_default_min': 0,
            'numeric_default_max': (1 - small_number),
            'optional': True
        }
    ]
}

vector_hazard_classification = {
    'key': 'vector_hazard_classification',
    'name': tr('Vector Hazard Classification'),
    'description': tr(
        'Vector Hazard Classification is a way to classify a value in one of '
        'the attribute or field in vector layer.'),
    'types': [
        generic_vector_hazard_classes,
        volcano_vector_hazard_classes,
        flood_vector_hazard_classes
    ]
}

all_vector_hazard_classes = vector_hazard_classification['types']

# Raster Hazard Classification
flood_raster_hazard_classes = {
    'key': 'flood_raster_hazard_classes',
    'name': tr('flood raster hazard classes'),
    'description': tr(
        'This is a binary description for an area. The area is either '
        '<b>wet</b> (affected by flood water) or <b>dry</b> (not affected '
        'by flood water). This unit does not describe how <b>wet</b> or '
        '<b>dry</b> an area is.'),
    'default_class': 'dry',  # unclassified value will go to this class
    'classes': [
        {
            'key': 'wet',
            'name': tr('wet'),
            'description': tr('Water above ground height.'),
            'numeric_default_min': 1,
            'numeric_default_max': 9999999999,
            'optional': True
        },
        {
            'key': 'dry',
            'name': tr('dry'),
            'description': tr('No water above ground height.'),
            'numeric_default_min': 0,
            'numeric_default_max': (1 - small_number),
            'optional': True
        }
    ]
}

generic_raster_hazard_classes = {
    'key': 'generic_raster_hazard_classes',
    'name': tr('generic raster hazard classes'),
    'description': tr(
        'This is a ternary description for an area. The area is either '
        'has <b>low</b>, <b>medium</b>, or <b>high</b> impact from the '
        'hazard.'),
    'default_class': 'high',  # unclassified value will go to this class
    'classes': [
        {
            'key': 'high',
            'name': tr('high'),
            'description': tr('The location that has highest impact.'),
            'numeric_default_min': 3,
            'numeric_default_max': 3,
            'optional': False
        },
        {
            'key': 'medium',
            'name': tr('medium'),
            'description': tr('The location that has medium impact.'),
            'numeric_default_min': 2,
            'numeric_default_max': 2,
            'optional': False
        },
        {
            'key': 'low',
            'name': tr('low'),
            'description': tr('The location that has lowest impact.'),
            'numeric_default_min': 1,
            'numeric_default_max': 1,
            'optional': False
        }
    ]
}

tsunami_raster_hazard_classes = {
    'key': 'tsunami_raster_hazard_classes',
    'name': tr('tsunami raster hazard classes'),
    'description': tr(
        'This is a binary description for an area. The area is either '
        '<b>wet</b> (affected by tsunami) or <b>dry</b> (not affected '
        'by tsunami). This unit does not describe how <b>wet</b> or '
        '<b>dry</b> an area is.'),
    'default_class': 'dry',  # unclassified value will go to this class
    'classes': [
        {
            'key': 'wet',
            'name': tr('wet'),
            'description': tr('Water above ground height.'),
            'numeric_default_min': 1,
            'numeric_default_max': 9999999999,
            'optional': True
        },
        {
            'key': 'dry',
            'name': tr('dry'),
            'description': tr('No water above ground height.'),
            'numeric_default_min': 0,
            'numeric_default_max': (1 - small_number),
            'optional': True
        }
    ]
}

raster_hazard_classification = {
    'key': 'raster_hazard_classification',
    'name': tr('Raster Hazard Classification'),
    'description': tr(
        'Raster Hazard Classification is a way to classify a value in each '
        'cell in raster layer.'),
    'types': [
        flood_raster_hazard_classes,
        generic_raster_hazard_classes,
        tsunami_raster_hazard_classes
    ]
}

all_raster_hazard_classes = raster_hazard_classification['types']

# Exposure Unit
count_exposure_unit = {
    'key': 'count',
    'name': tr('Count'),
    'description': tr(
        'Number of people (or any other object) per pixel or building.')
}

density_exposure_unit = {
    'key': 'density',
    'name': tr('Density'),
    'description': tr(
        'Density of people (or any other object) per cell.')
}

exposure_unit = {
    'key': 'exposure_unit',
    'name': tr('Exposure Unit'),
    'description': tr(
        'Exposure unit defines what is the unit for the exposure, for example '
        'people can have count unit or density unit.'),
    'types': [
        count_exposure_unit,
        density_exposure_unit
    ]
}

# Additional keywords
# Hazard related
hazard_zone_field = {
    'key': 'hazard_zone_field',
    'type': 'field',
    'master_keyword': None,
    'description': tr('Field where the hazard zone value is located.')
}

affected_field = {
    'key': 'affected_field',
    'type': 'field',
    'master_keyword': None,
    'description': tr('Field where the affected value is located.')
}

affected_value = {
    'key': 'affected_value',
    'type': 'value',
    'master_keyword': affected_field,
    'description': tr('Value for affected field.')
}

volcano_name_field = {
    'key': 'volcano_name_field',
    'type': 'field',
    'master_keyword': None,
    'description': tr('Field where the volcano name is located.')
}

# Exposure related
building_type_field = {
    'key': 'building_type_field',
    'type': 'field',
    'master_keyword': None,
    'description': tr('Field where the building type is located.')
}

road_type_field = {
    'key': 'road_type_field',
    'type': 'field',
    'master_keyword': None,
    'description': tr('Field where the building type is located.')
}
