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
from safe.definitionsv4.units import (
    unit_feet,
    unit_centimetres,
    unit_generic,
    unit_kilometres,
    unit_kilogram_per_meter_square,
    unit_millimetres,
    unit_metres,
    unit_percentage,
    unit_mmi,
    count_exposure_unit,
    density_exposure_unit,
    unit_metres)


from safe.definitionsv4.exposure_definitions import *

__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '13/04/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

inasafe_keyword_version_key = 'keyword_version'
inasafe_keyword_version = '3.5'

# InaSAFE Keyword Version compatibility.
keyword_version_compatibilities = {
    # 'InaSAFE keyword version': 'List of supported InaSAFE keyword version'
    '3.3': ['3.2'],
    '3.4': ['3.2', '3.3'],
    '3.5': ['3.4', '3.3']
}

# constants
small_number = 2 ** -53  # I think this is small enough

# No data warnings for appending to actions if
# nulls were encountered in rasters
no_data_warning = [
    tr(
        'The layers contained "no data" values. This missing data '
        'was carried through to the impact layer.'),
    tr(
        '"No data" values in the impact layer were treated as 0 '
        'when counting the affected or total population.')
]

# Aggregation keywords
global_default_attribute = {
    'id': 'Global default',
    'name': tr('Global default')
}

do_not_use_attribute = {
    'id': 'Don\'t use',
    'name': tr('Don\'t use')
}

# Hazard Category
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

# Renamed key from exposure to exposures in 3.2 because key was not unique TS
exposures = {
    'key': 'exposures',
    'name': tr('Exposure'),
    'description': concepts['exposure']['description'],
    'citations': concepts['exposure']['citations'],
    'types': exposure_all,
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

# Exposure class field
structure_class_field = {
    'key': 'structure_class_field',
    'name': tr('Attribute field'),
    'description': tr('Attribute where the structure type is defined.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

road_class_field = {
    'key': 'road_class_field',
    'name': tr('Attribute field'),
    'description': tr('Attribute where the road type is defined.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

# Additional keywords
# Hazard related
volcano_name_field = {
    'key': 'volcano_name_field',
    'name': tr('Name field'),
    'type': 'field',
    'description': tr('Attribute where the volcano name is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

area_name_field = {
    'key': 'area_name_field',
    'name': tr('Name field'),
    'type': 'field',
    'description': tr(
            'Attribute for the area name. We will show the name for each area '
            'by using this attribute.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

area_id_field = {
    'key': 'area_id_field',
    'name': tr('Id field'),
    'type': 'field',
    'description': tr(
            'Attribute for the id on the area. We will group the result by '
            'this attribute'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

# General terminology and descriptive terms

field = {
    'key': 'field',
    'name': tr('Attribute field'),
    'description': tr(
        'The attribute field identifies a field in the attribute table used '
        'to identify the function of a feature e.g.  a road type, '
        'building type, hazard zone etc.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

field_value = {
    'key': 'field_value',
    'name': tr('Attribute value'),
    'description': tr(
        'The attribute value identifies features with similar meanings. For '
        'example building attributes may include schools and hospitals. '),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

value_map = {
    'key': 'value_map',
    'name': tr('Attribute value map'),
    'description': tr(
        'Attribute value maps are used to group related attribute '
        'values. For example flooded polygons with attribute values of "yes" '
        ', "YES", "1" and "Flooded" might all be grouped together as '
        '"FLOODPRONE".'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

multipart_polygon_key = 'multipart_polygon'
