# coding=utf-8
"""Unittest for qgis expressions."""

import unittest

from qgis.core import QgsExpression

from safe.definitions.reports.infographic import (
    map_overview_header,
    population_chart_header,
    people_section_header,
    age_gender_section_header,
    age_gender_section_notes,
    vulnerability_section_header,
    female_vulnerability_section_header,
    minimum_needs_section_header,
    additional_minimum_needs_section_header,
    minimum_needs_section_notes)
from safe.definitions.reports.map_report import (
    black_inasafe_logo_path,
    white_inasafe_logo_path,
    inasafe_north_arrow_path,
    inasafe_organisation_logo_path,
    disclaimer_text,
    information_title_header,
    time_title_header,
    caution_title_header,
    caution_text,
    source_title_header,
    analysis_title_header,
    version_title_header,
    reference_title_header,
    unknown_source_text,
    aggregation_not_used_text)
from safe.report.expressions.infographic import (
    map_overview_header_element,
    population_chart_header_element,
    people_section_header_element,
    age_gender_section_header_element,
    age_gender_section_notes_element,
    vulnerability_section_header_element,
    female_vulnerability_section_header_element,
    minimum_needs_section_header_element,
    additional_minimum_needs_section_header_element,
    minimum_needs_section_notes_element)
from safe.report.expressions.map_report import (
    legend_title_header_element,
    disclaimer_title_header_element,
    disclaimer_text_element,
    information_title_header_element,
    time_title_header_element,
    caution_title_header_element,
    caution_text_element,
    source_title_header_element,
    analysis_title_header_element,
    version_title_header_element,
    reference_title_header_element,
    unknown_source_text_element,
    aggregation_not_used_text_element,
    inasafe_logo_black_path,
    inasafe_logo_white_path,
    north_arrow_path,
    organisation_logo_path)

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

default_params = []
feature = None
parent = None


class TestExpressions(unittest.TestCase):
    """Test Expressions.

    .. versionadded:: 4.3
    """

    def get_function(self, function_name):
        """Get an expression function which is already loaded in qgis.

        :param function_name: Name of the function.
        :type function_name: str

        :return: The function.
        :rtype: QgsExpressionFunction

        .. versionadded:: 4.3
        """
        for func in QgsExpression.Functions():
            if func.name() == function_name:
                return func
        return None

    def evaluate(self, func, expected_result, params=None):
        """Evaluate the result of a function.

        :param func: The function.
        :type func: QgsExpressionFunction

        :param expected_result: The expected result.
        :type expected_result: str

        :param params: The parameters that used by the function.
        :type params: list

        .. versionadded:: 4.3
        """
        if params is None:
            params = default_params

        actual_result = func.funcV2(params, feature, parent)
        self.assertEqual(actual_result, expected_result)

    def test_map_report_expressions(self):
        """Test all expressions in the map report expressions.

        .. versionadded:: 4.3
        """

        # legend_title_header_element
        expected_result = 'Legend'
        self.evaluate(legend_title_header_element, expected_result)

        # disclaimer_title_header_element
        expected_result = 'Disclaimer'
        self.evaluate(disclaimer_title_header_element, expected_result)

        # disclaimer_text_element
        expected_result = disclaimer_text['string_format']
        self.evaluate(disclaimer_text_element, expected_result)

        # information_title_header_element
        expected_result = (
            information_title_header['string_format'].capitalize())
        self.evaluate(information_title_header_element, expected_result)

        # time_title_header_element
        expected_result = time_title_header['string_format'].capitalize()
        self.evaluate(time_title_header_element, expected_result)

        # caution_title_header_element
        expected_result = caution_title_header['string_format'].capitalize()
        self.evaluate(caution_title_header_element, expected_result)

        # caution_text_element
        expected_result = caution_text['string_format'].capitalize()
        self.evaluate(caution_text_element, expected_result)

        # source_title_header_element
        expected_result = source_title_header['string_format'].capitalize()
        self.evaluate(source_title_header_element, expected_result)

        # analysis_title_header_element
        expected_result = analysis_title_header['string_format'].capitalize()
        self.evaluate(analysis_title_header_element, expected_result)

        # version_title_header_element
        expected_result = version_title_header['string_format'].capitalize()
        self.evaluate(version_title_header_element, expected_result)

        # reference_title_header_element
        expected_result = reference_title_header['string_format'].capitalize()
        self.evaluate(reference_title_header_element, expected_result)

        # TODO: We need to figure out how to call expression with parameters.

        # crs_text_element
        # params = ['EPSG:3857']
        # expected_result = (
        #     u'Coordinate Reference System - WGS 84 / Pseudo Mercator')
        # self.evaluate(crs_text_element, expected_result, params=params)

        # unknown_source_text_element
        expected_result = unknown_source_text['string_format'].capitalize()
        self.evaluate(unknown_source_text_element, expected_result)

        # aggregation_not_used_text_element
        expected_result = (
            aggregation_not_used_text['string_format'].capitalize())
        self.evaluate(aggregation_not_used_text_element, expected_result)

        # Below here we are using definition as a comparison because path are
        # relative to the user's inasafe directory path.

        # inasafe_logo_black_path
        expected_result = black_inasafe_logo_path['path']  # special case
        self.evaluate(inasafe_logo_black_path, expected_result)

        # inasafe_logo_white_path
        expected_result = white_inasafe_logo_path['path']  # special case
        self.evaluate(inasafe_logo_white_path, expected_result)

        # north_arrow_path
        expected_result = inasafe_north_arrow_path['path']  # special case
        self.evaluate(north_arrow_path, expected_result)

        # organisation_logo_path
        # special case
        expected_result = inasafe_organisation_logo_path['path']
        self.evaluate(organisation_logo_path, expected_result)

    def test_infographic_expressions(self):
        """Test all the expressions in the infographic expressions.

        .. versionadded:: 4.3
        """
        # TODO: We need to figure out how to call expression with parameters.

        # inasafe_field_header
        # params = ['minimum_needs__clean_water']
        # expected_result = u'Clean water'
        # self.evaluate(inasafe_field_header, expected_result, params=params)

        # minimum_needs_unit
        # params = ['minimum_needs__clean_water']
        # expected_result = u'l/weekly'
        # self.evaluate(minimum_needs_unit, expected_result, params=params)

        # infographic_header_element
        # params = ['flood']
        # expected_result = u'Estimated impact of a flood'
        # self.evaluate(
        #     infographic_header_element, expected_result, params=params)

        # map_overview_header_element
        expected_result = map_overview_header['string_format'].capitalize()
        self.evaluate(map_overview_header_element, expected_result)

        # population_chart_header_element
        expected_result = population_chart_header['string_format'].capitalize()
        self.evaluate(population_chart_header_element, expected_result)

        # people_section_header_element
        expected_result = people_section_header['string_format'].capitalize()
        self.evaluate(people_section_header_element, expected_result)

        # age_gender_section_header_element
        expected_result = (
            age_gender_section_header['string_format'].capitalize())
        self.evaluate(age_gender_section_header_element, expected_result)

        # age_gender_section_notes_element
        expected_result = (
            age_gender_section_notes['string_format'])
        self.evaluate(age_gender_section_notes_element, expected_result)

        # vulnerability_section_header_element
        expected_result = (
            vulnerability_section_header['string_format'].capitalize())
        self.evaluate(vulnerability_section_header_element, expected_result)

        # female_vulnerability_section_header_element
        expected_result = (
            female_vulnerability_section_header['string_format'])
        self.evaluate(
            female_vulnerability_section_header_element, expected_result)

        # minimum_needs_section_header_element
        expected_result = (
            minimum_needs_section_header['string_format'].capitalize())
        self.evaluate(minimum_needs_section_header_element, expected_result)

        # additional_minimum_needs_section_header_element
        expected_result = (
            additional_minimum_needs_section_header[
                'string_format'].capitalize())
        self.evaluate(
            additional_minimum_needs_section_header_element, expected_result)

        # minimum_needs_section_notes_element
        expected_result = minimum_needs_section_notes['string_format']
        self.evaluate(minimum_needs_section_notes_element, expected_result)
