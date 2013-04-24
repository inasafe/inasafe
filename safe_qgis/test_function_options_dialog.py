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
import unittest
import sys
import os
import logging

from PyQt4.QtGui import QLineEdit

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from safe_interface import get_plugins
from third_party.odict import OrderedDict

from safe_qgis.function_options_dialog import FunctionOptionsDialog
from safe_qgis.utilities_test import getQgisTestApp
# pylint: disable=W0611
from safe.engine.impact_functions_for_testing.itb_fatality_model_configurable\
    import ITBFatalityFunctionConfigurable
# pylint: enable=W0611

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
LOGGER = logging.getLogger('InaSAFE')


class FunctionOptionsDialogTest(unittest.TestCase):
    """Test the InaSAFE GUI for Configurable Impact Functions"""

    def setUp(self):
        """Fixture run before all tests"""
        pass

    def tearUp(self):
        """Fixture run before each test"""
        pass

    def tearDown(self):
        """Fixture run after each test"""
        pass

    def test_buildForm(self):
        """Test that we can build a form by passing it a function and params.
        """
        myFunctionId = 'I T B Fatality Function Configurable'
        myFunctionList = get_plugins(myFunctionId)
        assert len(myFunctionList) == 1
        assert myFunctionList[0].keys()[0] == myFunctionId

        myDialog = FunctionOptionsDialog(None)
        myParameters = {
            'thresholds': [1.0],
            'postprocessors': {
                'Gender': {'on': True},
                'Age': {
                    'on': True,
                    'params': {
                        'youth_ratio': 0.263,
                        'elder_ratio': 0.078,
                        'adult_ratio': 0.659}}}}

        myDialog.buildForm(myParameters)

        assert myDialog.tabWidget.count() == 2

        myChildren = myDialog.tabWidget.findChildren(QLineEdit)
        assert len(myChildren) == 4

    def test_buildWidget(self):
        myDialog = FunctionOptionsDialog(None)
        myValue = myDialog.buildWidget(myDialog.configLayout, 'foo', [2.3])
        myWidget = myDialog.findChild(QLineEdit)

        # initial value must be same with default
        assert myValue() == [2.3]

        # change to 5.9
        myWidget.setText('5.9')
        assert myValue() == [5.9]

        myWidget.setText('5.9, 70')
        assert myValue() == [5.9, 70]

        myWidget.setText('bar')
        try:
            myValue()
        except ValueError:
            ## expected to raises this exception
            pass
        else:
            raise Exception("Fail: must be raise an exception")

    def test_parseInput(self):
        myInput = {
            'thresholds': lambda: [1.0],
            'postprocessors': {
                'Gender': {'on': lambda: True},
                'Age': {
                    'on': lambda: True,
                    'params': {
                        'youth_ratio': lambda: 0.263,
                        'elder_ratio': lambda: 0.078,
                        'adult_ratio': lambda: 0.659}}}}

        myDialog = FunctionOptionsDialog(None)
        myResult = myDialog.parseInput(myInput)
        print myResult
        assert myResult == OrderedDict([
            ('thresholds', [1.0]),
            ('postprocessors', OrderedDict([
                ('Gender', OrderedDict([('on', True)])),
                ('Age', OrderedDict([
                    ('on', True),
                    ('params', OrderedDict([
                        ('youth_ratio', 0.263),
                        ('elder_ratio', 0.078),
                        ('adult_ratio', 0.659)]))]))]))])

if __name__ == '__main__':
    suite = unittest.makeSuite(FunctionOptionsDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
