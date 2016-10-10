# coding=utf-8
"""
Definitions relating to fields.
"""

from PyQt4.QtCore import QVariant

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

default_field_length = 10
default_field_precision = 5

# Exposure
# Exposure ID
exposure_id_field = {
    'key': 'exposure_id_field',
    'name': tr('Exposure ID'),
    'field_name': 'exp_id',
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
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
    'type': QVariant.String,
    'length': default_field_length,
    'precision': 0,
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
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
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
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
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
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'description': tr(
        'Attribute where the rate value of the feature is located. A rate '
        'value is the cost per unit of measure (m2 / m) for the feature.'),
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
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
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
    'type': [QVariant.String, QVariant.Int, QVariant.Double],
    'length': default_field_length,
    'precision': 0,
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
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
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
    'type': QVariant.String,
    'length': default_field_length,
    'precision': 0,
    'description': tr(
        'Attribute where the aggregation name of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
# Female Ratio
female_ratio_field = {
    'key': 'female_ratio_field',
    'name': tr('Female Ratio'),
    'field_name': 'female_r',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
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
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
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
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
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
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
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
    'type': QVariant.String,
    'length': default_field_length,
    'precision': 0,
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
    'type': QVariant.String,
    'length': default_field_length,
    'precision': 0,
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
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
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
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
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
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
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
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
    'description': tr(
        'Attribute where the number of elderly people of the feature is '
        'located.'
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
    feature_rate_field,
    women_count_field,
    youth_count_field,
    adult_count_field,
    elderly_count_field
]

hazard_fields = [
    hazard_id_field,
    hazard_value_field,
    hazard_class_field
]

aggregation_fields = [
    aggregation_id_field,
    aggregation_name_field,
    female_ratio_field,
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
    female_ratio_field,
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field,
    women_count_field,
    youth_count_field,
    adult_count_field,
    elderly_count_field
]

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
