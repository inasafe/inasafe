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

import sys
import os
from qgis.core import (
    QgsApplication,
    QgsRectangle,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsMapLayerRegistry
    )
import unittest
from riabclipper import clipLayer, getBestResolution, reprojectLayer
from impactcalculator import getOptimalExtent


myRoot = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..'))

vectorPath = os.path.join(myRoot, 'riab_test_data',
                          'Padang_WGS84.shp')
rasterPath = os.path.join(myRoot, 'riab_test_data',
                          'Shakemap_Padang_2009.asc')
rasterPath2 = os.path.join(myRoot, 'riab_test_data',
                           'population_padang_1.asc')

# Start one QGis application to test agaist
myGuiFlag = False  # We don't need to enable qgis app in gui mode
qgis_app = QgsApplication(sys.argv, myGuiFlag)
if os.environ.has_key('QGISPATH'):
    myPath = os.environ['QGISPATH']
    myUseDefaultPathFlag = True
    qgis_app.setPrefixPath(myPath, myUseDefaultPathFlag)

qgis_app.initQgis()
print 'QGIS settings', qgis_app.showSettings()


class RiabTest(unittest.TestCase):
    """Test the risk in a box clipper"""
    app = None

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_clipVector(self):
        """Vector layers can be clipped
        """

        # Create a vector
        myName = 'padang'
        myVectorLayer = QgsVectorLayer(vectorPath, myName, 'ogr')

        msg = 'Did not find layer "%s" in path "%s"' % (myName,
                                                        vectorPath)
        assert myVectorLayer is not None, msg

        # Create a bounding box
        myRect = QgsRectangle(100.03, -1.14, 100.81, -0.73)

        # Clip the vector to the bbox
        myResult = clipLayer(myVectorLayer, myRect)

        # Check the output is valid
        assert(os.path.exists(myResult))

    def test_clipRaster(self):
        """Raster layers can be clipped
        """

        # Create a raster
        myName = 'shake'
        myRasterLayer = QgsRasterLayer(rasterPath, myName)

        msg = 'Did not find layer "%s" in path "%s"' % (myName,
                                                        rasterPath)
        assert myRasterLayer is not None, msg

        # Create a bounding box
        myRect = QgsRectangle(97, -3, 104, 1)

        # Clip the vector to the bbox
        myResult = clipLayer(myRasterLayer, myRect)

        # Check the output is valid
        assert(os.path.exists(myResult))

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
        myRect = QgsRectangle(99.53, -1.22, 101.20, -0.36)

        myExtent = [myRect.xMinimum(),
                    myRect.yMinimum(),
                    myRect.xMaximum(),
                    myRect.yMaximum()]
        myExtent = getOptimalExtent(rasterPath,
                                    vectorPath,
                                    myExtent)
        myRect = QgsRectangle(myExtent[0],
                              myExtent[1],
                              myExtent[2],
                              myExtent[3])
        # Clip the vector to the bbox
        myResult = clipLayer(myVectorLayer, myRect)

        # Check the output is valid
        assert(os.path.exists(myResult))

        # Clip the raster to the bbox
        myResult = clipLayer(myRasterLayer, myRect)

        # Check the output is valid
        assert(os.path.exists(myResult))

    def test_getBestResolution(self):
        """Test if getBestResolution is working."""

        myName = 'shake'  # Pixel size 0.00833333
        myRasterLayer = QgsRasterLayer(rasterPath, myName)
        myName = 'population'  # 0.0307411 (courser than shake)
        myRasterLayer2 = QgsRasterLayer(rasterPath2, myName)
        assert(getBestResolution(myRasterLayer, myRasterLayer2)
               == myRasterLayer)

if __name__ == '__main__':
    unittest.main()
