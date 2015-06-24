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
    'name': tr('Hazard'),
    'description': tr(
        'A <b>hazard</b> layer represents '
        'something that will impact on the people, infrastructure or  '
        'land cover in an area. For example; flood, earthquake, tsunami and '
        'volcano are all examples of hazards.')
}
layer_purpose_exposure = {
    'key': 'exposure',
    'name': tr('Exposure'),
    'description': tr(
        'An <b>exposure</b> layer represents '
        'people, property, infrastructure or land cover that may be affected '
        'in the event of a flood, earthquake, volcano etc.')
}
layer_purpose_aggregation = {
    'key': 'aggregation',
    'name': tr('Aggregation'),
    'description': tr(
        'An <b>aggregation</b> layer represents '
        'regions that can be used to summarise impact analysis results. '
        'For example, we might summarise the affected people after '
        'a flood according to administration boundaries.')
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
    'name': tr('Continuous'),
    'description': tr(
        '<b>Continuous</b> data can be used in raster hazard or exposure data '
        'where the values in the data are are either integers or decimal  '
        'values representing a continuously varying phenomenon. '
        'For example flood depth is a continuous value from 0 to the maximum '
        'reported depth during a flood. '
        'Raster data is considered to be continuous by default and you '
        'should explicitly indicate that it is classified if each cell in the '
        'raster represents a discrete class (e.g. low depth = 1, medium depth '
        '= 2, high depth = 3).'),
}
layer_mode_classified = {
    'key': 'classified',
    'name': tr('Classified'),
    'description': tr(
        '<b>Classified</b> data can be used for either hazard or exposure '
        'data and can be used for both raster and vector layer types where '
        'the attribute values represent a classified or coded value. '
        'For example, classified values in a flood raster data set might '
        'represent discrete classes where a value of 1 might represent the '
        'low inundation class, a value of 2 might represent the medium '
        'inundation class and a value of 3 might represent the '
        'high inundation class.'
        'Classified values in a vector Volcano data set might represent '
        'discrete clases where a value of I might represent low volcanic '
        'hazard, a value of II might represent medium volcanic hazard and '
        'a value of III  might represent a high volcanic hazard. '
    ),
}

layer_mode = {
    'key': 'layer_mode',
    'name': tr('Layer Mode'),
    'description': tr(
        'The mode of the layer describes the type of data value in the layer. '
        'It can be continuous or classified'),
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
        '(for a hazard) or building footprints represented as polygons '
        '(for an exposure). The polygon layer will often need the presence '
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
        'A raster data layer consists of a matrix of cells organised into '
        'rows and columns. The value in the cells represents information such '
        'as a flood depth value or a hazard class. ')
}

layer_geometry = {
    'key': 'layer_geometry',
    'name': tr('Layer Geometry'),
    'description': tr(
        'This describes the format and type of the layer. There '
        'are four possible values : raster, point, line, and polygon. The '
        'last three values are implicitly included in the vector format.'),
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
        'A <b>single hazard event</b> can be based on either a specific event '
        'that has happened in the past, for example a flood like Jakarta '
        '2013, or a possible event such as the tsunami that results from an '
        'earthquake near Bima that might happen in the future.')
}

hazard_category_multiple_event = {
    'key': 'multiple_event',
    'name': tr('Multiple Event'),
    'description': tr(
        'A <b>multiple hazard event</b> data can be based on historical '
        'observations such as a hazard map of all observed volcanic '
        ' deposits around a volcano. '
        'This type of hazard data shows those locations that might be '
        'impacted by a volcanic eruption in the future . Another example '
        'might be a probabilistic hazard model that shows the likelihood of a '
        'magnitude 7 earthquake happening in the next 50 yrs.')
}

hazard_category = {
    'key': 'hazard_category',
    'name': tr('Hazard Category'),
    'description': tr(
        'This describes the category of the hazard that is represented by the '
        'layer. There are two possible values for this attribute, single '
        'event and multiple event.'),
    'types': [
        hazard_category_single_event,
        hazard_category_multiple_event
    ]
}

# Hazard
hazard_generic = {
    'key': 'generic',
    'name': tr('Generic'),
    'description': tr(
        'A <b>generic hazard</b> can be used for any type of hazard where the '
        'data have been classified or generalised. For example: earthquake, '
        'flood, volcano, or tsunami.')
}

hazard_earthquake = {
    'key': 'earthquake',
    'name': tr('Earthquake'),
    'description': tr(
        'An <b>earthquake</b> describes the sudden violent shaking of the '
        'ground that occurs as a result of volcanic activity or movement '
        'in the earth\'s crust.')
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
        'to become wet.')
}

hazard_volcanic_ash = {
    'key': 'volcanic_ash',
    'name': tr('Volcanic Ash'),
    'description': tr(
        '<b>Volcanic ash</b> describes fragments of pulverized rock, minerals '
        'and volcanic glass, created during volcanic eruptions, less than '
        '2 mm (0.079 inches) in diameter')
}

hazard_tsunami = {
    'key': 'tsunami',
    'name': tr('Tsunami'),
    'description': tr(
        'A <b>tsunami</b> describes a large ocean wave or series or '
        'waves usually caused by an under water earthquake or volcano.'
        'A <b>tsunami</b> at sea may go unnoticed but a <b>tsunami</b> '
        'wave that strikes land may cause massive destruction and '
        'flooding.')
}

hazard_volcano = {
    'key': 'volcano',
    'name': tr('Volcano'),
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
    'name': tr('Land Cover'),
    'description': tr(
        'The <b>land cover</b> exposure data describes features on '
        'the surface of the earth that might be exposed to a particular '
        ' hazard. This might include crops, forest and urban areas. ')
}

exposure_people_in_building = {
    'key': 'people_in_building',
    'name': tr('People in Buildings'),
    'description': tr(
        'The <b>people in buildings</b> exposure data is an experimental '
        'data set that assigns the population of a specific administrative '
        'area to the buildings with a residential function in that area.'
        'The process of assigning people to buildings assumes that all people '
        'and buildings in the area are mapped. There are no InaSAFE impact '
        'functions that use this exposure data yet.')
}

exposure_population = {
    'key': 'population',
    'name': tr('Population'),
    'description': tr(
        'The <b>population</b> describes the people that might be '
        'exposed to a particular hazard.')
}

exposure_road = {
    'key': 'road',
    'name': tr('Road'),
    'description': tr(
        'A <b>road</b> is a defined route used by a vehicle or people to '
        'travel between two or more points.')
}

exposure_structure = {
    'key': 'structure',
    'name': tr('Structure'),
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
    'name': tr('Feet'),
    'description': tr(
        '<b>Feet</b> are an imperial unit of measure. There are 12 '
        'inches in 1 foot and 3 feet in 1 yard.'),
}

unit_generic = {
    'key': 'generic',
    'name': tr('Generic'),
    'description': tr(
        'A generic unit for value that does not have unit or we do not know '
        'about the unit. It also can be used for normalised values.'),
    }

unit_kilogram_per_meter_square = {
    'key': 'kilogram_per_meter_square',
    'name': tr('Kg/m2'),
    'description': tr(
        '<b>Kilograms per square metre</b> is a metric unit of measure where '
        'the weight is specified according to area.  This unit is relevant '
        'for hazards such as volcanic ash.')
}

unit_kilometres = {
    'key': 'kilometres',
    'name': tr('Kilometres'),
    'description': tr(
        '<b>Kilometres</b> are a metric unit of measure. There are 1000 '
        'metres in 1 kilometre (km).'),
    }

unit_metres = {
    'key': 'metres',
    'name': tr('Metres'),
    'description': tr(
        '<b>Metres</b> are a metric unit of measure. There are 100 '
        'centimetres in 1 meter.'),
}

unit_millimetres = {
    'key': 'millimetres',
    'name': tr('Millimetres'),
    'description': tr(
        '<b>Millimetres</b> are a metric unit of measure. There are 1000 '
        'millimetres in 1 metre.'),
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
        'Continuous hazard unit is the unit used for continuous layer mode.'),
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
    'name': tr('Generic classes'),
    'description': tr(
        'This is a ternary description for an area. The area may have either '
        '<b>low</b>, <b>medium</b>, or <b>high</b> impact from the '
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
    'name': tr('Volcano classes'),
    'description': tr(
        'This is a ternary description for an area. The area has either a '
        '<b>low</b>, <b>medium</b>, or <b>high</b> classification for '
        'volcano hazard.'),
    'default_attribute': 'affected',
    'default_class': 'high',  # unclassified value will go to this class
    'classes': [
        {
            'key': 'high',
            'name': tr('high'),
            'description': tr('The highest hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana III', 'high'],
            'numeric_default_min': 0,
            'numeric_default_max': (3 - small_number),
            'optional': False
        },
        {
            'key': 'medium',
            'name': tr('medium'),
            'description': tr('The medium hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana II', 'medium'],
            'numeric_default_min': 3,
            'numeric_default_max': (5 - small_number),
            'optional': False
        },
        {
            'key': 'low',
            'name': tr('low'),
            'description': tr('The lowest hazard class.'),
            'string_defaults': ['Kawasan Rawan Bencana I', 'low'],
            'numeric_default_min': 5,
            'numeric_default_max': 10,
            'optional': False
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
        'the attributes or fields in a vector layer.'),
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
    'name': tr('Flood classes'),
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
    'name': tr('Generic classes'),
    'description': tr(
        'This is a ternary description for an area. The area is classified as '
        'either a <b>low</b>, <b>medium</b>, or <b>high</b> hazard class.'),
    'default_class': 'high',  # unclassified value will go to this class
    'classes': [
        {
            'key': 'high',
            'name': tr('high'),
            'description': tr('The highest hazard classification.'),
            'numeric_default_min': 3,
            'numeric_default_max': 3,
            'optional': False
        },
        {
            'key': 'medium',
            'name': tr('medium'),
            'description': tr('The medium hazard classification.'),
            'numeric_default_min': 2,
            'numeric_default_max': 2,
            'optional': False
        },
        {
            'key': 'low',
            'name': tr('low'),
            'description': tr('The lowest hazard classification.'),
            'numeric_default_min': 1,
            'numeric_default_max': 1,
            'optional': False
        }
    ]
}

tsunami_raster_hazard_classes = {
    'key': 'tsunami_raster_hazard_classes',
    'name': tr('Tsunami classes'),
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
        'Raster Hazard Classification is a way to classify the cell values '
        'in a raster layer.'),
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

# Exposure class field
structure_class_field = {
    'key': 'structure_class_field',
    'name': tr('Structure class field'),
    'description': tr('Field where the structure type is defined.')
}

road_class_field = {
    'key': 'road_class_field',
    'name': tr('Road class field'),
    'description': tr('Field where the road type is defined.')
}

# Additional keywords
# Hazard related
volcano_name_field = {
    'key': 'volcano_name_field',
    'name': tr('Volcano name field'),
    'type': 'field',
    'description': tr('Field where the volcano name is located.')
}
