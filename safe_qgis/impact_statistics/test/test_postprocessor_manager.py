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
import sys
import os
import logging

from qgis.core import QgsMapLayerRegistry
from os.path import join
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)
#for p in sys.path:
#    print p + '\n'

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe_qgis.utilities.utilities_for_testing import (
    set_canvas_crs,
    set_jakarta_extent,
    GEOCRS,
    load_standard_layers,
    setup_scenario,
    canvas_list)
from safe_qgis.widgets.dock import Dock

DOCK = Dock(IFACE)

LOGGER = logging.getLogger('InaSAFE')


#noinspection PyArgumentList
class PostprocessorManagerTest(unittest.TestCase):
    """Test the postprocessor manager"""

    #noinspection PyPep8Naming
    def setUp(self):
        """Fixture run before all tests"""
        os.environ['LANG'] = 'en'
        DOCK.show_only_visible_layers_flag = True
        load_standard_layers(DOCK)
        DOCK.cboHazard.setCurrentIndex(0)
        DOCK.cboExposure.setCurrentIndex(0)
        DOCK.cboFunction.setCurrentIndex(0)
        DOCK.run_in_thread_flag = False
        DOCK.show_only_visible_layers_flag = False
        DOCK.set_layer_from_title_flag = False
        DOCK.zoom_to_impact_flag = False
        DOCK.hide_exposure_flag = False
        DOCK.show_intermediate_layers = False
        set_jakarta_extent()

    def tearDown(self):
        """Run after each test."""
        # Let's use a fresh registry, canvas, and dock for each test!
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        DOCK.cboHazard.clear()
        DOCK.cboExposure.clear()

    #noinspection PyMethodMayBeStatic
    def test_check_postprocessing_layers_visibility(self):
        """Generated layers are not added to the map registry."""
        # Explicitly disable showing intermediate layers
        DOCK.show_intermediate_layers = False
        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta singlepart')
        assert result, message

        #LOGGER.info("Registry list before:\n%s" %
        #            QgsMapLayerRegistry.instance().mapLayers())

        #one layer (the impact) should have been added
        expected_count = len(CANVAS.layers()) + 1
        #
        # # Press RUN
        DOCK.accept()
        # no KW dialog will popuo due to complete keywords
        after_count = len(CANVAS.layers())
        #LOGGER.info("Registry list after:\n%s" %
        #            QgsMapLayerRegistry.instance().mapLayers())
        message = (
            'Expected %s items in canvas, got %s' %
            (expected_count, after_count))
        assert expected_count == after_count, message

        # Now run again showing intermediate layers
        DOCK.show_intermediate_layers = True
        # Press RUN
        DOCK.accept()
        # no KW dialog will popup due to complete keywords
        #one layer (the impact) should have been added
        expected_count += 2
        after_count = len(CANVAS.layers())

        LOGGER.info("Canvas list after:\n %s" % canvas_list())
        message = (
            'Expected %s items in canvas, got %s' %
            (expected_count, after_count))
        # We expect two more since we enabled showing intermediate layers
        assert expected_count == after_count, message

    #noinspection PyMethodMayBeStatic
    def test_post_processor_output(self):
        """Check that the post processor does not add spurious report rows."""

        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function_id='Flood Evacuation Function')

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        assert result, message

        # Press RUN
        DOCK.accept()
        message = 'Spurious 0 filled rows added to post processing report.'
        result = DOCK.wvResults.page().currentFrame().toPlainText()
        for line in result.split('\n'):
            if 'Entire area' in line:
                tokens = str(line).split('\t')
                tokens = tokens[1:]
                total = 0
                for token in tokens:
                    total += float(token.replace(',', '.'))

                assert total != 0, message

if __name__ == '__main__':
    suite = unittest.makeSuite(PostprocessorManagerTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
