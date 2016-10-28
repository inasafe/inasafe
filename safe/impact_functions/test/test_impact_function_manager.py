# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Test Impact Function Manager**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '20/03/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.impact_functions.loader import register_impact_functions
from safe.impact_functions.impact_function_manager import ImpactFunctionManager

from safe.definitionsv4.fields import structure_class_field

from safe.definitionsv4.hazard import hazard_earthquake


class TestImpactFunctionManager(unittest.TestCase):
    """Test for ImpactFunctionManager.

    .. versionadded:: 2.1
    """

    def setUp(self):
        register_impact_functions()

    def test_init(self):
        """TestImpactFunctionManager: Test initialize ImpactFunctionManager."""
        impact_function_manager = ImpactFunctionManager()
        expected_result = len(impact_function_manager.registry.list())
        i = 0
        '''
        print 'Your impact functions:'
        for impact_function in \
                impact_function_manager.registry.impact_functions:
            i += 1
            print i, impact_function.metadata().as_dict()['name']
        '''
        result = len(impact_function_manager.registry.list())
        message = (
            'I expect %s but I got %s, please check the number of current '
            'enabled impact functions' % (expected_result, result))
        self.assertEqual(result, expected_result, message)

    def test_available_hazards(self):
        """Test available_hazards API."""
        impact_function_manager = ImpactFunctionManager()

        result = impact_function_manager.available_hazards(
            'single_event')
        expected_result = [hazard_earthquake]
        message = ('I expect %s but I got %s.' % (expected_result, result))
        self.assertItemsEqual(result, expected_result, message)

    def test_exposure_class_fields(self):
        """Test for exposure_class_fields."""
        ifm = ImpactFunctionManager()
        additional_keywords = ifm.exposure_class_fields(
            layer_mode_key='classified',
            layer_geometry_key='polygon',
            exposure_key='structure'
        )
        expected = [structure_class_field]

        self.assertItemsEqual(additional_keywords, expected)

if __name__ == '__main__':
    unittest.main()
