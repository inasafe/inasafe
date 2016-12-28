# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Function Centric Wizard Step: Exposure Layer From Canvas

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

# noinspection PyPackageRequirements
from PyQt4 import QtCore, QtGui
# noinspection PyPackageRequirements
from PyQt4.QtCore import pyqtSignature
# noinspection PyPackageRequirements
from PyQt4.QtGui import QListWidgetItem, QPixmap

from qgis.core import QgsMapLayerRegistry

from safe.definitionsv4.layer_purposes import layer_purpose_exposure
from safe.utilities.resources import resources_path

from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_utils import layers_intersect

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcExpLayerFromCanvas(WizardStep, FORM_CLASS):
    """Function Centric Wizard Step: Exposure Layer From Canvas"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_canvas_explayer())

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
            if layers_intersect(self.parent.hazard_layer,
                                self.parent.exposure_layer):
                new_step = self.parent.step_fc_agglayer_origin
            else:
                new_step = self.parent.step_fc_disjoint_layers
        return new_step

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_lstCanvasExpLayers_itemSelectionChanged(self):
        """Update layer description label

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        self.parent.exposure_layer = self.selected_canvas_explayer()
        lblText = self.parent.get_layer_description_from_canvas(
            self.parent.exposure_layer, 'exposure')
        self.lblDescribeCanvasExpLayer.setText(lblText)
        self.parent.pbnNext.setEnabled(True)

    def selected_canvas_explayer(self):
        """Obtain the canvas exposure layer selected by user.

        :returns: The currently selected map layer in the list.
        :rtype: QgsMapLayer
        """
        if self.lstCanvasExpLayers.selectedItems():
            item = self.lstCanvasExpLayers.currentItem()
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
        list_widget = self.lstCanvasExpLayers
        # Add compatible layers
        list_widget.clear()
        for layer in self.parent.get_compatible_canvas_layers('exposure'):
            item = QListWidgetItem(layer['name'], list_widget)
            item.setData(QtCore.Qt.UserRole, layer['id'])
            if not layer['keywords']:
                item.setFont(italic_font)
            list_widget.addItem(item)

    def set_widgets(self):
        """Set widgets on the Exposure Layer From Canvas tab"""
        # The list is already populated in the previous step, but now we
        # need to do it again in case we're back from the Keyword Wizard.
        # First, preserve self.parent.layer before clearing the list
        last_layer = self.parent.layer and self.parent.layer.id() or None
        self.lblDescribeCanvasExpLayer.clear()
        self.list_compatible_canvas_layers()
        self.auto_select_one_item(self.lstCanvasExpLayers)
        # Try to select the last_layer, if found:
        if last_layer:
            layers = []
            for indx in xrange(self.lstCanvasExpLayers.count()):
                item = self.lstCanvasExpLayers.item(indx)
                layers += [item.data(QtCore.Qt.UserRole)]
            if last_layer in layers:
                self.lstCanvasExpLayers.setCurrentRow(layers.index(last_layer))

        # Set icon
        exposure = self.parent.step_fc_functions1.selected_value(
            layer_purpose_exposure['key'])
        icon_path = resources_path(
            'img', 'wizard', 'keyword-subcategory-%s.svg'
                             % (exposure['key'] or 'notset'))
        self.lblIconIFCWExposureFromCanvas.setPixmap(QPixmap(icon_path))
