# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'misugijunz@gmail.com'
__date__ = '15/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import sys
PARAMETERS_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), '..', 'safe_extras', 'parameters'))
if PARAMETERS_DIR not in sys.path:
    sys.path.append(PARAMETERS_DIR)

import unittest

import logging
from collections import OrderedDict

# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from PyQt4.QtGui import QLineEdit, QCheckBox

from safe.test.utilities import get_qgis_app
from safe.common.resource_parameter import ResourceParameter
from safe.impact_statistics.function_options_dialog import (
    FunctionOptionsDialog)
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
# noinspection PyUnresolvedReferences


QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')


class FunctionOptionsDialogTest(unittest.TestCase):
    """Test the InaSAFE GUI for Configurable Impact Functions"""
    def test_build_form(self):
        """Test that we can build a form by passing it a function and params.
        """
        class_name = 'ITBFatalityFunction'
        impact_function = ImpactFunctionManager().get(class_name)
        assert impact_function.__name__ == class_name

        dialog = FunctionOptionsDialog()

        # Define rice for minimum needs
        rice = ResourceParameter()
        rice.value = 2.8
        rice.frequency = 'weekly'
        rice.minimum_allowed_value = 1.4
        rice.maximum_allowed_value = 5.6
        rice.name = 'Rice'
        rice.unit.abbreviation = 'kg'
        rice.unit.name = 'kilogram'
        rice.unit.plural = 'kilograms'

        parameter = {
            'thresholds': [1.0],
            'postprocessors': {
                'Gender': {'on': True},
                'Age': {
                    'on': True,
                    'params': {
                        'youth_ratio': 0.263,
                        'elderly_ratio': 0.078,
                        'adult_ratio': 0.659
                    }
                }
            },
            'minimum needs': [rice]
        }

        dialog.build_form(parameter)

        message = 'There should be %s tabwidget but got %s' % (
            3, dialog.tabWidget.count())
        self.assertEqual(dialog.tabWidget.count(), 3, message)

        children = dialog.tabWidget.findChildren(QLineEdit)
        message = 'There should be %s QLineEdit but got %s' % (
            5, len(children))
        self.assertEqual(len(children), 5, message)

    def test_build_form_minimum_needs(self):
        """Test that we can build a form by passing it a function and params.
        """
        class_name = 'FloodEvacuationFunctionVectorHazard'
        impact_function = ImpactFunctionManager().get(class_name)
        assert impact_function.__name__ == class_name

        dialog = FunctionOptionsDialog()
        parameters = {
            'thresholds': [1.0],
            'postprocessors': {
                'Gender': {'on': True},
                'Age': {
                    'on': True,
                    'params': {
                        'youth_ratio': 0.263,
                        'elderly_ratio': 0.078,
                        'adult_ratio': 0.659}}}}

        dialog.build_form(parameters)

        assert dialog.tabWidget.count() == 2

        children = dialog.tabWidget.findChildren(QLineEdit)
        assert len(children) == 4

    def test_build_widget(self):
        dialog = FunctionOptionsDialog()
        value = dialog.build_widget(dialog.configLayout, 'foo', [2.3])
        widget = dialog.findChild(QLineEdit)

        # initial value must be same with default
        expected_value = [2.3]
        real_value = value()
        message = 'Expected %s but got %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        # change to 5.9
        widget.setText('5.9')
        expected_value = [5.9]
        real_value = value()
        message = 'Expected %s but got %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget.setText('5.9, 70')
        expected_value = [5.9, 70]
        real_value = value()
        message = 'Expected %s but got %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget.setText('bar')
        try:
            value()
        except ValueError:
            # expected to raises this exception
            pass
        else:
            raise Exception("Fail: must be raise an exception")

        dialog = FunctionOptionsDialog()
        value = dialog.build_widget(dialog.configLayout, 'foo', True)
        widget = dialog.findChild(QCheckBox)

        # initial value must be same with default
        expected_value = True
        real_value = value()
        message = 'Expected %s but got %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget.setChecked(False)
        expected_value = False
        real_value = value()
        message = 'Expected %s but got %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        original_value = {'a': 1, 'b': 2}
        dialog = FunctionOptionsDialog()
        value = dialog.build_widget(dialog.configLayout, 'foo', original_value)
        widget = dialog.findChild(QLineEdit)

        # initial value must be same with default
        expected_value = original_value
        real_value = value()
        message = 'Expected %s but got %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        expected_value = {'a': 2, 'b': 1}
        widget.setText(str(expected_value))
        real_value = value()
        message = 'Expected %s but got %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

    def test_parse_input(self):
        function_input = {
            'thresholds': lambda: [1.0],
            'postprocessors': {
                'Gender': {'on': lambda: True},
                'Age': {
                    'on': lambda: True,
                    'params': {
                        'youth_ratio': lambda: 0.263,
                        'elderly_ratio': lambda: 0.078,
                        'adult_ratio': lambda: 0.659}}}}

        dialog = FunctionOptionsDialog()
        result = dialog.parse_input(function_input)
        print result
        expected = OrderedDict([
            ('thresholds', [1.0]),
            ('postprocessors', OrderedDict([
                ('Gender', OrderedDict([('on', True)])),
                ('Age', OrderedDict([
                    ('on', True),
                    ('params', OrderedDict([
                        ('elderly_ratio', 0.078),
                        ('youth_ratio', 0.263),
                        ('adult_ratio', 0.659)]))]))]))])
        # noinspection PyPep8Naming
        self.maxDiff = None
        self.assertDictEqual(result, expected)

if __name__ == '__main__':
    suite = unittest.makeSuite(FunctionOptionsDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
