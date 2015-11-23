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
from safe_extras.parameters.boolean_parameter import BooleanParameter
from safe_extras.parameters.dict_parameter import DictParameter

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
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QLineEdit, QCheckBox, QPushButton, QListWidget, \
    QTreeWidget

from safe.test.utilities import get_qgis_app
from safe.defaults import (
    default_gender_postprocessor,
    age_postprocessor,
    minimum_needs_selector)
from safe.common.resource_parameter import ResourceParameter
from safe.gui.tools.function_options_dialog import (
    FunctionOptionsDialog)
from safe_extras.parameters.input_list_parameter import InputListParameter


QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')


class FunctionOptionsDialogTest(unittest.TestCase):
    """Test the InaSAFE GUI for Configurable Impact Functions"""
    def test_build_form(self):
        """Test that we can build a form by passing params.
        """

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

        # Define threshold
        threshold = InputListParameter()
        threshold.name = 'Thresholds [m]'
        threshold.is_required = True
        threshold.element_type = float
        threshold.expected_type = list
        threshold.ordering = InputListParameter.AscendingOrder
        threshold.minimum_item_count = 1
        threshold.maximum_item_count = 3
        threshold.value = [1.0]  # default value

        parameter = {
            'thresholds': threshold,
            'postprocessors': OrderedDict([
                ('Gender', default_gender_postprocessor()),
                ('Age', age_postprocessor()),
                ('MinimumNeeds', minimum_needs_selector()),
                ]),
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
        """Test that we can build a form by passing it params.
        """
        dialog = FunctionOptionsDialog()

        # Define threshold
        threshold = InputListParameter()
        threshold.name = 'Thresholds [m]'
        threshold.is_required = True
        threshold.element_type = float
        threshold.expected_type = list
        threshold.ordering = InputListParameter.AscendingOrder
        threshold.minimum_item_count = 1
        threshold.maximum_item_count = 3
        threshold.value = [1.0]  # default value

        parameters = {
            'thresholds': threshold,
            'postprocessors': OrderedDict([
                ('Gender', default_gender_postprocessor()),
                ('Age', age_postprocessor()),
                ('MinimumNeeds', minimum_needs_selector()),
                ])
        }

        dialog.build_form(parameters)

        assert dialog.tabWidget.count() == 2

        children = dialog.tabWidget.findChildren(QLineEdit)
        assert len(children) == 4

    @staticmethod
    def click_list_widget_item(list_widget, content):
        """Clicking a list widget item using User Interface

        :param list_widget: the list widget to clear for
        :type list_widget: QListWidget
        :param content: the content text of the list widget item to click
        :type content: str
        """
        # iterate through widget items
        items = list_widget.findItems(content, Qt.MatchExactly)
        for item in items:
            item.setSelected(True)

    def test_build_widget(self):
        dialog = FunctionOptionsDialog()

        # Define threshold
        threshold = InputListParameter()
        threshold.name = 'Thresholds [m]'
        threshold.is_required = True
        threshold.element_type = float
        threshold.expected_type = list
        threshold.ordering = InputListParameter.AscendingOrder
        threshold.minimum_item_count = 1
        threshold.maximum_item_count = 3
        threshold.value = [2.3]  # default value

        value = dialog.build_widget(dialog.configLayout, 'foo', threshold)
        widget = dialog.findChild(QLineEdit)
        add_button = dialog.findChildren(QPushButton)[0]
        remove_button = dialog.findChildren(QPushButton)[1]
        list_widget = dialog.findChild(QListWidget)

        # initial value must be same with default
        expected_value = [2.3]
        real_value = value().value
        message = 'Expected %s but got %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        # change to 5.9
        # select 2.3 list item
        self.click_list_widget_item(list_widget, '2.3')
        # remove 2.3 list item
        remove_button.click()
        # typing 5.9
        widget.setText('5.9')
        # add it to list
        add_button.click()
        expected_value = [5.9]
        real_value = value().value
        message = 'Expected %s but got %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        # add 70
        widget.setText('70')
        # add it to list
        add_button.click()
        expected_value = [5.9, 70]
        real_value = value().value
        message = 'Expected %s but got %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget.setText('bar')
        self.assertEqual('bar', widget.text())

        def trigger_error(error):
            message = 'Expected %s type but got %s' % (
                ValueError, type(error))
            self.assertIsInstance(error, ValueError, message)

        threshold.add_row_error_handler = trigger_error
        add_button.click()

        bool_param = BooleanParameter()
        bool_param.name = 'boolean checkbox'
        bool_param.value = True

        dialog = FunctionOptionsDialog()
        value = dialog.build_widget(dialog.configLayout, 'foo', bool_param)
        widget = dialog.findChild(QCheckBox)

        # initial value must be same with default
        expected_value = True
        real_value = value().value
        message = 'Expected %s but got %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget.setChecked(False)
        expected_value = False
        real_value = value().value
        message = 'Expected %s but got %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        dict_param = DictParameter()
        dict_param.name = 'Dictionary tree'
        dict_param.element_type = int
        dict_param.value = {'a': 1, 'b': 2}
        dialog = FunctionOptionsDialog()
        value = dialog.build_widget(dialog.configLayout, 'foo', dict_param)
        widget = dialog.findChild(QTreeWidget)

        # initial value must be same with default
        expected_value = {'a': 1, 'b': 2}
        real_value = value().value
        message = 'Expected %s but got %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        expected_value = {'a': 2, 'b': 1}
        # get tree items
        tree_items = widget.invisibleRootItem()
        # set the input
        tree_items.child(0).setText(1, str(2))
        tree_items.child(1).setText(1, str(1))
        real_value = value().value
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
