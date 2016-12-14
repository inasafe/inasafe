# coding=utf-8
"""Test for Wizard Util."""

import unittest
from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.PyQt.QtCore import QSettings
from safe.definitionsv4.constants import zero_default_value
from safe.gui.tools.wizard.wizard_utils import (
    get_question_text,
    get_inasafe_default_value_qsetting,
    set_inasafe_default_value_qsetting
)

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

    def test_inasafe_default_value_qsetting(self):
        """Test for set and get inasafe_default_value_qsetting."""
        qsetting = QSettings('InaSAFETest')
        # Make sure it's empty
        qsetting.clear()

        female_ratio_key = 'female_ratio'
        real_value = get_inasafe_default_value_qsetting(
            qsetting, female_ratio_key)
        self.assertEqual(zero_default_value, real_value)

        female_ratio_value = 0.8
        set_inasafe_default_value_qsetting(
            qsetting, female_ratio_key, female_ratio_value)
        real_value = get_inasafe_default_value_qsetting(
            qsetting, female_ratio_key)
        self.assertEqual(female_ratio_value, real_value)

        # Make sure it's empty
        qsetting.clear()


if __name__ == '__main__':
    unittest.main()
