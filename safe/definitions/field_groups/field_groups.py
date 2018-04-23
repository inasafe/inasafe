# coding=utf-8

"""Definitions relating to group of fields."""
from builtins import range

from safe.definitions.concepts import concepts
from safe.definitions.field_groups.age_field_group import (
    age_ratio_group,
    age_count_group,
    age_displaced_count_group)
from safe.definitions.field_groups.age_vulnerability_field_group import (
    age_vulnerability_ratio_group,
    age_vulnerability_count_group,
    age_vulnerability_displaced_count_group)
from safe.definitions.field_groups.disability_vulnerability_field_group \
    import (
        disability_vulnerability_ratio_group,
        disability_vulnerability_count_group,
        disability_vulnerability_displaced_count_group)
from safe.definitions.field_groups.gender_field_group import (
    gender_ratio_group,
    gender_count_group,
    gender_displaced_count_group)
from safe.definitions.field_groups.gender_vulnerability_field_group import (
    gender_vulnerability_ratio_group,
    gender_vulnerability_count_group,
    gender_vulnerability_displaced_count_group)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

aggregation_field_groups = [
    age_ratio_group,
    gender_ratio_group,
    age_vulnerability_ratio_group,
    gender_vulnerability_ratio_group,
    disability_vulnerability_ratio_group
]

population_field_groups = [
    age_count_group,
    gender_count_group,
    age_vulnerability_count_group,
    gender_vulnerability_count_group,
    disability_vulnerability_count_group
]

# Count ratio pairs field group
count_ratio_group_pairs = [
    (gender_count_group, gender_ratio_group),
    (age_count_group, age_ratio_group),
    (age_vulnerability_count_group, age_vulnerability_ratio_group),
    (gender_vulnerability_count_group, gender_vulnerability_ratio_group),
    (disability_vulnerability_count_group,
     disability_vulnerability_ratio_group)
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
    disability_vulnerability_ratio_group,
    disability_vulnerability_count_group,
    disability_vulnerability_displaced_count_group,
    gender_vulnerability_ratio_group,
    gender_vulnerability_count_group,
    gender_vulnerability_displaced_count_group,
    age_vulnerability_ratio_group,
    age_vulnerability_count_group,
    age_vulnerability_displaced_count_group
]

# Update notes for each group
age_group_notes = [
    tr('Infant: {note}').format(note=concepts['infant']['description']),
    tr('Child: {note}').format(note=concepts['child']['description']),
    tr('Youth: {note}').format(note=concepts['youth']['description']),
    tr('Adult: {note}').format(note=concepts['adult']['description']),
    tr('Elderly: {note}').format(note=concepts['elderly']['description'])
]

gender_group_notes = [
    tr('Male: {note}').format(note=concepts['male']['description']),
    tr('Female: {note}').format(note=concepts['female']['description']),
]

age_vulnerability_group_notes = [
    tr('Under 5: {note}').format(note=concepts['under_5']['description']),
    tr('Over 60: {note}').format(note=concepts['over_60']['description']),
]

gender_vulnerability_group_notes = [
    tr('Child bearing age: {note}').format(
        note=concepts['child_bearing_age']['description']),
    tr('Pregnant: {note}').format(
        note=concepts['pregnant']['description']),
    tr('Lactating: {note}').format(
        note=concepts['lactating']['description'])
]

disability_vulnerability_group_notes = [
    tr('Disabled: {note}').format(note=concepts['disabled']['description'])
]

age_ratio_group['notes'] += age_group_notes
age_count_group['notes'] += age_group_notes
age_displaced_count_group['notes'] += age_group_notes
gender_ratio_group['notes'] += gender_group_notes
gender_count_group['notes'] += gender_group_notes
gender_displaced_count_group['notes'] += gender_group_notes
age_vulnerability_ratio_group['notes'] += age_vulnerability_group_notes
age_vulnerability_count_group['notes'] += age_vulnerability_group_notes
age_vulnerability_displaced_count_group['notes'] += \
    age_vulnerability_group_notes
gender_vulnerability_ratio_group['notes'] += \
    gender_vulnerability_group_notes
gender_vulnerability_count_group['notes'] += \
    gender_vulnerability_group_notes
gender_vulnerability_displaced_count_group['notes'] += \
    gender_vulnerability_group_notes
disability_vulnerability_ratio_group['notes'] += \
    disability_vulnerability_group_notes
disability_vulnerability_count_group['notes'] += \
    disability_vulnerability_group_notes
disability_vulnerability_displaced_count_group['notes'] += \
    disability_vulnerability_group_notes

# see issue #4334

# for field_group in all_field_groups:
#     field_group['notes'].insert(
#         0,
#         tr('{group_name} group: {note}').format(
#             group_name=field_group['name'],
#             note=field_group['description']))
#     del field_group  # to prevent duplicate definition

displaced_field_groups = [
    age_displaced_count_group,
    gender_displaced_count_group,
    age_vulnerability_displaced_count_group,
    gender_vulnerability_displaced_count_group,
    disability_vulnerability_displaced_count_group
]

vulnerability_displaced_count_groups = [
    age_vulnerability_displaced_count_group,
    gender_vulnerability_displaced_count_group,
    disability_vulnerability_displaced_count_group
]
