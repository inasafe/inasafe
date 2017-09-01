# coding=utf-8
"""Gender related field groups."""

from safe.definitions.fields import (
    female_ratio_field,
    male_ratio_field,
    female_count_field,
    male_count_field,
    male_displaced_count_field,
    female_displaced_count_field)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

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
        male_ratio_field,
        female_ratio_field,
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
        'in each age group.'),
    'fields': [
        male_count_field,
        female_count_field,
    ],
    # Exclusive = False: able to put same layer's field to some fields
    # Exclusive = True: only able to put a layer's field to a field
    'exclusive': True,
    'notes': []
}
gender_displaced_count_group = {
    'key': 'gender_displaced_count_group',
    'name': tr('Gender Displaced Count'),
    'header_name': tr('Gender'),
    'description': tr(
        'Demographic breakdown produced for displaced population based on '
        'gender specific groups (pregnant, lactating etc.). These demographic '
        'concepts provide a detailed break down of the number of people '
        'displaced in each gender specific group.'),
    'fields': [
        male_displaced_count_field,
        female_displaced_count_field,
    ],
    # Exclusive = False: able to put same layer's field to some fields
    # Exclusive = True: only able to put a layer's field to a field
    'exclusive': True,
    'notes': []
}
