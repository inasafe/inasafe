# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid **People In BuildingsDialog.**

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""
__author__ = 'christian@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '12/02/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore

from safe.utilities.resources import get_ui_class

FORM_CLASS = get_ui_class('people_in_buildings_base.ui')


class PeopleInBuildingsDialog(QtGui.QDialog, FORM_CLASS):
    """Options dialog for the InaSAFE plugin."""

    def __init__(self, iface, parent=None):
        """Constructor for the dialog.

        :param iface: A Quantum GIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param parent: Parent widget of this dialog
        :type parent: QWidget

        :param dock: Optional dock widget instance that we can notify of
            changes to the keywords.
        :type dock: Dock
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent

        self.load_layers_into_combo_box()

        self.buildingLayerComboBox.activated['QString'].connect(
            self.handle_building_layer)
        self.censusLayerComboBox.activated['QString'].connect(
            self.handle_census_layer)

    def load_layers_into_combo_box(self):
        layer_names = self._get_layer_names()
        self._update_combobox(self.buildingLayerComboBox, layer_names)
        self._update_combobox(self.censusLayerComboBox, layer_names)
        self.handle_building_layer(self.buildingLayerComboBox.currentText())
        self.handle_census_layer(self.censusLayerComboBox.currentText())

    def _select_layer_by_name(self, layer_name):
        """Get a layer by name
        :param layer_name: The layer's name
        :type layer_name: basestring

        :returns: The layer that has the appropriate name or none
        :rtype: QgsMapLayer, None
        """
        layers = self._get_layers()
        layer_names = [layer.name() for layer in layers]
        if not layer_name in layer_names:
            return None
        index = layer_names.index(layer_name)
        return layers[index]

    def _get_layers(self):
        layers = self.iface.legendInterface().layers()
        return layers

    def _get_layer_names(self):
        layers = self._get_layers()
        layer_names = [l.name() for l in layers]
        return layer_names

    @staticmethod
    def _get_field_names(layer):
        field_names = [field.name() for field in layer.pendingFields()]
        return field_names

    def handle_building_layer(self, layer_name):
        layer = self._select_layer_by_name(layer_name)
        if layer is None:
            return
        field_names = self._get_field_names(layer)
        self._update_combobox(self.usageColumnComboBox, field_names)
        self._update_combobox(self.levelsColumnComboBox, field_names)

    def handle_census_layer(self, layer_name):
        layer = self._select_layer_by_name(layer_name)
        if layer is None:
            return
        field_names = self._get_field_names(layer)
        self._update_combobox(self.populationCountComboBox, field_names)

    def _update_combobox(self, combobox, options):
        """Shorthand for clearing and loading options (this happens a lot)
        """
        combobox.clear()
        combobox.addItems(options)

