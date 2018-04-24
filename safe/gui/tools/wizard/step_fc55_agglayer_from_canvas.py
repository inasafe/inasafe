# coding=utf-8
"""InaSAFE Wizard Step Aggregation Layer Canvas."""

from qgis.core import QgsProject
# noinspection PyPackageRequirements
from qgis.PyQt import QtCore, QtGui
# noinspection PyPackageRequirements
from qgis.PyQt.QtCore import pyqtSlot
# noinspection PyPackageRequirements
from qgis.PyQt.QtWidgets import QListWidgetItem
from qgis.PyQt.QtGui import QPixmap

from safe import messaging as m
from safe.gui.tools.wizard.utilities import layers_intersect
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcAggLayerFromCanvas(WizardStep, FORM_CLASS):

    """Function Centric Wizard Step: Aggregation Layer From Canvas."""

    def is_ready_to_next_step(self):
        """Check if the step is complete.

        If so, there is no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_canvas_agglayer())

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to.
        :rtype: WizardStep instance or None
        """
        if self.parent.is_selected_layer_keywordless:
            # insert keyword creation thread here
            self.parent.parent_step = self
            self.parent.existing_keywords = None
            self.parent.set_mode_label_to_keywords_creation()
            new_step = self.parent.step_kw_purpose
        else:
            if layers_intersect(self.parent.exposure_layer,
                                self.parent.aggregation_layer):
                new_step = self.parent.step_fc_summary
            else:
                new_step = self.parent.step_fc_agglayer_disjoint
        return new_step

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSlot()
    def on_lstCanvasAggLayers_itemSelectionChanged(self):
        """Update layer description label.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        self.parent.aggregation_layer = self.selected_canvas_agglayer()
        lblText = self.parent.get_layer_description_from_canvas(
            self.parent.aggregation_layer, 'aggregation')
        self.lblDescribeCanvasAggLayer.setText(lblText)
        self.parent.pbnNext.setEnabled(True)

    def selected_canvas_agglayer(self):
        """Obtain the canvas aggregation layer selected by user.

        :returns: The currently selected map layer in the list.
        :rtype: QgsMapLayer
        """
        if self.lstCanvasAggLayers.selectedItems():
            item = self.lstCanvasAggLayers.currentItem()
        else:
            return None
        try:
            layer_id = item.data(QtCore.Qt.UserRole)
        except (AttributeError, NameError):
            layer_id = None

        layer = QgsProject.instance().mapLayer(layer_id)
        return layer

    def list_compatible_canvas_layers(self):
        """Fill the list widget with compatible layers.

        :returns: Metadata of found layers.
        :rtype: list of dicts
        """
        italic_font = QtGui.QFont()
        italic_font.setItalic(True)
        list_widget = self.lstCanvasAggLayers
        # Add compatible layers
        list_widget.clear()
        for layer in self.parent.get_compatible_canvas_layers('aggregation'):
            item = QListWidgetItem(layer['name'], list_widget)
            item.setData(QtCore.Qt.UserRole, layer['id'])
            if not layer['keywords']:
                item.setFont(italic_font)
            list_widget.addItem(item)

    def set_widgets(self):
        """Set widgets on the Aggregation Layer from Canvas tab."""
        # The list is already populated in the previous step, but now we
        # need to do it again in case we're back from the Keyword Wizard.
        # First, preserve self.parent.layer before clearing the list
        last_layer = self.parent.layer and self.parent.layer.id() or None
        self.lblDescribeCanvasAggLayer.clear()
        self.list_compatible_canvas_layers()
        self.auto_select_one_item(self.lstCanvasAggLayers)
        # Try to select the last_layer, if found:
        if last_layer:
            layers = []
            for indx in range(self.lstCanvasAggLayers.count()):
                item = self.lstCanvasAggLayers.item(indx)
                layers += [item.data(QtCore.Qt.UserRole)]
            if last_layer in layers:
                self.lstCanvasAggLayers.setCurrentRow(layers.index(last_layer))
        # Set icon
        self.lblIconIFCWAggregationFromCanvas.setPixmap(QPixmap(None))

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        return tr('Select Aggregation from Canvas Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, You can choose a aggregation '
            'layer from the list of layers that have been loaded to '
            'QGIS.').format(step_name=self.step_name)))
        return message
