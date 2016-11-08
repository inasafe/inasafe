# coding=utf-8
"""Definitions relating to fields."""

from PyQt4.QtCore import QVariant

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

default_field_length = 10
default_field_precision = 5

# # # # # # # # # #
# Exposure
# # # # # # # # # #

# Exposure ID
exposure_id_field = {
    'key': 'exposure_id_field',
    'name': tr('Exposure ID'),
    'field_name': 'exposure_id',
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
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Exposure Name Field
exposure_name_field = {
    'key': 'exposure_name_field',
    'name': tr('Exposure Name'),
    'field_name': 'exposure_name',
    'type': QVariant.String,
    'length': default_field_length,
    'precision': 0,
    'description': tr(
        'Attribute where the exposure name of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Exposure Type
exposure_type_field = {
    'key': 'exposure_type_field',
    'name': tr('Exposure Type'),
    'field_name': 'exposure_type',
    'type': QVariant.String,
    'length': default_field_length,
    'precision': 0,
    'description': tr(
        'Attribute where the exposure type of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}


# Exposure Class
exposure_class_field = {
    'key': 'exposure_class_field',
    'name': tr('Exposure Class'),
    'field_name': 'exposure_class',
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
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# # # # # # # # # #
# Hazard
# # # # # # # # # #

# Hazard ID
hazard_id_field = {
    'key': 'hazard_id_field',
    'name': tr('Hazard ID'),
    'field_name': 'hazard_id',
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
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Hazard name
hazard_name_field = {
    'key': 'hazard_name_field',
    'name': tr('Hazard Name'),
    'field_name': 'hazard_name',
    'type': QVariant.String,
    'length': default_field_length,
    'precision': 0,
    'description': tr(
        'Attribute where the hazard name of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Hazard Value
hazard_value_field = {
    'key': 'hazard_value_field',
    'name': tr('Hazard Value'),
    'field_name': 'hazard_value',
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
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Hazard Class
hazard_class_field = {
    'key': 'hazard_class_field',
    'name': tr('Hazard Class'),
    'field_name': 'hazard_class',
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
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# # # # # # # # # #
# Aggregation
# # # # # # # # # #

# Aggregation ID
aggregation_id_field = {
    'key': 'aggregation_id_field',
    'name': tr('Aggregation ID'),
    'field_name': 'aggregation_id',
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
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Aggregation Name
aggregation_name_field = {
    'key': 'aggregation_name_field',
    'name': tr('Aggregation Name'),
    'field_name': 'aggregation_name',
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
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# # # # # # # # # #
# Analysis
# # # # # # # # # #

analysis_id_field = {
    'key': 'analysis_id_field',
    'name': tr('Analysis ID'),
    'field_name': 'analysis_id',
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
    'absolute': False,
    'description': tr(
        'Attribute where the analysis ID of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

analysis_name_field = {
    'key': 'analysis_name_field',
    'name': tr('Analysis Name'),
    'field_name': 'analysis_name',
    'type': QVariant.String,
    'length': default_field_length,
    'precision': 0,
    'absolute': False,
    'description': tr(
        'Attribute where the analysis name of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

# # # # # # # # # #
# Count, inputs (Absolute values)
# # # # # # # # # #

# Feature Value
feature_value_field = {
    'key': 'feature_value_field',
    'name': tr('Feature Value'),
    'field_name': 'exposure_value',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': True,
    'description': tr('Attribute where the value of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Population Count
population_count_field = {
    'key': 'population_count_field',
    'name': tr('Population count'),
    'field_name': 'population',
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr('Attribute where the number of population is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Women Count
women_count_field = {
    'key': 'women_count_field',
    'name': tr('Women Count'),
    'field_name': 'women',
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'Attribute where the number of women of the feature is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Youth Count
youth_count_field = {
    'key': 'youth_count_field',
    'name': tr('Youth Count'),
    'field_name': 'youth',
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'Attribute where the number of youth people of the feature is located.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Adult Count
adult_count_field = {
    'key': 'adult_count_field',
    'name': tr('Adult Count'),
    'field_name': 'adult',
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'Attribute where the number of adult people of the feature is located.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Elderly Count
elderly_count_field = {
    'key': 'elderly_count_field',
    'name': tr('Elderly Count'),
    'field_name': 'elderly',
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'Attribute where the number of elderly people of the feature is '
        'located.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Size
size_field = {
    'key': 'size_field',
    'name': tr('Geometric Size'),
    'field_name': 'size',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': 2,
    'absolute': True,
    'description': tr(
        'Attribute where the size of the gemetry is located.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# # # # # # # # # #
# Rate (Not absolute values)
# # # # # # # # # #

# Feature Rate
feature_rate_field = {
    'key': 'feature_rate_field',
    'name': tr('Feature Rate'),
    'field_name': 'exposure_rate',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': False,
    'description': tr(
        'Attribute where the rate value of the feature is located. A rate '
        'value is the cost per unit of measure (m2 / m) for the feature.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True
}

# Female Ratio
female_ratio_field = {
    'key': 'female_ratio_field',
    'name': tr('Female Ratio'),
    'field_name': 'female_ratio',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': False,
    'description': tr('Attribute where the ratio of women is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True
}

# Youth Ratio
youth_ratio_field = {
    'key': 'youth_ratio_field',
    'name': tr('Youth Ratio'),
    'field_name': 'youth_ratio',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': False,
    'description': tr('Attribute where the ratio of youth people is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True
}

# Adult Ratio
adult_ratio_field = {
    'key': 'adult_ratio_field',
    'name': tr('Adult Ratio'),
    'field_name': 'adult_ratio',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': False,
    'description': tr('Attribute where the ratio of adult people is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True
}

# Elderly Ratio
elderly_ratio_field = {
    'key': 'elderly_ratio_field',
    'name': tr('Elderly Ratio'),
    'field_name': 'elderly_ratio',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': False,
    'description': tr(
        'Attribute where the ratio of elderly people is located.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True
}

# # # # # # # # # #
# Special fields from post processors
# # # # # # # # # #

# Affected or not
affected_field = {
    'key': 'affected_field',
    'name': tr('Affected'),
    'field_name': 'affected',
    'type': QVariant.String,
    'length': default_field_length,
    'precision': 0,
    'description': tr(
        'Attribute where the feature is affected or not.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# # # # # # # # # #
# Count, outputs (Absolute values)
# # # # # # # # # #

# Total per aggregation area
total_field = {
    'key': 'total_field',
    'name': tr('Total'),
    'field_name': 'total',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': 2,
    'absolute': True,
    'description': tr(
        'Attribute where the total of the total is located.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

total_affected_field = {
    'key': 'total_affected_field',
    'name': tr('Total Affected'),
    'field_name': 'total_affected',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': 2,
    'absolute': True,
    'description': tr(
        'Attribute where the total affected is located.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Special dynamic field for each exposure type in the aggregate hazard table.
exposure_count_field = {
    'key': '%s_exposure_count_field',
    'name': tr('Total %s'),
    'field_name': '%s_exposure_count',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': True,
    'description': tr(
        'Attribute where the total of the count is located.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

affected_exposure_count_field = {
    'key': '%s_affected_field',
    'name': tr('Affected %s'),
    'field_name': '%s_affected',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': True,
    'description': tr(
        'Attribute where the total of the affected feature is located.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Count for affected
affected_count_field = {
    'key': 'affected_count_field',
    'name': tr('Affected count'),
    'field_name': 'affected_count',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': True,
    'description': tr(
        'Count the number of affected features.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}


# Special dynamic field for each hazard class in analysis layer.
hazard_count_field = {
    'key': '%s_hazard_count_field',
    'name': tr('Total %s'),
    'field_name': '%s_hazard_count',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': 2,
    'absolute': True,
    'description': tr(
        'Attribute where the total of the count is located.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Inputs
exposure_fields = [
    exposure_id_field,
    feature_value_field,
    feature_rate_field
]

hazard_fields = [
    hazard_id_field,
]

aggregation_fields = [
    aggregation_id_field,
    aggregation_name_field,
    female_ratio_field,
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field
]

# Outputs
impact_fields = [
    exposure_id_field,
    exposure_class_field,
    hazard_id_field,
    hazard_class_field,
    population_count_field,
    feature_value_field,
    feature_rate_field,
    aggregation_id_field,
    aggregation_name_field,
    female_ratio_field,
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field,
    women_count_field,
    youth_count_field,
    adult_count_field,
    elderly_count_field,
    size_field,
    affected_field,
    exposure_count_field,
    total_field,
]

aggregate_hazard_fields = [
    aggregation_id_field,
    aggregation_name_field,
    hazard_id_field,
    hazard_class_field,
    exposure_count_field,
    affected_field,
    total_field,
]

aggregation_impacted = [
    aggregation_id_field,
    aggregation_name_field,
    affected_exposure_count_field,
    total_affected_field,
]

exposure_breakdown_fields = [
    exposure_class_field,
    hazard_count_field,
    total_affected_field,
    total_field,
]

analysis_fields = [
    analysis_id_field,
    analysis_name_field,
    hazard_count_field,
    affected_count_field,
    total_affected_field,
]

count_fields = [
    feature_value_field,
    population_count_field,
    women_count_field,
    youth_count_field,
    adult_count_field,
    elderly_count_field,
    size_field,
]

ratio_fields = [
    feature_rate_field,
    female_ratio_field,
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field,
]

# Used by earthquake, please remove after we remove the earthquake
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
