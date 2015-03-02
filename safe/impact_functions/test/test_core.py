# coding=utf-8
"""Tests for core.py

InaSAFE Disaster risk assessment tool developed by AusAid -
**Test Core**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'Christian Christelis <christian@kartoza.com>'
__revision__ = '$Format:%H$'
__date__ = '24/10/14'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import random
import os
import logging
from collections import OrderedDict

from safe.impact_functions.core import (
    FunctionProvider,
    get_plugins,
    requirements_collect,
    requirement_check,
    requirements_met,
    get_function_title,
    parse_single_requirement,
    aggregate,
    convert_to_old_keywords,
    get_admissible_plugins,
    population_rounding_full,
    population_rounding,
    evacuated_population_needs,
    compatible_layers,
    remove_impact_function)
from safe.common.resource_parameter import ResourceParameter
from safe.storage.core import read_layer
from safe.utilities.utilities import read_file_keywords
from safe.defaults import default_minimum_needs
from safe.impact_functions.utilities import (
    admissible_plugins_to_str)
from safe.definitions import converter_dict
from safe.impact_functions.impact_function_metadata import (
    ImpactFunctionMetadata)
from safe.test.utilities import TESTDATA, HAZDATA

LOGGER = logging.getLogger('InaSAFE')


# noinspection PyUnresolvedReferences
class BasicFunctionCore(FunctionProvider):
    """Risk plugin for testing

    :author Allen
    :rating 1
    :param requires category=="test_cat1"
    :param requires unit=="MMI"
    """

    class Metadata(ImpactFunctionMetadata):
        """Metadata for Basic Function Core.
        """

        @staticmethod
        def get_metadata():
            """Return metadata as a dictionary.

            This is a static method. You can use it to get the metadata in
            dictionary format for an impact function.

            :returns: A dictionary representing all the metadata for the
                concrete impact function.
            :rtype: dict
            """
            dict_meta = {
                'id': 'BasicFunctionCore',
                'name': 'Basic Function Core',
                'impact': 'Be affected',
                'author': 'N/A',
                'date_implemented': 'N/A',
                'overview': (
                    'This impact function will calculate the impact of an '
                    'earthquake on buildings, reporting how many are expected '
                    'to be damaged etc.'),
            }
            return dict_meta

    @staticmethod
    def run():
        """ Run mock method.

        :returns: None
        """
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
    class Metadata(ImpactFunctionMetadata):
        """Metadata for Basic Function Core.
        """

        @staticmethod
        def get_metadata():
            """Return metadata as a dictionary.

            This is a static method. You can use it to get the metadata in
            dictionary format for an impact function.

            :returns: A dictionary representing all the metadata for the
                concrete impact function.
            :rtype: dict
            """
            dict_meta = {
                'id': 'F1',
                'name': 'F1',
                'title': 'Title for F1',
                'impact': 'Be affected',
                'author': 'N/A',
                'date_implemented': 'N/A',
                'overview': (
                    'This impact function will calculate the impact of an '
                    'earthquake on buildings, reporting how many are expected '
                    'to be damaged etc.'),
                }
            return dict_meta

    @staticmethod
    def run():
        """ Run mock method.

        :returns: None
        """
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
    class Metadata(ImpactFunctionMetadata):
        """Metadata for Basic Function Core.
        """

        @staticmethod
        def get_metadata():
            """Return metadata as a dictionary.

            This is a static method. You can use it to get the metadata in
            dictionary format for an impact function.

            :returns: A dictionary representing all the metadata for the
                concrete impact function.
            :rtype: dict
            """
            dict_meta = {
                'id': 'F2',
                'name': 'F2',
                'title': 'Title for F2',
                'impact': 'Be affected',
                'author': 'N/A',
                'date_implemented': 'N/A',
                'overview': (
                    'This impact function will calculate the impact of an '
                    'earthquake on buildings, reporting how many are expected '
                    'to be damaged etc.'),
                }
            return dict_meta

    title = 'Title for F2'

    @staticmethod
    def run():
        """ Run mock method.

        :returns: None
        """
        return None


class F3(FunctionProvider):
    """Risk plugin for testing

    :param requires category=='test_cat1'
    :param requires category=='test_cat2'
    """

    class Metadata(ImpactFunctionMetadata):
        """Metadata for Basic Function Core.
        """

        @staticmethod
        def get_metadata():
            """Return metadata as a dictionary.

            This is a static method. You can use it to get the metadata in
            dictionary format for an impact function.

            :returns: A dictionary representing all the metadata for the
                concrete impact function.
            :rtype: dict
            """
            dict_meta = {
                'id': 'F3',
                'name': 'F3',
                'title': 'F3',
                'impact': 'Be affected',
                'author': 'N/A',
                'date_implemented': 'N/A',
                'overview': (
                    'This impact function will calculate the impact of an '
                    'earthquake on buildings, reporting how many are expected '
                    'to be damaged etc.'),
                }
            return dict_meta

    @staticmethod
    def run():
        """ Run mock method.

        :returns: None
        """
        return None


class F4(FunctionProvider):
    """Risk plugin for testing

    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami']

    :param requires category=='exposure' and \
                    subcategory in ['building', 'structure'] and \
                    layertype=='vector'
    """

    class Metadata(ImpactFunctionMetadata):
        """Metadata for Basic Function Core.
        """

        @staticmethod
        def get_metadata():
            """Return metadata as a dictionary.

            This is a static method. You can use it to get the metadata in
            dictionary format for an impact function.

            :returns: A dictionary representing all the metadata for the
                concrete impact function.
            :rtype: dict
            """
            dict_meta = {
                'id': 'F4',
                'name': 'F4',
                'impact': 'Be affected',
                'author': 'N/A',
                'date_implemented': 'N/A',
                'overview': (
                    'This impact function will calculate the impact of an '
                    'earthquake on buildings, reporting how many are expected '
                    'to be damaged etc.'),
                }
            return dict_meta

    @staticmethod
    def run():
        """ Run mock method.

        :returns: None
        """
        return None


class SyntaxErrorFunction(FunctionProvider):
    """Risk plugin for testing

    :author Allen
    :rating 1
    :param requires category=="test_cat1"
    :param requires unit="MMI"  # Note the error should be ==
    """

    class Metadata(ImpactFunctionMetadata):
        """Metadata for Basic Function Core.
        """

        @staticmethod
        def get_metadata():
            """Return metadata as a dictionary.

            This is a static method. You can use it to get the metadata in
            dictionary format for an impact function.

            :returns: A dictionary representing all the metadata for the
                concrete impact function.
            :rtype: dict
            """
            dict_meta = {
                'id': 'SyntaxErrorFunction',
                'name': 'Syntax Error Function',
                'impact': 'Be affected',
                'author': 'N/A',
                'date_implemented': 'N/A',
                'overview': (
                    'This impact function will calculate the impact of an '
                    'earthquake on buildings, reporting how many are expected '
                    'to be damaged etc.'),
                }
            return dict_meta

    @staticmethod
    def run():
        """ Run mock method.

        :returns: None
        """
        return None


class TestCore(unittest.TestCase):
    def setUp(self):
        """Setup test before each unit"""
        self.vector_path = os.path.join(TESTDATA, 'Padang_WGS84.shp')
        self.raster_shake_path = os.path.join(
            HAZDATA, 'Shakemap_Padang_2009.asc')

    def test_get_plugin_list(self):
        """It is possible to retrieve the list of functions."""
        plugin_list = get_plugins()
        message = 'No plugins were found, not even the built-in ones'
        assert len(plugin_list) > 0, message

    def test_single_get_plugins(self):
        """Named plugin can be retrieved"""
        plugin_name = 'ITBFatalityFunction'
        plugin_list = get_plugins(plugin_name)
        message = 'No plugins were found matching %s' % plugin_name
        assert len(plugin_list) > 0, message

    def test_get_admissible_plugins(self):
        """Test for get_admissible_plugins function."""
        functions = get_admissible_plugins()
        message = 'No functions available (len=%ss)' % len(functions)
        self.assertTrue(len(functions) > 0, message)

        # Also test if it works when we give it two layers
        # to see if we can determine which functions will
        # work for them.
        keywords1 = read_file_keywords(self.raster_shake_path)
        keywords2 = read_file_keywords(self.vector_path)
        # We need to explicitly add the layer type to each keyword list
        keywords1['layertype'] = 'raster'
        keywords2['layertype'] = 'vector'

        functions = [keywords1, keywords2]
        functions = get_admissible_plugins(functions)
        message = 'No functions available (len=%ss)' % len(functions)
        self.assertTrue(len(functions) > 0, message)

    def test_get_plugins(self):
        """Plugins can be collected."""
        os.environ['LANG'] = 'en'
        plugin_list = get_plugins()
        self.assertGreater(len(plugin_list), 0)

        # Obtain string representation
        string_rep = admissible_plugins_to_str(plugin_list)

        # Check each plugin
        for plugin in plugin_list.values():
            # Check that it's name appears in string representation
            title = get_function_title(plugin)
            message = (
                'Expected title %s in string representation: %s'
                % (title, string_rep))
            assert title in string_rep, message

            # Check that every plugin has a requires line
            requirements = requirements_collect(plugin)
            message = 'There were no requirements in plugin %s' % plugin
            assert (len(requirements) > 0), message

            for required_string in requirements:
                message = 'All plugins should return True or False'
                assert (requirement_check(
                    {'category': 'hazard',
                     'subcategory': 'earthquake',
                     'layerType': 'raster'},
                    required_string) in [True, False]), message

    def test_plugin_compatibility(self):
        """Default plugins perform as expected."""

        # Get list of plugins
        plugin_list = get_plugins()
        assert len(plugin_list) > 0

        # Characterisation test to preserve the behaviour of
        # get_layer_descriptors. FIXME: I think we should change this to be
        # a dictionary of metadata entries (ticket #126).
        reference = [
            ['lembang_schools', {'layertype': 'vector',
                                 'category': 'exposure',
                                 'subcategory': 'building',
                                 'title': 'lembang_schools'}],
            ['shakemap_padang_20090930', {'layertype': 'raster',
                                          'category': 'hazard',
                                          'subcategory': 'earthquake',
                                          'title': 'shakemap_padang_20090930'}]
        ]

        # Check plugins are returned
        metadata = reference
        annotated_plugins = [{'name': name,
                              'doc': f.__doc__,
                              'layers': compatible_layers(f, metadata)}
                             for name, f in plugin_list.items()]

        msg = 'No compatible layers returned'
        assert len(annotated_plugins) > 0, msg

    def test_population_rounding(self):
        """Test for population_rounding_full function."""
        # rounding up
        for _ in range(100):
            # After choosing some random numbers the sum of the randomly
            # selected and one greater than that should be less than the
            # population rounded versions of these.
            n = random.randint(1, 1000000)
            n_pop, dummy = population_rounding_full(n)
            n1 = n + 1
            n1_pop, dummy = population_rounding_full(n1)
            self.assertGreater(n_pop + n1_pop, n + n1)

        self.assertEqual(population_rounding_full(989)[0], 990)
        self.assertEqual(population_rounding_full(991)[0], 1000)
        self.assertEqual(population_rounding_full(8888)[0], 8900)
        self.assertEqual(population_rounding_full(9888888)[0], 9889000)

        for _ in range(100):
            n = random.randint(1, 1000000)
            self.assertEqual(
                population_rounding(n),
                population_rounding_full(n)[0])

    def test_evacuated_population_needs(self):
        """Test evacuated_population_needs function."""
        water = ResourceParameter()
        water.name = 'Water'
        water.unit.name = 'litre'
        water.unit.abbreviation = 'l'
        water.unit.plural = 'litres'
        water.frequency = 'weekly'
        water.maximum_allowed_value = 10
        water.minimum_allowed_value = 0
        water.value = 5
        rice = ResourceParameter()
        rice.name = 'Rice'
        rice.unit.name = 'kilogram'
        rice.unit.abbreviation = 'kg'
        rice.unit.plural = 'kilograms'
        rice.frequency = 'daily'
        rice.maximum_allowed_value = 1
        rice.minimum_allowed_value = 0
        rice.value = 0.5
        total_needs = evacuated_population_needs(
            10,
            [water.serialize(), rice.serialize()]
        )
        self.assertEqual(total_needs['weekly'][0]['name'], 'Water')
        self.assertEqual(total_needs['weekly'][0]['amount'], 50)
        self.assertEqual(total_needs['weekly'][0]['table name'], 'Water [l]')
        self.assertEqual(total_needs['daily'][0]['name'], 'Rice')
        self.assertEqual(total_needs['daily'][0]['amount'], 5)
        self.assertEqual(total_needs['daily'][0]['table name'], 'Rice [kg]')

    def test_basic_plugin_requirements(self):
        """Test requirements_collect."""
        requirements = requirements_collect(BasicFunctionCore)
        valid_return = ['category=="test_cat1"', 'unit=="MMI"']
        for ret1, ret2 in zip(valid_return, requirements):
            self.assertEqual(ret1, ret2, "Error in requirements extraction")

    def test_basic_plugin_requirements_met(self):
        """Test requirements_met"""
        requirements = requirements_collect(BasicFunctionCore)
        params = {'category': 'test_cat1', 'unit': 'MMI'}
        self.assertTrue(requirements_met(requirements, params))

        params = {'category': 'test_cat2', 'unit': 'mmi2'}
        self.assertFalse(requirements_met(requirements, params))

    def test_basic_requirements_check(self):
        """Test requirement_check."""
        requirements = requirements_collect(BasicFunctionCore)
        params = {'category': 'test_cat2'}
        for line in requirements:
            check = requirement_check(params, line)
            self.assertFalse(check)

        line = "unit='MMI'"
        params = {'category': 'test_cat2'}
        msg = 'Malformed statement (logged)'
        self.assertFalse(requirement_check(params, line), msg)

    def test_keywords_error(self):
        """Handling of reserved python keywords """
        line = "unit=='MMI'"
        params = {'class': 'myclass'}
        msg = 'Reserved keyword in statement (logged)'
        self.assertFalse(requirement_check(params, line), msg)

    def test_filtering_of_impact_functions(self):
        """Impact functions are filtered correctly
        """
        # Keywords matching F1 and F3
        haz_keywords1 = dict(category='test_cat1', subcategory='flood',
                             layertype='raster', unit='m')
        exp_keywords1 = dict(category='test_cat2',
                             subcategory='population',
                             layertype='raster', datatype='population')

        # Keywords matching F2 and F3
        haz_keywords2 = dict(category='test_cat1', subcategory='flood',
                             layertype='raster', unit='m')
        exp_keywords2 = dict(category='test_cat2',
                             subcategory='building')

        # Check correct matching of keyword set 1
        plugins = get_admissible_plugins([haz_keywords1, exp_keywords1])
        msg = 'Expected impact functions F1 and F3 in %s' % str(plugins.keys())
        self.assertIn('F1', plugins, msg)
        self.assertIn('F3', plugins, msg)
        self.assertNotIn('F2', plugins, msg)

        # Check correctness of title attribute
        self.assertEqual(get_function_title(plugins['F1']), 'Title for F1')
        self.assertEqual(get_function_title(plugins['F3']), 'F3')

        # Check correct matching of keyword set 2
        plugins = get_admissible_plugins([haz_keywords2, exp_keywords2])
        msg = 'Expected impact functions F2 and F3 in %s' % str(
            plugins.keys())
        self.assertIn('F2', plugins, msg)
        self.assertIn('F3', plugins, msg)
        self.assertNotIn('F1', plugins, msg)

        # Check correctness of title attribute
        self.assertEqual(get_function_title(plugins['F2']), 'Title for F2')
        self.assertEqual(get_function_title(plugins['F3']), 'F3')

        # Check empty call returns all
        plugins = get_admissible_plugins([])
        msg = ('Expected at least impact functions F1, F2 and F3 in %s'
               % str(plugins.keys()))
        self.assertIn('F1', plugins, msg)
        self.assertIn('F2', plugins, msg)
        self.assertIn('F3', plugins, msg)

    def test_parse_requirement(self):
        """Test parse requirements of a function to dictionary."""
        requirements = requirements_collect(F4)[0]
        parsed_req = parse_single_requirement(requirements)
        expected_req = {'category': 'hazard',
                        'subcategory': ['flood', 'tsunami']}
        message = 'Get %s should be % s' % (parsed_req, expected_req)
        self.assertEqual(parsed_req, expected_req, message)

        requirements = requirements_collect(F4)[1]
        parsed_req = parse_single_requirement(requirements)
        expected_req = {'category': 'exposure',
                        'subcategory': ['building', 'structure'],
                        'layertype': 'vector'}
        message = 'Get %s should be % s' % (parsed_req, expected_req)
        assert parsed_req == expected_req, message

    def test_default_needs(self):
        """default calculated needs are as expected
        """
        minimum_needs = [
            parameter.serialize() for parameter in
            default_minimum_needs()]
        # 20 Happens to be the smallest number at which integer rounding
        # won't make a difference to the result
        result = evacuated_population_needs(20, minimum_needs)['weekly']
        result = OrderedDict(
            [[r['table name'], r['amount']] for r in result])

        assert (result['Rice [kg]'] == 56
                and result['Drinking Water [l]'] == 350
                and result['Clean Water [l]'] == 1340
                and result['Family Kits'] == 4)

        result = evacuated_population_needs(10, minimum_needs)['single']
        result = OrderedDict(
            [[r['table name'], r['amount']] for r in result])
        assert result['Toilets'] == 1

    def test_arbitrary_needs(self):
        """custom need ratios calculated are as expected
        """
        minimum_needs = [
            parameter.serialize() for parameter in
            default_minimum_needs()]
        minimum_needs[0]['value'] = 4
        minimum_needs[1]['value'] = 3
        minimum_needs[2]['value'] = 2
        minimum_needs[3]['value'] = 1
        minimum_needs[4]['value'] = 0.2
        result = evacuated_population_needs(10, minimum_needs)['weekly']
        result = OrderedDict(
            [[r['table name'], r['amount']] for r in result])

        assert (result['Rice [kg]'] == 40
                and result['Drinking Water [l]'] == 30
                and result['Clean Water [l]'] == 20
                and result['Family Kits'] == 10)
        result = evacuated_population_needs(10, minimum_needs)['single']
        result = OrderedDict(
            [[r['table name'], r['amount']] for r in result])
        assert result['Toilets'] == 2

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

    def test_aggregate_real(self):
        """Aggregation by boundaries works."""

        # Name file names for hazard level and exposure
        boundary_filename = ('%s/kecamatan_jakarta_osm.shp' % TESTDATA)
        # data_filename = ('%s/Population_Jakarta_geographic.asc' % TESTDATA)

        # Get reference building impact data
        building_filename = ('%s/building_impact_scenario.shp' % TESTDATA)

        boundary_layer = read_layer(boundary_filename)
        building_layer = read_layer(building_filename)

        res = aggregate(
            data=building_layer,
            boundaries=boundary_layer,
            attribute_name='AFFECTED',
            aggregation_function='count')

        # print res, len(res)
        # print boundary_layer, len(boundary_layer)
        msg = (
            'Number of aggregations %i should be the same as the number of '
            'specified boundaries %i' % (len(res), len(boundary_layer)))
        assert len(res) == len(boundary_layer), msg

        # FIXME (Ole): Need test by manual inspection in QGis
        # print res

    test_aggregate.slow = True

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
        msg = 'Expected %s but I got %s' % (
            expected_keywords, new_keywords)
        self.assertDictEqual(new_keywords, expected_keywords, msg)

    @classmethod
    def tearDownClass(cls):
        remove_impact_function(BasicFunctionCore)
        remove_impact_function(F1)
        remove_impact_function(F2)
        remove_impact_function(F3)
        remove_impact_function(F4)
        remove_impact_function(SyntaxErrorFunction)

if __name__ == '__main__':
    unittest.main()
