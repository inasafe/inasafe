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
    'default_value': 0.496,
    # Updated for InaSAFE 4.1
    # UNSD World Data, 2010.
    'min_value': 0,
    'max_value': 1,
    'increment': 0.001,
    'description': tr(
        'Default ratio of females per 100 people in the total population.')
}

male_ratio_default_value = {
    'key': 'male_ratio_default_value',
    'name': tr('Male Ratio Global Default'),
    'default_value': 0.504,
    # Updated for InaSAFE 4.1
    # UNSD World Data, 2010.
    'min_value': 0,
    'max_value': 1,
    'increment': 0.001,
    'description': tr(
        'Default ratio of males per 100 people in the total population.')
}

feature_rate_default_value = {
    'key': 'feature_rate_default_value',
    'name': tr('Feature Rate Global Default'),
    'default_value': 1000000,
    'min_value': 0,
    'max_value': 1000000000,
    'increment': 1000000,
    'description': tr('Default value for feature rate per m²')
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

# Default ratios for world population revised 9 May 2017.
# update to address new concepts in 4.1 and to better align with humanitarian
# analysis and reporting.
# http://data.un.org/
# Source:  United Nations Statistics Division. World Data 2010.


infant_ratio_default_value = {
    'key': 'infant_ratio_default_value',
    'name': tr('Infant Ratio Global Default'),
    'default_value': 0.0925,
    # http://data.un.org/Data.aspx?d=PopDiv&f=variableID%3a30
    # UNSD World Data, 2010.
    'min_value': 0,
    'max_value': 1,
    'increment': 0.001,
    'description': tr(
        'Default ratio of infants per 100 people in the total population.')
}

child_ratio_default_value = {
    'key': 'child_ratio_default_value',
    'name': tr('Child Ratio Global Default'),
    'default_value': 0.1735,
    # http://data.un.org/Data.aspx?d=PopDiv&f=variableID%3a31
    # UNSD World Data, 2010.
    'min_value': 0,
    'max_value': 1,
    'increment': 0.001,
    'description': tr(
        'Default ratio of children per 100 people in the total population.')
}

youth_ratio_default_value = {
    'key': 'youth_ratio_default_value',
    'name': tr('Youth Ratio Global Default'),
    # Updated from 0.263 to 0.254 in InaSAFE 4.0
    # Updated for InaSAFE 4.1
    # http://data.un.org/Data.aspx?d=PopDiv&f=variableID%3a101
    # UNSD World Data, 2010.
    'default_value': 0.266,
    'min_value': 0,
    'max_value': 1,
    'increment': 0.001,
    'description': tr(
        'Default ratio of youths per 100 people in the total population.')
}

adult_ratio_default_value = {
    'key': 'adult_ratio_default_value',
    'name': tr('Adult Ratio Global Default'),
    # Updated for InaSAFE 4.1
    # http://data.un.org/Data.aspx?d=PopDiv&f=variableID%3a103
    # UNSD World Data, 2010.
    'default_value': 0.657,
    'min_value': 0,
    'max_value': 1,
    'increment': 0.001,
    'description': tr(
        'Default ratio of adults per 100 people in the total population.')
}

elderly_ratio_default_value = {
    'key': 'elderly_ratio_default_value',
    'name': tr('Elderly Ratio Global Default'),
    # Updated from 0.078 to 0.087 in InaSAFE 4.0
    # Updated for InaSAFE 4.1
    # http://data.un.org/Data.aspx?d=PopDiv&f=variableID%3a103
    # UNSD World Data, 2010.
    'default_value': 0.077,
    'min_value': 0,
    'max_value': 1,
    'increment': 0.001,
    'description': tr('Default ratio of elderly people per 100 people in the '
                      'total population.')
}

# Default values for vulnerabilities
under_5_ratio_default_value = {
    'key': 'under_5_ratio_default_value',
    'name': tr('Under 5 Years Ratio Global Default'),
    'default_value': 0.093,
    # Updated for InaSAFE 4.1
    # http://data.un.org/Data.aspx?d=PopDiv&f=variableID%3a30
    # UNSD World Data, 2010.
    'min_value': 0,
    'max_value': 1,
    'increment': 0.001,
    'description': tr(
        'Default ratio of under 5 year olds per 100 people in the total '
        'population.')
}

over_60_ratio_default_value = {
    'key': 'over_60_ratio_default_value',
    'name': tr('Over 60 Years Ratio Global Default'),
    'default_value': 0.111,
    # Updated for InaSAFE 4.1
    # http://data.un.org/Data.aspx?d=PopDiv&f=variableID%3a103
    # UNSD World Data, 2010.
    'min_value': 0,
    'max_value': 1,
    'increment': 0.001,
    'description': tr(
        'Default ratio of over 60 year olds per 100 people in the total '
        'population.')
}

disabled_ratio_default_value = {
    'key': 'disabled_ratio_default_value',
    'name': tr('Disabled Ratio Global Default'),
    'default_value': 0.15,
    # Updated for InaSAFE 4.1
    # http://www.who.int/disabilities/world_report/2011/report.pdf
    'min_value': 0,
    'max_value': 1,
    'increment': 0.001,
    'description': tr(
        'Default ratio of disabled people per 100 people in the total '
        'population.')
}

child_bearing_age_ratio_default_value = {
    'key': 'child_bearing_age_ratio_default_value',
    'name': tr('Child Bearing Age Ratio Global Default'),
    'default_value': 0.259,
    # Updated for InaSAFE 4.1
    # http://data.un.org/Data.aspx?d=PopDiv&f=variableID%3a36
    # UNSD World Data, 2010.
    'min_value': 0,
    'max_value': 1,
    'increment': 0.001,
    'description': tr(
        'Default ratio of child bearing age per 100 people in the '
        'total population.')
}

pregnant_ratio_default_value = {
    'key': 'pregnant_ratio_default_value',
    'name': tr('Pregnant Ratio Global Default'),
    'default_value': 0.024,
    # Updated for InaSAFE 4.1
    # http://www.spherehandbook.org/en/appendix-6/
    # UNSD World Population Data, 2010.
    'min_value': 0,
    'max_value': 1,
    'increment': 0.001,
    'description': tr(
        'Default ratio of pregnant people per 100 people in the total '
        'population.')
}
lactating_ratio_default_value = {
    'key': 'lactating_ratio_default_value',
    'name': tr('Lactating Ratio Global Default'),
    'default_value': 0.026,
    # Updated for InaSAFE 4.1
    # http://www.spherehandbook.org/en/appendix-6/
    # UNSD World Population Data, 2010.
    'min_value': 0,
    'max_value': 1,
    'increment': 0.001,
    'description': tr(
        'Default ratio of lactating people per 100 people in the total '
        'population.')
}
