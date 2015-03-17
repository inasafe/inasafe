# coding=utf-8
"""
InaSAFE uDisaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'christian@kartoza.com'
__date__ = '25/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import os
import shutil
from collections import OrderedDict
# noinspection PyPackageRequirements
from nose import SkipTest

from qgis.core import (
    QgsVectorLayer,
    QgsMapLayerRegistry)
from PyQt4 import QtGui

from safe.test.utilities import (
    test_data_path,
    clone_shp_layer,
    clone_raster_layer,
    temp_dir,
    get_qgis_app)
from safe.gui.tools.people_in_buildings_dialog import PeopleInBuildingsDialog
from safe.utilities.gis import qgis_version
from safe.defaults import get_defaults

from safe.test.utilities import (
    test_data_path,
    load_standard_layers,
    setup_scenario,
    set_canvas_crs,
    combos_to_string,
    populate_dock,
    canvas_list,
    GEOCRS,
    GOOGLECRS,
    load_layer,
    load_layers,
    set_jakarta_extent,
    set_jakarta_google_extent,
    set_yogya_extent,
    get_ui_state,
    set_small_jakarta_extent,
    get_qgis_app,
    TESTDATA,
    BOUNDDATA,
    HAZDATA)


QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class KeywordsDialogTest(unittest.TestCase):
    """Test the InaSAFE keywords GUI."""

    def setUp(self):
        """Create fresh dialog for each test."""
        self.dialog = PeopleInBuildingsDialog(IFACE, PARENT)
        IFACE.setActiveLayer(None)
        os.path.join(TESTDATA, 'people_in_buildings_buildings')
        os.path.join(TESTDATA, 'people_in_buildings_census')

    def tearDown(self):
        """Destroy the dialog after each test."""
        # Clear all the loaded layers in Map Registry
        # noinspection PyArgumentList,PyUnresolvedReferences
        for layer in QgsMapLayerRegistry.instance().mapLayers():
            # noinspection PyArgumentList,PyUnresolvedReferences
            QgsMapLayerRegistry.instance().removeMapLayer(layer)

    @staticmethod
    def _get_combobox_content(combo_box):
        items = [combo_box.itemText(i) for i in range(combo_box.count())]
        return items

    def test_0001_load_layer(self):
        """
        :return:
        """
        self.dialog.load_layers_into_combo_box()
        print self._get_combobox_content(self.dialog.buildingLayerComboBox)
        print self._get_combobox_content(self.dialog.censusLayerComboBox)

    def test_0002_add_attributes_to_buildings_layer(self):
        """Ensure the people attributes are being assigned to buildings layer.
        :return:
        """
        self.dialog.load_layers_into_combo_box()

