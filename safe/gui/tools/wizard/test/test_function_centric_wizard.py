# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'borysjurgiel.pl'
__date__ = '24/02/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os
import shutil

# Import qgis in order to set SIP API.
# pylint: disable=unused-import
import qgis
# pylint: enable=unused-import
from qgis.core import QgsMapLayerRegistry
from PyQt4 import QtCore

# noinspection PyPackageRequirements
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)

from safe.common.utilities import temp_dir
from safe.test.utilities import (
    clone_raster_layer,
    clone_shp_layer,
    get_qgis_app,
    get_dock,
    standard_data_path)

# AG: get_qgis_app() should be called before importing modules from
# safe.gui.tools.wizard
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.impact_functions.loader import register_impact_functions
from safe.gui.tools.wizard.wizard_dialog import WizardDialog


# noinspection PyTypeChecker
class WizardDialogTest(unittest.TestCase):
    """Test the InaSAFE wizard GUI"""

    @classmethod
    def setUpClass(cls):
        cls.dock = get_dock()

    def setUp(self):
        # register impact functions
        register_impact_functions()

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
        self.assertEqual(expected_step, current_step)

    # noinspection PyUnresolvedReferences
    def select_from_list_widget(self, option, list_widget):
        """Helper function to select option from list_widget

        :param option: Option to be chosen
        :type option: str

        :param list_widget: List widget that wants to be checked.
        :type list_widget: QListWidget
        """
        for i in range(list_widget.count()):
            if list_widget.item(i).text() == option:
                list_widget.setCurrentRow(i)
                return
        message = 'There is no %s in the list widget' % option
        raise Exception(message)

    @unittest.skip('This test is failing with the docker QGIS environment.')
    def test_input_function_centric_wizard(self):
        """Test the IFCW mode: FloodRasterBuildingFunction"""

        expected_test_layer_count = 2

        expected_hazards_count = 5
        # expected_exposures_count = 3
        expected_exposures_count = 4
        expected_flood_structure_functions_count = 4
        expected_raster_polygon_functions_count = 2
        expected_functions_count = 2
        chosen_if = 'FloodRasterBuildingFunction'

        expected_hazard_layers_count = 1
        expected_exposure_layers_count = 1
        expected_aggregation_layers_count = 0

        # expected_summary_key = 'minimum needs'
        # expected_summary_value_fragment = 'rice'

        # expected_report_size = 4055  # as saved on Ubuntu
        # TS : changed tolerance from 120 to 160 because above change
        # causes fail on fedora
        # AG: updated the tolerance from 160 to 190
        # MD: more tolerance please! 190 -> 200
        # tolerance = 200  # windows EOL etc

        # Initialize dialog
        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.dock = self.dock
        dialog.set_function_centric_mode()
        QgsMapLayerRegistry.instance().removeAllMapLayers()

        # Load test layers
        layer = clone_raster_layer(
            name='continuous_flood_20_20',
            extension='.asc',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        layer = clone_shp_layer(
            name='buildings',
            include_keywords=True,
            source_directory=standard_data_path('exposure'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # Check the environment first
        self.assertIsNotNone(layer.dataProvider())

        count = len(dialog.iface.mapCanvas().layers())
        self.assertEqual(count, expected_test_layer_count)

        # step_fc_functions1: test function matrix dimensions
        col_count = dialog.step_fc_functions1.tblFunctions1.columnCount()
        self.assertEqual(col_count, expected_hazards_count)
        row_count = dialog.step_fc_functions1.tblFunctions1.rowCount()
        self.assertEqual(row_count, expected_exposures_count)

        # step_fc_functions1: test number of functions for flood x structure
        dialog.step_fc_functions1.tblFunctions1.setCurrentCell(3, 1)
        count = len(dialog.step_fc_functions1.selected_functions_1())
        self.assertEqual(count, expected_flood_structure_functions_count)

        # step_fc_functions1: press ok
        dialog.pbnNext.click()

        # step_fc_functions2: test number of functions for raster flood
        # and polygon structure
        self.check_current_step(dialog.step_fc_functions2)
        dialog.step_fc_functions2.tblFunctions2.setCurrentCell(3, 0)

        count = len(dialog.step_fc_functions2.selected_functions_2())
        self.assertEqual(count, expected_raster_polygon_functions_count)

        # step_fc_functions2: press ok
        dialog.pbnNext.click()

        # step_fc_function: test number of available functions
        self.check_current_step(dialog.step_fc_function)
        count = dialog.step_fc_function.lstFunctions.count()
        self.assertEqual(count, expected_functions_count)

        # step_fc_function: test if chosen_if is on the list
        role = QtCore.Qt.UserRole
        flood_ifs = [
            dialog.step_fc_function.lstFunctions.item(row).data(role)['id']
            for row in range(count)]
        self.assertTrue(chosen_if in flood_ifs)

        # step_fc_function: select FloodRasterBuildingImpactFunction and
        # press ok
        chosen_if_row = flood_ifs.index(chosen_if)
        dialog.step_fc_function.lstFunctions.setCurrentRow(chosen_if_row)
        dialog.pbnNext.click()

        # step_fc_hazlayer_from_canvas: test the lstCanvasHazLayers state
        # Note this step is tested prior to step_fc_hazlayer_origin
        # as the list is prepared prior to autoselecting the radiobuttons
        count = dialog.step_fc_hazlayer_from_canvas.lstCanvasHazLayers.count()
        self.assertEqual(count, expected_hazard_layers_count)

        # step_fc_hazlayer_origin: test if the radiobuttons are autmatically
        # enabled and selected
        self.assertTrue(
            dialog.step_fc_hazlayer_origin.rbHazLayerFromCanvas.isEnabled())
        self.assertTrue(
            dialog.step_fc_hazlayer_origin.rbHazLayerFromCanvas.isChecked())

        # step_fc_hazlayer_origin: press ok
        self.check_current_step(dialog.step_fc_hazlayer_origin)
        dialog.pbnNext.click()

        # step_fc_hazlayer_from_canvas: press ok
        self.check_current_step(dialog.step_fc_hazlayer_from_canvas)
        dialog.pbnNext.click()

        # step_fc_explayer_from_canvas: test the lstCanvasExpLayers state
        # Note this step is tested prior to step_fc_explayer_origin
        # as the list is prepared prior to autoselecting the radiobuttons
        count = dialog.step_fc_explayer_from_canvas.lstCanvasExpLayers.count()
        self.assertEqual(count, expected_exposure_layers_count)

        # step_fc_explayer_origin: test if the radiobuttons are automatically
        # enabled and selected
        self.assertTrue(
            dialog.step_fc_explayer_origin.rbExpLayerFromCanvas.isEnabled())
        self.assertTrue(
            dialog.step_fc_explayer_origin.rbExpLayerFromCanvas.isChecked())

        # step_fc_explayer_origin: press ok
        self.check_current_step(dialog.step_fc_explayer_origin)
        dialog.pbnNext.click()

        # step_fc_explayer_from_canvas: press ok
        self.check_current_step(dialog.step_fc_explayer_from_canvas)
        dialog.pbnNext.click()

        # step_fc_explayer_from_canvas: test the lstCanvasAggLayers state
        # Note this step is tested prior to step_fc_agglayer_origin
        # as the list is prepared prior to auto selecting the radio buttons
        count = dialog.step_fc_agglayer_from_canvas.lstCanvasAggLayers.count()
        self.assertEqual(count, expected_aggregation_layers_count)

        # step_fc_agglayer_origin: test if the radio buttons are automatically
        # enabled and selected
        self.assertFalse(
            dialog.step_fc_agglayer_origin.rbAggLayerFromCanvas.isEnabled())
        self.assertTrue(
            dialog.step_fc_agglayer_origin.rbAggLayerFromBrowser.isChecked())

        # step_fc_agglayer_origin: switch to no aggregation and press ok
        self.check_current_step(dialog.step_fc_agglayer_origin)
        dialog.step_fc_agglayer_origin.rbAggLayerNoAggregation.click()
        dialog.pbnNext.click()

        # step_fc_extent: switch to layer's extent and press ok
        self.check_current_step(dialog.step_fc_extent)
        dialog.step_fc_extent.extent_dialog.hazard_exposure_only.click()
        dialog.pbnNext.click()

        # step_fc_params: press ok (already covered by the relevant test)
        self.check_current_step(dialog.step_fc_params)
        dialog.pbnNext.click()

        # step_fc_summary: test minimum needs text
        # summaries = dialog.lblSummary.text().split('<br/>')

        # #TODO: temporarily disable minimum needs test as they seem
        # #te be removed from params
        # minneeds = [s for s in summaries
        #            if expected_summary_key.upper() in s.upper()]
        # self.assertTrue(minneeds)
        # self.assertTrue(expected_summary_value_fragment.upper()
        #                in minneeds[0].upper())

        # step_fc_summary: run analysis
        dialog.pbnNext.click()

        # No longer valid for impact data.
        # step_fc_analysis: test the html output
        # report_path = dialog.wvResults.report_path
        # size = os.stat(report_path).st_size
        # self.assertTrue(
        #     (expected_report_size - tolerance < size < expected_report_size +
        #      tolerance))
        # close the wizard
        dialog.pbnNext.click()

    @unittest.skip('This test is failing with the docker QGIS environment.')
    def test_input_function_centric_wizard_test_2(self):
        """Test the IFCW mode: """

        chosen_if = 'FloodEvacuationRasterHazardFunction'

        # Initialize dialog
        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.dock = self.dock
        dialog.set_function_centric_mode()
        QgsMapLayerRegistry.instance().removeAllMapLayers()

        # Load test layers
        # Hazard layer
        layer = clone_raster_layer(
            name='continuous_flood_20_20',
            extension='.asc',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # Exposure layer
        layer = clone_raster_layer(
            name='people_allow_resampling_true',
            extension='.tif',
            include_keywords=True,
            source_directory=standard_data_path('exposure'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # step_fc_functions1: select functions for flood x population
        self.check_current_step(dialog.step_fc_functions1)
        dialog.step_fc_functions1.tblFunctions1.setCurrentCell(1, 1)
        dialog.pbnNext.click()

        # step_fc_functions2: select functions for raster x raster
        self.check_current_step(dialog.step_fc_functions2)
        dialog.step_fc_functions2.tblFunctions2.setCurrentCell(0, 0)
        dialog.pbnNext.click()

        # step_fc_function: test if FloodEvacuationRasterHazardFunction
        # is on the list
        role = QtCore.Qt.UserRole
        flood_ifs = [
            dialog.step_fc_function.lstFunctions.item(row).data(role)['id']
            for row in range(dialog.step_fc_function.lstFunctions.count())]
        self.assertTrue(chosen_if in flood_ifs)

        # step_fc_function: select FloodEvacuationRasterHazardFunction and
        # press ok
        self.check_current_step(dialog.step_fc_function)
        chosen_if_row = flood_ifs.index(chosen_if)
        dialog.step_fc_function.lstFunctions.setCurrentRow(chosen_if_row)
        dialog.pbnNext.click()

        # step_fc_hazlayer_origin:
        self.check_current_step(dialog.step_fc_hazlayer_origin)
        dialog.pbnNext.click()

        # step_fc_hazlayer_from_canvas:
        self.check_current_step(dialog.step_fc_hazlayer_from_canvas)
        dialog.pbnNext.click()

        # step_fc_explayer_origin:
        self.check_current_step(dialog.step_fc_explayer_origin)
        dialog.pbnNext.click()

        # step_fc_explayer_from_canvas:
        self.check_current_step(dialog.step_fc_explayer_from_canvas)
        dialog.pbnNext.click()

        # step_fc_agglayer_origin:
        self.check_current_step(dialog.step_fc_agglayer_origin)
        dialog.step_fc_agglayer_origin.rbAggLayerNoAggregation.click()
        dialog.pbnNext.click()

        # step_fc_extent:
        self.check_current_step(dialog.step_fc_extent)
        dialog.pbnNext.click()

        # step_fc_params:
        self.check_current_step(dialog.step_fc_params)
        dialog.pbnNext.click()

        # step_fc_summary:
        self.check_current_step(dialog.step_fc_summary)
        dialog.pbnNext.click()

        # step_fc_analysis:
        self.check_current_step(dialog.step_fc_analysis)

        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_summary)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_params)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_extent)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_agglayer_origin)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_explayer_from_canvas)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_explayer_origin)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_hazlayer_from_canvas)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_hazlayer_origin)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_function)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_functions2)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_functions1)
        dialog.pbnCancel.click()

    @unittest.skip('This test is failing with the docker QGIS environment.')
    def test_input_function_centric_wizard_test_3(self):
        """Test various usecases of the wizard:
           keywordless layers, disjoint layers, browsers,
           stepping back and forth ."""

        chosen_if1 = 'FloodRasterBuildingFunction'
        chosen_if2 = 'ClassifiedRasterHazardBuildingFunction'

        expected_hazard_layers_count = 2
        expected_exposure_layers_count = 2
        expected_aggregation_layers_count = 2

        # Initialize dialog
        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.dock = self.dock
        dialog.set_function_centric_mode()
        QgsMapLayerRegistry.instance().removeAllMapLayers()

        # Load test layers
        # Hazard layer without keywords
        layer = clone_raster_layer(
            name='keywordless_layer',
            extension='.tif',
            include_keywords=False,
            source_directory=standard_data_path('hazard'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # Hazard layer - disjoint
        layer = clone_raster_layer(
            name='continuous_flood_unaligned_big_size',
            extension='.tif',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # Hazard layer
        layer = clone_raster_layer(
            name='classified_flood_20_20',
            extension='.asc',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # Exposure layer
        layer = clone_shp_layer(
            name='building-points',
            include_keywords=True,
            source_directory=standard_data_path('exposure'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # Exposure layer without keywords
        layer = clone_shp_layer(
            name='building-points',
            include_keywords=False,
            source_directory=standard_data_path('exposure'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # Aggregation layer
        layer = clone_shp_layer(
            name='district_osm_jakarta',
            include_keywords=True,
            source_directory=standard_data_path('boundaries'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # Aggregation layer without keywords
        layer = clone_shp_layer(
            name='grid_jakarta',
            include_keywords=False,
            source_directory=standard_data_path('boundaries'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # step_fc_functions1: select functions for flood x structure
        self.check_current_step(dialog.step_fc_functions1)
        dialog.step_fc_functions1.tblFunctions1.setCurrentCell(3, 1)
        dialog.pbnNext.click()

        # step_fc_functions2: select functions for raster x point
        self.check_current_step(dialog.step_fc_functions2)
        dialog.step_fc_functions2.tblFunctions2.setCurrentCell(1, 0)
        dialog.pbnNext.click()

        # step_fc_function: test if FloodRasterBuildingFunction is on the list
        role = QtCore.Qt.UserRole
        flood_ifs = [
            dialog.step_fc_function.lstFunctions.item(row).data(role)['id']
            for row in range(dialog.step_fc_function.lstFunctions.count())]
        self.assertTrue(chosen_if1 in flood_ifs)

        # step_fc_function: select FloodRasterBuildingFunction and
        # press ok
        self.check_current_step(dialog.step_fc_function)
        chosen_if_row = flood_ifs.index(chosen_if1)
        dialog.step_fc_function.lstFunctions.setCurrentRow(chosen_if_row)
        dialog.pbnNext.click()

        # step_fc_hazlayer_origin:
        self.check_current_step(dialog.step_fc_hazlayer_origin)

        # step_fc_hazlayer_from_canvas: test the lstCanvasHazLayers state
        # Note this step is tested prior to step_fc_hazlayer_origin
        # as the list is prepared prior to autoselecting the radiobuttons
        count = dialog.step_fc_hazlayer_from_canvas.lstCanvasHazLayers.count()
        self.assertEqual(count, expected_hazard_layers_count)

        # test if hazard browser works
        dialog.step_fc_hazlayer_origin.rbHazLayerFromBrowser.click()
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_fc_hazlayer_from_browser)
        # step back and continue with hazard from canvas
        dialog.pbnBack.click()
        dialog.step_fc_hazlayer_origin.rbHazLayerFromCanvas.click()
        dialog.pbnNext.click()

        # step_fc_hazlayer_from_canvas
        self.check_current_step(dialog.step_fc_hazlayer_from_canvas)
        # Select the second (keywordless) layer in order to trigger preparing
        # the 'missing keywords' description.
        dialog.step_fc_hazlayer_from_canvas.lstCanvasHazLayers.setCurrentRow(1)
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_kw_purpose)
        dialog.pbnBack.click()
        # Now select the first (proper) layer and press ok
        dialog.step_fc_hazlayer_from_canvas.lstCanvasHazLayers.setCurrentRow(0)
        dialog.pbnNext.click()

        # step_fc_explayer_origin
        self.check_current_step(dialog.step_fc_explayer_origin)
        count = dialog.step_fc_explayer_from_canvas.lstCanvasExpLayers.count()
        self.assertEqual(count, expected_exposure_layers_count)

        # test if exposure browser works
        dialog.step_fc_explayer_origin.rbExpLayerFromBrowser.click()
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_fc_explayer_from_browser)
        # step back and continue with exposure from canvas
        dialog.pbnBack.click()
        dialog.step_fc_explayer_origin.rbExpLayerFromCanvas.click()
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_fc_explayer_from_canvas)
        # Select the second (keywordless) layer in order to trigger preparing
        # the 'missing keywords' description.
        dialog.step_fc_explayer_from_canvas.lstCanvasExpLayers.setCurrentRow(1)
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_kw_purpose)
        dialog.pbnBack.click()
        # Now select the first (proper) layer and press ok
        dialog.step_fc_explayer_from_canvas.lstCanvasExpLayers.setCurrentRow(0)
        dialog.pbnNext.click()

        # step_fc_disjoint_layers
        self.check_current_step(dialog.step_fc_disjoint_layers)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_explayer_from_canvas)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_explayer_origin)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_hazlayer_from_canvas)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_hazlayer_origin)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_function)

        # Select ClassifiedRasterHazardBuildingFunction
        chosen_if_row = flood_ifs.index(chosen_if2)
        dialog.step_fc_function.lstFunctions.setCurrentRow(chosen_if_row)
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_fc_hazlayer_origin)
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_fc_hazlayer_from_canvas)

        # Select the first (proper) layer and press ok
        dialog.step_fc_hazlayer_from_canvas.lstCanvasHazLayers.setCurrentRow(0)
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_fc_explayer_origin)
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_fc_explayer_from_canvas)
        dialog.step_fc_explayer_from_canvas.lstCanvasExpLayers.setCurrentRow(0)
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_fc_agglayer_origin)

        # test if no aggregation works
        dialog.step_fc_agglayer_origin.rbAggLayerNoAggregation.click()
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_fc_extent)

        # step back and test if aggregation browser works
        dialog.pbnBack.click()
        dialog.step_fc_agglayer_origin.rbAggLayerFromBrowser.click()
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_fc_agglayer_from_browser)

        # step back and continue with aggregation from canvas
        dialog.pbnBack.click()
        dialog.step_fc_agglayer_origin.rbAggLayerFromCanvas.click()
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_fc_agglayer_from_canvas)
        count = dialog.step_fc_agglayer_from_canvas.lstCanvasAggLayers.count()
        self.assertEqual(count, expected_aggregation_layers_count)
        # Select the second (keywordless) layer in order to trigger preparing
        # the 'missing keywords' description.
        dialog.step_fc_agglayer_from_canvas.lstCanvasAggLayers.setCurrentRow(1)
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_kw_purpose)
        dialog.pbnBack.click()
        # Now select the first (proper) layer and press ok
        dialog.step_fc_agglayer_from_canvas.lstCanvasAggLayers.setCurrentRow(0)
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_fc_extent)
        dialog.pbnNext.click()

        self.check_current_step(dialog.step_fc_params)
        # Step back and enter the params step again
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_extent)
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_fc_params)
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_fc_summary)

        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_params)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_extent)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_agglayer_from_canvas)
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_fc_agglayer_origin)
        # No need to test more backward steps (already tested in other test)
        dialog.pbnCancel.click()

    @unittest.skip('This test is failing with the docker QGIS environment.')
    def test_input_function_centric_wizard_test_4(self):
        """Test keyword creation wizard called from the IF centric one."""

        chosen_if = 'FloodEvacuationRasterHazardFunction'

        # Initialize dialog
        # noinspection PyTypeChecker
        dialog = WizardDialog(iface=IFACE)
        dialog.dock = self.dock
        dialog.set_function_centric_mode()
        QgsMapLayerRegistry.instance().removeAllMapLayers()

        # Load test layers
        # Just the hazard layer in two copies
        layer = clone_raster_layer(
            name='continuous_flood_20_20',
            extension='.asc',
            include_keywords=False,
            source_directory=standard_data_path('hazard'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        layer = clone_raster_layer(
            name='continuous_flood_20_20',
            extension='.asc',
            include_keywords=False,
            source_directory=standard_data_path('hazard'))
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # step_fc_functions1: select functions for flood x population
        self.check_current_step(dialog.step_fc_functions1)
        dialog.step_fc_functions1.tblFunctions1.setCurrentCell(1, 1)
        dialog.pbnNext.click()

        # step_fc_functions2: select functions for raster x raster
        self.check_current_step(dialog.step_fc_functions2)
        dialog.step_fc_functions2.tblFunctions2.setCurrentCell(0, 0)
        dialog.pbnNext.click()

        # step_fc_function: test if FloodEvacuationRasterHazardFunction
        # is on the list
        role = QtCore.Qt.UserRole
        flood_ifs = [
            dialog.step_fc_function.lstFunctions.item(row).data(role)['id']
            for row in range(dialog.step_fc_function.lstFunctions.count())]
        self.assertTrue(chosen_if in flood_ifs)

        # step_fc_function: select FloodEvacuationRasterHazardFunction and
        # press ok
        self.check_current_step(dialog.step_fc_function)
        chosen_if_row = flood_ifs.index(chosen_if)
        dialog.step_fc_function.lstFunctions.setCurrentRow(chosen_if_row)
        dialog.pbnNext.click()

        # step_fc_hazlayer_origin:
        self.check_current_step(dialog.step_fc_hazlayer_origin)
        dialog.pbnNext.click()

        # step_fc_hazlayer_from_canvas:
        self.check_current_step(dialog.step_fc_hazlayer_from_canvas)
        # Select the first layer and register it as unsuitable (Tsunmami)
        dialog.step_fc_hazlayer_from_canvas.lstCanvasHazLayers.setCurrentRow(0)
        dialog.pbnNext.click()

        # step_kw_purpose
        self.check_current_step(dialog.step_kw_purpose)
        self.select_from_list_widget(
            'Hazard', dialog.step_kw_purpose.lstCategories)
        dialog.pbnNext.click()

        # step_kw_subcategory
        self.check_current_step(dialog.step_kw_subcategory)
        self.select_from_list_widget(
            'Tsunami', dialog.step_kw_subcategory.lstSubcategories)
        dialog.pbnNext.click()

        # step_kw_hazard_category
        self.check_current_step(dialog.step_kw_hazard_category)
        self.select_from_list_widget(
            'Single event',
            dialog.step_kw_hazard_category.lstHazardCategories)
        dialog.pbnNext.click()

        # step_kw_layermode
        self.check_current_step(dialog.step_kw_layermode)
        self.select_from_list_widget(
            'Continuous', dialog.step_kw_layermode.lstLayerModes)
        dialog.pbnNext.click()

        # step_kw_unit
        self.check_current_step(dialog.step_kw_unit)
        self.select_from_list_widget(
            'Metres', dialog.step_kw_unit.lstUnits)
        dialog.pbnNext.click()

        # step_kw_source
        self.check_current_step(dialog.step_kw_source)
        dialog.pbnNext.click()

        # step_kw_title
        self.check_current_step(dialog.step_kw_title)
        dialog.pbnNext.click()

        # step_kw_summary
        self.check_current_step(dialog.step_kw_summary)
        # step back and forth
        dialog.pbnBack.click()
        self.check_current_step(dialog.step_kw_title)
        dialog.pbnNext.click()
        self.check_current_step(dialog.step_kw_summary)

        # Finish the keyword thread and register the unsuitable layer
        dialog.pbnNext.click()

        # Should be again in the step_fc_hazlayer_from_canvas
        self.check_current_step(dialog.step_fc_hazlayer_from_canvas)
        # Now there is only one layer listed - register it properly
        dialog.pbnNext.click()

        # step_kw_purpose
        self.check_current_step(dialog.step_kw_purpose)
        self.select_from_list_widget(
            'Hazard', dialog.step_kw_purpose.lstCategories)
        dialog.pbnNext.click()

        # step_kw_subcategory
        self.check_current_step(dialog.step_kw_subcategory)
        self.select_from_list_widget(
            'Flood', dialog.step_kw_subcategory.lstSubcategories)
        dialog.pbnNext.click()

        # step_kw_hazard_category
        self.check_current_step(dialog.step_kw_hazard_category)
        self.select_from_list_widget(
            'Single event',
            dialog.step_kw_hazard_category.lstHazardCategories)
        dialog.pbnNext.click()

        # step_kw_layermode
        self.check_current_step(dialog.step_kw_layermode)
        self.select_from_list_widget(
            'Continuous', dialog.step_kw_layermode.lstLayerModes)
        dialog.pbnNext.click()

        # step_kw_unit
        self.check_current_step(dialog.step_kw_unit)
        self.select_from_list_widget(
            'Metres', dialog.step_kw_unit.lstUnits)
        dialog.pbnNext.click()

        # step_kw_source
        self.check_current_step(dialog.step_kw_source)
        dialog.pbnNext.click()

        # step_kw_title
        self.check_current_step(dialog.step_kw_title)
        dialog.pbnNext.click()

        # step_kw_summary
        self.check_current_step(dialog.step_kw_summary)
        dialog.pbnNext.click()

        # Should be in the step_fc_explayer_origin
        self.check_current_step(dialog.step_fc_explayer_origin)

        dialog.pbnCancel.click()

if __name__ == '__main__':
    suite = unittest.makeSuite(WizardDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
