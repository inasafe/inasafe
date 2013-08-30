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


from os.path import join
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)
#for p in sys.path:
#    print p + '\n'

# this import required to enable PyQt API v2
import qgis  # pylint: disable=W0611

#from qgis.core import QgsMapLayerRegistry

from safe_qgis.utilities.utilities_for_testing import (
    get_qgis_app,
    set_canvas_crs,
    set_jakarta_extent,
    GEOCRS)

from safe_qgis.widgets.dock import Dock

from safe_qgis.utilities.utilities_for_testing import (
    load_standard_layers,
    setup_scenario,
    canvas_list)

QGISAPP, CANVAS, IFACE, PARENT = get_qgis_app()
DOCK = Dock(IFACE)

LOGGER = logging.getLogger('InaSAFE')


#noinspection PyArgumentList
class PostprocessorManagerTest(unittest.TestCase):
    """Test the postprocessor manager"""

    def setUp(self):
        """Fixture run before all tests"""
        os.environ['LANG'] = 'en'
        DOCK.showOnlyVisibleLayersFlag = True
        load_standard_layers()
        DOCK.cboHazard.setCurrentIndex(0)
        DOCK.cboExposure.setCurrentIndex(0)
        DOCK.cboFunction.setCurrentIndex(0)
        DOCK.runInThreadFlag = False
        DOCK.showOnlyVisibleLayersFlag = False
        DOCK.setLayerNameFromTitleFlag = False
        DOCK.zoomToImpactFlag = False
        DOCK.hideExposureFlag = False
        DOCK.showIntermediateLayers = False
        set_jakarta_extent()

    def test_checkPostProcessingLayersVisibility(self):
        """Generated layers are not added to the map registry."""
        # Explicitly disable showing intermediate layers
        DOCK.showIntermediateLayers = False
        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta singlepart')
        assert myResult, myMessage

        #LOGGER.info("Registry list before:\n%s" %
        #            QgsMapLayerRegistry.instance().mapLayers())

        #one layer (the impact) should have been added
        myExpectedCount = len(CANVAS.layers()) + 1
        #
        # # Press RUN
        DOCK.accept()
        # no KW dialog will popuo due to complete keywords
        myAfterCount = len(CANVAS.layers())
        #LOGGER.info("Registry list after:\n%s" %
        #            QgsMapLayerRegistry.instance().mapLayers())
        myMessage = ('Expected %s items in canvas, got %s' %
                     (myExpectedCount, myAfterCount))
        assert myExpectedCount == myAfterCount, myMessage

        # Now run again showing intermediate layers
        DOCK.showIntermediateLayers = True
        # Press RUN
        DOCK.accept()
        # no KW dialog will popuo due to complete keywords
        #one layer (the impact) should have been added
        myExpectedCount += 2
        myAfterCount = len(CANVAS.layers())

        LOGGER.info("Canvas list after:\n %s" % canvas_list())
        myMessage = ('Expected %s items in canvas, got %s' %
                     (myExpectedCount, myAfterCount))
        # We expect two more since we enabled showing intermedate layers
        assert myExpectedCount == myAfterCount, myMessage

    def test_postProcessorOutput(self):
        """Check that the post processor does not add spurious report rows."""

        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function')

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        assert myResult, myMessage

        # Press RUN
        DOCK.accept()
        myMessage = 'Spurious 0 filled rows added to post processing report.'
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()
        for line in myResult.split('\n'):
            if 'Entire area' in line:
                myTokens = str(line).split('\t')
                myTokens = myTokens[1:]
                mySum = 0
                for myToken in myTokens:
                    mySum += float(myToken.replace(',', '.'))

                assert mySum != 0, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(PostprocessorManagerTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
