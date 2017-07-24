# coding=utf-8
"""Test for Wizard Util."""

import unittest
from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gui.tools.wizard.utilities import get_question_text

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestWizardUtil(unittest.TestCase):
    """Test Wizard Utils"""
    def test_get_missing_question_text(self):
        """Test how the wizard copes with importing missing texts."""
        constant = '_dummy_missing_constant'
        expected_text = '<b>MISSING CONSTANT: %s</b>' % constant
        text = get_question_text(constant)
        self.assertEqual(text, expected_text)


if __name__ == '__main__':
    unittest.main()
