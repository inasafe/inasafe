# coding=utf-8
"""Test InaSAFE Options Dialog"""

import unittest
import logging

from safe.gui.tools.options_dialog import OptionsDialog
from safe.test.utilities import get_qgis_app
from safe.common.utilities import temp_dir
from safe.defaults import (
    default_north_arrow_path,
    supporters_logo_path,
    disclaimer

)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestOptionsDialog(unittest.TestCase):
    """Test Options Dialog"""

    def test_setup_dialog(self):
        """Test Setup Options Dialog."""
        dialog = OptionsDialog(PARENT, IFACE, qsetting='InaSAFETest')
        self.assertIsNotNone(dialog)

        # Check default values
        self.assertTrue(dialog.cbxVisibleLayersOnly.isChecked())
        self.assertTrue(dialog.cbxSetLayerNameFromTitle.isChecked())
        self.assertTrue(dialog.cbxZoomToImpact.isChecked())
        self.assertFalse(dialog.cbxHideExposure.isChecked())
        self.assertFalse(dialog.cbxUseSelectedFeaturesOnly.isChecked())
        self.assertEqual(
            dialog.leKeywordCachePath.text(),
            dialog.keyword_io.default_keyword_db_path())
        self.assertTrue(dialog.template_warning_checkbox.isChecked())
        self.assertEqual(
            dialog.leNorthArrowPath.text(), default_north_arrow_path())
        self.assertEqual(
            dialog.leOrganisationLogoPath.text(), supporters_logo_path())
        self.assertFalse(dialog.organisation_on_dock_checkbox.isChecked())
        self.assertEqual(dialog.leReportTemplatePath.text(), '')
        self.assertEqual(dialog.txtDisclaimer.toPlainText(), disclaimer())
        self.assertFalse(dialog.cbxDevMode.isChecked())
        self.assertEqual(
            dialog.leUserDirectoryPath.text(), temp_dir('impacts'))

        self.assertEqual(
            dialog.iso19115_organization_le.text(),
            dialog.defaults['ISO19115_ORGANIZATION'])
        self.assertEqual(
            dialog.iso19115_url_le.text(), dialog.defaults['ISO19115_URL'])
        self.assertEqual(
            dialog.iso19115_email_le.text(), dialog.defaults['ISO19115_EMAIL'])
        self.assertEqual(
            dialog.iso19115_title_le.text(), dialog.defaults['ISO19115_TITLE'])
        self.assertEqual(
            dialog.iso19115_license_le.text(),
            dialog.defaults['ISO19115_LICENSE'])


if __name__ == '__main__':
    suite = unittest.makeSuite(TestOptionsDialog, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
