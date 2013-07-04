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

from os.path import join
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)
#for p in sys.path:
#    print p + '\n'

from PyQt4 import QtCore
from PyQt4.QtTest import QTest


from qgis.core import QgsVectorLayer, QgsFeature

from safe_qgis.safe_interface import (
    TESTDATA,
    BOUNDDATA,
    Raster,
    Vector,
    safe_read_layer)

from safe_qgis.utilities.utilities_test import (
    getQgisTestApp,
    setCanvasCrs,
    setJakartaGeoExtent,
    GEOCRS)

from safe_qgis.dock import Dock
from safe_qgis.impact_statistics.aggregator import Aggregator
from safe_qgis.utilities.clipper import clipLayer
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.utilities.utilities import (
    getDefaults, extentToGeoArray)

from safe_qgis.utilities.utilities_test import (
    loadStandardLayers,
    setupScenario,
    loadLayers)

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
DOCK = Dock(IFACE)

LOGGER = logging.getLogger('InaSAFE')


#noinspection PyArgumentList
class AggregatorTest(unittest.TestCase):
    """Test the InaSAFE GUI"""

    def setUp(self):
        """Fixture run before all tests"""

        self.maxDiff = None  # show full diff for assert errors

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

        self.keywordIO = KeywordIO()
        self.defaults = getDefaults()

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
            theAggregationLayer='kabupaten jakarta singlepart with None '
                                'keyword')
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

    def _aggregate(self, myImpactLayer, myExpectedResults):
        myAggregationLayer = QgsVectorLayer(
            os.path.join(BOUNDDATA, 'kabupaten_jakarta.shp'),
            'test aggregation',
            'ogr')
        # create a copy of aggregation layer
        myGeoExtent = extentToGeoArray(
            myAggregationLayer.extent(),
            myAggregationLayer.crs())

        myAggrAttribute = self.keywordIO.readKeywords(
            myAggregationLayer, self.defaults['AGGR_ATTR_KEY'])
        myAggregationLayer = clipLayer(
            theLayer=myAggregationLayer,
            theExtent=myGeoExtent,
            theExplodeFlag=True,
            theExplodeAttribute=myAggrAttribute)

        myAggregator = Aggregator(None, myAggregationLayer)
        # setting up
        myAggregator.isValid = True
        myAggregator.layer = myAggregationLayer
        myAggregator.safeLayer = safe_read_layer(
            str(myAggregator.layer.source()))
        myAggregator.aoiMode = False
        myAggregator.aggregate(myImpactLayer)

        myProvider = myAggregator.layer.dataProvider()
        myProvider.select(myProvider.attributeIndexes())
        myFeature = QgsFeature()
        myResults = []

        while myProvider.nextFeature(myFeature):
            myFeatureResults = {}
            myAtMap = myFeature.attributeMap()
            for (k, attr) in myAtMap.iteritems():
                myFeatureResults[k] = attr.toString()
            myResults.append(myFeatureResults)

        self.assertEqual(myResults, myExpectedResults)

    def test_aggregate_raster_impact(self):
        # created from loadStandardLayers.qgs with:
        # - a flood in Jakarta like in 2007
        # - Penduduk Jakarta
        # - need evacuation
        # - kabupaten_jakarta_singlepart.shp
        myImpactLayer = Raster(
            data=os.path.join(TESTDATA, 'aggregation_test_impact_raster.tif'),
            name='test raster impact')

        myExpectedResults = [
            {0: 'JAKARTA BARAT',
             1: '50540',
             2: '12015061.8769531',
             3: '237.733713433976',
             4: '50539',
             5: '12015061.8769531',
             6: '237.738417399496'},
            {0: 'JAKARTA PUSAT',
             1: '19492',
             2: '2943702.11401367',
             3: '151.021040119725',
             4: '19492',
             5: '2945658.12207031',
             6: '151.121389394126'},
            {0: 'JAKARTA SELATAN',
             1: '57367',
             2: '1645498.26947021',
             3: '28.6837078716024',
             4: '57372',
             5: '1643522.39849854',
             6: '28.6467684323108'},
            {0: 'JAKARTA UTARA',
             1: '55004',
             2: '11332095.7334595',
             3: '206.023120745027',
             4: '54998',
             5: '11330910.4882202',
             6: '206.024046114772'},
            {0: 'JAKARTA TIMUR',
             1: '73949',
             2: '10943934.3182373',
             3: '147.992999475819',
             4: '73944',
             5: '10945062.4354248',
             6: '148.018262947971'}]

        self._aggregate(myImpactLayer, myExpectedResults)

    def test_aggregate_vector_impact(self):
         # created from loadStandardLayers.qgs with:
        # - a flood in Jakarta like in 2007
        # - Essential buildings
        # - be flodded
        # - kabupaten_jakarta_singlepart.shp
        myImpactLayer = Vector(
            data=os.path.join(TESTDATA, 'aggregation_test_impact_vector.shp'),
            name='test vector impact')

        myExpectedResults = [
            {0: 'JAKARTA BARAT', 1: '87'},
            {0: 'JAKARTA PUSAT', 1: '117'},
            {0: 'JAKARTA SELATAN', 1: '22'},
            {0: 'JAKARTA UTARA', 1: '286'},
            {0: 'JAKARTA TIMUR', 1: '198'}
        ]
        self._aggregate(myImpactLayer, myExpectedResults)

        myImpactLayer = Vector(
            data=TESTDATA + '/aggregation_test_impact_vector_small.shp',
            name='test vector impact')

        myExpectedResults = [
            {0: 'JAKARTA BARAT', 1: '87'},
            {0: 'JAKARTA PUSAT', 1: '117'},
            {0: 'JAKARTA SELATAN', 1: '22'},
            {0: 'JAKARTA UTARA', 1: '286'},
            {0: 'JAKARTA TIMUR', 1: '198'}
        ]

        # TODO (MB) enable this
        # self._aggregate(myImpactLayer, myExpectedResults)

if __name__ == '__main__':
    suite = unittest.makeSuite(AggregatorTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
