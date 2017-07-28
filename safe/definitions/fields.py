# coding=utf-8

"""Definitions relating to fields."""

from PyQt4.QtCore import QVariant

from safe.definitions import concepts
from safe.definitions.constants import (
    qvariant_whole_numbers, qvariant_numbers)
from safe.definitions.currencies import currencies
from safe.definitions.default_values import (
    female_ratio_default_value,
    male_ratio_default_value,
    feature_rate_default_value,
    youth_ratio_default_value,
    adult_ratio_default_value,
    elderly_ratio_default_value,
    infant_ratio_default_value,
    child_ratio_default_value,
    under_5_ratio_default_value,
    over_60_ratio_default_value,
    disabled_ratio_default_value,
    child_bearing_age_ratio_default_value,
    pregnant_ratio_default_value,
    lactating_ratio_default_value
)
from safe.definitions.units import unit_quintal
from safe.utilities.i18n import tr

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

exposure_id_field = {
    'key': 'exposure_id_field',
    'name': tr('Exposure ID'),
    'field_name': 'exposure_id',
    'type': qvariant_whole_numbers,
    'length': default_field_length,
    'precision': 0,
    'description': tr(  # this is the short description
        'An ID attribute in the exposure layer'
    ),
    'help_text': tr(
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
    'description': tr(  # short description
        'A NAME attribute in the exposure layer.'),
    'help_text': tr(
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
    'description': tr(  # 'Short description'
        'A TYPE attribute in the exposure layer.'),
    'help_text': tr(
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
    'description': tr(  # Short description
        'A CLASS attribute in the exposure layer.'),
    'help_text': tr(
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
    'description': tr(  # short description
        'An ID attribute in the hazard layer.'),
    'help_text': tr(
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
    'description': tr(  # short description
        'A NAME attribute in the hazard layer.'),
    'help_text': tr(
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
    'description': tr(  # short description
        'An ID attribute in the aggregation layer.'),
    'help_text': tr(
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
        'can be useful to label the area names that are used in '
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
    'description': tr(  # short description
        'An ID attribute in the analysis layer.'),
    'help_text': tr(
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
        'The profiling system in InaSAFE provides metrics about which '
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

profiling_memory_field = {
    'key': 'profiling_memory_field',
    'name': tr('Profiling memory'),
    'field_name': 'memory_mb',
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': default_field_precision,
    'help_text': tr(
        'The total used memory (in mb) in the function being measured.'),
    'description': tr(
        'The profiling system in InaSAFE provides metrics about which '
        'python functions were called during the analysis workflow and '
        'how much memory is used in each function. These data are assembled '
        'into a table and shown in QGIS as part of the analysis layer group. '
        'Using the profiling memory field we are able to refer back '
        'to a how much memory was used in each specific python function when '
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
        'The VALUE field in a layer.'),
    'description': tr(
        'The value field is used to indicate the financial value of an '
        'exposed feature. The value is usually calculated as the function '
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
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'help_text': tr('A count of the population for each feature.'),
    'description': tr(
        'During the impact analysis, population counts are used to calculate '
        'the total number of people, expected number of impacted, displaced '
        'people and in some cases fatality counts. Population data are also '
        'used to calculate demographic data (e.g. how many women, youths, '
        'adults etc. were affected) and minimum needs data (i.e. what '
        'quantities of provisions and supplies are needed to support '
        'displaced persons.)'),
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
    'header_name': tr('Female'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of females for each feature.'),
    'help_text': tr(
        '"Female" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of females per exposure '
        'feature, aggregate hazard area, aggregation area and for the '
        'analysis area as a whole. The female count is calculated based on '
        'standard ratios either provided as a global setting in InaSAFE, or '
        '(if available) counts or ratios in the input analysis data.').format(
            concept=concepts['female']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Male Count
# Included as complementary in the report
male_count_field = {
    'key': 'male_count_field',
    'name': tr('Male Count'),
    'field_name': 'male',
    'header_name': tr('Male'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of males for each feature.'),
    'help_text': tr(
        '"Male" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of males per exposure '
        'feature, aggregate hazard area, aggregation area and for the '
        'analysis area as a whole. The male count is calculated based on '
        'standard ratios either provided as a global setting in InaSAFE, or '
        '(if available) counts or ratios in the input analysis data.').format(
            concept=concepts['male']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Child Bearing Age Count
child_bearing_age_count_field = {
    'key': 'child_bearing_age_count_field',
    'name': tr('Child Bearing Age Count'),
    'field_name': 'child_bearing_age',
    'header_name': tr('Child Bearing Age'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of child bearing age for each feature.'),
    'help_text': tr(
        '"Child Bearing Age" is defined as: {concept} In cases where '
        'population data is available, InaSAFE will calculate the number of '
        'child bearing age per exposure feature, aggregate hazard area, '
        'aggregation area and for the analysis area as a whole. The child '
        'bearing age count is calculated based on standard ratios either '
        'provided as a global setting in InaSAFE, or (if available) ratios in '
        'the input analysis data.').format(
            concept=concepts['child_bearing_age']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Pregnant Count
pregnant_count_field = {
    'key': 'pregnant_count_field',
    'name': tr('Pregnant Women Count'),
    'field_name': 'pregnant',
    'header_name': tr('Pregnant'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of pregnant women for each feature.'),
    'help_text': tr(
        '"Pregnant" is defined as: {concept} In cases where '
        'population data is available, InaSAFE will calculate the number of '
        'pregnant women per exposure feature, aggregate hazard '
        'area, aggregation area and for the analysis area as a whole. The '
        'pregnant women count is calculated based on standard ratios '
        'either provided as a global setting in InaSAFE, or (if available) '
        'ratios in the input analysis data.').format(
        concept=concepts['pregnant']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}
# Lactating Count
lactating_count_field = {
    'key': 'lactating_count_field',
    'name': tr('Lactating Count'),
    'field_name': 'lactating',
    'header_name': tr('Lactating'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of lactating women for each feature.'),
    'help_text': tr(
        '"Lactating" is defined as: {concept} In cases where '
        'population data is available, InaSAFE will calculate the number of '
        'lactating women per exposure feature, aggregate hazard '
        'area, aggregation area and for the analysis area as a whole. The '
        'lactating count is calculated based on standard ratios '
        'either provided as a global setting in InaSAFE, or (if available) '
        'ratios in the input analysis data.').format(
        concept=concepts['lactating']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Infant Count
infant_count_field = {
    'key': 'infant_count_field',
    'name': tr('Infant Count'),
    'field_name': 'infant',
    'header_name': tr('Infant'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of infant people for each feature.'),
    'help_text': tr(
        '"Infant" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of infants per exposure '
        'feature, aggregate hazard area, aggregation area and for the '
        'analysis area as a whole. The infant count is calculated based on '
        'standard ratios either provided as a global setting in InaSAFE, or '
        '(if available) counts or ratios in the input analysis data.').format(
            concept=concepts['infant']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Child Count
child_count_field = {
    'key': 'child_count_field',
    'name': tr('Child Count'),
    'field_name': 'child',
    'header_name': tr('Child'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of child people for each feature.'),
    'help_text': tr(
        '"Child" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of child per exposure '
        'feature, aggregate hazard area, aggregation area and for the '
        'analysis area as a whole. The child count is calculated based on '
        'standard ratios either provided as a global setting in InaSAFE, or '
        '(if available) counts or ratios in the input analysis data.').format(
            concept=concepts['child']['description']),
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
    'header_name': tr('Youth'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of young people for each feature.'),
    'help_text': tr(
        '"Youth" is defined as: {concept} This definition may not align well '
        'with the definition of youth in the humanitarian sector. It should '
        'be noted that this concept overlaps with the concepts of infant and '
        'child in InaSAFE. In cases where population data is available, '
        'InaSAFE will calculate the number of youths per exposure '
        'feature, aggregate hazard area, aggregation area and for the '
        'analysis area as a whole. The youth count is calculated based on '
        'standard ratios either provided as a global setting in InaSAFE, or '
        '(if available) counts or ratios in the input analysis data.').format(
            concept=concepts['youth']['description']),
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
    'header_name': tr('Adult'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of adults for each feature.'),
    'help_text': tr(
        '"Adult" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of adults per exposure '
        'feature, aggregate hazard area, aggregation area and for the '
        'analysis area as a whole. The adult count is calculated based on '
        'standard ratios either provided as a global setting in InaSAFE, or '
        '(if available) counts or ratios in the input analysis data.').format(
            concept=concepts['adult']['description']),
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
    'header_name': tr('Elderly'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of elderly people for each feature.'),
    'help_text': tr(
        '"Elderly" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of adults per exposure '
        'feature, aggregate hazard area, aggregation area and for the '
        'analysis area as a whole. The elderly count is calculated based on '
        'standard ratios either provided as a global setting in InaSAFE, or '
        '(if available) counts or ratios in the input analysis data.').format(
            concept=concepts['elderly']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Under 5 Count
under_5_count_field = {
    'key': 'under_5_count_field',
    'name': tr('Under 5 Count'),
    'field_name': 'under_5',
    'header_name': tr('Under 5'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of under 5 years old for each feature.'),
    'help_text': tr(
        '"Under 5" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of people under 5 years '
        'old per exposure feature, aggregate hazard area, aggregation area '
        'and for the analysis area as a whole. The under 5 years count is '
        'calculated based on standard ratios either provided as a global '
        'setting in InaSAFE, or (if available) ratios in the input analysis '
        'data.').format(concept=concepts['under_5']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Over 60 Count
over_60_count_field = {
    'key': 'over_60_count_field',
    'name': tr('Over 60 Count'),
    'field_name': 'over_60',
    'header_name': tr('Over 60'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of over 60 years old for each feature.'),
    'help_text': tr(
        '"Over 60" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of people over 60 years '
        'old per exposure feature, aggregate hazard area, aggregation area '
        'and for the analysis area as a whole. The over 60 years count is '
        'calculated based on standard ratios either provided as a global '
        'setting in InaSAFE, or (if available) ratios in the input analysis '
        'data.').format(concept=concepts['over_60']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Disabled Count
disabled_count_field = {
    'key': 'disabled_count_field',
    'name': tr('Disabled Count'),
    'field_name': 'disabled',
    'header_name': tr('Disabled'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The proportion of disabled people for each feature.'),
    'help_text': tr(
        '"Disabled" is defined as: {concept} In cases where population data '
        'is available, InaSAFE will calculate the number of disabled people '
        'per exposure feature, aggregate hazard area, aggregation area '
        'and for the analysis area as a whole. The disabled count is '
        'calculated based on standard ratios either provided as a global '
        'setting in InaSAFE, or (if available) ratios in the input analysis '
        'data.').format(concept=concepts['disabled']['description']),
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
    'help_text': tr(
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

buffer_distance_field = {
    'key': 'buffer_distance_field',
    'name': tr('Buffer Distance'),
    'field_name': 'buffer_distance_m',
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr('The distance of the buffer for each feature.'),
    'help_text': tr('The distance of the buffer for each feature.'),
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
    'help_text': tr(
        'The rate field in a layer.'),
    'description': tr(
        'The rate field is used to indicate the financial value of an '
        'exposed feature. The rate, when multiplied by the '
        'of the length or area of a given exposure feature, can be used '
        'to calculate an estimated value of the feature. '
        'For example in buildings the rate * the area of a building '
        'can be used to estimate the value of the building.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False,  # It should be True,but disabled in V4.0,ET 1/03/17
    'default_value': feature_rate_default_value
}

# Female Ratio
female_ratio_field = {
    'key': 'female_ratio_field',
    'name': tr('Female Ratio'),
    'field_name': 'female_ratio',
    'header_name': tr('Female'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'The proportion of females for each feature.'),
    'help_text': tr(
        '"Female" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of females per exposure '
        'feature, aggregate hazard area, aggregation area and for the '
        'analysis area as a whole. The female count is calculated based on '
        'standard ratios either provided as a global setting in InaSAFE, or '
        '(if available) ratios in the input analysis data.').format(
            concept=concepts['female']['description']),
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

# Male Ratio
male_ratio_field = {
    'key': 'male_ratio_field',
    'name': tr('Male Ratio'),
    'field_name': 'male_ratio',
    'header_name': tr('Male'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'The proportion of male for each feature.'),
    'help_text': tr(
        '"Male" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of males per exposure '
        'feature, aggregate hazard area, aggregation area and for the '
        'analysis area as a whole. The male count is calculated based on '
        'standard ratios either provided as a global setting in InaSAFE, or '
        '(if available) ratios in the input analysis data.').format(
            concept=concepts['male']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True,
    'default_value': male_ratio_default_value
}

# Child Bearing Age Ratio
child_bearing_age_ratio_field = {
    'key': 'child_bearing_age_ratio_field',
    'name': tr('Child Bearing Age Ratio'),
    'field_name': 'child_bearing_age_ratio',
    'header_name': tr('Child Bearing Age'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'The proportion of child bearing age for each feature.'),
    'help_text': tr(
        '"Child Bearing Age" is defined as: {concept} In cases where '
        'population data is available, InaSAFE will calculate the number of '
        'child bearing age per exposure feature, aggregate hazard area, '
        'aggregation area and for the analysis area as a whole. The child '
        'bearing age count is calculated based on standard ratios either '
        'provided as a global setting in InaSAFE, or (if available) ratios in '
        'the input analysis data.').format(
            concept=concepts['child_bearing_age']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True,
    'default_value': child_bearing_age_ratio_default_value
}

pregnant_ratio_field = {
    'key': 'pregnant_ratio_field',
    'name': tr('Pregnant Ratio'),
    'field_name': 'pregnant_ratio',
    'header_name': tr('Pregnant'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'The proportion of pregnant women for each feature.'),
    'help_text': tr(
        '"Pregnant or Lactating" is defined as: {concept} In cases where '
        'population data is available, InaSAFE will calculate the number of '
        'pregnant women per exposure feature, aggregate hazard '
        'area, aggregation area and for the analysis area as a whole. The '
        'pregnant count is calculated based on standard ratios '
        'either provided as a global setting in InaSAFE, or (if available) '
        'ratios in the input analysis data.').format(
        concept=concepts['pregnant']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True,
    'default_value': pregnant_ratio_default_value
}
lactating_ratio_field = {
    'key': 'lactating_ratio_field',
    'name': tr('Lactating Ratio'),
    'field_name': 'lactating_ratio',
    'header_name': tr('Lactating'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'The proportion of lactating women for each feature.'),
    'help_text': tr(
        '"Lactating" is defined as: {concept} In cases where '
        'population data is available, InaSAFE will calculate the number of '
        'lactating people per exposure feature, aggregate hazard '
        'area, aggregation area and for the analysis area as a whole. The '
        'lactating count is calculated based on standard ratios '
        'either provided as a global setting in InaSAFE, or (if available) '
        'ratios in the input analysis data.').format(
            concept=concepts['lactating']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True,
    'default_value': lactating_ratio_default_value
}

# Infant Ratio
infant_ratio_field = {
    'key': 'infant_ratio_field',
    'name': tr('Infant Ratio'),
    'field_name': 'infant_ratio',
    'header_name': tr('Infant'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'The proportion of infant people for each feature.'),
    'help_text': tr(
        '"Infant" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of infants per exposure '
        'feature, aggregate hazard area, aggregation area and for the '
        'analysis area as a whole. The infant count is calculated based on '
        'standard ratios either provided as a global setting in InaSAFE, or '
        '(if available) ratios in the input analysis data.').format(
            concept=concepts['infant']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True,
    'default_value': infant_ratio_default_value
}

# Child Ratio
child_ratio_field = {
    'key': 'child_ratio_field',
    'name': tr('Child Ratio'),
    'field_name': 'child_ratio',
    'header_name': tr('Child'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'The proportion of child people for each feature.'),
    'help_text': tr(
        '"Child" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of child per exposure '
        'feature, aggregate hazard area, aggregation area and for the '
        'analysis area as a whole. The child count is calculated based on '
        'standard ratios either provided as a global setting in InaSAFE, or '
        '(if available) ratios in the input analysis data.').format(
            concept=concepts['child']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True,
    'default_value': child_ratio_default_value
}

# Youth Ratio
youth_ratio_field = {
    'key': 'youth_ratio_field',
    'name': tr('Youth Ratio'),
    'field_name': 'youth_ratio',
    'header_name': tr('Youth'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'The proportion of young people for each feature.'),
    'help_text': tr(
        '"Youth" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of youths per exposure '
        'feature, aggregate hazard area, aggregation area and for the '
        'analysis area as a whole. The youth count is calculated based on '
        'standard ratios either provided as a global setting in InaSAFE, or '
        '(if available) ratios in the input analysis data.').format(
            concept=concepts['youth']['description']),
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
    'header_name': tr('Adult'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'The proportion of adults for each feature.'),
    'help_text': tr(
        '"Adult" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of adults per exposure '
        'feature, aggregate hazard area, aggregation area and for the '
        'analysis area as a whole. The adult count is calculated based on '
        'standard ratios either provided as a global setting in InaSAFE, or '
        '(if available) ratios in the input analysis data.').format(
            concept=concepts['adult']['description']),
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
    'header_name': tr('Elderly'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'The proportion of elderly people for each feature.'),
    'help_text': tr(
        '"Elderly" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of adults per exposure '
        'feature, aggregate hazard area, aggregation area and for the '
        'analysis area as a whole. The elderly count is calculated based on '
        'standard ratios either provided as a global setting in InaSAFE, or '
        '(if available) ratios in the input analysis data.').format(
            concept=concepts['elderly']['description']),
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

# Under 5 years ratio
under_5_ratio_field = {
    'key': 'under_5_ratio_field',
    'name': tr('Under 5 Years Ratio'),
    'field_name': 'under_5_ratio',
    'header_name': tr('Under 5'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'The proportion of under 5 years old for each feature.'),
    'help_text': tr(
        '"Under 5" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of people under 5 years '
        'old per exposure feature, aggregate hazard area, aggregation area '
        'and for the analysis area as a whole. The under 5 years count is '
        'calculated based on standard ratios either provided as a global '
        'setting in InaSAFE, or (if available) ratios in the input analysis '
        'data.').format(concept=concepts['under_5']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True,
    'default_value': under_5_ratio_default_value
}

# Over 60 years ratio
over_60_ratio_field = {
    'key': 'over_60_ratio_field',
    'name': tr('Over 60 Years Ratio'),
    'field_name': 'over_60_ratio',
    'header_name': tr('Over 60'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'The proportion of over 60 years old for each feature.'),
    'help_text': tr(
        '"Over 60" is defined as: {concept} In cases where population data is '
        'available, InaSAFE will calculate the number of people over 60 years '
        'old per exposure feature, aggregate hazard area, aggregation area '
        'and for the analysis area as a whole. The over 60 years count is '
        'calculated based on standard ratios either provided as a global '
        'setting in InaSAFE, or (if available) ratios in the input analysis '
        'data.').format(concept=concepts['over_60']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True,
    'default_value': over_60_ratio_default_value
}

# Over 60 years ratio
disabled_ratio_field = {
    'key': 'disabled_ratio_field',
    'name': tr('Disabled Ratio'),
    'field_name': 'disabled_ratio',
    'header_name': tr('Disabled'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'The proportion of disabled people for each feature.'),
    'help_text': tr(
        '"Disabled" is defined as: {concept} In cases where population data '
        'is available, InaSAFE will calculate the number of disabled people '
        'per exposure feature, aggregate hazard area, aggregation area '
        'and for the analysis area as a whole. The disabled count is '
        'calculated based on standard ratios either provided as a global '
        'setting in InaSAFE, or (if available) ratios in the input analysis '
        'data.').format(concept=concepts['disabled']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': True,
    'default_value': disabled_ratio_default_value
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
        'The affected field indicates whether a feature is affected by the '
        ' hazard.'),
    'help_text': tr(
        '"Affected" is defined as: {concept}').format(
            concept=concepts['affected']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Displacement ratio
population_displacement_ratio_field = {
    'key': 'population_displacement_ratio_field',
    'name': tr('Population Displacement Ratio'),
    'field_name': 'population_displacement_ratio',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_ratio_field_precision,
    'absolute': False,
    'description': tr(
        'The population displacement ratio for a given hazard class.'),
    'help_text': tr(
        '"Displaced" is defined as: {concept} In cases where population data '
        'is available, InaSAFE will calculate the number of displaced people '
        'per exposure feature, aggregate hazard area, aggregation area and '
        'for the analysis area as a whole. The population displaced ratio is '
        'calculated based on definitions for each hazard class.').format(
            concept=concepts['displaced_people']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False,
    'default_value': None
}

# Fatality ratio
population_fatality_ratio_field = {
    'key': 'fatality_ratio_field',
    'name': tr('Fatality Ratio'),
    'field_name': 'fatality_ratio',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': 10,  # I think we need some precision for this field.
    'absolute': False,
    'description': tr(
        'The population fatality ratio for a given hazard class.'),
    'help_text': tr(
        '"Fatalities" is defined as: {concept} In cases where population data '
        'is available and the hazard is an earthquake, InaSAFE will calculate '
        'the estimated number of killed people per exposure feature, '
        'aggregate hazard area, aggregation area and for the analysis area '
        'as a whole. The population displaced ratio is calculated based on '
        'definitions for each hazard class.').format(
            concept=concepts['killed_people']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False,
    'default_value': None
}

male_displaced_count_field = {
    'key': 'male_displaced_count_field',
    'name': tr('Male Displaced Count'),
    'field_name': 'male_displaced',
    'header_name': tr('Male'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of displaced males for each feature.'),
    'help_text': tr(
        'The number of displaced males for each feature.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

female_displaced_count_field = {
    'key': 'female_displaced_count_field',
    'name': tr('Female Displaced Count'),
    'field_name': 'female_displaced',
    'header_name': tr('Female'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of displaced females for each feature.'),
    'help_text': tr(
        'The number of displaced females for each feature.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

child_bearing_age_displaced_count_field = {
    'key': 'child_bearing_age_displaced_count_field',
    'name': tr('Child Bearing Age Displaced Count'),
    'field_name': 'child_bearing_age_displaced',
    'header_name': tr('Child Bearing Age'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of displaced child bearing age for each feature.'),
    'help_text': tr(
        'The number of displaced child bearing age for each feature.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

pregnant_displaced_count_field = {
    'key': 'pregnant_displaced_count_field',
    'name': tr('Lactating Displaced Count'),
    'field_name': 'pregnant_displaced',
    'header_name': tr('Pregnant'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of displaced pregnant women for each feature.'),
    'help_text': tr(
        'The number of displaced pregnant women for each feature.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}
lactating_displaced_count_field = {
    'key': 'lactating_displaced_count_field',
    'name': tr('Pregnant Displaced Count'),
    'field_name': 'lactating_displaced',
    'header_name': tr('Lactating'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of displaced pregnant women for each feature.'),
    'help_text': tr(
        'The number of displaced pregnant women for each feature.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

infant_displaced_count_field = {
    'key': 'infant_displaced_count_field',
    'name': tr('Infant Displaced Count'),
    'field_name': 'infant_displaced',
    'header_name': tr('Infant'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of infant displaced for each feature.'),
    'help_text': tr(
        'The number of infant displaced for each feature.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

child_displaced_count_field = {
    'key': 'child_displaced_count_field',
    'name': tr('Child Displaced Count'),
    'field_name': 'child_displaced',
    'header_name': tr('Child'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of child displaced for each feature.'),
    'help_text': tr(
        'The number of child displaced for each feature.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

youth_displaced_count_field = {
    'key': 'youth_displaced_count_field',
    'name': tr('Youth Displaced Count'),
    'field_name': 'youth_displaced',
    'header_name': tr('Youth'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of young people displaced for each feature.'),
    'help_text': tr(
        'The number of young people displaced for each feature.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

adult_displaced_count_field = {
    'key': 'adult_displaced_count_field',
    'name': tr('Adult Displaced Count'),
    'field_name': 'adult_displaced',
    'header_name': tr('Adult'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of adults displaced for each feature.'),
    'help_text': tr(
        'The number of adults displaced for each feature.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

elderly_displaced_count_field = {
    'key': 'elderly_displaced_count_field',
    'name': tr('Elderly Displaced Count'),
    'field_name': 'elderly_displaced',
    'header_name': tr('Elderly'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of elderly people displaced for each feature.'),
    'help_text': tr(
        'The number of elderly people displaced for each feature.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

under_5_displaced_count_field = {
    'key': 'under_5_displaced_count_field',
    'name': tr('Under 5 Displaced Count'),
    'field_name': 'under_5_displaced',
    'header_name': tr('Under 5'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of under 5 years old displaced for each feature.'),
    'help_text': tr(
        'The number of under 5 years old displaced for each feature.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

over_60_displaced_count_field = {
    'key': 'over_60_displaced_count_field',
    'name': tr('Over 60 Years Displaced Count'),
    'field_name': 'over_60_displaced',
    'header_name': tr('Over 60'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of over 60 years old displaced for each feature.'),
    'help_text': tr(
        'The number of over 60 years old displaced for each feature.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

disabled_displaced_count_field = {
    'key': 'disabled_displaced_count_field',
    'name': tr('Disabled Displaced Count'),
    'field_name': 'disabled_displaced',
    'header_name': tr('Disabled'),
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of disabled people displaced for each feature.'),
    'help_text': tr(
        'The number of disabled people displaced for each feature.'),
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
        'The total field stores the cumulative total number of features or '
        'entities.'),
    'help_text': tr(
        'The total field is added to the analysis layer, aggregate impact '
        'layer and aggregate hazard impact layer during the impact analysis. '
        'It represents the cumulative count of exposure features (e.g. '
        'buildings) or entities (e.g. people) for each area.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Fatalities
fatalities_field = {
    'key': 'fatalities_field',
    'name': tr('Fatalities'),
    'field_name': 'fatalities',
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr('Number of fatalities.'),
    'help_text': tr('Number of fatalities.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}


# Displaced
displaced_field = {
    'key': 'displaced_field',
    'name': tr('Displaced'),
    'field_name': 'displaced',
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr('Number of displaced people.'),
    'help_text': tr('Number of displaced people.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Female hygiene packs
hygiene_packs_count_field = {
    'key': 'hygiene_packs_field',
    'name': tr('Weekly Hygiene Packs'),
    'field_name': 'hygiene_packs',
    'header_name': tr('Hygiene Packs'),
    'type': QVariant.Int,
    'length': default_field_length,
    'frequency': tr('weekly'),
    'precision': 0,
    'absolute': True,
    'description': tr('Number of Hygiene Packs Weekly for Women.'),
    'help_text': tr('Number of Hygiene Packs Weekly for Women.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Additional Rice for Pregnant and Lactating Women
additional_rice_count_field = {
    'key': 'additional_rice_field',
    'name': tr('Additional Weekly Rice kg for Pregnant and Lactating Women'),
    'field_name': 'additional_rice',
    'header_name': tr('Additional Rice for Pregnant and Lactating Women'),
    'type': QVariant.Int,
    'length': default_field_length,
    'unit': {
        'name': 'Kilogram',
        'abbreviation': 'kg'
    },
    'frequency': tr('weekly'),
    'precision': 0,
    'absolute': True,
    'help_text': tr(
        'Additional Weekly Rice kg for Pregnant and Lactating Women.'),
    'description': tr(
        'Additional Weekly Rice kg for Pregnant and Lactating Women.'),
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
        'The total affected field stores the cumulative total number of '
        'affected features or entities.'),
    'help_text': tr(
        '"Affected" is defined as: {concept} The total affected field is '
        'added to the analysis layer, aggregate impact layer and aggregate '
        'hazard impact layer during the impact analysis. It represents the '
        'cumulative count of affected exposure features (e.g. buildings) or '
        'entities (e.g. people) for each area.').format(
            concept=concepts['affected']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Total not affected field to store the number of not affected by the hazard
total_not_affected_field = {
    'key': 'total_not_affected_field',
    'name': tr('Total Not Affected'),
    'field_name': 'total_not_affected',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': 2,
    'absolute': True,
    'help_text': tr(
        'The total not affected field stores the cumulative total number of '
        'not affected features or entities.'),
    'description': tr(
        'The total not affected field is added to the analysis layer, '
        'aggregate impact layer and aggregate hazard impact layer during the '
        'impact analysis. It represents the cumulative count of not affected '
        'exposure features (e.g. buildings) or entities (e.g. people) for '
        'each area.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Total not exposed field to store the number of not exposed by the hazard
total_not_exposed_field = {
    'key': 'total_not_exposed_field',
    'name': tr('Total Not Exposed'),
    'field_name': 'total_not_exposed',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': 2,
    'absolute': True,
    'description': tr(
        'The total not exposed field stores the cumulative total number of '
        'not exposed features or entities.'),
    'help_text': tr(
        'The total not exposed field is added to the analysis layer, '
        'aggregate impact layer and aggregate hazard impact layer during the '
        'impact analysis. It represents the cumulative count of not exposed '
        'exposure features (e.g. buildings) or entities (e.g. people) for '
        'each area.'),
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
        'The total exposure count field stores the cumulative total number of '
        'exposed features or entities.'),
    'help_text': tr(
        'The total exposure count field is added to the analysis layer, '
        'aggregate impact layer and aggregate hazard impact layer during the '
        'impact analysis. It represents the cumulative count of affected '
        'exposured features (e.g. buildings) or entities (e.g. people) for '
        'each area.'),
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
        'The total affected field stores the cumulative total number of '
        'affected exposure features or entities.'),
    'help_text': tr(
        '"Affected" is defined as: {concept} The total affected field is '
        'added to the analysis layer, aggregate impact layer and aggregate '
        'hazard impact layer during the impact analysis. It represents the '
        'cumulative count of affected exposure features (e.g. buildings) or '
        'entities (e.g. people) for each area.').format(
            concept=concepts['affected']['description']),
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
    # TODO: Etienne review this
    'description': tr(
        'The total affected field stores the cumulative total number of '
        'affected exposure features or entities.'),
    'help_text': tr(
        '"Hazard" is defined as: {concept} The hazard count field is added to '
        'the analysis layer, aggregate impact layer and aggregate hazard '
        'impact layer during the impact analysis. It represents the '
        'cumulative count of hazard features for each area.').format(
            concept=concepts['hazard']['description']),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Count of population exposed after an EQ for a given MMI level.
population_exposed_per_mmi_field = {
    'key': 'mmi_%s_exposed',
    'name': tr('MMI %s exposed'),
    'field_name': 'mmi_%s_exposed',
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of exposed population for a given MMI level.'),
    'help_text': tr(
        'The number of exposed population for a given MMI level.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Count of fatalities after an EQ for a given MMI level.
fatalities_per_mmi_field = {
    'key': 'mmi_%s_fatalities',
    'name': tr('MMI %s fatalities'),
    'field_name': 'mmi_%s_fatalities',
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The number of fatalities for a given MMI level.'),
    'help_text': tr('The number of fatalities for a given MMI level.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}

# Count of population displaced after an EQ for a given MMI level.
population_displaced_per_mmi = {
    'key': 'mmi_%s_displaced',
    'name': tr('MMI %s displaced'),
    'field_name': 'mmi_%s_displaced',
    'type': QVariant.Int,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'help_text': tr(
        'The number of displaced population for a given MMI level.'),
    'description': tr(
        'The number of displaced population for a given MMI level.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False
}


# Productivity field
productivity_rate_field = {
    'key': 'productivity_rate_field',
    'name': tr('Productivity Rate'),
    'field_name': 'productivity_rate',
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The rate of productivity of a crop in Quintal (hundred '
        'kilograms)/Hectare unit.'),
    'help_text': tr(
        'For a land cover, productivity is the rate of product weight per '
        'area.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False,
}

productivity_field = {
    'key': 'productivity_field',
    'name': tr('Productivity'),
    'field_name': 'productivity',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': True,
    'description': tr(
        'The productivity of a crop in Quintal (hundred kilograms unit.)'),
    'help_text': tr(
        'For a land cover, productivity is the weight of product.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False,
}

affected_productivity_field = {
    'key': 'affected_productivity_field',
    'name': tr('Affected Productivity'),
    'field_name': 'affected_productivity',
    'header_name': tr('Productivity'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': True,
    'description': tr(
        'The affected productivity of a crop in Quintal (hundred kilograms '
        'unit.)'),
    'help_text': tr(
        'For a land cover, affected productivity is the weight of product '
        'that is affected by the hazard.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False,
    'units': [unit_quintal]
}

# Productivity cost field
productivity_cost_rate_field = {
    'key': 'productivity_cost_rate_field',
    'name': tr('Productivity Cost Rate'),
    'field_name': 'productivity_cost_rate',
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The rate of productivity cost of a crop in Currency/Hectare unit.'),
    'help_text': tr(
        'For a land cover, productivity cost rate is the rate of product '
        'cost per area. It is the cost to build the area.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False,
}

productivity_cost_field = {
    'key': 'productivity_cost_field',
    'name': tr('Productivity Cost'),
    'field_name': 'productivity_cost',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': True,
    'description': tr(
        'The productivity cost of a crop in Currency unit.'),
    'help_text': tr(
        'For a land cover, productivity cost is the cost to build the area.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False,
}

affected_productivity_cost_field = {
    'key': 'affected_productivity_cost_field',
    'name': tr('Affected Productivity Cost'),
    'field_name': 'affected_productivity_cost',
    'header_name': tr('Production Cost'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': True,
    'description': tr(
        'The affected productivity cost of a crop in Currency unit.'),
    'help_text': tr(
        'For a land cover, affected productivity cost is the cost to build '
        'the area that is affected by a hazard.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False,
    'units': currencies,
}


# Productivity value field
productivity_value_rate_field = {
    'key': 'productivity_value_rate_field',
    'name': tr('Productivity Value Rate'),
    'field_name': 'productivity_value_rate',
    'type': qvariant_numbers,
    'length': default_field_length,
    'precision': 0,
    'absolute': True,
    'description': tr(
        'The rate of productivity value of a crop in Currency/Hectare unit.'),
    'help_text': tr(
        'For a land cover, productivity cost rate is the rate of product '
        'cost per area. It is the value of the area.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False,
}

productivity_value_field = {
    'key': 'productivity_value_field',
    'name': tr('Productivity Value'),
    'field_name': 'productivity_value',
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': True,
    'description': tr(
        'The productivity value of a crop in Currency unit.'),
    'help_text': tr(
        'For a land cover, productivity cost is the value of the area.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False,
}

affected_productivity_value_field = {
    'key': 'affected_productivity_value_field',
    'name': tr('Affected Productivity Value'),
    'field_name': 'affected_productivity_value',
    'header_name': tr('Production Value'),
    'type': QVariant.Double,
    'length': default_field_length,
    'precision': default_field_precision,
    'absolute': True,
    'description': tr(
        'The affected productivity value of a crop in Currency unit.'),
    'help_text': tr(
        'For a land cover, affected productivity cost is the value of the '
        'area that is affected by a hazard.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    # Null value can be replaced by default or not
    'replace_null': False,
    'units': currencies,
}

# Inputs
exposure_fields = [
    exposure_id_field,
]

hazard_fields = [
    hazard_id_field,
]

aggregation_fields = [
    aggregation_id_field,
    aggregation_name_field
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
    male_count_field,
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

aggregation_summary_fields = [
    aggregation_id_field,
    aggregation_name_field,
    affected_exposure_count_field,
    total_affected_field,
]

exposure_summary_table_fields = [
    exposure_class_field,
    hazard_count_field,
    total_affected_field,
    total_not_affected_field,
    total_not_exposed_field,
    total_field,
]

analysis_fields = [
    analysis_id_field,
    analysis_name_field,
    hazard_count_field,
    total_affected_field,
    total_not_affected_field,
    total_not_exposed_field,
    total_field
]

# Field that can be used to summarize / aggregate the result in exposure
# summary table
summarizer_fields = [
    productivity_field,
    productivity_cost_field,
    productivity_value_field
]

# Mapping between summarizer field and its affected fields in the exposure
# summary table
affected_summarizer_fields = {
    productivity_field['key']: affected_productivity_field,
    productivity_cost_field['key']: affected_productivity_cost_field,
    productivity_value_field['key']: affected_productivity_value_field,
}

# Add also minimum needs fields
from safe.definitions.minimum_needs import minimum_needs_fields  # noqa
count_fields = [
    feature_value_field,
    population_count_field,
    displaced_field,
    fatalities_field,
    # Gender count fields
    female_count_field,
    child_bearing_age_count_field,
    pregnant_count_field,
    lactating_count_field,
    male_count_field,
    # Additional needs count fields
    hygiene_packs_count_field,
    additional_rice_count_field,
    # Age count fields
    infant_count_field,
    child_count_field,
    youth_count_field,
    adult_count_field,
    elderly_count_field,
    # Vulnerability fields
    under_5_count_field,
    over_60_count_field,
    disabled_count_field,
    # Displaced
    # Gender displaced count fields
    female_displaced_count_field,
    child_bearing_age_displaced_count_field,
    pregnant_displaced_count_field,
    lactating_displaced_count_field,
    male_displaced_count_field,
    # Age count fields
    infant_displaced_count_field,
    child_displaced_count_field,
    youth_displaced_count_field,
    adult_displaced_count_field,
    elderly_displaced_count_field,
    # Vulnerability fields
    under_5_displaced_count_field,
    over_60_displaced_count_field,
    disabled_displaced_count_field
] + minimum_needs_fields

# And also additional minimum needs
additional_minimum_needs = [
    hygiene_packs_count_field,
    additional_rice_count_field
]
