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
#from unittest import expectedFailure

from os.path import join
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from PyQt4 import QtCore
from PyQt4.QtTest import QTest

from safe.common.testing import HAZDATA, EXPDATA, TESTDATA, UNITDATA

from safe_qgis.utilities_test import (getQgisTestApp,
                                setCanvasCrs,
                                setPadangGeoExtent,
                                setBatemansBayGeoExtent,
                                setJakartaGeoExtent,
                                setYogyaGeoExtent,
                                setJakartaGoogleExtent,
                                setGeoExtent,
                                GEOCRS,
                                GOOGLECRS,
                                loadLayer)

from safe_qgis.dock import Dock
from safe_qgis.utilities import (setRasterStyle,
                          qgisVersion,
                          getDefaults)


# pylint: enable=W0611
LOGGER = logging.getLogger('InaSAFE')

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
DOCK = Dock(IFACE)


from safe.engine.impact_functions_for_testing.itb_fatality_model_configurable\
    import ITBFatalityFunctionConfigurable


class FunctionOptionsDialogTest(unittest.TestCase):
    """Test the InaSAFE GUI for Configurable Impact Functions"""

    def setUp(self):
        """Fixture run before all tests"""
        os.environ['LANG'] = 'en'
        pass

    def tearUp(self):
        """Fixture run before each test"""
        pass

    def tearDown(self):
        """Fixture run after each test"""
        pass

    def test_defaults(self):
        pass

    def test_hasParametersButtonEnabled(self):
        pass

    def test_noParametersButtonDisabled(self):
        pass


if __name__ == "__main__":
    suite = unittest.makeSuite(FunctionOptionsDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
