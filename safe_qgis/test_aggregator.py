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
print sys.path

from os.path import join
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)
#for p in sys.path:
#    print p + '\n'

from PyQt4 import QtCore
from PyQt4.QtTest import QTest

from qgis.core import QgsMapLayerRegistry
from safe_interface import (TESTDATA, BOUNDDATA)

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
        DOCK.showIntermediateLayers = False
        setJakartaGeoExtent()

    def test_cboAggregationLoadedProject(self):
        """Aggregation combo changes properly according loaded layers"""
        myLayerList = [DOCK.tr('Entire area'),
                       DOCK.tr('kabupaten jakarta singlepart')]
        currentLayers = [DOCK.cboAggregation.itemText(i) for i in range(
            DOCK.cboAggregation.count())]

        myMessage = ('The aggregation combobox should have:\n %s \nFound: %s'
                     % (myLayerList, currentLayers))
        self.assertEquals(currentLayers, myLayerList, myMessage)

    def test_checkAggregationAttributeInKW(self):
        """Aggregation attribute is chosen correctly when present
            in kezwords."""
        myRunButton = DOCK.pbnRunStop
        myAttrKey = getDefaults('AGGR_ATTR_KEY')

        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregationLayer='kabupaten jakarta singlepart',
            theAggregationEnabledFlag=True)
        assert myResult, myMessage
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKeywordsDialog.accept()
        myAttribute = DOCK.aggregator.attributes[myAttrKey]
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
            DOCK,
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregationLayer='kabupaten jakarta singlepart 1 good attr')
        assert myResult, myMessage
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKeywordsDialog.accept()
        print myAttrKey
        print DOCK.aggregator.attributes
        myAttribute = DOCK.aggregator.attributes[myAttrKey]
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
            DOCK,
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregationLayer='kabupaten jakarta singlepart 0 good attr')
        assert myResult, myMessage
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKeywordsDialog.accept()
        myAttribute = DOCK.aggregator.attributes[myAttrKey]
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
            DOCK,
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregationLayer='kabupaten jakarta singlepart with None keyword')
        assert myResult, myMessage
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKeywordsDialog.accept()
        myAttribute = DOCK.aggregator.attributes[myAttrKey]
        myMessage = ('The aggregation should be None. Found: %s' % myAttribute)
        assert myAttribute is None, myMessage

    def test_preprocessing(self):
        """Preprocessing results are correct.

        TODO - this needs to be fixed post dock refactor.

        """

        # See qgis project in test data: vector_preprocessing_test.qgs
        #add additional layers
        myFileList = ['jakarta_crosskabupaten_polygons.shp']
        loadLayers(myFileList, theClearFlag=False, theDataDirectory=TESTDATA)
        myFileList = ['kabupaten_jakarta.shp']
        loadLayers(myFileList, theClearFlag=False, theDataDirectory=BOUNDDATA)

        myRunButton = DOCK.pbnRunStop

        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='jakarta_crosskabupaten_polygons',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function Vector Hazard',
            theAggregationLayer='kabupaten jakarta',
            theAggregationEnabledFlag=True)
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()
        # Press RUN
        # noinspection PyTypeChecker,PyCallByClass
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKeywordsDialog.accept()

        myExpectedFeatureCount = 20
        myMessage = ('The preprocessing should have generated %s features, '
                     'found %s' % (myExpectedFeatureCount,
                                   DOCK.aggregator.preprocessedFeatureCount))
        self.assertEqual(myExpectedFeatureCount,
                         DOCK.aggregator.preprocessedFeatureCount,
                         myMessage)

if __name__ == '__main__':
    suite = unittest.makeSuite(AggregatorTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
