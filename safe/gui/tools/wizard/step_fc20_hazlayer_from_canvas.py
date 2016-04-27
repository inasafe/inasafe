# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Function Centric Wizard Step: Hazard Layer From Canvas

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'qgis@borysjurgiel.pl'
__revision__ = '$Format:%H$'
__date__ = '16/03/2016'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# noinspection PyPackageRequirements
from PyQt4 import QtCore, QtGui
# noinspection PyPackageRequirements
from PyQt4.QtCore import pyqtSignature
# noinspection PyPackageRequirements
from PyQt4.QtGui import QListWidgetItem

from qgis.core import QgsMapLayerRegistry

from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step import WizardStep


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcHazLayerFromCanvas(WizardStep, FORM_CLASS):
    """Function Centric Wizard Step: Hazard Layer From Canvas"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_canvas_hazlayer())

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_fc_hazlayer_origin
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.parent.is_selected_layer_keywordless:
            # insert keyword creation thread here
            self.parent.parent_step = self
            self.parent.existing_keywords = None
            self.parent.set_mode_label_to_keywords_creation()
            new_step = self.parent.step_kw_purpose
        else:
            new_step = self.parent.step_fc_explayer_origin
        return new_step

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_lstCanvasHazLayers_itemSelectionChanged(self):
        """Update layer description label

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """

        self.parent.hazard_layer = self.selected_canvas_hazlayer()
        lblText = self.parent.get_layer_description_from_canvas(
            self.parent.hazard_layer, 'hazard')
        self.lblDescribeCanvasHazLayer.setText(lblText)
        self.parent.pbnNext.setEnabled(True)

    def selected_canvas_hazlayer(self):
        """Obtain the canvas layer selected by user.

        :returns: The currently selected map layer in the list.
        :rtype: QgsMapLayer
        """

        if self.lstCanvasHazLayers.selectedItems():
            item = self.lstCanvasHazLayers.currentItem()
        else:
            return None
        try:
            layer_id = item.data(QtCore.Qt.UserRole)
        except (AttributeError, NameError):
            layer_id = None

        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    def list_compatible_canvas_layers(self):
        """Fill the list widget with compatible layers.

        :returns: Metadata of found layers.
        :rtype: list of dicts
        """
        italic_font = QtGui.QFont()
        italic_font.setItalic(True)
        list_widget = self.lstCanvasHazLayers
        # Add compatible layers
        list_widget.clear()
        for layer in self.parent.get_compatible_canvas_layers('hazard'):
            item = QListWidgetItem(layer['name'], list_widget)
            item.setData(QtCore.Qt.UserRole, layer['id'])
            if not layer['keywords']:
                item.setFont(italic_font)
            list_widget.addItem(item)

    def set_widgets(self):
        """Set widgets on the Hazard Layer From TOC tab"""
        # The list is already populated in the previous step, but now we
        # need to do it again in case we're back from the Keyword Wizard.
        # First, preserve self.parent.layer before clearing the list
        last_layer = self.parent.layer and self.parent.layer.id() or None
        self.lblDescribeCanvasHazLayer.clear()
        self.list_compatible_canvas_layers()
        self.auto_select_one_item(self.lstCanvasHazLayers)
        # Try to select the last_layer, if found:
        if last_layer:
            layers = []
            for indx in xrange(self.lstCanvasHazLayers.count()):
                item = self.lstCanvasHazLayers.item(indx)
                layers += [item.data(QtCore.Qt.UserRole)]
            if last_layer in layers:
                self.lstCanvasHazLayers.setCurrentRow(layers.index(last_layer))
