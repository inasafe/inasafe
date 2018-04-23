# coding=utf-8
"""Tests for the Impact Function Centric Wizard."""
from builtins import range

import unittest
import sys
import os
import shutil

# Import qgis in order to set SIP API.
# pylint: disable=unused-import
import qgis
# pylint: enable=unused-import
from qgis.core import QgsMapLayerRegistry
from qgis.gui import QgsMapCanvasLayer
from qgis.PyQt import QtCore

# noinspection PyPackageRequirements
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)

from safe.common.utilities import temp_dir
from safe.test.utilities import (
    load_test_vector_layer,
    clone_raster_layer,
    clone_shp_layer,
    get_qgis_app,
    get_dock,
    standard_data_path)

from safe.definitions.hazard import hazard_all, hazard_volcano
from safe.definitions.exposure import exposure_all, exposure_structure
from safe.definitions import (
    layer_purpose_hazard,
    layer_purpose_exposure,
    layer_geometry_polygon
)
from safe.definitions.utilities import get_allowed_geometries

# AG: get_qgis_app() should be called before importing modules from
# safe.gui.tools.wizard
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gui.tools.wizard.wizard_dialog import WizardDialog

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


# noinspection PyTypeChecker
class TestImpactFunctionCentricWizard(unittest.TestCase):
    """Test the Impact Function Centric Wizard."""

    @classmethod
    def setUpClass(cls):
        cls.dock = get_dock()
        # cls.dock = None

    def setUp(self):
        pass

    def tearDown(self):
        """Run after each test."""
        # Remove the mess that we made on each test
        shutil.rmtree(temp_dir(sub_dir='test'))

    def check_current_step(self, expected_step):
        """Helper function to check the current step is expected_step

        :param expected_step: The expected current step.
        :type expected_step: WizardStep instance
        """
        current_step = expected_step.parent.get_current_step()
        message = 'Should be step %s but it got %s' % (
            expected_step.__class__.__name__, current_step.__class__.__name__)
        self.assertEqual(expected_step, current_step, message)

    # noinspection PyUnresolvedReferences
    @staticmethod
    def select_from_list_widget(option, list_widget):
        """Helper function to select option from list_widget

        :param option: Option to be chosen
        :type option: str

        :param list_widget: List widget that wants to be checked.
        :type list_widget: QListWidget
        """
        available_options = []
        for i in range(list_widget.count()):
            if list_widget.item(i).text() == option:
                list_widget.setCurrentRow(i)
                return
            else:
                available_options.append(list_widget.item(i).text())
        message = (
            'There is no %s in the list widget. The available options are %s'
            % (option, available_options))

        raise Exception(message)

    def test_analysis_wizard(self):
        """Test Analysis Wizard."""
        dialog = WizardDialog(iface=IFACE)
        dialog.dock = self.dock
        dialog.set_function_centric_mode()
        QgsProject.instance().removeAllMapLayers()
        number_of_column = len(hazard_all)

        volcano_layer = load_test_vector_layer(
            'hazard',
            'volcano_krb.shp',
            clone=True)

        structure_layer = load_test_vector_layer(
            'exposure',
            'buildings.shp',
            clone=True)

        test_layers = [volcano_layer, structure_layer]

        QgsProject.instance().addMapLayers(test_layers)
        # Need to set the layers manually to map canvas. See:
        # https://gist.github.com/ismailsunni/dd2c30a38cef0147bd0dc8d6ba1aeac6
        qgs_map_canvas_layers = [QgsMapCanvasLayer(x) for x in test_layers]
        CANVAS.setLayerSet(qgs_map_canvas_layers)

        count = len(dialog.iface.mapCanvas().layers())
        self.assertEqual(count, len(test_layers))

        # step_fc_functions1: test function matrix dimensions
        col_count = dialog.step_fc_functions1.tblFunctions1.columnCount()
        self.assertEqual(col_count, number_of_column)
        row_count = dialog.step_fc_functions1.tblFunctions1.rowCount()
        self.assertEqual(row_count, len(exposure_all))

        # Select Volcano vs Structure
        volcano_index = hazard_all.index(hazard_volcano)
        structure_index = exposure_all.index(exposure_structure)

        dialog.step_fc_functions1.tblFunctions1.setCurrentCell(
            structure_index, volcano_index)

        selected_hazard = dialog.step_fc_functions1.selected_value(
            layer_purpose_hazard['key'])
        selected_exposure = dialog.step_fc_functions1.selected_value(
            layer_purpose_exposure['key'])
        self.assertEqual(selected_hazard, hazard_volcano)
        self.assertEqual(selected_exposure, exposure_structure)

        # step_fc_functions1: press next
        dialog.pbnNext.click()

        # step_fc_functions2
        # Check in the correct step
        self.check_current_step(dialog.step_fc_functions2)
        hazard_polygon_index = get_allowed_geometries(
            layer_purpose_hazard['key']).index(layer_geometry_polygon)
        exposure_polygon_index = get_allowed_geometries(
            layer_purpose_exposure['key']).index(layer_geometry_polygon)
        dialog.step_fc_functions2.tblFunctions2.setCurrentCell(
            exposure_polygon_index, hazard_polygon_index)

        selected_hazard_geometry = dialog.step_fc_functions2.selected_value(
            layer_purpose_hazard['key'])
        selected_exposure_geometry = dialog.step_fc_functions2.selected_value(
            layer_purpose_exposure['key'])
        self.assertEqual(selected_hazard_geometry, layer_geometry_polygon)
        self.assertEqual(selected_exposure_geometry, layer_geometry_polygon)

        # step_fc_functions2: press next
        dialog.pbnNext.click()

        # Check in the correct step
        self.check_current_step(dialog.step_fc_hazlayer_origin)

        # step hazard origin: press next
        dialog.pbnNext.click()

        # Check in the correct step
        self.check_current_step(dialog.step_fc_hazlayer_from_canvas)

        # Check the number of layer in the list
        self.assertEqual(
            dialog.step_fc_hazlayer_from_canvas.lstCanvasHazLayers.count(), 1)

        # step hazard from canvas: press next
        dialog.pbnNext.click()

        # Check in the correct step
        self.check_current_step(dialog.step_fc_explayer_origin)

        # step exposure origin: press next
        dialog.pbnNext.click()

        # Check in the correct step
        self.check_current_step(dialog.step_fc_explayer_from_canvas)

        # Check the number of layer in the list
        self.assertEqual(
            dialog.step_fc_explayer_from_canvas.lstCanvasExpLayers.count(), 1)

        # step exposure from canvas: press next
        dialog.pbnNext.click()

        # Check in the correct step
        self.check_current_step(dialog.step_fc_agglayer_origin)

        # Check no aggregation
        dialog.step_fc_agglayer_origin.rbAggLayerNoAggregation.setChecked(True)

        # step aggregation origin: press next
        dialog.pbnNext.click()

        # Check in the correct step
        self.check_current_step(dialog.step_fc_summary)

        # step extent: press next
        dialog.pbnNext.click()

        # Check in the correct step
        self.check_current_step(dialog.step_fc_analysis)

if __name__ == '__main__':
    suite = unittest.makeSuite(TestImpactFunctionCentricWizard)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
