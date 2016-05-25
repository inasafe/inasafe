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
__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '19/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import unittest
import os
import logging

from qgis.core import QgsMapLayerRegistry

from safe.impact_functions.loader import register_impact_functions
from safe.test.utilities import (
    set_canvas_crs,
    set_jakarta_extent,
    GEOCRS,
    load_standard_layers,
    setup_scenario,
    canvas_list,
    get_qgis_app)

# AG: get_qgis_app() should be called before importing modules from
# safe.gui.widgets.dock
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gui.widgets.dock import Dock

LOGGER = logging.getLogger('InaSAFE')


# noinspection PyArgumentList
class PostprocessorManagerTest(unittest.TestCase):
    """Test the postprocessor manager"""

    @classmethod
    def setUpClass(cls):
        cls.DOCK = Dock(IFACE)

    # noinspection PyPep8Naming
    def setUp(self):
        """Fixture run before all tests"""
        os.environ['LANG'] = 'en'
        self.DOCK.show_only_visible_layers_flag = True
        load_standard_layers(self.DOCK)
        self.DOCK.cboHazard.setCurrentIndex(0)
        self.DOCK.cboExposure.setCurrentIndex(0)
        self.DOCK.cboFunction.setCurrentIndex(0)
        self.DOCK.run_in_thread_flag = False
        self.DOCK.show_only_visible_layers_flag = False
        self.DOCK.set_layer_from_title_flag = False
        self.DOCK.zoom_to_impact_flag = False
        self.DOCK.hide_exposure_flag = False
        self.DOCK.show_intermediate_layers = False
        set_jakarta_extent()

        register_impact_functions()

    def tearDown(self):
        """Run after each test."""
        # Let's use a fresh registry, canvas, and dock for each test!
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        self.DOCK.cboHazard.clear()
        self.DOCK.cboExposure.clear()

    # noinspection PyMethodMayBeStatic
    def test_check_postprocessing_layers_visibility(self):
        """Generated layers are not added to the map registry."""
        # Explicitly disable showing intermediate layers
        self.DOCK.show_intermediate_layers = False
        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        result, message = setup_scenario(
            self.DOCK,
            hazard='Continuous Flood',
            exposure='Population',
            function_id='FloodEvacuationRasterHazardFunction',
            aggregation_layer=u"Dístríct's of Jakarta")
        set_jakarta_extent(dock=self.DOCK)
        assert result, message

        # LOGGER.info("Registry list before:\n%s" %
        #            QgsMapLayerRegistry.instance().mapLayers())

        # one layer (the impact) should have been added
        expected_count = len(CANVAS.layers()) + 1
        #
        # Press RUN
        self.DOCK.accept()
        # no KW dialog will popuo due to complete keywords
        after_count = len(CANVAS.layers())
        # LOGGER.info("Registry list after:\n%s" %
        #            QgsMapLayerRegistry.instance().mapLayers())
        message = (
            'Expected %s items in canvas, got %s' %
            (expected_count, after_count))
        assert expected_count == after_count, message

        # Now run again showing intermediate layers
        self.DOCK.show_intermediate_layers = True
        # Press RUN
        self.DOCK.accept()
        # no KW dialog will popup due to complete keywords
        # one layer (the impact) should have been added
        expected_count += 2
        after_count = len(CANVAS.layers())

        # LOGGER.info("Canvas list after:\n %s" % canvas_list())
        message = (
            'Expected %s items in canvas, got %s' %
            (expected_count, after_count))
        # We expect two more since we enabled showing intermediate layers
        assert expected_count == after_count, message

    # noinspection PyMethodMayBeStatic
    def test_post_processor_output(self):
        """Check that the post processor does not add spurious report rows."""

        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        result, message = setup_scenario(
            self.DOCK,
            hazard='Continuous Flood',
            exposure='Population',
            function_id='FloodEvacuationRasterHazardFunction')

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        assert result, message

        # Press RUN
        self.DOCK.accept()
        message = 'Spurious 0 filled rows added to post processing report.'
        result = self.DOCK.wvResults.page().currentFrame().toPlainText()
        for line in result.split('\n'):
            if 'Entire area' in line:
                tokens = str(line).split('\t')
                tokens = tokens[1:]
                total = 0
                for token in tokens:
                    try:
                        total += float(token.replace(',', ''))
                    except ValueError:
                        total += float(token[0])

                assert total != 0, message

if __name__ == '__main__':
    suite = unittest.makeSuite(PostprocessorManagerTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
