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
        message = (
            'Available impact functions are: %s' %
            str(admissible_plugins.keys()))

        if_names = [
            'Flood Evacuation Function Vector Hazard',
            'Earthquake Building Impact Function',
            'PAG Fatality Function',
            'Flood Evacuation Function',
            'Flood Vector Building Impact Function',
            'Flood Raster Building Impact Function',
            'ITB Fatality Function',
            'Volcano Building Impact',
            'Volcano Polygon Hazard Population',
            ]

        for if_name in if_names:
            self.assertIn(if_name, admissible_plugins, message)

        # This one should get 1 earthquake building impact functions
        dict1 = dict(
            category='hazard',
            subcategory='earthquake',
            layertype='raster',
            unit='MMI')

        dict2 = dict(
            category='exposure',
            subcategory='structure',
            layertype='vector',
            datatype='itb')

        admissible_plugins = get_admissible_plugins([dict1, dict2])
        message = (
            'Expected: len(admissible_plugins) >= 1, Got: '
            'len(admissible_plugins) is %i' % len(admissible_plugins))
        # Depending on other tests there could be more
        self.assertTrue(len(admissible_plugins) >= 1, message)
        self.assertIn(
            'Earthquake Building Impact Function', admissible_plugins)

        # This one should get 1 flood population impact functions
        dict1 = dict(
            category='hazard',
            subcategory='flood',
            layertype='raster',
            unit='m')
        dict2 = dict(
            category='exposure',
            subcategory='population',
            layertype='raster')

        admissible_plugins = get_admissible_plugins([dict1, dict2])
        # Depending on other tests there could be more
        self.assertTrue(len(admissible_plugins) >= 1)
        # Try to get general inundation population impact function
        f_name = 'Flood Evacuation Function'
        self.assertIn(f_name, admissible_plugins)

        admissible_plugins = get_admissible_plugins(dict1)
        self.assertTrue(len(admissible_plugins) >= 1)
        self.assertIn(f_name, admissible_plugins)

        dict1 = dict(
            category='hazard',
            subcategory='flood',
            layertype='raster')
        dict2 = dict(
            category='exposure',
            subcategory='structure',
            layertype='vector')

        admissible_plugins = get_admissible_plugins([dict1, dict2])
        f_name = 'Flood Raster Building Impact Function'
        message = 'Expected name "%s" in admissible_plugins: %s' % (
            f_name, admissible_plugins)
        self.assertIn(f_name, admissible_plugins, message)

        # Get requirements from expected function
        all_plugins = get_admissible_plugins()
        self.assertEqual(admissible_plugins[f_name], all_plugins[f_name])

        requirelines = requirements_collect(admissible_plugins[f_name])
        for i, D in enumerate([dict1, dict2]):
            for key in D:
                message = 'Key %s was not found in %s' % (key, requirelines[i])
                self.assertIn(key, requirelines[i], message)

                message = (
                    'Val %s was not found in %s' % (D[key], requirelines[i]))
                self.assertIn(D[key], requirelines[i], message)

if __name__ == '__main__':
    suite = unittest.makeSuite(TestRealImpactFunctions)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
