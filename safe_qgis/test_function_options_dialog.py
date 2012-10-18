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
__version__ = '0.5.0'
__date__ = '15/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import unittest
import sys
import os
import logging

from PyQt4.QtGui import QWidget, QApplication

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from safe.impact_functions import get_plugins

from safe_qgis.function_options_dialog import FunctionOptionsDialog

# pylint: disable=W0611
from safe.engine.impact_functions_for_testing.itb_fatality_model_configurable\
    import ITBFatalityFunctionConfigurable
# pylint: enable=W0611

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
        myGuiFlag = True
        #QGISAPP = QApplication(sys.argv, myGuiFlag)
        QApplication(sys.argv, myGuiFlag)
        myWidget = QWidget()
        myFunctionId = 'I T B Fatality Function Configurable'
        myFunctionList = get_plugins(myFunctionId)
        assert len(myFunctionList) == 1
        assert myFunctionList[0].keys()[0] == myFunctionId
        myFunction = myFunctionList[0]
        myDialog = FunctionOptionsDialog(myWidget)
        myParameters = {'foo': 'bar'}
        myDialog.buildForm(myFunction, myParameters)

        # Mockup
        myChildren = myDialog.children()
        for myChild in myChildren:
            LOGGER.debug('Child name:' % myChild.objectName())

        # For localised testing only, disable when test works!
        myDialog.exec_()

if __name__ == "__main__":
    suite = unittest.makeSuite(FunctionOptionsDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
