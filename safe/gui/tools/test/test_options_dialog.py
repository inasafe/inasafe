# coding=utf-8
"""Test InaSAFE Options Dialog"""

import unittest
import logging

from safe.gui.tools.options_dialog import OptionsDialog
from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')


class TestOptionsDialog(unittest.TestCase):
    """Test Options Dialog"""

    def test_setup_dialog(self):
        """Test Setup Options Dialog."""
        dialog = OptionsDialog(PARENT, IFACE, qsetting='InaSAFETest')
        self.assertIsNotNone(dialog)


if __name__ == '__main__':
    suite = unittest.makeSuite(TestOptionsDialog, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
