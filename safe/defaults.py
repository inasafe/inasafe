# coding=utf-8
"""**SAFE (Scenario Assessment For Emergencies) - API**

The purpose of the module is to provide a well defined public API
for the packages that constitute the SAFE engine. Modules using SAFE
should only need to import functions from here.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '05/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from safe_extras.parameters.resource_parameter import ResourceParameter

from safe.common.utilities import ugettext as tr

DEFAULTS = dict()

# https://www.cia.gov/library/publications/the-world-factbook/geos/xx.html
# total population: 1.01 male(s)/female (2011 est.)
DEFAULTS['FEMALE_RATIO'] = 0.50

# https://www.cia.gov/library/publications/the-world-factbook/geos/xx.html
# Age structure:
# 0-14 years: 26.3% (male 944,987,919/female 884,268,378)
# 15-64 years: 65.9% (male 2,234,860,865/female 2,187,838,153)
# 65 years and over: 7.9% (male 227,164,176/female 289,048,221) (2011 est.)

# NOTE (MB) CIA can not do maths!!!  this gives 100.1%
# inaSAFE can, thus we remove 0.1% from the elderly
# I wrote them and got this contact confirmation number: CTCU1K2

DEFAULTS['YOUTH_RATIO'] = 0.263
DEFAULTS['ADULT_RATIO'] = 0.659
DEFAULTS['ELDERLY_RATIO'] = 0.078

# Keywords key names
DEFAULTS['FEMALE_RATIO_ATTR_KEY'] = 'female ratio attribute'
DEFAULTS['FEMALE_RATIO_KEY'] = 'female ratio default'
DEFAULTS['YOUTH_RATIO_ATTR_KEY'] = 'youth ratio attribute'
DEFAULTS['YOUTH_RATIO_KEY'] = 'youth ratio default'
DEFAULTS['ADULT_RATIO_ATTR_KEY'] = 'adult ratio attribute'
DEFAULTS['ADULT_RATIO_KEY'] = 'adult ratio default'
DEFAULTS['ELDERLY_RATIO_ATTR_KEY'] = 'elderly ratio attribute'
DEFAULTS['ELDERLY_RATIO_KEY'] = 'elderly ratio default'
DEFAULTS['AGGR_ATTR_KEY'] = 'aggregation attribute'
DEFAULTS['NO_DATA'] = tr('No data')

# Defaults for iso_19115_template.xml
DEFAULTS['ISO19115_ORGANIZATION'] = 'InaSAFE.org'
DEFAULTS['ISO19115_URL'] = 'http://inasafe.org'
DEFAULTS['ISO19115_EMAIL'] = 'info@inasafe.org'
DEFAULTS['ISO19115_TITLE'] = 'InaSAFE analysis result'
DEFAULTS['ISO19115_LICENSE'] = 'Free use with accreditation'


# noinspection PyUnresolvedReferences
# this is used when we are in safe without access to qgis (e.g. web ) and is
# monkey patched in safe_qgis.__init__
def get_defaults(default=None):
    """Get defaults for aggregation / post processing.

    :param default: Optional parameter if you only want a specific default.
    :type default: str

    :return: A single value (when default is passed) or a dict of values.
    :rtype: str, int, float, dict
    """
    print "SAFE defaults CALL. If in QGIS this is a WRONG CALL"
    if default is None:
        return DEFAULTS
    elif default in DEFAULTS:
        return DEFAULTS[default]
    else:
        return None


def default_minimum_needs():
    """Helper to get the default minimum needs.

    .. note:: Key names will be translated.
    """
    # TODO: update this to use parameters
    rice = ResourceParameter()
    rice.value = 2.8
    rice.frequency = 'weekly'
    rice.minimum_allowed_value = 1.4
    rice.maximum_allowed_value = 5.6
    rice.name = 'Rice'
    rice.unit.abbreviation = 'kg'
    rice.unit.name = 'kilogram'
    rice.unit.plural = 'kilograms'

    drinking_water = ResourceParameter()
    drinking_water.value = 17.5
    drinking_water.frequency = 'weekly'
    drinking_water.minimum_allowed_value = 10
    drinking_water.maximum_allowed_value = 30
    drinking_water.name = 'Drinking Water'
    drinking_water.unit.abbreviation = 'l'
    drinking_water.unit.name = 'litre'
    drinking_water.unit.plural = 'litres'

    water = ResourceParameter()
    water.value = 67
    water.frequency = 'weekly'
    water.minimum_allowed_value = 30
    water.maximum_allowed_value = 100
    water.name = 'Clean Water'
    water.unit.abbreviation = 'l'
    water.unit.name = 'litre'
    water.unit.plural = 'litres'

    family_kits = ResourceParameter()
    family_kits.value = 0.2
    family_kits.frequency = 'weekly'
    family_kits.minimum_allowed_value = 0.2
    family_kits.maximum_allowed_value = 0.2
    family_kits.name = 'Family Kits'

    toilets = ResourceParameter()
    toilets.value = 0.05
    toilets.frequency = 'weekly'
    toilets.minimum_allowed_value = 0.02
    toilets.maximum_allowed_value = 0.05
    toilets.name = 'Toilets'

    minimum_needs = [
        rice,
        drinking_water,
        water,
        family_kits,
        toilets,
    ]
    return minimum_needs


def default_provenance():
    """The provenance for the default values.

    :return: default provenance.
    :rtype: str
    """
    return 'The minimum needs are based on Perka 7/2008.'
