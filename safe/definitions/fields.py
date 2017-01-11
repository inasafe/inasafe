# coding=utf-8
"""Definitions relating to fields."""

from PyQt4.QtCore import QVariant

from safe.utilities.i18n import tr
from safe.definitions.constants import qvariant_whole_numbers
from safe.definitions.default_values import (
    female_ratio_default_value,
    feature_rate_default_value,
    youth_ratio_default_value,
    adult_ratio_default_value,
    elderly_ratio_default_value
)
from safe.definitions import concepts

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

default_field_length = 10
default_field_precision = 5
default_ratio_field_precision = 2

# # # # # # # # # #
# Exposure
# # # # # # # # # #

# Exposure ID
exposure_id_field = {
    'key': 'exposure_id_field',
    'name': tr('Exposure ID'),
    'field_name': 'exposure_id',
    'type': qvariant_whole_numbers,
    'length': default_field_length,
    'precision': 0,
    'help_text': tr(  # this is the short description
        'An ID attribute in the exposure layer'
    ),
    'description': tr(
        'A unique identifier for each exposure feature. If you provide this '
        'we will persist these identifiers in the output datasets so that '
        'you can do a table join back to the original exposure layer if '
        'needed.'),
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
    'help_text': tr(  # short description
        'A NAME attribute in the exposure layer.'),
    'description': tr(
        'This will be carried over to the impact layer if provided. The name '
        'can be useful in some cases e.g. where exposure is a place, the '
        'name can be used to label the place names.'),
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
    'help_text': tr(  # 'Short description'
        'A TYPE attribute in the exposure layer.'),
    'description': tr(
        'The type attribute will be used to differentiate between different '
        'kinds of features when generating reports. For example with roads '
        'the type attribute will be used to report on affected roads based '
        'on their types. InaSAFE will also apply groupings ("exposure classes"'
        ') based on type which you can configure during the keyword creation '
        'process. '),
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
    'help_text': tr(  # Short description
        'A CLASS attribute in the exposure layer.'),
    'description': tr(
        'The class attribute will be used to group features according to '
        'their types. For example several types of ("secondary, residential") '
        'may be  grouped into a single class ("other").'),
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
    'type': qvariant_whole_numbers,
    'length': default_field_length,
    'precision': 0,
    'help_text': tr(  # short description
        'An ID attribute in the hazard layer.'),
    'description': tr(
        'A unique identifier for each hazard feature. If you provide this '
        'we will persist these identifiers in the output datasets so that '
        'you can do a table join back to the original hazard layer if '
        'needed.'),
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
    'help_text': tr(  # short description
        'A NAME attribute in the hazard layer.'),
    'description': tr(
        'This will be carried over to the impact layer if provided. The name '
        'can be useful in some cases e.g. where hazard is a known entity '
        'such as a volcano, the name can be used to label the place names.'),
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
    'help_text': tr(
        'A VALUE attribute for the hazard.'),
    'description': tr(
        'The value attribute for a layer describes the intensity of a hazard'
        'over the area described by the geometry of the feature. For example '
        'a flood polygon may have a hazard value of "1" indicating that the '
        'flood depth over that whole polygon is 1m. The hazard value is the '
        'basis for carrying out an impact assessment. InaSAFE will always '
        'classify the values in the value field into thresholds. For example, '
        'values greater than or equal to zero meters and less than 0.5m '
        'might be a reclassified into a threshold used to define a "Low" '
        'flood class).'),
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
    'help_text': tr('A CLASS attribute for the hazard.'),
    'description': tr(
        'Classes are used to group values in a hazard dataset. In the context '
        'of a hazard, classes indicate the intensity of the hazard and are '
        'typically presented as "Low", "Medium", "High" etc.'),
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
    'type': qvariant_whole_numbers,
    'length': default_field_length,
    'precision': 0,
    'help_text': tr(  # short description
        'An ID attribute in the aggregation layer.'),
    'description': tr(
        'A unique identifier for each aggregation feature. If you provide '
        'this we will persist these identifiers in the output datasets so '
        'that you can do a table join back to the original aggregation layer '
        'if needed.'),
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
    'help_text': tr(  # short description
        'A NAME attribute in the aggregation layer.'),
    'description': tr(
        'This will be carried over to the impact layer if provided. The name '
        'can be useful labelling label the area names that are used in '
        'the report generation process.'),
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
    'type': qvariant_whole_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': False,
    'help_text': tr(  # short description
        'An ID attribute in the analysis layer.'),
    'description': tr(
        'A unique identifier for each analysis feature.'),
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
    'help_text': tr(  # short description
        'A NAME attribute in the analysis layer.'),
    'description': tr(
        'This will be carried over to the analysis layer if provided. The '
        'name will provide context if the analysis layer is shared since '
        'the recipient of the layer will be able to tell what kind of '
        'analysis was carried out when generating the impact layer. For '
        'example when doing a flood on roads analysis, "flood on roads" will '
        'be written to the analysis name field in the analysis layer.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

# # # # # # # # # #
# Profiling
# # # # # # # # # #

profiling_function_field = {
    'key': 'profiling_function_field',
    'name': tr('Profiling function'),
    'field_name': 'function',
    'type': QVariant.String,
    'length': default_field_length,
    'precision': 0,
    'help_text': tr('The name of the function being measured.'),
    'description': tr(
        'The profiling system in InaSAFE provide metrics about which '
        'python functions were called during the analysis workflow and '
        'how long was spent in each function. These data are assembled into '
        'a table and shown in QGIS as part of the analysis layer group. '
        'Using the profiling function name field we are able to refer back '
        'to a specific python function when doing performance optimisation.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

profiling_time_field = {
    'key': 'profiling_time_field',
    'name': tr('Profiling time'),
    'field_name': 'time',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'help_text': tr(
        'The total elapsed time spent in the function being measured.'),
    'description': tr(
        'The profiling system in InaSAFE provide metrics about which '
        'python functions were called during the analysis workflow and '
        'how long was spent in each function. These data are assembled into '
        'a table and shown in QGIS as part of the analysis layer group. '
        'Using the profiling time field we are able to refer back '
        'to a how long was spent in each specific python function when '
        'doing performance optimisation.'),
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
    'help_text': tr(
        'The VALUE field in an impact layer.'),
    'description': tr(
        'The value field is used to indicate the financial value of a '
        ' exposed feature. The value is usually calculated as the function '
        'of the length or area of a given exposure feature.'),
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
    'type': qvariant_whole_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr('Attribute where the number of population is located.'),
    'help_text': tr(''

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

# Women Count
female_count_field = {
    'key': 'female_count_field',
    'name': tr('Female Count'),
    'field_name': 'female',
    'type': qvariant_whole_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'Attribute where the number of females of the feature is located.'),
    'help_text': tr(''

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

# Youth Count
youth_count_field = {
    'key': 'youth_count_field',
    'name': tr('Youth Count'),
    'field_name': 'youth',
    'type': qvariant_whole_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'Attribute where the number of youth people of the feature is located.'
    ),
    'help_text': concepts['youth']['description']

    ,
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
    'type': qvariant_whole_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'Attribute where the number of adult people of the feature is located.'
    ),
    'help_text': tr(''

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
    'type': qvariant_whole_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'Attribute where the number of elderly people of the feature is '
        'located.'
    ),
    'help_text': tr(''

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
    'help_text': tr(''

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
    'precision': 0,
    'absolute': False,
    'description': tr(
        'Attribute where the rate value of the feature is located. A rate '
        'value is the cost per unit of measure (m2 / m) for the feature.'),
    'help_text': tr(''

    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True,
    'default_value': feature_rate_default_value
}

# Female Ratio
female_ratio_field = {
    'key': 'female_ratio_field',
    'name': tr('Female Ratio'),
    'field_name': 'female_ratio',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr('Attribute where the ratio of females is located.'),
    'help_text': tr(''

    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True,
    'default_value': female_ratio_default_value
}

# Youth Ratio
youth_ratio_field = {
    'key': 'youth_ratio_field',
    'name': tr('Youth Ratio'),
    'field_name': 'youth_ratio',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr('Attribute where the ratio of youth people is located.'),
    'help_text': tr(''

    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True,
    'default_value': youth_ratio_default_value
}

# Adult Ratio
adult_ratio_field = {
    'key': 'adult_ratio_field',
    'name': tr('Adult Ratio'),
    'field_name': 'adult_ratio',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr('Attribute where the ratio of adult people is located.'),
    'help_text': tr(''

    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True,
    'default_value': adult_ratio_default_value
}

# Elderly Ratio
elderly_ratio_field = {
    'key': 'elderly_ratio_field',
    'name': tr('Elderly Ratio'),
    'field_name': 'elderly_ratio',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'Attribute where the ratio of elderly people is located.'),
    'help_text': tr(''

    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True,
    'default_value': elderly_ratio_default_value
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
    'help_text': tr(''

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
# Count, outputs (Absolute values)
# # # # # # # # # #

# Total field to store the total number of feature
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
    'help_text': tr(''

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

# Total affected field to store the total affected by the hazard
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
    'help_text': tr(''

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

# Total unaffected field to store the number of unaffected by the hazard
total_unaffected_field = {
    'key': 'total_unaffected_field',
    'name': tr('Total Unaffected'),
    'field_name': 'total_unaffected',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': 2,
    'absolute': False,
    'description': tr(
        'Attribute where the total unaffected is located.'
    ),
    'help_text': tr(''

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
# Count, dynamics, outputs (Absolute values)
# # # # # # # # # #

# Count for each exposure type
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
    'help_text': tr(''

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

# Count for each exposure type affected
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
    'help_text': tr(''

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

# Count for each hazard class
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
    'help_text': tr(''

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
    aggregation_id_field,
    aggregation_name_field,
    feature_value_field,
    feature_rate_field,
    female_ratio_field,
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field,
    population_count_field,
    female_count_field,
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
    total_affected_field,
    total_field
]

# Add also minimum needs fields
from safe.definitions.minimum_needs import minimum_needs_fields  # noqa
count_fields = [
    feature_value_field,
    population_count_field,
    female_count_field,
    youth_count_field,
    adult_count_field,
    elderly_count_field,
] + minimum_needs_fields

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
