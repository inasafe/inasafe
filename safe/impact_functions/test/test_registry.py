from safe.impact_functions import register_impact_functions
from safe.impact_functions.inundation.flood_building_impact_qgis import \
    FloodNativePolygonExperimentalFunction
from safe.impact_functions.registry import Registry

__author__ = 'lucernae'
__project_name__ = 'inasafe'
__filename__ = 'test_registry'
__date__ = '19/03/15'
__copyright__ = 'lana.pcfre@gmail.com'

import unittest


class TestRegistry(unittest.TestCase):

    def setUp(self):
        register_impact_functions()

    def test_register_and_clear(self):
        registry = Registry()
        registry.clear()
        message = 'Expecting registry should be cleared. %s impact functions ' \
                  'exists instead' % len(registry.impact_functions)
        self.assertEqual(0, len(registry.impact_functions), message)
        registry.register(FloodNativePolygonExperimentalFunction)
        message = 'Expecting registry will contains 1 impact functions. %s ' \
                  'impact functions exists' % len(registry.impact_functions)
        self.assertEqual(1, len(registry.impact_functions), message)
        result = registry.get('FloodNativePolygonExperimentalFunction')\
            .metadata().as_dict()['id']
        expected = 'FloodNativePolygonExperimentalFunction'
        message = 'Expected registered impact function name should be %s. ' \
                  'Got %s instead' % (expected, result)
        self.assertEqual(expected, result,
                         message)
        # restore registry state
        register_impact_functions()

    def test_filter_by_keywords(self):
        # keywords should be a dictionary string
        hazard_keywords = {
            'subcategory': 'flood',
            'units': 'wetdry',
            'layer_type': 'vector',
            'data_type': 'polygon'
        }

        exposure_keywords = {
            'subcategory': 'structure',
            'units': 'building_type',
            'layer_type': 'vector',
            'data_type': 'polygon'
        }
        registry = Registry()
        impact_functions = registry.filter_by_keyword_string(
            hazard_keywords, exposure_keywords)
        message = 'Registry should returns matched impact functions. ' \
                  'Nothing returned instead. Please check registered IF.'
        self.assertTrue(len(impact_functions) > 0, message)
        for imp_f in impact_functions:
            result = imp_f.metadata().as_dict()['categories']['hazard'][
                'subcategories']
            result_list = [subcat.get('id') for subcat in result]
            expected = 'flood'
            message = 'Expecting flood hazard impactfunctions. Got %s ' \
                      'instead' % result_list[0]
            self.assertTrue(expected in result_list, message)

            result = imp_f.metadata().as_dict()['categories']['exposure'][
                'subcategories']
            result_list = [subcat.get('id') for subcat in result]
            expected = 'structure'
            message = 'Expecting structure exposure impact functions. Got %s ' \
                      'instead' % result_list[0]
            self.assertTrue(expected in result_list, message)

    def test_get_impact_function(self):
        registry = Registry()
        expected = 'FloodNativePolygonExperimentalFunction'
        impact_function = registry.get(
            expected)
        result = impact_function.metadata().as_dict().get('id', '')
        message = 'Expecting FloodNativePolygonExperimentalFunction. Got %s ' \
                  'instead.' % result
        self.assertEqual(expected, result, message)

        expected = 'FloodNativePolygonExperimentalFunction'
        impact_function = registry.get_class(
            expected)
        result = impact_function.metadata().as_dict().get('id', '')
        message = 'Expecting FloodNativePolygonExperimentalFunction. Got %s ' \
                  'instead.' % result
        self.assertEqual(expected, result, message)
        message = 'Expecting a \'type\' object, but returned another.'
        self.assertTrue(isinstance(impact_function, type), message)

        expected = 'FloodNativePolygonExperimentalFunction'
        impact_function = registry.get_by_metadata_id(
            expected)
        result = impact_function.metadata().as_dict().get('id', '')
        message = 'Expecting FloodNativePolygonExperimentalFunction. Got %s ' \
                  'instead.' % result
        self.assertEqual(expected, result, message)
        message = 'Expecting a \'type\' object, but returned another.'
        self.assertTrue(isinstance(impact_function, type), message)

        expected = 'Flood Native Polygon Experimental Function'
        impact_function = registry.get_by_metadata_name(
            expected)
        result = impact_function.metadata().as_dict().get('name', '')
        message = 'Expecting Flood Native Polygon Experimental Function. ' \
                  'Got %s instead.' % result
        self.assertEqual(expected, result, message)
        message = 'Expecting a \'type\' object, but returned another.'
        self.assertTrue(isinstance(impact_function, type), message)