# coding=utf-8
"""InaSAFE Wizard Step Hazard Layer Canvas."""

# noinspection PyPackageRequirements
from PyQt4.QtCore import pyqtSignature, Qt
# noinspection PyPackageRequirements
from PyQt4.QtGui import QListWidgetItem, QPixmap, QFont
from qgis.core import QgsMapLayerRegistry

from safe import messaging as m
from safe.definitions.layer_purposes import layer_purpose_hazard
from safe.gui.tools.wizard.utilities import get_image_path
from safe.gui.tools.wizard.wizard_step import (
    WizardStep, get_wizard_step_ui_class)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcHazLayerFromCanvas(WizardStep, FORM_CLASS):
    """InaSAFE Wizard Step Hazard Layer Canvas."""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_canvas_hazlayer())

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
            layer_id = item.data(Qt.UserRole)
        except (AttributeError, NameError):
            layer_id = None

        # noinspection PyArgumentList
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    def list_compatible_canvas_layers(self):
        """Fill the list widget with compatible layers.

        :returns: Metadata of found layers.
        :rtype: list of dicts
        """
        italic_font = QFont()
        italic_font.setItalic(True)
        list_widget = self.lstCanvasHazLayers
        # Add compatible layers
        list_widget.clear()
        for layer in self.parent.get_compatible_canvas_layers('hazard'):
            item = QListWidgetItem(layer['name'], list_widget)
            item.setData(Qt.UserRole, layer['id'])
            if not layer['keywords']:
                item.setFont(italic_font)
            list_widget.addItem(item)

    def set_widgets(self):
        """Set widgets on the Hazard Layer From TOC tab."""
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
            for index in xrange(self.lstCanvasHazLayers.count()):
                item = self.lstCanvasHazLayers.item(index)
                layers += [item.data(Qt.UserRole)]
            if last_layer in layers:
                self.lstCanvasHazLayers.setCurrentRow(layers.index(last_layer))

        # Set icon
        hazard = self.parent.step_fc_functions1.selected_value(
            layer_purpose_hazard['key'])
        icon_path = get_image_path(hazard)
        self.lblIconIFCWHazardFromCanvas.setPixmap(QPixmap(icon_path))

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        return tr('Select Hazard from Canvas Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, You can choose a hazard layer '
            'from the list of layers that have been loaded to QGIS and that '
            'matches with the geometry and hazard type you set in the '
            'previous step').format(step_name=self.step_name)))
        return message
