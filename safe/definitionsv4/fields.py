"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**InaSAFE Field Definitions**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

from utilities.i18n import tr
__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '21/09/16'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# Exposure
# Exposure ID
exposure_id_field = {
    'key': 'exposure_id_field',
    'name': tr('Exposure ID'),
    'field_name': 'exp_id',
    'type': int,
    'description': tr(
        'Attribute where the exposure ID of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Feature Type
feature_type_field = {
    'key': 'feature_type_field',
    'name': tr('Feature Type'),
    'field_name': 'feature_type',
    'type': str,
    'description': tr(
        'Attribute where the type of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Population Count
population_count_field = {
    'key': 'population_count_field',
    'name': tr('Population count'),
    'field_name': 'population',
    'type': int,
    'description': tr('Attribute where the number of population is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Feature Value
feature_value_field = {
    'key': 'feature_value_field',
    'name': tr('Feature Value'),
    'field_name': 'exp_value',
    'type': float,
    'description': tr('Attribute where the value of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Feature Rate
feature_rate_field = {
    'key': 'feature_rate_field',
    'name': tr('Feature Rate'),
    'field_name': 'exp_rate',
    'type': float,
    'description': tr(
        'Attribute where the rate value of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

# Hazard
# Hazard ID
hazard_id_field = {
    'key': 'hazard_id_field',
    'name': tr('Hazard ID'),
    'field_name': 'haz_id',
    'type': int,
    'description': tr(
        'Attribute where the hazard ID of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Hazard Value
hazard_value_field = {
    'key': 'hazard_value_field',
    'name': tr('Hazard Value'),
    'field_name': 'haz_value',
    'type': [str, int, float],
    'description': tr(
        'Attribute where the hazard value of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

# Aggregation
# Aggregation ID
aggregation_id_field = {
    'key': 'aggregation_id_field',
    'name': tr('Aggregation ID'),
    'field_name': 'agg_id',
    'type': int,
    'description': tr(
        'Attribute where the aggregation ID of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Aggregation Name
aggregation_name_field = {
    'key': 'aggregation_name_field',
    'name': tr('Aggregation Name'),
    'field_name': 'agg_name',
    'type': str,
    'description': tr(
        'Attribute where the aggregation name of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Gender Ratio
gender_ratio_field = {
    'key': 'gender_ratio_field',
    'name': tr('Gender Ratio'),
    'field_name': 'gender_r',
    'type': float,
    'description': tr('Attribute where the ratio of women is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Youth Ratio
youth_ratio_field = {
    'key': 'youth_ratio_field',
    'name': tr('Youth Ratio'),
    'field_name': 'youth_r',
    'type': float,
    'description': tr('Attribute where the ratio of youth people is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Adult Ratio
adult_ratio_field = {
    'key': 'adult_ratio_field',
    'name': tr('Adult Ratio'),
    'field_name': 'adult_r',
    'type': float,
    'description': tr('Attribute where the ratio of adult people is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# elderly Ratio
elderly_ratio_field = {
    'key': 'elderly_ratio_field',
    'name': tr('Elderly Ratio'),
    'field_name': 'elderly_r',
    'type': float,
    'description': tr(
        'Attribute where the ratio of elderly people is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

# Impact
# Exposure Class
exposure_class_field = {
    'key': 'exposure_class_field',
    'name': tr('Exposure Class'),
    'field_name': 'exp_class',
    'type': str,
    'description': tr(
        'Attribute where the exposure class of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Hazard Class
hazard_class_field = {
    'key': 'hazard_class_field',
    'name': tr('Hazard Class'),
    'field_name': 'haz_class',
    'type': str,
    'description': tr(
        'Attribute where the hazard class of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Women Count
women_count_field = {
    'key': 'women_count_field',
    'name': tr('Women Count'),
    'field_name': 'women',
    'type': int,
    'description': tr(
        'Attribute where the number of women of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Youth Count
youth_count_field = {
    'key': 'youth_count_field',
    'name': tr('Youth Count'),
    'field_name': 'youth',
    'type': int,
    'description': tr(
        'Attribute where the number of youth people of the feature is located.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Adult Count
adult_count_field = {
    'key': 'adult_count_field',
    'name': tr('Adult Count'),
    'field_name': 'adult',
    'type': int,
    'description': tr(
        'Attribute where the number of adult people of the feature is located.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Elderly Count
elderly_count_field = {
    'key': 'elderly_count_field',
    'name': tr('Elderly Count'),
    'field_name': 'elderly',
    'type': int,
    'description': tr(
        'Attribute where the number of elderly people of the feature is located.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

exposure_fields = [
    exposure_id_field,
    feature_type_field,
    population_count_field,
    feature_value_field,
    feature_rate_field
]

hazard_fields = [
    hazard_id_field,
    hazard_value_field
]

aggregation_fields = [
    aggregation_id_field,
    aggregation_name_field,
    gender_ratio_field,
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field
]

impact_fields = [
    exposure_id_field,
    exposure_class_field,
    population_count_field,
    feature_value_field,
    feature_rate_field,
    hazard_id_field,
    hazard_class_field,
    aggregation_id_field,
    aggregation_name_field,
    gender_ratio_field,
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field,
    women_count_field,
    youth_count_field,
    adult_count_field,
    elderly_count_field
]