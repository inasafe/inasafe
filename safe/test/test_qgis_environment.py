# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**ISClipper test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@kartoza.com'
__date__ = '20/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from qgis.core import (
    QgsProviderRegistry,
    QgsCoordinateReferenceSystem,
    QgsRasterLayer)

from safe.test.utilities import get_qgis_app, standard_data_path

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting='InaSAFETest')


class QGISTest(unittest.TestCase):
    """Test the QGIS Environment."""

    def test_qgis_environment(self):
        """QGIS environment has the expected providers."""
        # noinspection PyUnresolvedReferences
        r = QgsProviderRegistry.instance()

        # print 'Provider count: %s' % len(r.providerList())
        assert 'gdal' in r.providerList()
        assert 'ogr' in r.providerList()
        assert 'postgres' in r.providerList()
        assert 'delimitedtext' in r.providerList()
        # assert 'wfs' in r.providerList()

    def test_proj_interpretation(self):
        """Test that QGIS properly parses a proj4 string.
        see https://github.com/AIFDR/inasafe/issues/349
        """
        # noinspection PyCallingNonCallable
        crs = QgsCoordinateReferenceSystem()
        proj4 = (
            'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",'
            'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
            'PRIMEM["Greenwich",0.0],UNIT["Degree",'
            '0.0174532925199433]]')
        crs.createFromWkt(proj4)
        auth_id = crs.authid()
        expected_auth_id = 'EPSG:4326'
        self.assertEqual(auth_id, expected_auth_id)

        # now test for a loaded layer
        path = standard_data_path('hazard', 'jakarta_flood_design.tif')
        title = 'Jakarta Flood'
        # noinspection PyCallingNonCallable
        layer = QgsRasterLayer(path, title)
        auth_id = layer.crs().authid()
        self.assertEqual(auth_id, expected_auth_id)

if __name__ == '__main__':
    unittest.main()
