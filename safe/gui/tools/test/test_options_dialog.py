# coding=utf-8
"""Test InaSAFE Options Dialog"""

import unittest
import logging

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import

from safe.gui.tools.options_dialog import OptionsDialog
from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')


class TestOptionsDialog(unittest.TestCase):
    """Test Options Dialog"""

    def test_setup_dialog(self):
        """Test Setup Options Dialog."""
        dialog = OptionsDialog(PARENT, IFACE)
        pass


if __name__ == '__main__':
    suite = unittest.makeSuite(TestOptionsDialog, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
