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

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

import unittest
from safe_qgis.utilities.analysis import Analysis
from safe_qgis.utilities.utilities_for_testing import FakeLayer


class TestAnalysis(unittest.TestCase):
    """Test for Analysis class."""
    def setUp(self):
        self.analysis = Analysis()

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
