# coding=utf-8
"""Test for Analysis Class.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'ismailsunni'
__revision__ = '$Format:%H$'
__date__ = '10/27/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import os
import unittest
import numpy

from safe.common.testing import (
    get_qgis_app,
    TESTDATA,
    HAZDATA)
from safe.storage.core import read_layer
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.utilities.analysis import Analysis
from safe.utilities.utilities_for_testing import FakeLayer
from safe.common.exceptions import BoundingBoxError
from safe.exceptions import InsufficientOverlapError


class TestAnalysis(unittest.TestCase):
    """Test for Analysis class."""
    def setUp(self):
        self.analysis = Analysis()

    def test_get_optimal_extent(self):
        """Optimal extent is calculated correctly
        """

        exposure_path = os.path.join(TESTDATA, 'Population_2010.asc')
        hazard_path = os.path.join(HAZDATA,
                                   'Lembang_Earthquake_Scenario.asc')

        # Expected data
        haz_metadata = {'bounding_box': (105.3000035,
                                         -8.3749994999999995,
                                         110.2914705,
                                         -5.5667784999999999),
                        'resolution': (0.0083330000000000001,
                                       0.0083330000000000001)}

        exp_metadata = {'bounding_box': (94.972335000000001,
                                         -11.009721000000001,
                                         141.0140016666665,
                                         6.0736123333332639),
                        'resolution': (0.0083333333333333003,
                                       0.0083333333333333003)}

        # Verify relevant metada is ok
        H = read_layer(hazard_path)
        E = read_layer(exposure_path)

        hazard_bbox = H.get_bounding_box()
        assert numpy.allclose(hazard_bbox, haz_metadata['bounding_box'],
                              rtol=1.0e-12, atol=1.0e-12)

        exposure_bbox = E.get_bounding_box()
        assert numpy.allclose(exposure_bbox, exp_metadata['bounding_box'],
                              rtol=1.0e-12, atol=1.0e-12)

        hazard_res = H.get_resolution()
        assert numpy.allclose(hazard_res, haz_metadata['resolution'],
                              rtol=1.0e-12, atol=1.0e-12)

        exposure_res = E.get_resolution()
        assert numpy.allclose(exposure_res, exp_metadata['resolution'],
                              rtol=1.0e-12, atol=1.0e-12)

        # First, do some examples that produce valid results
        ref_box = [105.3000035, -8.3749995, 110.2914705, -5.5667785]
        view_port = [94.972335, -11.009721, 141.014002, 6.073612]

        bbox = self.analysis.get_optimal_extent(
            hazard_bbox, exposure_bbox, view_port)
        assert numpy.allclose(bbox, ref_box, rtol=1.0e-12, atol=1.0e-12)

        # testing with viewport clipping disabled
        bbox = self.analysis.get_optimal_extent(
            hazard_bbox, exposure_bbox, None)
        assert numpy.allclose(bbox, ref_box, rtol=1.0e-12, atol=1.0e-12)

        view_port = [105.3000035,
                     -8.3749994999999995,
                     110.2914705,
                     -5.5667784999999999]
        bbox = self.analysis.get_optimal_extent(
            hazard_bbox, exposure_bbox, view_port)
        assert numpy.allclose(bbox, ref_box,
                              rtol=1.0e-12, atol=1.0e-12)

        # Very small viewport fully inside other layers
        view_port = [106.0, -6.0, 108.0, -5.8]
        bbox = self.analysis.get_optimal_extent(
            hazard_bbox, exposure_bbox, view_port)

        assert numpy.allclose(bbox, view_port,
                              rtol=1.0e-12, atol=1.0e-12)

        # viewport that intersects hazard layer
        view_port = [107.0, -6.0, 112.0, -3.0]
        ref_box = [107, -6, 110.2914705, -5.5667785]

        bbox = self.analysis.get_optimal_extent(
            hazard_bbox, exposure_bbox, view_port)
        assert numpy.allclose(bbox, ref_box,
                              rtol=1.0e-12, atol=1.0e-12)

        # Then one where boxes don't overlap
        view_port = [105.3, -4.3, 110.29, -2.5]
        try:
            self.analysis.get_optimal_extent(
                hazard_bbox, exposure_bbox, view_port)
        except InsufficientOverlapError, e:
            message = 'Did not find expected error message in %s' % str(e)
            assert 'did not overlap' in str(e), message
        else:
            message = ('Non ovelapping bounding boxes should have raised '
                       'an exception')
            raise Exception(message)

        # Try with wrong input data
        try:
            self.analysis.get_optimal_extent(
                haz_metadata, exp_metadata, view_port)
        except BoundingBoxError:
            # good this was expected
            pass
        except InsufficientOverlapError, e:
            message = 'Did not find expected error message in %s' % str(e)
            assert 'Invalid' in str(e), message
        else:
            message = 'Wrong input data should have raised an exception'
            raise Exception(message)

        try:
            self.analysis.get_optimal_extent(None, None, view_port)
        except BoundingBoxError, e:
            message = 'Did not find expected error message in %s' % str(e)
            assert 'cannot be None' in str(e), message
        else:
            message = 'Wrong input data should have raised an exception'
            raise Exception(message)

        try:
            self.analysis.get_optimal_extent('aoeush', 'oeuuoe', view_port)
        except BoundingBoxError, e:
            message = 'Did not find expected error message in %s' % str(e)
            assert 'Instead i got "aoeush"' in str(e), message
        else:
            message = 'Wrong input data should have raised an exception'
            raise Exception(message)

    def test_generate_insufficient_overlap_message(self):
        """Test we generate insufficent overlap messages nicely."""

        exposure_layer = FakeLayer('Fake exposure layer')

        hazard_layer = FakeLayer('Fake hazard layer')

        message = self.analysis.generate_insufficient_overlap_message(
            Exception('Dummy exception'),
            exposure_geoextent=[10.0, 10.0, 20.0, 20.0],
            exposure_layer=exposure_layer,
            hazard_geoextent=[15.0, 15.0, 20.0, 20.0],
            hazard_layer=hazard_layer,
            viewport_geoextent=[5.0, 5.0, 12.0, 12.0])
        self.assertIn('insufficient overlap', message.to_text())


if __name__ == '__main__':
    unittest.main()
