# coding=utf-8

"""Definitions relating to group of fields."""

from safe.utilities.i18n import tr
from safe.definitions.concepts import concepts

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
        'Demographic breakdown to use for displaced population based on age '
        'groups. Age ratio groupings are used when there is a vector '
        'aggregation layer that contains detailed demographic information ( '
        'as ratios) about the population living in each administrative or '
        'census area. These ratios are then applied to the count of displaced '
        'population per aggregation area to provide a more detailed break '
        'down of the number of people displaced in each age group.'),
    'fields': [
        infant_ratio_field,
        child_ratio_field,
        youth_ratio_field,
        adult_ratio_field,
        elderly_ratio_field
    ],
    # Exclusive = False: able to put same layer's field to some fields
    # Exclusive = True: only able to put a layer's field to a field
    'exclusive': False,
    'notes': [],
    'constraints': {
        'sum': {
            'kwargs': {
                'max': 1
            },
            'message': tr('The sum of age ratios should not more than 1.')
        }
    }
}

age_count_group = {
    'key': 'age_count_group',
    'name': tr('Age Count'),
    'description': tr(
        'Demographic breakdown to use for displaced population based on age '
        'groups. Age count groupings are used when there is a vector '
        'population dataset that contains detailed demographic information ('
        'as counts) about the population living in each administrative or '
        'census area.'
    ),
    'fields': [
        infant_count_field,
        child_count_field,
        youth_count_field,
        adult_count_field,
        elderly_count_field
    ],
    # Exclusive = False: able to put same layer's field to some fields
    # Exclusive = True: only able to put a layer's field to a field
    'exclusive': False,
    'notes': []
}

age_displaced_count_group = {
    'key': 'age_displaced_count_group',
    'name': tr('Age Displaced Count'),
    'description': tr(
        'Demographic breakdown produced for displaced population based on age '
        'groups. These demographic concepts provide a detailed break '
        'down of the number of people displaced in each age group.'),
    'fields': [
        infant_displaced_count_field,
        child_displaced_count_field,
        youth_displaced_count_field,
        adult_displaced_count_field,
        elderly_displaced_count_field
    ],
    # Exclusive = False: able to put same layer's field to some fields
    # Exclusive = True: only able to put a layer's field to a field
    'exclusive': False,
    'notes': []
}

gender_ratio_group = {
    'key': 'gender_ratio_group',
    'name': tr('Gender Ratio'),
    'description': tr(
        'Demographic breakdown to use for displaced population based on '
        'gender. Gender ratio groupings are used when there is a vector '
        'aggregation layer that contains detailed demographic information ( '
        'as ratios) about the population living in each administrative or '
        'census area. These ratios are then applied to the count of displaced '
        'population per aggregation area to provide a more detailed break '
        'down of the number of people displaced in each gender profile. '
        'Gender specific info can include criteria like the number of '
        'females, the number of females of child bearing age, and so on.'),
    'fields': [
        female_ratio_field,
        child_bearing_age_ratio_field,
        pregnant_lactating_ratio_field
    ],
    # Exclusive = False: able to put same layer's field to some fields
    # Exclusive = True: only able to put a layer's field to a field
    'exclusive': True,
    'notes': []
}

gender_count_group = {
    'key': 'gender_count_group',
    'name': tr('Gender Count'),
    'description': tr(
        'Demographic breakdown produced for displaced population based on '
        'gender groups (female, pregnant, etc.). These demographic concepts '
        'provide a detailed break down of the number of people displaced '
        'in each gender group.'),
    'fields': [
        female_count_field,
        child_bearing_age_count_field,
        pregnant_lactating_count_field
    ],
    # Exclusive = False: able to put same layer's field to some fields
    # Exclusive = True: only able to put a layer's field to a field
    'exclusive': True,
    'notes': []
}

gender_displaced_count_group = {
    'key': 'gender_displaced_count_group',
    'name': tr('Gender Displaced Count'),
    'description': tr(
        'Demographic breakdown produced for displaced population based on'
        'gender specific groups (pregnant, lactating etc.). These demographic '
        'concepts provide a detailed break down of the number of people '
        'displaced in each gender specific group.'),
    'fields': [
        female_displaced_count_field,
        child_bearing_age_displaced_count_field,
        pregnant_lactating_displaced_count_field
    ],
    # Exclusive = False: able to put same layer's field to some fields
    # Exclusive = True: only able to put a layer's field to a field
    'exclusive': True,
    'notes': []
}

vulnerability_ratio_group = {
    'key': 'vulnerability_ratio_group',
    'name': tr('Vulnerability Ratio'),
    'description': tr(
        'Demographic breakdown to use for displaced population based on '
        'vulnerability. Vulnerability ratio groupings are used when there '
        'is a vector aggregation layer that contains detailed demographic '
        'information (as ratios) about the population living in each '
        'administrative or census area. These ratios are then applied to the '
        'count of displaced population per aggregation area to provide a more '
        'detailed break down of the number of people displaced in each '
        'vulnerability profile. Vulnerable segments of the population '
        'can include criteria like the number of infants, the number of '
        'elderly, the number of disabled people, and so on.'),
    'fields': [
        under_5_ratio_field,
        over_60_ratio_field,
        disabled_ratio_field
    ],
    # Exclusive = False: able to put same layer's field to some fields
    # Exclusive = True: only able to put a layer's field to a field
    'exclusive': False,
    'notes': [],
    'constraints': {
        'sum': {
            'kwargs': {
                'max': 1
            },
            'message': tr(
                'The sum of vulnerability ratios should not more than 1.')
        }
    }
}

vulnerability_count_group = {
    'key': 'vulnerability_count_group',
    'name': tr('Vulnerability Count'),
    'description': tr(
        'Demographic breakdown to use for displaced population based on '
        'vulnerability. Vulnerability count groupings are used when there '
        'is a vector exposure layer that contains detailed demographic '
        'information (as counts) about the population living in each '
        'area. These counts are then used to calculate the ratio of '
        'vulnerable population sectors for each aggregation area. These are '
        'then used to produce a detailed break down of the number of '
        'displaced people in each vulnerability profile. Vulnerable segments '
        'of the population can include criteria like the number of infants, '
        'the number of elderly, the number of disabled people, and so on.'),
    'fields': [
        under_5_count_field,
        over_60_count_field,
        disabled_count_field
    ],
    # Exclusive = False: able to put same layer's field to some fields
    # Exclusive = True: only able to put a layer's field to a field
    'exclusive': False,
    'notes': []
}

vulnerability_displaced_count_group = {
    'key': 'vulnerability_displaced_count_group',
    'name': tr('Vulnerability Displaced Count'),
    'description': tr(
        'Demographic breakdown to use for displaced population based on '
        'vulnerability. These data are presented in the report as the number '
        'of displaced people in each vulnerability profile. Vulnerable '
        'segments of the population can include criteria like the number of '
        'infants, the number of elderly, the number of disabled people, and '
        'so on.'),
    'fields': [
        under_5_displaced_count_field,
        over_60_displaced_count_field,
        disabled_displaced_count_field
    ],
    # Exclusive = False: able to put same layer's field to some fields
    # Exclusive = True: only able to put a layer's field to a field
    'exclusive': False,
    'notes': []
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

# Update notes for each group
age_group_notes = [
        tr('Infant: {note}'.format(note=concepts['infant']['description'])),
        tr('Child: {note}'.format(note=concepts['child']['description'])),
        tr('Youth: {note}'.format(note=concepts['youth']['description'])),
        tr('Adult: {note}'.format(note=concepts['adult']['description'])),
        tr('Elderly: {note}'.format(note=concepts['elderly']['description']))
    ]

gender_group_notes = [
        tr('Female: {note}'.format(note=concepts['female']['description'])),
        tr('Child bearing age: {note}'.format(
            note=concepts['child_bearing_age']['description'])),
        tr('Pregnant lactating: {note}'.format(
            note=concepts['pregnant_lactating']['description']))
    ]

vulnerability_group_notes = [
        tr('Under 5: {note}'.format(note=concepts['under_5']['description'])),
        tr('Over 60: {note}'.format(note=concepts['over_60']['description'])),
        tr('Disabled: {note}'.format(note=concepts['disabled']['description']))
    ]

age_ratio_group['notes'] += age_group_notes
age_count_group['notes'] += age_group_notes
age_displaced_count_group['notes'] += age_group_notes
gender_ratio_group['notes'] += gender_group_notes
gender_count_group['notes'] += gender_group_notes
gender_displaced_count_group['notes'] += gender_group_notes
vulnerability_ratio_group['notes'] += vulnerability_group_notes
vulnerability_count_group['notes'] += vulnerability_group_notes
vulnerability_displaced_count_group['notes'] += vulnerability_group_notes

for field_group in all_field_groups:
    field_group['notes'].insert(
        0,
        tr('{group_name} group: {note}'.format(
            group_name=field_group['name'],
            note=field_group['description'])))
    del field_group  # to prevent duplicate definition
