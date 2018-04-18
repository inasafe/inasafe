# coding=utf-8

import unittest

from qgis.core import QgsMapLayerRegistry, QgsProject
from qgis.gui import QgsMapCanvasLayer

from safe.definitions.exposure import exposure_road, exposure_population
from safe.gui.tools.multi_exposure_dialog import (
    MultiExposureDialog)
from safe.test.utilities import load_test_vector_layer

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class MultiExposureDialogTest(unittest.TestCase):

    def setUp(self):
        from safe.test.utilities import get_qgis_app
        QGIS_APP, CANVAS, self.iface, PARENT = get_qgis_app(
            qsetting='InaSAFETest')

    def test_custom_order(self):
        """Test we can set a custom order after the analysis."""
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        population_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'population.geojson')
        roads_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'roads.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        test_layers = [
            hazard_layer, population_layer, roads_layer, aggregation_layer]
        QgsMapLayerRegistry.instance().addMapLayers(test_layers)

        qgs_map_canvas_layers = [QgsMapCanvasLayer(x) for x in test_layers]
        self.iface.mapCanvas().setLayerSet(qgs_map_canvas_layers)

        dialog = MultiExposureDialog(iface=self.iface)
        self.assertFalse(
            dialog.btn_run.isEnabled(),
            dialog.message_viewer.page_to_text())
        self.assertFalse(
            dialog.btn_run.isEnabled(),
            dialog.message_viewer.page_to_text())

        dialog.combos_exposures[exposure_road['key']].setCurrentIndex(1)
        dialog.combos_exposures[exposure_population['key']].setCurrentIndex(1)

        self.assertTrue(
            dialog.btn_run.isEnabled(),
            dialog.message_viewer.page_to_text())
        self.assertTrue(
            dialog.btn_run.isEnabled(),
            dialog.message_viewer.page_to_text())

        dialog.tab_widget.setCurrentIndex(1)
        root = dialog.tree.invisibleRootItem()

        self.assertFalse(dialog.move_down.isEnabled())
        self.assertFalse(dialog.move_up.isEnabled())
        self.assertFalse(dialog.add_layer.isEnabled())
        self.assertFalse(dialog.remove_layer.isEnabled())
        self.assertEqual(2, root.childCount())

        item_from_analysis = root.child(0)
        self.assertEqual('Layers from Analysis', item_from_analysis.text(0))

        # One for each exposure (roads and population) and one for the multi =3
        self.assertEqual(item_from_analysis.childCount(), 3)

        # The right panel is still empty.
        self.assertEqual(0, dialog.list_layers_in_map_report.count())

        # Let's select the impact layer.
        item_from_analysis.child(0).child(0).setSelected(True)
        self.assertFalse(dialog.move_down.isEnabled())
        self.assertFalse(dialog.move_up.isEnabled())
        self.assertTrue(dialog.add_layer.isEnabled())
        self.assertFalse(dialog.remove_layer.isEnabled())
        self.assertEqual(4, item_from_analysis.child(0).childCount())

        # Move the layer from left to right
        dialog.add_layer.click()
        self.assertEqual(3, item_from_analysis.child(0).childCount())
        self.assertEqual(1, dialog.list_layers_in_map_report.count())
        self.assertEqual(
            dialog.ordered_expected_layers(),
            [('FromAnalysis', u'impact_analysis',
              u'Generic Hazard Polygon On Population Polygon', None)])
        self.assertFalse(dialog.move_down.isEnabled())
        self.assertFalse(dialog.move_up.isEnabled())
        self.assertFalse(dialog.add_layer.isEnabled())
        self.assertFalse(dialog.remove_layer.isEnabled())

        item_from_analysis.child(2).child(0).setSelected(True)
        dialog.add_layer.click()
        self.assertEqual(
            dialog.ordered_expected_layers(),
            [
                ('FromAnalysis', u'impact_analysis',
                 u'Generic Hazard Polygon On Population Polygon', None),
                ('FromAnalysis', u'impact_analysis',
                 u'Generic Hazard Polygon On Roads Line', None)
            ])

        # Test move up/down
        self.assertEqual(2, dialog.list_layers_in_map_report.count())
        dialog.list_layers_in_map_report.setCurrentRow(0)
        self.assertTrue(dialog.move_down.isEnabled())
        self.assertFalse(dialog.move_up.isEnabled())
        self.assertFalse(dialog.add_layer.isEnabled())
        self.assertTrue(dialog.remove_layer.isEnabled())
        dialog.move_down.click()
        self.assertEqual(
            dialog.ordered_expected_layers(),
            [
                ('FromAnalysis', u'impact_analysis',
                 u'Generic Hazard Polygon On Roads Line', None),
                ('FromAnalysis', u'impact_analysis',
                 u'Generic Hazard Polygon On Population Polygon', None),
            ])

        # Let's add a layer from canvas
        item_from_canvas = root.child(1)
        self.assertEqual('Layers from Canvas', item_from_canvas.text(0))
        for i in range(item_from_canvas.childCount()):
            item_from_canvas.child(i).text(0)
            if item_from_canvas.child(i).text(0) == 'classified_vector':
                item_from_canvas.child(i).setSelected(True)
        self.assertFalse(dialog.move_down.isEnabled())
        self.assertTrue(dialog.move_up.isEnabled())  # Old selection
        self.assertTrue(dialog.add_layer.isEnabled())
        self.assertTrue(dialog.remove_layer.isEnabled())  # Old selection

        dialog.add_layer.click()
        custom_order = dialog.ordered_expected_layers()
        # We don't want to compare the QML included for layers coming from
        # canvas.
        self.assertEqual(3, len(custom_order))
        self.assertEqual(custom_order[2][0], 'FromCanvas')
        self.assertEqual(custom_order[2][1], 'classified_vector')
        self.assertTrue(
            custom_order[2][2].endswith(
                'classified_vector.geojson|qgis_provider=ogr'),
            custom_order[2][2]
        )
        self.assertTrue(custom_order[2][3].endswith('</qgis>\n'))

        self.assertEqual(
            custom_order[1],
            ('FromAnalysis', u'impact_analysis',
             u'Generic Hazard Polygon On Population Polygon', None),
        )
        self.assertEqual(
            custom_order[0],
            ('FromAnalysis', u'impact_analysis',
             u'Generic Hazard Polygon On Roads Line', None),
        )
