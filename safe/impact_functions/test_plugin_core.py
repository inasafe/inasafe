# coding=utf-8
import unittest
import logging
import os

from safe.impact_functions.core import (
    FunctionProvider,
    requirements_collect,
    requirement_check,
    requirements_met,
    get_admissible_plugins,
    get_function_title,
    get_plugins_as_table,
    parse_single_requirement,
    get_metadata,
    evacuated_population_weekly_needs,
    aggregate,
    convert_to_old_keywords
)
from safe.impact_functions.utilities import pretty_string
from safe.common.utilities import format_int
from safe.metadata import converter_dict

LOGGER = logging.getLogger('InaSAFE')


# noinspection PyUnresolvedReferences
class BasicFunctionCore(FunctionProvider):
    """Risk plugin for testing

    :author Allen
    :rating 1
    :param requires category=="test_cat1"
    :param requires unit=="MMI"
    """

    @staticmethod
    def run():
        return None


# noinspection PyUnresolvedReferences
class F1(FunctionProvider):
    """Risk plugin for testing

    :param requires category=='test_cat1' and \
                    subcategory.startswith('flood') and \
                    layertype=='raster' and \
                    unit=='m'

    :param requires category=='test_cat2' and \
                    subcategory.startswith('population') and \
                    layertype=='raster' and \
                    datatype=='population'

    """

    title = 'Title for F1'

    @staticmethod
    def run():
        return None


class F2(FunctionProvider):
    """Risk plugin for testing

    :param requires category=='test_cat1' and \
                    subcategory.startswith('flood') and \
                    layertype=='raster' and \
                    unit=='m'

    :param requires category=='test_cat2' and \
                    subcategory.startswith('building')
    """

    title = 'Title for F2'

    @staticmethod
    def run():
        return None


class F3(FunctionProvider):
    """Risk plugin for testing

    :param requires category=='test_cat1'
    :param requires category=='test_cat2'
    """

    @staticmethod
    def run():
        return None


class F4(FunctionProvider):
    """Risk plugin for testing

    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami']

    :param requires category=='exposure' and \
                    subcategory in ['building', 'structure'] and \
                    layertype=='vector'
    """

    @staticmethod
    def run():
        return None


class SyntaxErrorFunction(FunctionProvider):
    """Risk plugin for testing

    :author Allen
    :rating 1
    :param requires category=="test_cat1"
    :param requires unit="MMI"  # Note the error should be ==
    """

    @staticmethod
    def run():
        return None


class Test_plugin_core(unittest.TestCase):
    """Tests of InaSAFE calculations
    """

    def test_basic_plugin_requirements(self):
        """Basic plugin requirements collection
        """
        requirelines = requirements_collect(BasicFunctionCore)
        params = {'category': 'test_cat1', 'unit': 'MMI'}
        assert requirements_met(requirelines, params)

        params = {'category': 'test_cat2', 'unit': 'mmi2'}
        assert not requirements_met(requirelines, params)

    def test_basic_plugin_requirements_met(self):
        """Basic plugin requirements met
        """
        requirelines = requirements_collect(BasicFunctionCore)
        valid_return = ['category=="test_cat1"', 'unit=="MMI"']
        for ret1, ret2 in zip(valid_return, requirelines):
            assert ret1 == ret2, "Error in requirements extraction"

    def test_basic_requirements_check(self):
        """Basic plugin requirements check
        """
        requirelines = requirements_collect(BasicFunctionCore)
        params = {'category': 'test_cat2'}
        for line in requirelines:
            check = requirement_check(params, line)
            assert not check

        line = "unit='MMI'"
        params = {'category': 'test_cat2'}
        msg = 'Malformed statement (logged)'
        assert not requirement_check(params, line), msg
        #self.assertRaises(SyntaxError, requirement_check, params, line)

    def test_keywords_error(self):
        """Handling of reserved python keywords """
        line = "unit=='MMI'"
        params = {'class': 'myclass'}
        msg = 'Reserved keyword in statement (logged)'
        assert not requirement_check(params, line), msg

    def test_filtering_of_impact_functions(self):
        """Impact functions are filtered correctly
        """

        # Keywords matching F1 and F3
        haz_keywords1 = dict(category='test_cat1', subcategory='flood',
                             layertype='raster', unit='m')
        exp_keywords1 = dict(category='test_cat2', subcategory='population',
                             layertype='raster', datatype='population')

        # Keywords matching F2 and F3
        haz_keywords2 = dict(category='test_cat1', subcategory='flood',
                             layertype='raster', unit='m')
        exp_keywords2 = dict(category='test_cat2', subcategory='building')

        # Check correct matching of keyword set 1
        P = get_admissible_plugins([haz_keywords1, exp_keywords1])
        msg = 'Expected impact functions F1 and F3 in %s' % str(P.keys())
        assert 'F1' in P and 'F3' in P, msg

        # Check correctness of title attribute
        assert get_function_title(P['F1']) == 'Title for F1'
        assert get_function_title(P['F3']) == 'F3'

        # Check correct matching of keyword set 2
        P = get_admissible_plugins([haz_keywords2, exp_keywords2])
        msg = 'Expected impact functions F2 and F3 in %s' % str(P.keys())
        assert 'F2' in P and 'F3' in P, msg

        # Check correctness of title attribute
        assert get_function_title(P['F2']) == 'Title for F2'
        assert get_function_title(P['F3']) == 'F3'

        # Check empty call returns all
        P = get_admissible_plugins([])
        msg = ('Expected at least impact functions F1, F2 and F3 in %s'
               % str(P.keys()))
        assert 'F1' in P and 'F2' in P and 'F3' in P, msg

    def test_parse_requirement(self):
        """Test parse requirements of a function to dictionary."""
        myRequirement = requirements_collect(F4)[0]
        parsed_req = parse_single_requirement(myRequirement)
        expected_req = {'category': 'hazard',
                        'subcategory': ['flood', 'tsunami']}
        myMessage = 'Get %s should be % s' % (parsed_req, expected_req)
        assert parsed_req == expected_req, myMessage

        myRequirement = requirements_collect(F4)[1]
        parsed_req = parse_single_requirement(myRequirement)
        expected_req = {'category': 'exposure',
                        'subcategory': ['building', 'structure'],
                        'layertype': 'vector'}
        myMessage = 'Get %s should be % s' % (parsed_req, expected_req)
        assert parsed_req == expected_req, myMessage

    def test_pretty_string(self):
        """Test return pretty string from list or string."""
        myStr = 'Aloha'
        mylist = ['a', 'b', 'c']
        expectedStr = 'Aloha'
        expectedStr2 = 'a, b, c'
        realStr = pretty_string(myStr)
        realStr2 = pretty_string(mylist)
        assert expectedStr == realStr, 'String not Ok'
        myMessage = 'Get %s should be % s' % (realStr2, expectedStr2)
        assert expectedStr2 == realStr2, myMessage

    def test_get_plugins_as_table(self):
        """Test get plugins as table with filtering."""
        T = get_plugins_as_table()
        S = T.toNewlineFreeString()
        LOGGER.debug(S)

    def test_get_documentation(self):
        """Test get_documentation for a function"""
        dict_doc = get_metadata('Basic Function')
        myMsg = ('title should be Basic Function but found %s \n'
                 % (dict_doc['title']))
        myMsg += str(dict_doc)
        for key, value in dict_doc.iteritems():
            print key + ':\t' + str(value)
        assert dict_doc['title'] == 'Basic Function', myMsg

    def test_format_int(self):
        """Test formatting integer
        """
        my_int = 10000000
        lang = os.getenv('LANG')
        my_formated_int = format_int(my_int)
        if lang == 'id':
            expected_str = '10.000.000'
        else:
            expected_str = '10,000,000'
        my_msg = 'Format integer is not valid'
        assert (my_formated_int == expected_str or
                my_formated_int == str(my_int)), my_msg

        my_int = 1234
        lang = os.getenv('LANG')
        print lang
        my_formated_int = format_int(my_int)
        if lang == 'id':
            expected_str = '1.234'
        else:
            expected_str = '1,234'
        my_msg = 'Format integer %s is not valid' % my_formated_int
        assert (my_formated_int == expected_str or
                my_formated_int == str(my_int)), my_msg

    def test_default_weekly_needs(self):
        """default calculated needs are as expected
        """
        # 20 Happens to be the smallest number at which integer rounding
        # won't make a difference to the result
        result = evacuated_population_weekly_needs(20)
        assert (result['rice'] == 56 and result['drinking_water'] == 350
                and result['water'] == 1340 and result['family_kits'] == 4
                and result['toilets'] == 1)

    def test_arbitrary_weekly_needs(self):
        """custom need ratios calculated are as expected
        """

        minimum_needs = {'Rice': 4, 'Drinking Water': 3,
                         'Water': 2, 'Family Kits': 1, 'Toilets': 0.2}
        result = evacuated_population_weekly_needs(10, minimum_needs)
        assert (result['rice'] == 40 and result['drinking_water'] == 30
                and result['water'] == 20 and result['family_kits'] == 10
                and result['toilets'] == 2)

    def test_aggregate(self):
        """Test aggregate function behaves as expected."""
        class MockRasterData(object):
            """Fake raster data object."""
            def __init__(self):
                self.is_point_data = False
                self.is_raster_data = True

        class MockOtherData(object):
            """Fake other data object."""
            def __init__(self):
                self.is_point_data = False
                self.is_raster_data = False

        # Test raster data
        raster_data = MockRasterData()
        result = aggregate(raster_data)
        self.assertIsNone(result)

        # Test Not Point Data nor raster Data:
        other_data = MockOtherData()
        self.assertRaises(Exception, aggregate, other_data)

    def test_convert_to_old_keywords(self):
        """Test to convert new keywords to old keywords system."""
        new_keywords = {
            'category': 'hazard',
            'subcategory': 'tsunami',
            'unit': 'metres_depth'
        }

        convert_to_old_keywords(converter_dict, [new_keywords])
        expected_keywords = {
            'category': 'hazard',
            'subcategory': 'tsunami',
            'unit': 'm'
        }
        msg = 'Expected %s but I got %s' % (expected_keywords, new_keywords)
        self.assertDictEqual(new_keywords, expected_keywords, msg)


if __name__ == '__main__':
    suite = unittest.makeSuite(Test_plugin_core, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
