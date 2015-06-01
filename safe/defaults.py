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
from safe_extras.parameters.text_parameter import TextParameter

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '05/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from PyQt4.QtCore import QSettings

from safe_extras.parameters.boolean_parameter import BooleanParameter
from safe_extras.parameters.float_parameter import FloatParameter

from safe.common.resource_parameter import ResourceParameter
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path


def define_defaults():
    """Define standard defaults such as age ratios etc.

    :returns: A dictionary of standard default definitions.
    :rtype: dict
    """
    settings = QSettings()
    defaults = dict()
    # https://www.cia.gov/library/publications/the-world-factbook/geos/xx.html
    # total population: 1.01 male(s)/female (2011 est.)
    female_ratio = 0.50
    value = settings.value(
        'inasafe/defaultFemaleRatio', female_ratio, type=float)
    defaults['FEMALE_RATIO'] = float(value)

    # https://www.cia.gov/library/publications/the-world-factbook/geos/xx.html
    # Age structure:
    # 0-14 years: 26.3% (male 944,987,919/female 884,268,378)
    # 15-64 years: 65.9% (male 2,234,860,865/female 2,187,838,153)
    # 65 years and over: 7.9% (male 227,164,176/female 289,048,221) (2011 est.)

    # NOTE (MB) CIA can not do maths!!!  this gives 100.1%
    # inaSAFE can, thus we remove 0.1% from the elderly
    # I wrote them and got this contact confirmation number: CTCU1K2

    youth_ratio = 0.263
    value = settings.value(
        'inasafe/defaultYouthRatio', youth_ratio, type=float)
    defaults['YOUTH_RATIO'] = float(value)

    adult_ratio = 0.659
    value = settings.value(
        'inasafe/defaultAdultRatio', adult_ratio, type=float)
    defaults['ADULT_RATIO'] = float(value)

    elderly_ratio = 0.078
    value = settings.value(
        'inasafe/defaultElderlyRatio', elderly_ratio, type=float)
    defaults['ELDERLY_RATIO'] = float(value)

    # Keywords key names
    defaults['FEMALE_RATIO_ATTR_KEY'] = 'female ratio attribute'
    defaults['FEMALE_RATIO_KEY'] = 'female ratio default'
    defaults['YOUTH_RATIO_ATTR_KEY'] = 'youth ratio attribute'
    defaults['YOUTH_RATIO_KEY'] = 'youth ratio default'
    defaults['ADULT_RATIO_ATTR_KEY'] = 'adult ratio attribute'
    defaults['ADULT_RATIO_KEY'] = 'adult ratio default'
    defaults['ELDERLY_RATIO_ATTR_KEY'] = 'elderly ratio attribute'
    defaults['ELDERLY_RATIO_KEY'] = 'elderly ratio default'
    defaults['AGGR_ATTR_KEY'] = 'aggregation attribute'
    defaults['NO_DATA'] = tr('No data')

    # defaults for iso_19115_template.xml
    organisation = 'InaSAFE.org'
    value = settings.value(
        'ISO19115_ORGANIZATION', organisation, type=str)
    defaults['ISO19115_ORGANIZATION'] = value

    url = 'http://inasafe.org'
    value = settings.value('ISO19115_URL', url, type=str)
    defaults['ISO19115_URL'] = value

    email = 'info@inasafe.org'
    value = settings.value('ISO19115_EMAIL', email, type=str)
    defaults['ISO19115_EMAIL'] = value

    title = 'InaSAFE analysis result'
    value = settings.value('ISO19115_TITLE', title, type=str)
    defaults['ISO19115_TITLE'] = value

    iso_license = 'Free use with accreditation'
    value = settings.value('ISO19115_LICENSE', iso_license, type=str)
    defaults['ISO19115_LICENSE'] = value

    return defaults


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
    defaults = define_defaults()
    if default is None:
        return defaults
    elif default in defaults:
        return defaults[default]
    else:
        return None


def default_gender_postprocessor():
    """Get gender postprocessor selector.

    :return: A selector to activate gender postprocessor.
    :rtype: list
    """
    gender = BooleanParameter()
    gender.name = 'Gender'
    gender.value = True
    gender.description = tr(
        'Check this option if you wish to calculate the gender breakdown '
        'on the affected population.'
    )
    return [gender]


def minimum_needs_selector():
    """Get minimum needs postprocessor selector.

    :return: A selector to activate minimum needs postprocessor.
    :rtype: list
    """
    minimum_needs_flag = BooleanParameter()
    minimum_needs_flag.name = 'MinimumNeeds'
    minimum_needs_flag.value = True
    minimum_needs_flag.description = tr(
        'Check this option if you wish to calculate minimum needs for the '
        'affected population. Minimum needs will be calculated according to '
        'the defaults defined in the minimum needs configuration tool.'
    )
    return [minimum_needs_flag]


def age_postprocessor():
    """Get age postprocessor selectors.

    :return: Selectors to activate age postprocessor.
    :rtype: list
    """
    age = BooleanParameter()
    age.name = 'Age'
    age.value = True

    youth_ratio = FloatParameter()
    youth_ratio.name = 'Youth ratio'
    youth_ratio.value = get_defaults('YOUTH_RATIO')
    youth_ratio.description = tr(
        'Youth ratio defines what proportion of the population have not yet '
        'achieved financial independence. The age threshold for youth can '
        'vary by region - please consult with your local census bureau to find'
        'out what the relevant threshold is in your region. InaSAFE does not '
        'impose a particular age ratio scheme - it will break down the '
        'population according to the thresholds you define for your locality.'
    )

    adult_ratio = FloatParameter()
    adult_ratio.name = 'Adult ratio'
    adult_ratio.value = get_defaults('ADULT_RATIO')
    adult_ratio.description = tr(
        'Adult ratio defines what proportion of the population have '
        'passed into adulthood and are not yet aged. The age threshold for '
        'adults can vary by region - please consult with your local census '
        'bureau to find out what the relevant threshold is in your region. '
        'InaSAFE does not impose a particular age ratio scheme - it will '
        'break down the population according to the thresholds you define for '
        'your locality.'
    )

    elderly_ratio = FloatParameter()
    elderly_ratio.name = 'Elderly ratio'
    elderly_ratio.value = get_defaults('ELDERLY_RATIO')
    elderly_ratio.description = tr(
        'Elderly ratio defines what proportion of the population have '
        'passed from adulthood into their later life stage.  The age '
        'threshold for being considered elderly can vary by region - please '
        'consult with your local census bureau to find out what the relevant '
        'threshold is in your region. InaSAFE does not impose a particular '
        'age ratio scheme - it will break down the population according to '
        'the thresholds you define for your locality.'
    )

    return [age, youth_ratio, adult_ratio, elderly_ratio]


def aggregation_categorical_postprocessor():
    """Get aggregation categorical postprocessor selectors.

    :return: List of boolean parameter.
    :rtype: list
    """
    aggregation_categorical = BooleanParameter()
    aggregation_categorical.name = tr('Aggregation categorical')
    aggregation_categorical.value = True
    aggregation_categorical.description = tr(
        'Enable the aggregation by categories. For example if you have '
        'roads classified by type, you will get a breakdown by type of roads'
        'per aggregation area.'
    )

    return [aggregation_categorical]


def road_type_postprocessor():
    """Get road-type parameter for postprocessing.

    :return: A list of boolean parameter.
    :rtype: list
    """
    road_type = BooleanParameter()
    road_type.name = tr('Road type')
    road_type.value = True
    road_type.description = tr(
        'Check this option to enable reporting break down by road type.'
    )

    return [road_type]


def building_type_postprocessor():
    """Get building-type parameter for postprocessing.

    :return: A list of boolean parameter.
    :rtype: list
    """
    building_type = BooleanParameter()
    building_type.name = tr('Building type')
    building_type.value = True
    building_type.description = tr(
        'Check this option to enable the generation of a break down buildings '
        'by type for each aggregation area.'
    )

    return [building_type]


def default_minimum_needs():
    """Helper to get the default minimum needs.

    .. note:: Key names will be translated.
    """
    # TODO: update this to use parameters
    rice = ResourceParameter()
    rice.value = 2.8
    rice.frequency = tr('weekly')
    rice.minimum_allowed_value = 1.4
    rice.maximum_allowed_value = 5.6
    rice.name = tr('Rice')
    rice.unit.abbreviation = tr('kg')
    rice.unit.name = tr('kilogram')
    rice.unit.plural = tr('kilograms')

    drinking_water = ResourceParameter()
    drinking_water.value = 17.5
    drinking_water.frequency = tr('weekly')
    drinking_water.minimum_allowed_value = 10
    drinking_water.maximum_allowed_value = 30
    drinking_water.name = tr('Drinking Water')
    drinking_water.unit.abbreviation = tr('l')
    drinking_water.unit.name = tr('litre')
    drinking_water.unit.plural = tr('litres')

    water = ResourceParameter()
    water.value = 67
    water.frequency = tr('weekly')
    water.minimum_allowed_value = 30
    water.maximum_allowed_value = 100
    water.name = tr('Clean Water')
    water.unit.abbreviation = tr('l')
    water.unit.name = tr('litre')
    water.unit.plural = tr('litres')

    family_kits = ResourceParameter()
    family_kits.value = 0.2
    family_kits.frequency = tr('weekly')
    family_kits.minimum_allowed_value = 0.2
    family_kits.maximum_allowed_value = 0.2
    family_kits.name = tr('Family Kits')

    toilets = ResourceParameter()
    toilets.value = 0.05
    toilets.frequency = tr('single')
    toilets.minimum_allowed_value = 0.02
    toilets.maximum_allowed_value = 0.05
    toilets.name = tr('Toilets')
    toilets.help_text = tr(
        'Toilets are not provided on a regular bases - it is expected that '
        'installed toilets will be usable on a continuous basis.'
    )

    provenance = TextParameter()
    provenance.name = tr('Provenance')
    provenance.description = tr('The provenance of minimum needs')
    provenance.help_text = tr('The provenance of minimum needs')
    provenance.value = default_provenance()

    minimum_needs = [
        rice,
        drinking_water,
        water,
        family_kits,
        toilets,
        provenance
    ]
    return minimum_needs


def default_provenance():
    """The provenance for the default values.

    :return: default provenance.
    :rtype: str
    """
    return 'The minimum needs are based on Perka 7/2008.'


def disclaimer():
    """Get a standard disclaimer.

    :returns: Standard disclaimer string for InaSAFE.
    :rtype: str
    """
    text = tr(
        'InaSAFE has been jointly developed by Indonesian '
        'Government-BNPB, Australian Government-AIFDR and the World '
        'Bank-GFDRR. These agencies and the individual software '
        'developers of InaSAFE take no responsibility for the '
        'correctness of outputs from InaSAFE or decisions derived as '
        'a consequence.')
    return text


def default_organisation_logo_path():
    """Get a default organisation logo path.

    :return: Default organisation logo path.
    :rtype: str
    """
    path = resources_path('img', 'logos', 'supporters.png')
    return path


def default_north_arrow_path():
    """Get a default north arrow image path.

    :return: Default north arrow path.
    :rtype: str
    """
    path = resources_path('img', 'north_arrows', 'simple_north_arrow.png')
    return path


def limitations():
    """Get InaSAFE limitations.

    :return: All limitations on current InaSAFE.
    :rtype: list
    """
    limitation_list = list()
    limitation_list.append(tr('InaSAFE is not a hazard modelling tool.'))
    limitation_list.append(
        tr('Polygon area analysis (such as land use) is not yet supported.'))
    limitation_list.append(
        tr('Population count data (raster) must be provided in WGS84 '
           'geographic coordinates.'))
    limitation_list.append(
        tr('Population by administration boundary is not yet supported.'))
    limitation_list.append(
        tr('InaSAFE is a Free and Open Source Software (FOSS) project, '
           'published under the GPL V3 license. As such you may freely '
           'download, share and (if you like) modify the software.'))
    return limitation_list
