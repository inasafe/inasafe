# coding=utf-8

"""Definitions relating to group of fields."""

from safe.utilities.i18n import tr

from safe.definitions.fields import (
    youth_count_field,
    adult_count_field,
    elderly_count_field,
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field
)

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

age_count_group = {
    'key': 'age_count_group',
    'name': 'Age Count Group',
    'description': tr(
        'The group of fields that consists of population count per age '
        'class.'),
    'fields': [
        youth_count_field,
        adult_count_field,
        elderly_count_field
    ]
}

age_ratio_group = {
    'key': 'age_ratio_group',
    'name': 'Age Ratio Group',
    'description': tr(
        'The group of fields that consists of population ratio per age '
        'class.'),
    'fields': [
        youth_ratio_field,
        adult_ratio_field,
        elderly_ratio_field
    ]
}

field_groups_all = [
    age_count_group,
    age_ratio_group
]
