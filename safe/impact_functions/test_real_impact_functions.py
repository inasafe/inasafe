# coding=utf-8
"""Works with real library impact functions rather than test examples
"""

import unittest

from safe.impact_functions.core import get_admissible_plugins
from safe.impact_functions.core import requirements_collect


class TestRealImpactFunctions(unittest.TestCase):
    """Tests of SAFE calculations
    """

    def test_filtering_of_impact_functions(self):
        """Impact functions are filtered correctly
        """

        # Check empty call returns all
        admissible_plugins = get_admissible_plugins([])

        # List the known impact function names
        # based on their class names - not their titles
        msg = (
            'Available impact functions are: %s' %
            str(admissible_plugins.keys()))

        self.assertIn(
            'Flood Evacuation Function Vector Hazard',
            admissible_plugins, msg)
        self.assertIn(
            'I T B Earthquake Building Damage Function',
            admissible_plugins, msg)
        self.assertIn(
            'Earthquake Building Impact Function',
            admissible_plugins, msg)
        self.assertIn(
            'P A G Fatality Function',
            admissible_plugins, msg)
        self.assertIn(
            'Flood Evacuation Function',
            admissible_plugins, msg)
        self.assertIn(
            'Flood Building Impact Function',
            admissible_plugins, msg)
        self.assertIn(
            'I T B Fatality Function',
            admissible_plugins, msg)
        self.assertIn(
            'Volcano Building Impact',
            admissible_plugins, msg)
        self.assertIn(
            'Volcano Polygon Hazard Population',
            admissible_plugins, msg)

        # This one should get 2 earthquake building impact functions
        dict1 = {
            'category': 'hazard',
            'subcategory': 'earthquake',
            'unit': 'MMI'}
        dict2 = dict(
            category='exposure',
            datatype='itb',
            subcategory='structure')

        # Add layertype
        dict1['layertype'] = 'raster'
        dict2['layertype'] = 'vector'
        admissible_plugins = get_admissible_plugins([dict1, dict2])
        msg = (
            'Expected: len(admissible_plugins) >= 2, Got: '
            'len(admissible_plugins) is %i' % len(admissible_plugins))
        # Depending on other tests there could be more
        assert len(admissible_plugins) >= 1, msg
        assert 'Earthquake Building Impact Function' in admissible_plugins

        # This one should get 3 flood population impact functions
        dict1 = {'category': 'hazard', 'subcategory': 'flood', 'unit': 'm'}
        dict2 = dict(category='exposure', subcategory='population')

        # Add layertype
        dict1['layertype'] = 'raster'
        dict2['layertype'] = 'raster'
        admissible_plugins = get_admissible_plugins([dict1, dict2])
        # Depending on other tests there could be more
        assert len(admissible_plugins) >= 1
        #assert 'W B Flood Evacuation Function' in admissible_plugins

        # Try form where only one dictionary is passed
        # This one gets all the flood related impact functions

        # Try to get general inundation building impact function
        f_name = 'Flood Building Impact Function'

        admissible_plugins = get_admissible_plugins(dict1)
        assert len(admissible_plugins) >= 2
        #assert 'W B Flood Evacuation Function' in admissible_plugins
        assert f_name in admissible_plugins
        #assert 'Flood Road Impact Function' in admissible_plugins

        dict1 = {'category': 'hazard', 'subcategory': 'tsunami'}
        dict2 = dict(category='exposure', subcategory='structure')

        # Add layertype
        # Not required for flood building impact
        #dict1['layertype'] = 'raster'
        dict2['layertype'] = 'vector'
        admissible_plugins = get_admissible_plugins([dict1, dict2])

        msg = 'Expected name "%s" in admissible_plugins: %s' % (
            f_name, admissible_plugins)
        assert f_name in admissible_plugins, msg

        # Get requirements from expected function
        all_plugins = get_admissible_plugins()
        assert admissible_plugins[f_name] == all_plugins[f_name]

        requirelines = requirements_collect(admissible_plugins[f_name])
        for i, D in enumerate([dict1, dict2]):
            for key in D:
                msg = 'Key %s was not found in %s' % (key, requirelines[i])
                assert key in requirelines[i], msg

                msg = 'Val %s was not found in %s' % (D[key], requirelines[i])
                assert D[key] in requirelines[i], msg

if __name__ == '__main__':
    suite = unittest.makeSuite(TestRealImpactFunctions)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
