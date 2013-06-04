"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '19/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os
import logging
from unittest import expectedFailure


from os.path import join
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)
#for p in sys.path:
#    print p + '\n'

from PyQt4 import QtCore
from PyQt4.QtTest import QTest

from qgis.core import QgsMapLayerRegistry
from safe_interface import TESTDATA

from safe_qgis.utilities_test import (getQgisTestApp,
                                      setCanvasCrs,
                                      setJakartaGeoExtent,
                                      GEOCRS)

from safe_qgis.dock import Dock
from safe_qgis.utilities import getDefaults

from safe_qgis.utilities_test import (
    loadStandardLayers,
    setupScenario,
    loadLayers,
    canvasList)

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
DOCK = Dock(IFACE)

LOGGER = logging.getLogger('InaSAFE')


#noinspection PyArgumentList
class PostprocessorManagerTest(unittest.TestCase):
    """Test the postprocessor manager"""

    def setUp(self):
        """Fixture run before all tests"""
        os.environ['LANG'] = 'en'
        DOCK.showOnlyVisibleLayersFlag = True
        loadStandardLayers()
        DOCK.cboHazard.setCurrentIndex(0)
        DOCK.cboExposure.setCurrentIndex(0)
        DOCK.cboFunction.setCurrentIndex(0)
        DOCK.runInThreadFlag = False
        DOCK.showOnlyVisibleLayersFlag = False
        DOCK.setLayerNameFromTitleFlag = False
        DOCK.zoomToImpactFlag = False
        DOCK.hideExposureFlag = False
        DOCK.showIntermediateLayers = False
        setJakartaGeoExtent()

    def test_checkPostProcessingLayersVisibility(self):
        """Generated layers are not added to the map registry."""
        myRunButton = DOCK.pbnRunStop

        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregationLayer='kabupaten jakarta singlepart',
            theOkButtonFlag=True)
        assert myResult, myMessage

        LOGGER.info("Registry list before:\n%s" %
                    QgsMapLayerRegistry.instance().mapLayers())

        #one layer (the impact) should have been added
        myExpectedCount = len(CANVAS.layers()) + 1

        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKeywordsDialog.accept()

        myAfterCount = len(CANVAS.layers())
        LOGGER.info("Registry list after:\n%s" %
                    QgsMapLayerRegistry.instance().mapLayers())
        myMessage = ('Expected %s items in canvas, got %s' %
                     (myExpectedCount, myAfterCount))
        assert myExpectedCount == myAfterCount, myMessage

        # Now run again showing intermediate layers
        DOCK.showIntermediateLayers = True
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKeywordsDialog.accept()
        #one layer (the impact) should have been added
        myExpectedCount += 2
        myAfterCount = len(CANVAS.layers())

        LOGGER.info("Canvas list after:\n %s" % canvasList())
        myMessage = ('Expected %s items in canvas, got %s' %
                     (myExpectedCount, myAfterCount))
        # We expect two more since we enabled showing intermedate layers
        assert myExpectedCount == myAfterCount, myMessage

    def test_postProcessorOutput(self):
        """Check that the post processor does not add spurious report rows."""
        myRunButton = DOCK.pbnRunStop

        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theOkButtonFlag=True)

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()

        assert myResult, myMessage

        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        myMessage = 'Spurious 0 filled rows added to post processing report.'
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()
        for line in myResult.split('\n'):
            if 'Entire area' in line:
                myTokens = str(line).split('\t')
                myTokens = myTokens[1:]
                mySum = 0
                for myToken in myTokens:
                    mySum += float(myToken.replace(',', '.'))

                assert mySum != 0, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(PostprocessorManagerTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
