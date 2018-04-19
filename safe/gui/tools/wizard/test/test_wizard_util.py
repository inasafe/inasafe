# coding=utf-8
"""Test for Wizard Util."""

import unittest

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from safe.gui.tools.wizard.utilities import (
    get_question_text, get_image_path, not_set_image_path)
from safe.definitions.hazard import hazard_all
from safe.definitions.exposure import exposure_all

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestWizardUtil(unittest.TestCase):
    """Test Wizard Utils."""

    def test_get_missing_question_text(self):
        """Test how the wizard copes with importing missing texts."""
        constant = '_dummy_missing_constant'
        expected_text = '<b>MISSING CONSTANT: %s</b>' % constant
        text = get_question_text(constant)
        self.assertEqual(text, expected_text)

    def test_get_icon(self):
        """Test get icon."""
        list_definitions = [hazard_all, exposure_all]
        for definitions in list_definitions:
            for definition in definitions:
                path= get_image_path(definition)
                message = 'The icon for %s is not set.' % definition['key']
                self.assertNotEqual(path, not_set_image_path, message)


if __name__ == '__main__':
    unittest.main()
