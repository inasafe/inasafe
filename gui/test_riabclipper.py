"""
Disaster risk assessment tool developed by AusAid - **RiabClipper test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '20/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


import os
import numpy
import unittest

from qgis.core import (QgsApplication,
                       QgsRectangle,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsMapLayerRegistry)

from storage.core import read_layer
from riabclipper import clipLayer, extentToKml
from impactcalculator import getOptimalExtent
from utilities_test import getQgisTestApp
from storage.utilities_test import TESTDATA
from storage.utilities import nanallclose

# Setup pathnames for test data sets FIXME!!
myRoot = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..'))

VECTOR_PATH = os.path.join(myRoot, 'riab_test_data',
                          'Padang_WGS84.shp')
rasterPath = os.path.join(myRoot, 'riab_test_data',
                          'Shakemap_Padang_2009.asc')
rasterPath2 = os.path.join(myRoot, 'riab_test_data',
                           'population_padang_1.asc')

# Handle to common QGis test app
QGISAPP = getQgisTestApp()


class RiabClipper(unittest.TestCase):
    """Test the risk in a box clipper"""

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

        msg = 'Did not find layer "%s" in path "%s"' % (myName,
                                                        VECTOR_PATH)
        assert myVectorLayer is not None, msg
        assert myVectorLayer.isValid()
        # Create a bounding box
        myRect = [100.03, -1.14, 100.81, -0.73]

        # Clip the vector to the bbox
        myResult = clipLayer(myVectorLayer, myRect)

        # Check the output is valid
        assert(os.path.exists(myResult))

    def test_clipRaster(self):
        """Raster layers can be clipped
        """

        # Create a raster layer
        myName = 'shake'
        myRasterLayer = QgsRasterLayer(rasterPath, myName)

        msg = 'Did not find layer "%s" in path "%s"' % (myName,
                                                        rasterPath)
        assert myRasterLayer is not None, msg

        # Create a bounding box
        myRect = [97, -3, 104, 1]

        # Clip the vector to the bbox
        myResult = clipLayer(myRasterLayer, myRect)

        # Check the output is valid
        assert os.path.exists(myResult)

        # Clip and give a desired resolution for the output
        mySize = 0.05
        myResult = clipLayer(myRasterLayer, myRect, mySize)
        myNewRasterLayer = QgsRasterLayer(myResult, myName)
        assert myNewRasterLayer.isValid(), 'Resampled raster is not valid'

        msg = ('Resampled raster has incorrect pixel size.'
               'Expected: %f, Actual: %f' %
               (mySize, myNewRasterLayer.rasterUnitsPerPixel()))
        assert myNewRasterLayer.rasterUnitsPerPixel() == mySize, msg

    def test_clipBoth(self):
        """Raster and Vector layers can be clipped
        """

        # Create a vector layer
        myName = 'padang'
        myVectorLayer = QgsVectorLayer(VECTOR_PATH, myName, 'ogr')
        msg = 'Did not find layer "%s" in path "%s"' % (myName,
                                                        VECTOR_PATH)
        assert myVectorLayer is not None, msg

        # Create a raster layer
        myName = 'shake'
        myRasterLayer = QgsRasterLayer(rasterPath, myName)

        msg = 'Did not find layer "%s" in path "%s"' % (myName,
                                                        rasterPath)
        assert myRasterLayer is not None, msg

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
        assert os.path.exists(myResult)
        read_layer(myResult)

        # Clip the raster to the bbox
        myResult = clipLayer(myRasterLayer, myGeoExtent)

        # Check the output is valid
        assert os.path.exists(myResult)
        read_layer(myResult)

        # -------------------------------
        # Check the extra keywords option
        # -------------------------------
        # Clip the vector to the bbox
        myResult = clipLayer(myVectorLayer, myGeoExtent,
                             extraKeywords={'kermit': 'piggy'})

        # Check the output is valid
        assert os.path.exists(myResult)
        L = read_layer(myResult)
        kwds = L.get_keywords()
        msg = 'Extra keyword was not found in %s: %s' % (myResult, kwds)
        assert kwds['kermit'] == 'piggy'

        # Clip the raster to the bbox
        myResult = clipLayer(myRasterLayer, myGeoExtent,
                             extraKeywords={'zoot': 'animal'})

        # Check the output is valid
        assert os.path.exists(myResult)
        L = read_layer(myResult)
        kwds = L.get_keywords()

        msg = 'Extra keyword was not found in %s: %s' % (myResult, kwds)
        assert kwds['zoot'] == 'animal', msg


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

        for test_filename in ['Population_Jakarta_geographic.asc',
                              'Population_2010.asc']:

            myRasterPath = ('%s/%s' % (TESTDATA, test_filename))

            # Get reference values
            R = read_layer(myRasterPath)
            R_min_ref, R_max_ref = R.get_extrema()
            native_resolution = R.get_resolution()

            # Get the Hazard extents as an array in EPSG:4326
            bounding_box = R.get_bounding_box()

            # Test for a range of resolutions
            for res in [0.02, 0.01, 0.005, 0.002, 0.001, 0.0005,  # Coarser
                        0.0002]:                                  # Finer

                # To save time only do two resolutions for the
                # large population set
                if test_filename.startswith('Population_2010'):
                    if res > 0.01 or res < 0.005:
                        break

                # Clip the raster to the bbox
                myRasterLayer = QgsRasterLayer(myRasterPath, 'xxx')
                myResult = clipLayer(myRasterLayer, bounding_box, res,
                                     extraKeywords={'resolution': native_resolution})

                R = read_layer(myResult)
                A_native = R.get_data(scaling=False)
                A_scaled = R.get_data(scaling=True)

                sigma = (R.get_resolution()[0] / native_resolution[0]) ** 2

                # Compare extrema
                expected_scaled_max = sigma * numpy.nanmax(A_native)
                msg = ('Resampled raster was not rescaled correctly: '
                       'max(A_scaled) was %f but expected %f'
                       % (numpy.nanmax(A_scaled), expected_scaled_max))

                # FIXME (Ole): The rtol used to be 1.0e-8 -
                #              now it has to be 1.0e-6, otherwise we get
                #              max(A_scaled) was 12083021.000000 but
                #              expected 12083020.414316
                #              Is something being rounded to the nearest integer?
                assert numpy.allclose(expected_scaled_max,
                                      numpy.nanmax(A_scaled),
                                      rtol=1.0e-6, atol=1.0e-8), msg

                expected_scaled_min = sigma * numpy.nanmin(A_native)
                msg = ('Resampled raster was not rescaled correctly: '
                       'min(A_scaled) was %f but expected %f'
                       % (numpy.nanmin(A_scaled), expected_scaled_min))
                assert numpy.allclose(expected_scaled_min,
                                      numpy.nanmin(A_scaled),
                                      rtol=1.0e-8, atol=1.0e-12), msg

                # Compare elementwise
                msg = 'Resampled raster was not rescaled correctly'
                assert nanallclose(A_native * sigma, A_scaled,
                                   rtol=1.0e-8, atol=1.0e-8), msg

                # Check that it also works with manual scaling
                A_manual = R.get_data(scaling=sigma)
                msg = 'Resampled raster was not rescaled correctly'
                assert nanallclose(A_manual, A_scaled,
                                   rtol=1.0e-8, atol=1.0e-8), msg

                # Check that an exception is raised for bad arguments
                try:
                    R.get_data(scaling='bad')
                except:
                    pass
                else:
                    msg = 'String argument should have raised exception'
                    raise Exception(msg)

                try:
                    R.get_data(scaling='(1, 3)')
                except:
                    pass
                else:
                    msg = 'Tuple argument should have raised exception'
                    raise Exception(msg)

                # Check None option without existence of density keyword
                A_none = R.get_data(scaling=None)
                msg = 'Data should not have changed'
                assert nanallclose(A_native, A_none,
                                   rtol=1.0e-12, atol=1.0e-12), msg

                # Try with None and density keyword
                R.keywords['density'] = 'true'
                A_none = R.get_data(scaling=None)
                msg = 'Resampled raster was not rescaled correctly'
                assert nanallclose(A_scaled, A_none,
                                   rtol=1.0e-12, atol=1.0e-12), msg

                R.keywords['density'] = 'Yes'
                A_none = R.get_data(scaling=None)
                msg = 'Resampled raster was not rescaled correctly'
                assert nanallclose(A_scaled, A_none,
                                   rtol=1.0e-12, atol=1.0e-12), msg

                R.keywords['density'] = 'False'
                A_none = R.get_data(scaling=None)
                msg = 'Data should not have changed'
                assert nanallclose(A_native, A_none,
                                   rtol=1.0e-12, atol=1.0e-12), msg

                R.keywords['density'] = 'no'
                A_none = R.get_data(scaling=None)
                msg = 'Data should not have changed'
                assert nanallclose(A_native, A_none,
                                   rtol=1.0e-12, atol=1.0e-12), msg


    def test_extentToKml(self):
        """Test if extent too KML is working."""
        myExtent = [100.03, -1.14, 100.81, -0.73]
        kmlFilename = extentToKml(myExtent)
        assert os.path.exists(kmlFilename)
        f = open(kmlFilename)
        kml = f.read()
        f.close()

        msg = 'Generated KML was not as expected: %s' % kml
        assert '<?xml version' in kml, msg
        for x in myExtent:
            assert str(x) in kml, msg


if __name__ == '__main__':
    suite = unittest.makeSuite(RiabClipper, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
