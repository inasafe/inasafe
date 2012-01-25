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
import unittest
from qgis.core import QgsApplication, QgsProviderRegistry
from utilities_test import get_qgis_test_app

qgis_app = get_qgis_test_app()


class RiabTest(unittest.TestCase):
    """Test the QGIS Environment"""

    def test_QGISEnvironment(self):
        """QGIS environment has the expected providers"""

        r = QgsProviderRegistry.instance()
        #for item in r.providerList():
        #    print str(item)

        #print 'Provider count: %s' % len(r.providerList())
        assert 'gdal' in r.providerList()
        assert 'ogr' in r.providerList()

        # FIXME (Ole): When we start using PostGIS and WFS we
        #              can add more tests

if __name__ == '__main__':
    unittest.main()
