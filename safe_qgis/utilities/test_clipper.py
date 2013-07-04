"""
InaSAFE Disaster risk assessment tool developed by AusAid -
 **ISClipper test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""


__author__ = 'tim@linfiniti.com'
__date__ = '20/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os
from unittest import expectedFailure

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..//'))
sys.path.append(pardir)

import numpy

from qgis.core import (QgsVectorLayer,
                       QgsRasterLayer,
                       QgsGeometry,
                       QgsPoint)

from safe_qgis.safe_interface import (readSafeLayer,
                                      getOptimalExtent,
                                      HAZDATA, TESTDATA, EXPDATA, UNITDATA,
                                      GetDataError,
                                      nanallclose)
from safe_qgis.exceptions import InvalidProjectionError, CallGDALError
from safe_qgis.utilities.clipper import (
    clipLayer,
    extentToKml,
    explodeMultiPartGeometry,
    clipGeometry)
from safe_qgis.utilities.utilities import qgisVersion

from safe_qgis.utilities.utilities_test import (
    getQgisTestApp,
    setCanvasCrs,
    RedirectStdStreams,
    DEVNULL,
    GEOCRS,
    setJakartaGeoExtent)

# Setup path names for test data sets
VECTOR_PATH = os.path.join(TESTDATA, 'Padang_WGS84.shp')
VECTOR_PATH2 = os.path.join(TESTDATA, 'OSM_subset_google_mercator.shp')
VECTOR_PATH3 = os.path.join(UNITDATA, 'exposure', 'buildings_osm_4326.shp')

RASTERPATH = os.path.join(HAZDATA, 'Shakemap_Padang_2009.asc')
RASTERPATH2 = os.path.join(TESTDATA, 'population_padang_1.asc')


# Handle to common QGis test app
QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


class ClipperTest(unittest.TestCase):
    """Test the InaSAFE clipper"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_clipVector(self):
        """Vector layers can be clipped
        """

        # Create a vector layer
        myName = 'padang'
        myVectorLayer = QgsVectorLayer(VECTOR_PATH, myName, 'ogr')

        myMessage = 'Did not find layer "%s" in path "%s"' % \
                    (myName, VECTOR_PATH)
        assert myVectorLayer is not None, myMessage
        assert myVectorLayer.isValid()
        # Create a bounding box
        myRect = [100.03, -1.14, 100.81, -0.73]

        # Clip the vector to the bbox
        myResult = clipLayer(myVectorLayer, myRect)

        # Check the output is valid
        assert(os.path.exists(myResult.source()))

    def test_clipRaster(self):
        """Raster layers can be clipped
        """

        # Create a raster layer
        myName = 'shake'
        myRasterLayer = QgsRasterLayer(RASTERPATH, myName)

        myMessage = 'Did not find layer "%s" in path "%s"' % \
                    (myName, RASTERPATH)
        assert myRasterLayer is not None, myMessage

        # Create a bounding box
        myRect = [97, -3, 104, 1]

        # Clip the vector to the bbox
        myResult = clipLayer(myRasterLayer, myRect)

        # Check the output is valid
        assert os.path.exists(myResult.source())

        # Clip and give a desired resolution for the output
        mySize = 0.05
        myResult = clipLayer(myRasterLayer, myRect, mySize)
        myNewRasterLayer = QgsRasterLayer(myResult.source(), myName)
        assert myNewRasterLayer.isValid(), 'Resampled raster is not valid'

        myMessage = ('Resampled raster has incorrect pixel size.'
                     'Expected: %f, Actual: %f' %
                     (mySize, myNewRasterLayer.rasterUnitsPerPixel()))
        assert myNewRasterLayer.rasterUnitsPerPixel() == mySize, myMessage

    # See issue #349
    @expectedFailure
    def test_clipOnePixel(self):
        # Create a raster layer
        myRasterPath = os.path.join(EXPDATA, 'glp10ag.asc')
        myTitle = 'people'
        myRasterLayer = QgsRasterLayer(myRasterPath, myTitle)

        # Create very small bounding box
        mySmallRect = [100.3430, -0.9089, 100.3588, -0.9022]

        # Clip the raster to the bbox
        try:
            _ = clipLayer(myRasterLayer, mySmallRect)
        except CallGDALError:
            pass
        except Exception, e:
            raise Exception('Exception is not expected, %s' % e)
        else:
            myMsg = "Failed, does not raise exception"
            raise Exception(myMsg)

        # Create not very small bounding box
        myNotSmallRect = [100.3430, -0.9089, 101.3588, -1.9022]

        # Clip the raster to the bbox
        myResult = clipLayer(myRasterLayer, myNotSmallRect)
        assert myResult is not None, 'Should be a success clipping'

    def test_invalidFilenamesCaught(self):
        """Invalid filenames raise appropriate exceptions

        Wrote this test because test_clipBoth raised the wrong error
        when file was missing. Instead of reporting that, it gave
        Western boundary must be less than eastern. I got [0.0, 0.0, 0.0, 0.0]

        See issue #170
        """

        # Try to create a vector layer from non-existing filename
        myName = 'stnhaoeu_78oeukqjkrcgA'
        myPath = 'OEk_tnshoeu_439_kstnhoe'

        with RedirectStdStreams(stdout=DEVNULL, stderr=DEVNULL):
            myVectorLayer = QgsVectorLayer(myPath, myName, 'ogr')

        myMessage = ('QgsVectorLayer reported "valid" for non '
                     'existent path "%s" and name "%s".'
                     % (myPath, myName))
        assert not myVectorLayer.isValid(), myMessage

        # Create a raster layer
        with RedirectStdStreams(stdout=DEVNULL, stderr=DEVNULL):
            myRasterLayer = QgsRasterLayer(myPath, myName)
        myMessage = ('QgsRasterLayer reported "valid" for non '
                     'existent path "%s" and name "%s".'
                     % (myPath, myName))
        assert not myRasterLayer.isValid(), myMessage

    def test_clipBoth(self):
        """Raster and Vector layers can be clipped
        """

        # Create a vector layer
        myName = 'padang'
        myVectorLayer = QgsVectorLayer(VECTOR_PATH, myName, 'ogr')
        myMessage = 'Did not find layer "%s" in path "%s"' % \
                    (myName, VECTOR_PATH)
        assert myVectorLayer.isValid(), myMessage

        # Create a raster layer
        myName = 'shake'
        myRasterLayer = QgsRasterLayer(RASTERPATH, myName)
        myMessage = 'Did not find layer "%s" in path "%s"' % \
                    (myName, RASTERPATH)
        assert myRasterLayer.isValid(), myMessage

        # Create a bounding box
        myViewportGeoExtent = [99.53, -1.22, 101.20, -0.36]

        # Get the Hazard extents as an array in EPSG:4326
        myHazardGeoExtent = [myRasterLayer.extent().xMinimum(),
                             myRasterLayer.extent().yMinimum(),
                             myRasterLayer.extent().xMaximum(),
                             myRasterLayer.extent().yMaximum()]

        # Get the Exposure extents as an array in EPSG:4326
        myExposureGeoExtent = [myVectorLayer.extent().xMinimum(),
                               myVectorLayer.extent().yMinimum(),
                               myVectorLayer.extent().xMaximum(),
                               myVectorLayer.extent().yMaximum()]

        # Now work out the optimal extent between the two layers and
        # the current view extent. The optimal extent is the intersection
        # between the two layers and the viewport.
        # Extent is returned as an array [xmin,ymin,xmax,ymax]
        myGeoExtent = getOptimalExtent(myHazardGeoExtent,
                                       myExposureGeoExtent,
                                       myViewportGeoExtent)

        # Clip the vector to the bbox
        myResult = clipLayer(myVectorLayer, myGeoExtent)

        # Check the output is valid
        assert os.path.exists(myResult.source())
        readSafeLayer(myResult.source())

        # Clip the raster to the bbox
        myResult = clipLayer(myRasterLayer, myGeoExtent)

        # Check the output is valid
        assert os.path.exists(myResult.source())
        readSafeLayer(myResult.source())

        # -------------------------------
        # Check the extra keywords option
        # -------------------------------
        # Clip the vector to the bbox
        myResult = clipLayer(myVectorLayer, myGeoExtent,
                             theExtraKeywords={'kermit': 'piggy'})

        # Check the output is valid
        assert os.path.exists(myResult.source())
        L = readSafeLayer(myResult.source())
        kwds = L.get_keywords()
        # myMessage = 'Extra keyword wasn\'t found in %s: %s' % (myResult,
        # kwds)
        assert kwds['kermit'] == 'piggy'

        # Clip the raster to the bbox
        myResult = clipLayer(myRasterLayer, myGeoExtent,
                             theExtraKeywords={'zoot': 'animal'})

        # Check the output is valid
        assert os.path.exists(myResult.source())
        L = readSafeLayer(myResult.source())
        kwds = L.get_keywords()

        myMessage = 'Extra keyword was not found in %s: %s' % (
            myResult.source(), kwds)
        assert kwds['zoot'] == 'animal', myMessage

    def testRasterScaling(self):
        """Raster layers can be scaled when resampled

        This is a test for ticket #52

        Native test .asc data has

        Population_Jakarta_geographic.asc
        ncols         638
        nrows         649
        cellsize      0.00045228819716044

        Population_2010.asc
        ncols         5525
        nrows         2050
        cellsize      0.0083333333333333

        Scaling is necessary for raster data that represents density
        such as population per km^2
        """

        for myFilename in ['Population_Jakarta_geographic.asc',
                           'Population_2010.asc']:

            myRasterPath = ('%s/%s' % (TESTDATA, myFilename))

            # Get reference values
            mySafeLayer = readSafeLayer(myRasterPath)
            myMinimum, myMaximum = mySafeLayer.get_extrema()
            del myMaximum
            del myMinimum
            myNativeResolution = mySafeLayer.get_resolution()

            # Get the Hazard extents as an array in EPSG:4326
            myBoundingBox = mySafeLayer.get_bounding_box()

            # Test for a range of resolutions
            for myResolution in [0.02,
                                 0.01,
                                 0.005,
                                 0.002,
                                 0.001,
                                 0.0005,   # Coarser
                                 0.0002]:  # Finer

                # To save time only do two resolutions for the
                # large population set
                if myFilename.startswith('Population_2010'):
                    if myResolution > 0.01 or myResolution < 0.005:
                        break

                # Clip the raster to the bbox
                myExtraKeywords = {'resolution': myNativeResolution}
                myRasterLayer = QgsRasterLayer(myRasterPath, 'xxx')
                myResult = clipLayer(myRasterLayer,
                                     myBoundingBox,
                                     myResolution,
                                     theExtraKeywords=myExtraKeywords)

                mySafeLayer = readSafeLayer(myResult.source())
                myNativeData = mySafeLayer.get_data(scaling=False)
                myScaledData = mySafeLayer.get_data(scaling=True)

                mySigma = (mySafeLayer.get_resolution()[0] /
                           myNativeResolution[0]) ** 2

                # Compare extrema
                myExpectedScaledMax = mySigma * numpy.nanmax(myNativeData)
                myMessage = ('Resampled raster was not rescaled correctly: '
                             'max(myScaledData) was %f but expected %f'
                             % (numpy.nanmax(myScaledData),
                                myExpectedScaledMax))

                # FIXME (Ole): The rtol used to be 1.0e-8 -
                #              now it has to be 1.0e-6, otherwise we get
                #              max(myScaledData) was 12083021.000000 but
                #              expected 12083020.414316
                #              Is something being rounded to the nearest
                #              integer?
                assert numpy.allclose(myExpectedScaledMax,
                                      numpy.nanmax(myScaledData),
                                      rtol=1.0e-6, atol=1.0e-8), myMessage

                myExpectedScaledMin = mySigma * numpy.nanmin(myNativeData)
                myMessage = ('Resampled raster was not rescaled correctly: '
                             'min(myScaledData) was %f but expected %f'
                             % (numpy.nanmin(myScaledData),
                                myExpectedScaledMin))
                assert numpy.allclose(myExpectedScaledMin,
                                      numpy.nanmin(myScaledData),
                                      rtol=1.0e-8, atol=1.0e-12), myMessage

                # Compare elementwise
                myMessage = 'Resampled raster was not rescaled correctly'
                assert nanallclose(myNativeData * mySigma, myScaledData,
                                   rtol=1.0e-8, atol=1.0e-8), myMessage

                # Check that it also works with manual scaling
                myManualData = mySafeLayer.get_data(scaling=mySigma)
                myMessage = 'Resampled raster was not rescaled correctly'
                assert nanallclose(myManualData, myScaledData,
                                   rtol=1.0e-8, atol=1.0e-8), myMessage

                # Check that an exception is raised for bad arguments
                try:
                    mySafeLayer.get_data(scaling='bad')
                except GetDataError:
                    pass
                else:
                    myMessage = 'String argument should have raised exception'
                    raise Exception(myMessage)

                try:
                    mySafeLayer.get_data(scaling='(1, 3)')
                except GetDataError:
                    pass
                else:
                    myMessage = 'Tuple argument should have raised exception'
                    raise Exception(myMessage)

                # Check None option without keyword datatype == 'density'
                mySafeLayer.keywords['datatype'] = 'undefined'
                myUnscaledData = mySafeLayer.get_data(scaling=None)
                myMessage = 'Data should not have changed'
                assert nanallclose(myNativeData, myUnscaledData,
                                   rtol=1.0e-12, atol=1.0e-12), myMessage

                # Try with None and density keyword
                mySafeLayer.keywords['datatype'] = 'density'
                myUnscaledData = mySafeLayer.get_data(scaling=None)
                myMessage = 'Resampled raster was not rescaled correctly'
                assert nanallclose(myScaledData, myUnscaledData,
                                   rtol=1.0e-12, atol=1.0e-12), myMessage

                mySafeLayer.keywords['datatype'] = 'counts'
                myUnscaledData = mySafeLayer.get_data(scaling=None)
                myMessage = 'Data should not have changed'
                assert nanallclose(myNativeData, myUnscaledData,
                                   rtol=1.0e-12, atol=1.0e-12), myMessage

    def testRasterScaling_projected(self):
        """Attempt to scale projected density raster layers raise exception

        Automatic scaling when resampling density data
        does not currently work for projected layers. See issue #123.

        For the time being this test checks that an exception is raised
        when scaling is attempted on projected layers.
        When we resolve issue #123, this test should be rewritten.
        """

        myTestFilename = 'Population_Jakarta_UTM48N.tif'
        myRasterPath = ('%s/%s' % (TESTDATA, myTestFilename))

        # Get reference values
        mySafeLayer = readSafeLayer(myRasterPath)
        myMinimum, myMaximum = mySafeLayer.get_extrema()
        myNativeResolution = mySafeLayer.get_resolution()

        print
        print myMinimum, myMaximum
        print myNativeResolution

        # Define bounding box in EPSG:4326
        myBoundingBox = [106.61, -6.38, 107.05, -6.07]

        # Test for a range of resolutions
        for myResolution in [0.02, 0.01, 0.005, 0.002, 0.001]:

            # Clip the raster to the bbox
            myExtraKeywords = {'resolution': myNativeResolution}
            myRasterLayer = QgsRasterLayer(myRasterPath, 'xxx')
            try:
                clipLayer(myRasterLayer,
                          myBoundingBox,
                          myResolution,
                          theExtraKeywords=myExtraKeywords)
            except InvalidProjectionError:
                pass
            else:
                myMessage = 'Should have raised InvalidProjectionError'
                raise Exception(myMessage)

    def test_extentToKml(self):
        """Test if extent to KML is working."""
        myExtent = [100.03, -1.14, 100.81, -0.73]
        myKmlFilename = extentToKml(myExtent)
        assert os.path.exists(myKmlFilename)
        myFile = open(myKmlFilename)
        myKml = myFile.read()
        myFile.close()

        myMessage = 'Generated KML was not as expected: %s' % myKml
        assert '<?xml version' in myKml, myMessage
        for myValue in myExtent:
            assert str(myValue) in myKml, myMessage

    def test_vectorProjections(self):
        """Test that vector input data is reprojected properly during clip"""
        # Input data is OSM in GOOGLE CRS
        # We are reprojecting to GEO and expecting the output shp to be in GEO
        # see https://github.com/AIFDR/inasafe/issues/119
        # and https://github.com/AIFDR/inasafe/issues/95
        myVectorLayer = QgsVectorLayer(VECTOR_PATH2,
                                       'OSM Buildings',
                                       'ogr')
        myMessage = 'Failed to load osm buildings'
        assert myVectorLayer is not None, myMessage
        assert myVectorLayer.isValid()
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()
        myClipRect = [106.52, -6.38, 107.14, -6.07]
        # Clip the vector to the bbox
        myResult = clipLayer(myVectorLayer, myClipRect)
        assert(os.path.exists(myResult.source()))

    def test_explodeMultiPolygonGeometry(self):
        """Test exploding POLY multipart to single part geometries works"""
        myGeometry = QgsGeometry.fromWkt(
            'MULTIPOLYGON(((-0.966314 0.445890,'
            '-0.281133 0.555729,-0.092839 0.218369,-0.908780 0.035305,'
            '-0.966314 0.445890)),((-0.906164 0.003923,-0.077148 0.197447,'
            '0.043151 -0.074533,-0.882628 -0.296824,-0.906164 0.003923)))')
        myCollection = explodeMultiPartGeometry(myGeometry)
        myMessage = 'Expected 2 parts from multipart polygon geometry'
        assert len(myCollection) == 2, myMessage

    def test_explodeMultiLineGeometry(self):
        """Test exploding LINES multipart to single part geometries works"""
        myGeometry = QgsGeometry.fromWkt(
            'MULTILINESTRING((-0.974159 0.526961,'
            ' -0.291594 0.644645), (-0.411893 0.728331,'
            ' -0.160834 0.568804))')
        myCollection = explodeMultiPartGeometry(myGeometry)
        myMessage = 'Expected 2 parts from multipart line geometry'
        assert len(myCollection) == 2, myMessage

    def test_explodeMultiPointGeometry(self):
        """Test exploding POINT multipart to single part geometries works"""
        myGeometry = QgsGeometry.fromWkt(
            'MULTIPOINT((-0.966314 0.445890),'
            '(-0.281133 0.555729))')
        myCollection = explodeMultiPartGeometry(myGeometry)
        myMessage = 'Expected 2 parts from multipart point geometry'
        assert len(myCollection) == 2, myMessage

    def test_clipGeometry(self):
        """Test that we can clip a geometry using another geometry."""
        myGeometry = QgsGeometry.fromPolyline([
            QgsPoint(10, 10),
            QgsPoint(20, 20),
            QgsPoint(30, 30),
            QgsPoint(40, 40)])

        myClipPolygon = QgsGeometry.fromPolygon([[QgsPoint(20, 20),
                                                  QgsPoint(20, 30),
                                                  QgsPoint(30, 30),
                                                  QgsPoint(30, 20),
                                                  QgsPoint(20, 20)]])

        myResult = clipGeometry(myClipPolygon, myGeometry)

        if qgisVersion() > 10800:
            myExpectedWkt = 'LINESTRING(20.0 20.0, 30.0 30.0)'
        else:
            myExpectedWkt = ('LINESTRING(20.000000 20.000000, '
                             '30.000000 30.000000)')
        # There should only be one feature that intersects this clip
        # poly so this assertion should work.
        self.assertEqual(myExpectedWkt, str(myResult.exportToWkt()))

        # Now poly on poly clip test
        myClipPolygon = QgsGeometry.fromWkt(
            'POLYGON((106.8218 -6.1842,106.8232 -6.1842,'
            '106.82304963 -6.18317148,106.82179736 -6.18314774,'
            '106.8218 -6.1842))')
        myGeometry = QgsGeometry.fromWkt(
            'POLYGON((106.8216869 -6.1852067,106.8213233 -6.1843051,'
            '106.8212891 -6.1835559,106.8222566 -6.1835184,'
            '106.8227557 -6.1835076,106.8228588 -6.1851204,'
            '106.8216869 -6.1852067))')
        myResult = clipGeometry(myClipPolygon, myGeometry)

        if qgisVersion() > 10800:
            myExpectedWkt = (
                'POLYGON((106.82179833 -6.18353616,106.8222566 -6.1835184,'
                '106.8227557 -6.1835076,106.82279996 -6.1842,'
                '106.8218 -6.1842,106.82179833 -6.18353616))')
        else:
            myExpectedWkt = (
                'POLYGON((106.821798 -6.183536,106.822257 -6.183518,'
                '106.822756 -6.183508,106.822800 -6.184200,'
                '106.821800 -6.184200,106.821798 -6.183536))')
        # There should only be one feature that intersects this clip
        # poly so this assertion should work.
        self.assertEqual(myExpectedWkt, str(myResult.exportToWkt()))

        # Now point on poly test clip

        myGeometry = QgsGeometry.fromWkt('POINT(106.82241 -6.18369)')
        myResult = clipGeometry(myClipPolygon, myGeometry)

        if qgisVersion() > 10800:
            myExpectedWkt = 'POINT(106.82241 -6.18369)'
        else:
            myExpectedWkt = 'POINT(106.822410 -6.183690)'
            # There should only be one feature that intersects this clip
        # poly so this assertion should work.
        self.assertEqual(myExpectedWkt, str(myResult.exportToWkt()))

    def test_clipVectorHard(self):
        """Vector layers can be hard clipped.

        Hard clipping will remove any dangling, non intersecting elements.
        """
        myVectorLayer = QgsVectorLayer(VECTOR_PATH3,
                                       'OSM Buildings',
                                       'ogr')
        myMessage = 'Failed to load osm buildings'
        assert myVectorLayer is not None, myMessage
        assert myVectorLayer.isValid()
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()
        myClipRect = [106.8218, -6.1842, 106.8232, -6.1830]

        # Clip the vector to the bbox
        myResult = clipLayer(myVectorLayer, myClipRect, theHardClipFlag=True)

        # Check the output is valid
        assert(os.path.exists(myResult.source()))

if __name__ == '__main__':
    suite = unittest.makeSuite(ClipperTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
