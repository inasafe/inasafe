# coding=utf-8

"""Definitions relating to group of fields."""

from safe.utilities.i18n import tr

from safe.definitions.fields import (
    infant_count_field,
    child_count_field,
    youth_count_field,
    adult_count_field,
    elderly_count_field,
    infant_ratio_field,
    child_ratio_field,
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field,
    female_ratio_field,
    male_ratio_field,
    female_count_field,
    male_count_field,
    under_5_ratio_field,
    over_60_ratio_field,
    disabled_ratio_field,
    under_5_count_field,
    over_60_count_field,
    disabled_count_field,
    child_bearing_age_ratio_field,
    pregnant_lactating_ratio_field,
    child_bearing_age_count_field,
    pregnant_lactating_count_field,
    infant_displaced_count_field,
    child_displaced_count_field,
    youth_displaced_count_field,
    adult_displaced_count_field,
    elderly_displaced_count_field,
    female_displaced_count_field,
    child_bearing_age_displaced_count_field,
    pregnant_lactating_displaced_count_field,
    under_5_displaced_count_field,
    over_60_displaced_count_field,
    disabled_displaced_count_field
)

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

age_ratio_group = {
    'key': 'age_ratio_group',
    'name': tr('Age Ratio'),
    'description': tr(
        'The group of fields that consists of population ratio per age '
        'class.'),
    'fields': [
        infant_ratio_field,
        child_ratio_field,
        youth_ratio_field,
        adult_ratio_field,
        elderly_ratio_field
    ]
}

age_count_group = {
    'key': 'age_count_group',
    'name': tr('Age Count'),
    'description': tr(
        'The group of fields that consists of population count per age '
        'class.'),
    'fields': [
        infant_count_field,
        child_count_field,
        youth_count_field,
        adult_count_field,
        elderly_count_field
    ]
}

age_displaced_count_group = {
    'key': 'age_displaced_count_group',
    'name': tr('Age Displaced Count'),
    'description': tr(
        'The group of fields that consists of displaced population count per '
        'age '
        'class.'),
    'fields': [
        infant_displaced_count_field,
        child_displaced_count_field,
        youth_displaced_count_field,
        adult_displaced_count_field,
        elderly_displaced_count_field
    ]
}

gender_ratio_group = {
    'key': 'gender_ratio_group',
    'name': tr('Gender Ratio'),
    'description': tr(
        'The group of fields that consists of population ratio per gender '
        'class.'),
    'fields': [
        female_ratio_field,
        child_bearing_age_ratio_field,
        pregnant_lactating_ratio_field
    ]
}

gender_count_group = {
    'key': 'gender_count_group',
    'name': tr('Gender Count'),
    'description': tr(
        'The group of fields that consists of population count per gender '
        'class.'),
    'fields': [
        female_count_field,
        child_bearing_age_count_field,
        pregnant_lactating_count_field
    ]
}

gender_displaced_count_group = {
    'key': 'gender_displaced_count_group',
    'name': tr('Gender Displaced Count'),
    'description': tr(
        'The group of fields that consists of displaced population count per '
        'gender class.'),
    'fields': [
        female_displaced_count_field,
        child_bearing_age_displaced_count_field,
        pregnant_lactating_displaced_count_field
    ]
}

vulnerability_ratio_group = {
    'key': 'vulnerability_ratio_group',
    'name': tr('Vulnerability Ratio'),
    'description': tr(
        'The group of fields that consists of population ratio per '
        'vulnerability class.'),
    'fields': [
        under_5_ratio_field,
        over_60_ratio_field,
        disabled_ratio_field
    ]
}

vulnerability_count_group = {
    'key': 'vulnerability_count_group',
    'name': tr('Vulnerability Count'),
    'description': tr(
        'The group of fields that consists of population count per '
        'vulnerability class.'),
    'fields': [
        under_5_count_field,
        over_60_count_field,
        disabled_count_field
    ]
}

vulnerability_displaced_count_group = {
    'key': 'vulnerability_displaced_count_group',
    'name': tr('Vulnerability Displaced Count'),
    'description': tr(
        'The group of fields that consists of displaced population count per '
        'vulnerability class.'),
    'fields': [
        under_5_displaced_count_field,
        over_60_displaced_count_field,
        disabled_displaced_count_field
    ]
}

aggregation_field_groups = [
    age_ratio_group,
    gender_ratio_group,
    vulnerability_ratio_group
]

exposure_field_groups = [
    age_count_group,
    gender_count_group,
    vulnerability_count_group
]

# Count ratio pairs field group
count_ratio_group_pairs = [
    (gender_count_group, gender_ratio_group),
    (age_count_group, age_ratio_group),
    (vulnerability_count_group, vulnerability_ratio_group)
]


# This table is useful when we need to match between counts and ratios.
count_ratio_mapping = {
    # feature_value_field['key']: feature_rate_field['key'], disabled V4.0 ET
}

# Generate count ratio mapping from the count ratio field group pairs
for count_ratio_pair in count_ratio_group_pairs:
    count_fields = count_ratio_pair[0]['fields']
    ratio_fields = count_ratio_pair[1]['fields']
    for index in range(len(count_fields)):
        count_ratio_mapping[
            count_fields[index]['key']] = ratio_fields[index]['key']

all_field_groups = [
    age_ratio_group,
    age_count_group,
    age_displaced_count_group,
    gender_ratio_group,
    gender_count_group,
    gender_displaced_count_group,
    vulnerability_ratio_group,
    vulnerability_count_group,
    vulnerability_displaced_count_group
]
