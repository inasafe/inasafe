# coding=utf-8
"""InaSAFE Defaults"""

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from PyQt4.QtCore import QSettings

from safe.common.parameters.resource_parameter import ResourceParameter
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path
from safe_extras.parameters.boolean_parameter import BooleanParameter
from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.group_parameter import GroupParameter
from safe_extras.parameters.text_parameter import TextParameter
from safe_extras.parameters.unit import Unit

from safe.definitionsv4.fields import (
    female_ratio_field,
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field
)
from safe.definitionsv4.default_values import (
    youth_ratio_default_value,
    adult_ratio_default_value,
    elderly_ratio_default_value
)
from safe.utilities.settings import get_inasafe_default_value_qsetting
from safe.definitionsv4.constants import GLOBAL

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def define_defaults():
    """Define standard defaults such as age ratios etc.

    :returns: A dictionary of standard default definitions.
    :rtype: dict
    """
    settings = QSettings()
    defaults = dict()

    defaults['FEMALE_RATIO'] = get_inasafe_default_value_qsetting(
        settings, GLOBAL, female_ratio_field['key'])

    defaults['YOUTH_RATIO'] = get_inasafe_default_value_qsetting(
        settings, GLOBAL, youth_ratio_field['key'])

    defaults['ADULT_RATIO'] = get_inasafe_default_value_qsetting(
        settings, GLOBAL, adult_ratio_field['key'])

    defaults['ELDERLY_RATIO'] = get_inasafe_default_value_qsetting(
        settings, GLOBAL, elderly_ratio_field['key'])

    # Keywords key names
    defaults['NO_DATA'] = tr('No data')

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
    gender.help_text = tr('Gender ratio breakdown.')
    gender.description = tr(
        'Check this option if you wish to calculate a breakdown by gender '
        'for the affected population.'
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
    minimum_needs_flag.help_text = tr('Minimum needs breakdown.')
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
    age = GroupParameter()
    age.name = 'Age'
    age.enable_parameter = True
    age.must_scroll = False
    age.help_text = tr('Age ratios breakdown.')
    age.description = tr(
        'Check this option if you wish to calculate a breakdown by age group '
        'for the affected population. '
    )

    unit_ratio = Unit()
    unit_ratio.name = tr('ratio')
    unit_ratio.plural = tr('ratios')
    unit_ratio.abbreviation = tr('ratio')
    unit_ratio.description = tr(
        'Ratio represents a fraction of 1, so it ranges from 0 to 1.'
    )

    youth_ratio = FloatParameter()
    youth_ratio.name = 'Youth ratio'
    youth_ratio.value = youth_ratio_default_value['default_value']
    youth_ratio.unit = unit_ratio
    youth_ratio.allowed_units = [unit_ratio]
    youth_ratio.help_text = tr('Youth ratio value.')
    youth_ratio.description = tr(
        'Youth ratio defines what proportion of the population have not yet '
        'achieved financial independence. The age threshold for youth can '
        'vary by region - please consult with your local census bureau to '
        'find out what the relevant threshold is in your region. InaSAFE does '
        'not impose a particular age ratio scheme - it will break down the '
        'population according to the thresholds you define for your locality. '
        'In InaSAFE, people 0-14 years old are defined as "youth". The '
        'default youth ratio is 0.263.'
    )

    adult_ratio = FloatParameter()
    adult_ratio.name = 'Adult ratio'
    adult_ratio.value = adult_ratio_default_value['default_value']
    adult_ratio.unit = unit_ratio
    adult_ratio.allowed_units = [unit_ratio]
    adult_ratio.help_text = tr('Adult ratio value.')
    adult_ratio.description = tr(
        'Adult ratio defines what proportion of the population have '
        'passed into adulthood and are not yet aged. The age threshold for '
        'adults can vary by region - please consult with your local census '
        'bureau to find out what the relevant threshold is in your region. '
        'InaSAFE does not impose a particular age ratio scheme - it will '
        'break down the population according to the thresholds you define '
        'for your locality. '
        'In InaSAFE, people 15-64 years old are defined as "adult". The '
        'default adult ratio is 0.659.'
    )

    elderly_ratio = FloatParameter()
    elderly_ratio.name = 'Elderly ratio'
    elderly_ratio.value = elderly_ratio_default_value['default_value']
    elderly_ratio.unit = unit_ratio
    elderly_ratio.allowed_units = [unit_ratio]
    elderly_ratio.help_text = tr('Elderly ratio value.')
    elderly_ratio.description = tr(
        'Elderly ratio defines what proportion of the population have '
        'passed from adulthood into their later life stage.  The age '
        'threshold for being considered elderly can vary by region - please '
        'consult with your local census bureau to find out what the relevant '
        'threshold is in your region. InaSAFE does not impose a particular '
        'age ratio scheme - it will break down the population according to '
        'the thresholds you define for your locality. '
        'In InaSAFE, people 65 years old and over are defined as "elderly". '
        'The default elderly ratio is 0.078.'
    )

    age.value = [youth_ratio, adult_ratio, elderly_ratio]

    def _age_validator(parameters=None):
        total_ratio = 0
        for p in parameters:
            total_ratio += p.value

        if not total_ratio == 1:
            message = tr('Total Age ratio is %s instead of 1') % total_ratio
            raise ValueError(message)

    age.custom_validator = _age_validator

    return [age]


def building_type_postprocessor():
    """Get building-type parameter for postprocessing.

    :return: Selectors to activate building breakdown postprocessor.
    :rtype: list
    """
    building_type = BooleanParameter()
    building_type.name = tr('Building type')
    building_type.value = True
    building_type.description = tr(
        'Check this option if you want to enable a building impact report '
        'broken down by building type for each aggregation area.'
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
        'Toilets are not provided on a regular basis - it is expected that '
        'installed toilets will continue to be usable.'
    )

    provenance = default_provenance()

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
    field = TextParameter()
    field.name = tr('Provenance')
    field.description = tr('The provenance of minimum needs')
    field.value = 'The minimum needs are based on BNPB Perka 7/2008.'
    return field


def disclaimer():
    """Get a standard disclaimer.

    :returns: Standard disclaimer string for InaSAFE.
    :rtype: str
    """
    text = tr(
        'InaSAFE has been jointly developed by the Indonesian '
        'Government-BNPB, the Australian Government, the World Bank-GFDRR and '
        'independent contributors. These agencies and the individual software '
        'developers of InaSAFE take no responsibility for the correctness of '
        'outputs from InaSAFE or decisions derived as a consequence.')
    return text


def black_inasafe_logo_path():
    """Get the path to the Black InaSAFE SVG logo.

    .. versionadded:: 3.2
    """
    path = resources_path('img', 'logos', 'inasafe-logo-url.svg')
    return path


def white_inasafe_logo_path():
    """Get the path to the White InaSAFE SVG logo.

    .. versionadded:: 3.2
    """
    path = resources_path('img', 'logos', 'inasafe-logo-url-white.svg')
    return path


def supporters_logo_path():
    """Get the supporters logo path.

    .. versionchanged:: Changed in 3.2 from default_organisation_path to
        supporters_logo_path.

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
        tr('Population count data (raster) must be provided in WGS84 '
           'geographic coordinates.'))
    limitation_list.append(
        tr('InaSAFE is a Free and Open Source Software (FOSS) project, '
           'published under the GPL V3 license. As such you may freely '
           'download, share and (if you like) modify the software.'))
    return limitation_list
