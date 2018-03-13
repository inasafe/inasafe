# coding=utf-8
"""Provenance Utilities."""

from safe.definitions.hazard import hazard_generic
from safe.definitions.hazard_category import hazard_category_single_event
from safe.definitions.hazard_exposure_specifications import (
    specific_analysis_question)
from safe.utilities.i18n import tr

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
        map_title = tr(u'{exposure_name} affected').format(
            exposure_name=exposure['name'])
    else:
        if hazard_category == hazard_category_single_event:
            map_title = tr(
                u'{exposure_name} affected by {hazard_name} event').format(
                    exposure_name=exposure['name'],
                    hazard_name=hazard['name'])
        else:
            map_title = tr(
                u'{exposure_name} affected by {hazard_name} hazard').format(
                    exposure_name=exposure['name'],
                    hazard_name=hazard['name'])
    return map_title


def get_analysis_question(hazard, exposure):
    """Construct analysis question based on hazard and exposure.

    :param hazard: A hazard definition.
    :type hazard: dict

    :param exposure: An exposure definition.
    :type exposure: dict

    :returns: Analysis question based on reporting standards.
    :rtype: str
    """
    # First we look for a translated hardcoded question.
    question = specific_analysis_question(hazard, exposure)
    if question:
        return question

    if hazard == hazard_generic:
        # Secondly, if the hazard is generic, we don't need the hazard.
        question = tr(
            'In each of the hazard zones {exposure_measure} {exposure_name} '
            'might be affected?').format(
            exposure_measure=exposure['measure_question'],
            exposure_name=exposure['name'])
        return question

    # Then, we fallback on a generated string on the fly.
    question = tr(
        'In the event of a {hazard_name}, {exposure_measure} {exposure_name} '
        'might be affected?').format(
            hazard_name=hazard['name'],
            exposure_measure=exposure['measure_question'],
            exposure_name=exposure['name'])
    return question


def get_multi_exposure_analysis_question(hazard, exposures):
    """Construct analysis question based on hazard and exposures.

    :param hazard: A hazard definition.
    :type hazard: dict

    :param exposure: A list of exposure definition.
    :type exposure: list

    :returns: Analysis question based on reporting standards.
    :rtype: str
    """
    exposures_question = ''
    exposure_format = '{exposure_measure} {exposure_name}'
    for index, exposure in enumerate(exposures):
        if index + 1 == len(exposures):
            if len(exposures) > 2:
                exposures_question += tr(', and ')
            else:
                exposures_question += tr(' and ')
        elif index != 0:
            exposures_question += ', '
        exposures_question += exposure_format.format(
            exposure_measure=exposure['measure_question'],
            exposure_name=exposure['name'])

    if hazard == hazard_generic:
        question = tr(
            'In each of the hazard zones, {exposures_question} '
            'might be affected?').format(exposures_question=exposures_question)
    else:
        question = tr(
            'In the event of a {hazard_name}, {exposures_question} '
            'might be affected?').format(
            hazard_name=hazard['name'], exposures_question=exposures_question)

    return question
