# coding=utf-8
"""Definitions relating to default value."""

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

female_ratio_default_value = {
    'key': 'female_ratio_default_value',
    'name': tr('Female Ratio Global Default'),
    # https://www.cia.gov/library/publications/the-world-factbook/geos/xx.html
    # total population: 1.01 male(s)/female (2011 est.)
    'default_value': 0.5,
    'min_value': 0,
    'max_value': 1,
    'description': tr('Default value for female ratio')
}

male_ratio_default_value = {
    'key': 'male_ratio_default_value',
    'name': tr('Male Ratio Global Default'),
    # https://www.cia.gov/library/publications/the-world-factbook/geos/xx.html
    # total population: 1.01 male(s)/female (2011 est.)
    'default_value': 0.5,
    'min_value': 0,
    'max_value': 1,
    'description': tr('Default value for male ratio')
}

feature_rate_default_value = {
    'key': 'feature_rate_default_value',
    'name': tr('Feature Rate Global Default'),
    'default_value': 1000000,
    'min_value': 0,
    'max_value': 1000000000,
    'description': tr(u'Default value for feature rate per m²')
}

# Note(IS): I copy here to preserve the history

# https://www.cia.gov/library/publications/the-world-factbook/geos/xx.html
# Age structure:
# 0-14 years: 26.3% (male 944,987,919/female 884,268,378)
# 15-64 years: 65.9% (male 2,234,860,865/female 2,187,838,153)
# 65 years and over: 7.9% (male 227,164,176/female 289,048,221) (2011 est.)

# NOTE (MB) CIA can not do maths!!!  this gives 100.1%
# inaSAFE can, thus we remove 0.1% from the elderly
# I wrote them and got this contact confirmation number: CTCU1K2

# Default ratios for world population revised 21 December 2016.
# https://www.cia.gov/library/publications/resources/the-world-factbook/
# fields/2010.html#4

# 0-14 years: 25.44% (male 963,981,944/female 898,974,458)
# 15-24 years: 16.16% (male 611,311,930/female 572,229,547)
# 25-54 years: 41.12% (male 1,522,999,578/female 1,488,011,505)
# 55-64 years: 8.6% (male 307,262,939/female 322,668,546)
# 65 years and over: 8.68% (male 283,540,918/female 352,206,092)(2016 est.)

# if CM can add up then youth 0.254; adult 0.659; elderly 0.087

# TODO(IS): Please complete this
infant_ratio_default_value = {
    'key': 'infant_ratio_default_value',
    'name': tr('Infant Ratio Global Default'),
    'default_value': 0.0,  # FIXME:It's random number
    'min_value': 0,
    'max_value': 1,
    'description': tr('Default value for infant ratio')
}

child_ratio_default_value = {
    'key': 'child_ratio_default_value',
    'name': tr('Child Ratio Global Default'),
    'default_value': 0.0,  # FIXME:It's random number
    'min_value': 0,
    'max_value': 1,
    'description': tr('Default value for child ratio')
}

youth_ratio_default_value = {
    'key': 'youth_ratio_default_value',
    'name': tr('Youth Ratio Global Default'),
    # Updated from 0.263 to 0.254 in InaSAFE 4.0
    'default_value': 0.254,
    'min_value': 0,
    'max_value': 1,
    'description': tr('Default value for youth ratio')
}

adult_ratio_default_value = {
    'key': 'adult_ratio_default_value',
    'name': tr('Adult Ratio Global Default'),
    'default_value': 0.659,
    'min_value': 0,
    'max_value': 1,
    'description': tr('Default value for adult ratio')
}

elderly_ratio_default_value = {
    'key': 'elderly_ratio_default_value',
    'name': tr('Elderly Ratio Global Default'),
    # Updated from 0.078 to 0.087 in InaSAFE 4.0
    'default_value': 0.087,
    'min_value': 0,
    'max_value': 1,
    'description': tr('Default value for elderly ratio')
}

# Default values for vulnerabilities
under_5_ratio_default_value = {
    'key': 'under_5_ratio_default_value',
    'name': tr('Under 5 Years Ratio Global Default'),
    'default_value': 0.0,  # FIXME:It's random number
    'min_value': 0,
    'max_value': 1,
    'description': tr('Default value for under 5 years old ratio')
}

over_60_ratio_default_value = {
    'key': 'over_60_ratio_default_value',
    'name': tr('Over 60 Years Ratio Global Default'),
    'default_value': 0.0,  # FIXME:It's random number
    'min_value': 0,
    'max_value': 1,
    'description': tr('Default value for over 60 years old ratio')
}

disabled_ratio_default_value = {
    'key': 'disabled_ratio_default_value',
    'name': tr('Disabled Ratio Global Default'),
    'default_value': 0.0,  # FIXME:It's random number
    'min_value': 0,
    'max_value': 1,
    'description': tr('Default value for disabled people ratio')
}
