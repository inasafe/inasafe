# coding=utf-8

"""Test Styling."""
from builtins import range

import unittest
import os

from safe.utilities.styling import mmi_colour
from safe.test.utilities import get_qgis_app

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class StylingTest(unittest.TestCase):

    """Tests for qgis styling related functions."""

    def setUp(self):
        os.environ['LANG'] = 'en'

    def tearDown(self):
        pass

    def test_mmi_colour(self):
        """Test that we can get a colour given an mmi number."""
        values = list(range(0, 12))
        myExpectedResult = ['#FFFFFF', '#FFFFFF', '#209fff', '#00cfff',
                            '#55ffff', '#aaffff', '#fff000', '#ffa800',
                            '#ff7000', '#ff0000', '#D00', '#800']
        myResult = []
        for value in values:
            myResult.append(mmi_colour(value))
        self.assertListEqual(myResult, myExpectedResult)


if __name__ == '__main__':
    suite = unittest.makeSuite(StylingTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
