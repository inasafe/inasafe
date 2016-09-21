# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**InaSAFE Post Processors Definitions**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from utilities.i18n import tr

__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '22/09/16'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

population_field = {
    'key': 'population_field',
    'name': tr('Population field'),
    'default_field': 'population',
    'type': int,
    'description': tr('Attribute where the number of population is located.'),
    'layer': 'exposure',
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
gender_ratio_field = {
    'key': 'gender_ratio_field',
    'name': tr('Gender Ratio field'),
    'default_field': 'gender_ratio',
    'type': float,
    'description': tr('Attribute where the ratio of women is located.'),
    'layer': 'aggregation',
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
value_field = {
    'key': 'value_field',
    'name': tr('Value field'),
    'default_field': 'value',
    'type': float,
    'description': tr('Attribute where the value of the feature is located.'),
    'layer': 'exposure',
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
women_field = {
    'key': 'women_field',
    'name': tr('Women field'),
    'default_field': 'women',
    'type': int,
    'description': tr(
        'Attribute where the number of women of the feature is located.'),
    'layer': 'impact',
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
post_processor_gender = {
    'key': 'post_processor_gender',
    'name': tr('Gender Post Processor'),
    'description': tr(
        'Post processor to calculate the number of affected woman'),
    'input': {
        'population': {
            'field': population_field,
            # We can add something later, like mandatory requirement, another
            #  source of input (e.g. parameter)
        },
        'gender_ratio': {
            'field': gender_ratio_field,
        }
    },
    'output': {
        'women': {
            'field': women_field,
            'formula': 'population * gender_ratio'
        }
    }
}
post_processor_value = {
    'key': 'post_processor_value',
    'name': tr('Value Post Processor'),
    'description': tr(
        'Post processor to calculate the value of a feature. A feature should '
        'have a value field.'),
    'input': {
        'value': {
            'field': value_field
        }
    },
    'output': {
        'value_field': {
            # No need to do anything. TODO: How?
        }
    }
}
post_processors = [
    post_processor_gender,
    post_processor_value
]