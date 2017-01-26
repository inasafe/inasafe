# coding=utf-8
"""**Volcano Buffer Implementation.**

"""

import logging
import os

from qgis.core import QgsVectorFileWriter, QgsMapLayerRegistry, QgsVectorLayer
from qgis.gui import QgsMapLayerProxyModel
from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSignature, pyqtSlot
from PyQt4.QtGui import QFileDialog, QIcon
from safe.common.version import get_version
from safe.gis.vector.multi_buffering import multi_buffering
from safe.gui.tools.help.multi_buffer_help import (
    multi_buffer_help)
from safe.messaging import styles
from safe.utilities.resources import (
    get_ui_class,
    resources_path,
    html_footer,
    html_header)

INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
LOGGER = logging.getLogger('InaSAFE')
FORM_CLASS = get_ui_class('multi_buffer_dialog_base.ui')


class MultiBufferDialog(QtGui.QDialog, FORM_CLASS):
    """Dialog implementation class for the InaSAFE multi buffer tool."""

    def __init__(self, parent=None):
        """Constructor for the multi buffer dialog.

        :param parent: Parent widget of this dialog
        :type parent: QWidget
        """
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr(
            'InaSAFE %s Multi Buffer Tool' % get_version()))

        # set icon
        self.add_class_button.setIcon(
            QIcon(os.path.join(
                resources_path(), 'img', 'icons', 'add.svg')))
        self.remove_class_button.setIcon(
            QIcon(os.path.join(
                resources_path(), 'img', 'icons', 'remove.svg')))

        # prepare dialog initialisation
        self.layer.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.directory_button.setEnabled(False)
        self.add_class_button.setEnabled(False)
        self.button_box.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

        # set signal
        self.layer.layerChanged.connect(self.get_output_from_input)
        self.layer.layerChanged.connect(self.directory_button_status)
        self.layer.layerChanged.connect(self.ok_button_status)
        self.output_form.textChanged.connect(self.ok_button_status)
        self.directory_button.clicked.connect(
            self.on_directory_button_tool_clicked)
        self.radius_form.valueChanged.connect(self.add_class_button_status)
        self.class_form.textChanged.connect(self.add_class_button_status)
        self.add_class_button.clicked.connect(
            self.populate_hazard_classification)
        self.add_class_button.clicked.connect(self.ok_button_status)
        self.remove_class_button.clicked.connect(
            self.remove_selected_classification)
        self.remove_class_button.clicked.connect(self.ok_button_status)

        # Set up things for context help
        self.help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)

        # Fix for issue 1699 - cancel button does noth  ing
        cancel_button = self.button_box.button(QtGui.QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(self.reject)
        # Fix ends
        ok_button = self.button_box.button(QtGui.QDialogButtonBox.Ok)
        ok_button.clicked.connect(self.accept)

    def accept(self):
        """Process the layer for multi buffering and generate a new layer.

        .. note:: This is called on OK click.

        """
        # set parameter from dialog
        input_layer = self.layer.currentLayer()
        output_path = self.output_form.text()
        radius = self.get_classification()
        # monkey patch keywords so layer works on multi buffering function
        input_layer.keywords = {'inasafe_fields': {}}

        # run multi buffering
        output_layer = multi_buffering(input_layer, radius)

        # setting up output format
        if self.output_form.text().endswith('.shp'):
            QgsVectorFileWriter.writeAsVectorFormat(
                output_layer, output_path, 'CP1250', None, 'ESRI Shapefile')
        elif self.output_form.text().endswith('.geojson'):
            QgsVectorFileWriter.writeAsVectorFormat(
                output_layer, output_path, 'CP1250', None, 'GeoJSON')

        output_layer = QgsVectorLayer(
            output_path,
            os.path.basename(output_path),
            'ogr')

        # add output layer to map canvas
        QgsMapLayerRegistry.instance().addMapLayers([output_layer])
        self.done(QtGui.QDialog.Accepted)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_directory_button_tool_clicked(self):
        """Autoconnect slot activated when directory button is clicked."""
        # noinspection PyCallByClass,PyTypeChecker
        # set up parameter from dialog
        input_path = self.layer.currentLayer().source()
        input_path = os.path.splitext(input_path)
        output_name = input_path[0].split('/')[-1]
        output_extension = input_path[1]
        # show file directory dialog
        output_path = QFileDialog.getSaveFileName(
            self,
            self.tr('Output file'),
            '%s_multi_buffer%s' % (output_name, output_extension),
            self.tr('GeoJSON (*.geojson);;Shapefile (*.shp)'))
        # set selected path to the dialog
        self.output_form.setText(output_path)

    def get_output_from_input(self):
        """Populate output form with default output path based on input layer.
        """
        input_path = self.layer.currentLayer().source()
        output_path = (
            os.path.splitext(input_path)[0] + '_multi_buffer' +
            os.path.splitext(input_path)[1])
        self.output_form.setText(output_path)

    def populate_hazard_classification(self):
        """Populate hazard classification on hazard class form."""
        new_class = '%s - %s' % (self.radius_form.value(),
                                 self.class_form.text())
        self.hazard_class_form.addItem(new_class)
        self.radius_form.setValue(0)
        self.class_form.clear()
        self.ok_button_status()

    def remove_selected_classification(self):
        """Remove selected item on hazard class form."""
        removed_classes = self.hazard_class_form.selectedItems()
        for item in removed_classes:
            self.hazard_class_form.takeItem(
                self.hazard_class_form.row(item))

    def get_classification(self):
        """Get all hazard class created by user.

        :return: Hazard class definition created by user.
        :rtype: Dictionary
        """
        classification = {}
        for index in xrange(self.hazard_class_form.count()):
            hazard_class = (
                self.hazard_class_form.item(index).text().replace(' ', ''))
            key = int(hazard_class.split('-')[0])
            value = hazard_class.split('-')[1]
            classification[key] = value
        return classification

    def directory_button_status(self):
        """Function to enable or disable directory button."""
        if len(self.layer.currentLayer().name()) > 0:
            self.directory_button.setEnabled(True)
        else:
            self.directory_button.setEnabled(False)

    def add_class_button_status(self):
        """Function to enable or disable add class button."""
        if len(self.class_form.text()) > 0 and self.radius_form >= 0:
            self.add_class_button.setEnabled(True)
        else:
            self.add_class_button.setEnabled(False)

    def ok_button_status(self):
        """Function to enable or disable OK button."""
        if (self.hazard_class_form.count() > 0 and
                len(self.layer.currentLayer().name()) > 0 and
                    len(self.output_form.text()) > 0):
            self.button_box.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.button_box.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

    @pyqtSlot()
    @pyqtSignature('bool')  # prevents actions being handled twice
    def help_toggled(self, flag):
        """Show or hide the help tab in the stacked widget.

        :param flag: Flag indicating whether help should be shown or hidden.
        :type flag: bool
        """
        if flag:
            self.help_button.setText(self.tr('Hide Help'))
            self.show_help()
        else:
            self.help_button.setText(self.tr('Show Help'))
            self.hide_help()

    def hide_help(self):
        """Hide the usage info from the user."""
        self.main_stacked_widget.setCurrentIndex(1)

    def show_help(self):
        """Show usage info to the user."""
        # Read the header and footer html snippets
        self.main_stacked_widget.setCurrentIndex(0)
        header = html_header()
        footer = html_footer()

        string = header

        message = multi_buffer_help()

        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)
