# coding=utf-8
"""Tests for impact function plugins."""
import os
import numpy
import unittest

from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_plugins

from safe.impact_functions.core import requirements_collect
from safe.impact_functions.core import requirement_check
from safe.impact_functions.core import compatible_layers
from safe.impact_functions.core import aggregate
from safe.impact_functions.core import get_function_title

from safe.impact_functions.utilities import Damage_curve
from safe.impact_functions.utilities import admissible_plugins_to_str
from safe.impact_functions.utilities import keywords_to_str

from safe.storage.core import read_layer
from safe.common.testing import TESTDATA

DEFAULT_PLUGINS = ('Earthquake Fatality Function',)

# These imports are needed for impact function registration if this test
# is to be run independently - dont remove
# If any of these get reinstated as "official" public impact functions,
# remove from here and update test to use the real one.
# pylint: disable=W0611
from safe.engine.impact_functions_for_testing import empirical_fatality_model
from safe.engine.impact_functions_for_testing import allen_fatality_model
# pylint: enable=W0611


class BasicFunction(FunctionProvider):
    """Risk plugin for testing

    :author Allen
    :rating 1
    :param requires category=="hazard"
    """

    @staticmethod
    def run():
        """Dummy run implementation.

        :return: None
        """
        return None


class Test_plugins(unittest.TestCase):
    """Tests of Risiko calculations"""
    def test_get_plugin_list(self):
        """It is possible to retrieve the list of functions."""

        plugin_list = get_plugins()
        message = 'No plugins were found, not even the built-in ones'
        assert len(plugin_list) > 0, message

    def test_single_get_plugins(self):
        """Named plugin can be retrieved"""
        plugin_name = DEFAULT_PLUGINS[0]
        plugin_list = get_plugins(plugin_name)
        message = 'No plugins were found matching %s' % plugin_name
        assert len(plugin_list) > 0, message

    def test_keywords_to_str(self):
        """String representation of keywords works."""

        keywords = {
            'category': 'hazard', 'subcategory': 'tsunami', 'unit': 'm'}
        string_keywords = keywords_to_str(keywords)
        for key in keywords:
            message = (
                'Expected key %s to appear in %s' % (key, string_keywords))
            assert key in string_keywords, message

            val = keywords[key]
            message = (
                'Expected value %s to appear in %s' % (val, string_keywords))
            assert val in string_keywords, message

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
            assert(len(requirements) > 0), message

            for required_string in requirements:
                message = 'All plugins should return True or False'
                assert(requirement_check(
                    {'category': 'hazard',
                     'subcategory': 'earthquake',
                     'layerType': 'raster'},
                    required_string) in [True, False]), message

    def test_requirements_check(self):
        """Plugins are correctly filtered based on requirements."""
        plugin_list = get_plugins('BasicFunction')
        self.assertEqual(len(plugin_list), 1)

        requirements = requirements_collect(plugin_list[0].values()[0])
        message = 'Requirements are %s' % requirements
        assert(len(requirements) == 1), message
        for req_str in requirements:
            message = 'Should eval to True'
            assert(requirement_check({'category': 'hazard'},
                                     req_str) is True), message
            message = 'Should eval to False'
            assert(requirement_check({'broke': 'broke'},
                                     req_str) is False), message

        try:
            plugin_list = get_plugins('NotRegistered')
        except RuntimeError:
            pass
        else:
            message = 'Search should fail'
            raise Exception(message)

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
                                          'title': 'shakemap_padang_20090930'}
            ]]

        # Check plugins are returned
        metadata = reference
        annotated_plugins = [{'name': name,
                              'doc': f.__doc__,
                              'layers': compatible_layers(f, metadata)}
                             for name, f in plugin_list.items()]

        msg = 'No compatible layers returned'
        assert len(annotated_plugins) > 0, msg

    def test_damage_curve(self):
        """Damage curve class works."""

        # Make data
        x = [1.0, 2.0, 4.0]

        # Define array with corresponding values
        A = numpy.zeros((len(x), 2), dtype='f')
        A[:, 0] = x

        # Define values for each x
        for i in range(len(x)):
            A[i, 1] = 2 * A[i, 0] + 3

        # Instantiate
        D = Damage_curve(A)

        # Check
        assert D(1.0) == 5
        assert D(1.5) == 6
        assert D(3.0) == 9

        # Check exceptions
        try:
            Damage_curve(None)
        except RuntimeError:
            pass
        else:
            message = 'Damage_curve should have raised exception for None'
            raise Exception(message)

        try:
            Damage_curve([[1, 2], [3, 4, 5]])
        except RuntimeError:
            pass
        else:
            message = (
                'Damage_curve should have raised exception for invalid input')
            raise Exception(message)

        try:
            Damage_curve(x)
        except RuntimeError:
            pass
        else:
            message = 'Damage_curve should have raised exception for 1d array'
            raise Exception(message)

        try:
            Damage_curve(numpy.zeros((3, 4, 5)))
        except RuntimeError:
            pass
        else:
            message = (
                'Damage_curve should have raised exception for more than '
                'two dimensions')
            raise Exception(message)

        try:
            Damage_curve(numpy.zeros((3, 3)))
        except RuntimeError:
            pass
        else:
            message = (
                'Damage_curve should have raised exception for more than '
                'two columns')
            raise Exception(message)

    def test_aggregate(self):
        """Aggregation by boundaries works."""

        # Name file names for hazard level and exposure
        boundary_filename = ('%s/kecamatan_jakarta_osm.shp' % TESTDATA)
        #data_filename = ('%s/Population_Jakarta_geographic.asc' % TESTDATA)

        # Get reference building impact data
        building_filename = ('%s/building_impact_scenario.shp' % TESTDATA)

        boundary_layer = read_layer(boundary_filename)
        building_layer = read_layer(building_filename)

        res = aggregate(
            data=building_layer,
            boundaries=boundary_layer,
            attribute_name='AFFECTED',
            aggregation_function='count')

        #print res, len(res)
        #print boundary_layer, len(boundary_layer)
        msg = (
            'Number of aggregations %i should be the same as the number of '
            'specified boundaries %i' % (len(res), len(boundary_layer)))
        assert len(res) == len(boundary_layer), msg

        # FIXME (Ole): Need test by manual inspection in QGis
        #print res
    test_aggregate.slow = True

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_plugins, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
