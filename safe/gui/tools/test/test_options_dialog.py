# coding=utf-8
"""Test InaSAFE Options Dialog"""

import unittest
import logging

from safe.definitionsv4.default_settings import inasafe_default_settings
from safe.gui.tools.options_dialog import OptionsDialog
from safe.test.utilities import get_qgis_app
from safe.common.utilities import temp_dir
from safe.defaults import (
    default_north_arrow_path,
    supporters_logo_path,
    disclaimer)

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
        self.assertEqual(
            dialog.cbxVisibleLayersOnly.isChecked(),
            inasafe_default_settings['visibleLayersOnlyFlag'])
        self.assertEqual(
            dialog.cbxSetLayerNameFromTitle.isChecked(),
            inasafe_default_settings['set_layer_from_title_flag'])
        self.assertEqual(
            dialog.cbxZoomToImpact.isChecked(),
            inasafe_default_settings['setZoomToImpactFlag'])
        self.assertEqual(
            dialog.cbxHideExposure.isChecked(),
            inasafe_default_settings['setHideExposureFlag'])
        self.assertEqual(
            dialog.cbxUseSelectedFeaturesOnly.isChecked(),
            inasafe_default_settings['useSelectedFeaturesOnly'])
        self.assertEqual(
            dialog.leKeywordCachePath.text(),
            inasafe_default_settings['keywordCachePath'])
        self.assertEqual(
            dialog.template_warning_checkbox.isChecked(),
            inasafe_default_settings['template_warning_verbose'])
        self.assertEqual(
            dialog.organisation_on_dock_checkbox.isChecked(),
            inasafe_default_settings['showOrganisationLogoInDockFlag'])
        self.assertEqual(
            dialog.cbxDevMode.isChecked(),
            inasafe_default_settings['developer_mode'])

        self.assertEqual(
            dialog.leNorthArrowPath.text(), default_north_arrow_path())
        self.assertEqual(
            dialog.leOrganisationLogoPath.text(), supporters_logo_path())
        self.assertEqual(dialog.leReportTemplatePath.text(), '')
        self.assertEqual(dialog.txtDisclaimer.toPlainText(), disclaimer())
        self.assertEqual(
            dialog.leUserDirectoryPath.text(), temp_dir('impacts'))

        self.assertEqual(
            dialog.iso19115_organization_le.text(),
            inasafe_default_settings['ISO19115_ORGANIZATION'])
        self.assertEqual(
            dialog.iso19115_url_le.text(),
            inasafe_default_settings['ISO19115_URL'])
        self.assertEqual(
            dialog.iso19115_email_le.text(),
            inasafe_default_settings['ISO19115_EMAIL'])
        self.assertEqual(
            dialog.iso19115_title_le.text(),
            inasafe_default_settings['ISO19115_TITLE'])
        self.assertEqual(
            dialog.iso19115_license_le.text(),
            inasafe_default_settings['ISO19115_LICENSE'])


if __name__ == '__main__':
    suite = unittest.makeSuite(TestOptionsDialog, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
