# coding=utf-8
"""Tests for interpolation functionality done with QGIS API."""

import unittest

from qgis.core import QgsFeatureRequest, QgsVectorLayer

from safe.test.utilities import get_qgis_app, TESTDATA
from safe.gis.qgis_vector_tools import create_layer
from safe.engine.interpolation_qgis import interpolate_polygon_polygon

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestInterpolationQGIS(unittest.TestCase):
    """Test for interpolation functionality done with QGIS API"""

    def test_interpolation_from_polygons_one_poly(self):
        """Point interpolation using one polygon from Maumere works

        There's a test with the same name in test_engine.py not using QGIS API.
        This one deals correctly with holes in polygons,
        so the resulting numbers are a bit different.
        """

        # Name file names for hazard level and exposure
        hazard_filename = ('%s/tsunami_polygon_WGS84.shp' % TESTDATA)
        exposure_filename = ('%s/building_Maumere.shp' % TESTDATA)

        # Read input data
        H_all = QgsVectorLayer(hazard_filename, 'Hazard', 'ogr')

        # Cut down to make test quick
        # Polygon #799 is the one used in separate test
        H = create_layer(H_all)
        polygon799 = H_all.getFeatures(QgsFeatureRequest(799)).next()
        H.dataProvider().addFeatures([polygon799])

        E = QgsVectorLayer(exposure_filename, 'Exposure', 'ogr')

        # Test interpolation function
        I = interpolate_polygon_polygon(H, E, E.extent())

        N = I.dataProvider().featureCount()
        assert N == I.dataProvider().featureCount()

        # Assert that expected attribute names exist
        I_names = [field.name() for field in I.dataProvider().fields()]
        for field in H.dataProvider().fields():
            name = field.name()
            msg = 'Did not find hazard name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        for field in E.dataProvider().fields():
            name = field.name()
            msg = 'Did not find exposure name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # Verify interpolated values with test result
        count = 0
        for f in I.getFeatures():
            category = f['Category']
            if category is not None:
                count += 1

        msg = ('Expected 453 points tagged with category, '
               'but got only %i' % count)
        assert count == 453, msg

    @unittest.skip('Slow test')
    def test_interpolation_from_polygons_multiple(self):
        """Point interpolation using multiple polygons from Maumere works

        There's a test with the same name in test_engine.py not using QGIS API.
        This one deals correctly with holes in polygons,
        so the resulting numbers are a bit different.
        """

        # Name file names for hazard and exposure
        hazard_filename = ('%s/tsunami_polygon_WGS84.shp' % TESTDATA)
        exposure_filename = ('%s/building_Maumere.shp' % TESTDATA)

        # Read input data
        H = QgsVectorLayer(hazard_filename, 'Hazard', 'ogr')

        E = QgsVectorLayer(exposure_filename, 'Exposure', 'ogr')

        # Test interpolation function
        I = interpolate_polygon_polygon(H, E, E.extent())

        N = I.dataProvider().featureCount()
        assert N == E.dataProvider().featureCount()

        # Assert that expected attribute names exist
        I_names = [field.name() for field in I.dataProvider().fields()]
        for field in H.dataProvider().fields():
            name = field.name()
            msg = 'Did not find hazard name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        for field in E.dataProvider().fields():
            name = field.name()
            msg = 'Did not find exposure name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # Verify interpolated values with test result
        counts = {}
        for f in I.getFeatures():

            # Count items in each specific category
            category = f['Category']
            if category not in counts:
                counts[category] = 0
            counts[category] += 1

        assert H.dataProvider().featureCount() == 1032
        assert I.dataProvider().featureCount() == 3528

        # The full version
        msg = ('Expected 2267 points tagged with category "High", '
               'but got only %i' % counts['High'])
        assert counts['High'] == 2267, msg

        msg = ('Expected 1179 points tagged with category "Very High", '
               'but got only %i' % counts['Very High'])
        assert counts['Very High'] == 1179, msg

        msg = ('Expected 2 points tagged with category "Medium" '
               'but got only %i' % counts['Medium'])
        assert counts['Medium'] == 2, msg

        msg = ('Expected 4 points tagged with category "Low" '
               'but got only %i' % counts['Low'])
        assert counts['Low'] == 4, msg

        msg = ('Expected 76 points tagged with no category '
               'but got only %i' % counts[None])
        assert counts[None] == 76, msg
