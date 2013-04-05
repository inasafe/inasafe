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

import os
import unittest
from qgis.core import (
    QgsProviderRegistry,
    QgsCoordinateReferenceSystem,
    QgsRasterLayer)
from safe_qgis.utilities_test import getQgisTestApp
from safe_interface import EXPDATA

QGISAPP = getQgisTestApp()


class QGISTest(unittest.TestCase):
    """Test the QGIS Environment"""

    def test_QGISEnvironment(self):
        """QGIS environment has the expected providers"""

        r = QgsProviderRegistry.instance()
        #for item in r.providerList():
        #    print str(item)

        #print 'Provider count: %s' % len(r.providerList())
        assert 'gdal' in r.providerList()
        assert 'ogr' in r.providerList()
        assert 'postgres' in r.providerList()
        #assert 'wfs' in r.providerList()

    def testProjInterpretation(self):
        """Test that QGIS properly parses a proj4 string.
        see https://github.com/AIFDR/inasafe/issues/349
        """
        myCrs = QgsCoordinateReferenceSystem()
        myProj4 = ('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",'
                   'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
                   'PRIMEM["Greenwich",0.0],UNIT["Degree",'
                   '0.0174532925199433]]')
        myCrs.createFromWkt(myProj4)
        myAuthId = myCrs.authid()
        myExpectedAuthId = 'EPSG:4326'
        self.assertEqual(myAuthId, myExpectedAuthId)

        # now test for a loaded layer
        myPath = os.path.join(EXPDATA, 'glp10ag.asc')
        myTitle = 'people'
        myLayer = QgsRasterLayer(myPath, myTitle)
        myAuthId = myLayer.crs().authid()
        self.assertEqual(myAuthId, myExpectedAuthId)

if __name__ == '__main__':
    unittest.main()
