"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'Marco Bernasocchi'
__date__ = '10/01/2011'
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
class AggregatorTest(unittest.TestCase):
    """Test the InaSAFE GUI"""

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
        DOCK.showPostProcLayers = False

    def test_cboAggregationEmptyProject(self):
        """Aggregation combo changes properly according on no loaded layers"""
        self.tearDown()
        myMessage = ('The aggregation combobox should have only the "Entire '
                     'area" item when the project has no layer. Found:'
                     ' %s' % (DOCK.cboAggregation.currentText()))

        self.assertEqual(DOCK.cboAggregation.currentText(), DOCK.tr(
            'Entire area'), myMessage)

        myMessage = ('The aggregation combobox should be disabled when the '
                     'project has no layer.')

        assert not DOCK.cboAggregation.isEnabled(), myMessage

    def test_cboAggregationLoadedProject(self):
        """Aggregation combo changes properly according loaded layers"""
        myLayerList = [DOCK.tr('Entire area'),
                       DOCK.tr('kabupaten jakarta singlepart')]
        currentLayers = [DOCK.cboAggregation.itemText(i) for i in range(
            DOCK.cboAggregation.count())]

        myMessage = ('The aggregation combobox should have:\n %s \nFound: %s'
                     % (myLayerList, currentLayers))
        self.assertEquals(currentLayers, myLayerList, myMessage)

    #FIXME (MB) this is actually wrong, when calling the test directly it works
    # in nosetest it fails at the second assert
    @expectedFailure
    def test_cboAggregationToggle(self):
        """Aggregation Combobox toggles on and off as expected."""
        #raster hazard
        #raster exposure
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregationEnabledFlag=True)
        myMessage += ' when the when hazard and exposure layer are raster'
        assert myResult, myMessage

        #vector hazard
        #raster exposure
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function Vector Hazard',
            theAggregationEnabledFlag=False)
        myMessage += ' when the when hazard is vector and exposure is raster'
        assert myResult, myMessage

        #raster hazard
        #vector exposure
        myResult, myMessage = setupScenario(
            theHazard='Tsunami Max Inundation',
            theExposure='Tsunami Building Exposure',
            theFunction='Be flooded',
            theFunctionId='Flood Building Impact Function',
            theAggregationEnabledFlag=False)
        myMessage += ' when the when hazard is raster and exposure is vector'
        assert myResult, myMessage

        #vector hazard
        #vector exposure
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta',
            theExposure='Essential buildings',
            theFunction='Be flooded',
            theFunctionId='Flood Building Impact Function',
            theAggregationEnabledFlag=False)
        myMessage += ' when the when hazard and exposure layer are vector'
        assert myResult, myMessage

    def test_checkAggregationAttributeInKW(self):
        """Aggregation attribute is chosen correctly when present
            in kezwords."""
        myRunButton = DOCK.pbnRunStop
        myAttrKey = getDefaults('AGGR_ATTR_KEY')

        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregation='kabupaten jakarta singlepart',
            theAggregationEnabledFlag=True)
        assert myResult, myMessage
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKeywordsDialog.accept()
        myAttribute = DOCK.postProcessingAttributes[myAttrKey]
        myMessage = ('The aggregation should be KAB_NAME. Found: %s' %
                     myAttribute)
        self.assertEqual(myAttribute, 'KAB_NAME', myMessage)

    def test_checkAggregationAttribute1Attr(self):
        """Aggregation attribute is chosen correctly when there is only
        one attr available."""
        myRunButton = DOCK.pbnRunStop
        myFileList = ['kabupaten_jakarta_singlepart_1_good_attr.shp']
        #add additional layers
        loadLayers(myFileList, theClearFlag=False, theDataDirectory=TESTDATA)
        myAttrKey = getDefaults('AGGR_ATTR_KEY')

        # with 1 good aggregation attribute using
        # kabupaten_jakarta_singlepart_1_good_attr.shp
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregation='kabupaten jakarta singlepart 1 good attr')
        assert myResult, myMessage
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKeywordsDialog.accept()
        myAttribute = DOCK.postProcessingAttributes[myAttrKey]
        myMessage = ('The aggregation should be KAB_NAME. Found: %s' %
                     myAttribute)
        self.assertEqual(myAttribute, 'KAB_NAME', myMessage)

    def test_checkAggregationAttributeNoAttr(self):
        """Aggregation attribute is chosen correctly when there is no
        attr available."""

        myRunButton = DOCK.pbnRunStop
        myFileList = ['kabupaten_jakarta_singlepart_0_good_attr.shp']
        #add additional layers
        loadLayers(myFileList, theClearFlag=False, theDataDirectory=TESTDATA)
        myAttrKey = getDefaults('AGGR_ATTR_KEY')
        # with no good aggregation attribute using
        # kabupaten_jakarta_singlepart_0_good_attr.shp
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregation='kabupaten jakarta singlepart 0 good attr')
        assert myResult, myMessage
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKeywordsDialog.accept()
        myAttribute = DOCK.postProcessingAttributes[myAttrKey]
        myMessage = ('The aggregation should be None. Found: %s' %
                     myAttribute)
        assert myAttribute is None, myMessage

    def test_checkAggregationAttributeNoneAttr(self):
        """Aggregation attribute is chosen correctly when there None in the
            kezwords"""

        myRunButton = DOCK.pbnRunStop
        myFileList = ['kabupaten_jakarta_singlepart_with_None_keyword.shp']
        #add additional layers
        loadLayers(myFileList, theClearFlag=False, theDataDirectory=TESTDATA)
        myAttrKey = getDefaults('AGGR_ATTR_KEY')
        # with None aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart_with_None_keyword.shp
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregation='kabupaten jakarta singlepart with None keyword')
        assert myResult, myMessage
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKeywordsDialog.accept()
        myAttribute = DOCK.postProcessingAttributes[myAttrKey]
        myMessage = ('The aggregation should be None. Found: %s' % myAttribute)
        assert myAttribute is None, myMessage

    def test_checkPostProcessingLayersVisibility(self):
        """Generated layers are not added to the map registry."""
        myRunButton = DOCK.pbnRunStop

        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregation='kabupaten jakarta singlepart',
            theOkButtonFlag=True)
        assert myResult, myMessage
        myBeforeCount = len(CANVAS.layers())
        #LOGGER.info("Canvas list before:\n%s" % canvasList())
        print [str(l.name()) for l in
               QgsMapLayerRegistry.instance().mapLayers().values()]
        LOGGER.info("Registry list before:\n%s" %
                    len(QgsMapLayerRegistry.instance().mapLayers()))
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        myAfterCount = len(CANVAS.layers())
        LOGGER.info("Registry list after:\n%s" %
                    len(QgsMapLayerRegistry.instance().mapLayers()))
        #        print [str(l.name()) for l in QgsMapLayerRegistry.instance(
        #           ).mapLayers().values()]
        #LOGGER.info("Canvas list after:\n%s" % canvasList())
        myMessage = ('Expected %s items in canvas, got %s' %
                     (myBeforeCount + 1, myAfterCount))
        assert myBeforeCount + 1 == myAfterCount, myMessage

        # Now run again showing intermediate layers

        DOCK.showPostProcLayers = True
        myBeforeCount = len(CANVAS.layers())
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        myAfterCount = len(CANVAS.layers())
        LOGGER.info("Canvas list after:\n %s" % canvasList())
        myMessage = ('Expected %s items in canvas, got %s' %
                     (myBeforeCount + 2, myAfterCount))
        # We expect two more since we enabled showing intermedate layers
        assert myBeforeCount + 2 == myAfterCount, myMessage

    def test_postProcessorOutput(self):
        """Check that the post processor does not add spurious report rows."""
        myRunButton = DOCK.pbnRunStop

        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        myResult, myMessage = setupScenario(
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
