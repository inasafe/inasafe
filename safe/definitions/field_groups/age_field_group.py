# coding=utf-8

"""Definitions about the age field group."""

from safe.definitions.fields import (
    infant_ratio_field,
    child_ratio_field,
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field,
    infant_count_field,
    child_count_field,
    youth_count_field,
    adult_count_field,
    elderly_count_field,
    infant_displaced_count_field,
    child_displaced_count_field,
    youth_displaced_count_field,
    adult_displaced_count_field,
    elderly_displaced_count_field)
from safe.utilities.i18n import tr

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
        'aggregation layer that contains detailed demographic information ('
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
    'constraints': {}
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
    'header_name': tr('Age'),
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
    'notes': [],
    'section_unavailable_note:': tr(
        'No age ratios provided, no demographic breakdown for age carried out.'
    )
}
