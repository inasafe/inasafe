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
import unittest

from qgis.core import (QgsApplication,
                       QgsRectangle,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsMapLayerRegistry)

from riabclipper import clipLayer, extentToKml
from impactcalculator import getOptimalExtent
from utilities_test import get_qgis_test_app

# Setup pathnames for test data sets
myRoot = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..'))

vectorPath = os.path.join(myRoot, 'riab_test_data',
                          'Padang_WGS84.shp')
rasterPath = os.path.join(myRoot, 'riab_test_data',
                          'Shakemap_Padang_2009.asc')
rasterPath2 = os.path.join(myRoot, 'riab_test_data',
                           'population_padang_1.asc')

# Handle to common QGis test app
QGISAPP = get_qgis_test_app()


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
        myVectorLayer = QgsVectorLayer(vectorPath, myName, 'ogr')

        msg = 'Did not find layer "%s" in path "%s"' % (myName,
                                                        vectorPath)
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
        myVectorLayer = QgsVectorLayer(vectorPath, myName, 'ogr')
        msg = 'Did not find layer "%s" in path "%s"' % (myName,
                                                        vectorPath)
        assert myVectorLayer is not None, msg

        # Create a raster layer
        myName = 'shake'
        myRasterLayer = QgsRasterLayer(rasterPath, myName)

        msg = 'Did not find layer "%s" in path "%s"' % (myName,
                                                        rasterPath)
        assert myRasterLayer is not None, msg

        # Create a bounding box
        myViewportGeoExtent = [99.53, -1.22, 101.20, -0.36]

        # get the Hazard extents as an array in EPSG:4326
        myHazardGeoExtent = [
                       myRasterLayer.extent().xMinimum(),
                       myRasterLayer.extent().yMinimum(),
                       myRasterLayer.extent().xMaximum(),
                       myRasterLayer.extent().yMaximum()]
        # get the Exposure extents as an array in EPSG:4326
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
        assert(os.path.exists(myResult))

        # Clip the raster to the bbox
        myResult = clipLayer(myRasterLayer, myGeoExtent)

        # Check the output is valid
        assert(os.path.exists(myResult))

    def test_extentToKml(self):
        """Test if extent too KML is working."""
        myExtent = [100.03, -1.14, 100.81, -0.73]
        assert extentToKml(myExtent)

if __name__ == '__main__':
    suite = unittest.makeSuite(RiabClipper, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
