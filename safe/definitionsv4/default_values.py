# coding=utf-8
"""Definitions relating to default value."""

from safe.utilities.i18n import tr

female_ratio_default_value = {
    'key': 'female_ratio_default_value',
    'name': tr('Female Ratio Default Value'),
    'default_value': 0.5,
    'min_value': 0,
    'max_value': 1,
    'description': tr('Default value for female ratio')
}

feature_rate_default_value = {
    'key': 'feature_rate_default_value',
    'name': tr('Feature Rate Default Value'),
    'default_value': 1000000,
    'min_value': 0,
    'max_value': 1000000000,
    'description': tr('Default value for feature rate per m^2')
}

youth_ratio_default_value = {
    'key': 'youth_ratio_default_value',
    'name': tr('Youth Ratio Default Value'),
    'default_value': 0.263,  # From CIA world fact book
    'min_value': 0,
    'max_value': 1,
    'description': tr('Default value for youth ratio')
}

adult_ratio_default_value = {
    'key': 'adult_ratio_default_value',
    'name': tr('Adult Ratio Default Value'),
    'default_value': 0.659,  # From CIA world fact book
    'min_value': 0,
    'max_value': 1,
    'description': tr('Default value for adult ratio')
}

elderly_ratio_default_value = {
    'key': 'elderly_ratio_default_value',
    'name': tr('Eldery Ratio Default Value'),
    'default_value': 0.078,  # From CIA world fact book
    'min_value': 0,
    'max_value': 1,
    'description': tr('Default value for elderly ratio')
}
