# coding=utf-8
"""Provenance Utilities."""

from safe.utilities.i18n import tr

from safe.definitions.hazard import hazard_generic
from safe.definitions.hazard_category import hazard_category_single_event

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def get_map_title(hazard, exposure, hazard_category):
    """Helper to get map title.

    :param hazard: A hazard definition.
    :type hazard: dict

    :param exposure: An exposure definition.
    :type exposure: dict

    :param hazard_category: A hazard category definition.
    :type hazard_category: dict

    :returns: Map title based on the input.
    :rtype: str
    """
    if hazard == hazard_generic:
        map_title = tr('{exposure_name} affected'.format(
            exposure_name=exposure['name']))
    else:
        if hazard_category == hazard_category_single_event:
            map_title = tr(
                '{exposure_name} affected by {hazard_name} event'.format(
                    exposure_name=exposure['name'],
                    hazard_name=hazard['name']))
        else:
            map_title = tr(
                '{exposure_name} affected by {hazard_name} hazard'.format(
                    exposure_name=exposure['name'],
                    hazard_name=hazard['name']))
    return map_title