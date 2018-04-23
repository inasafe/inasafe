# coding=utf-8
"""**Multi Buffer Tool Implementation.**"""

import logging
import os
from collections import OrderedDict
from operator import itemgetter

from qgis.PyQt import QtGui
from qgis.PyQt.QtCore import pyqtSlot
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsMapLayerRegistry
from qgis.gui import QgsMapLayerProxyModel

from safe.common.utilities import unique_filename, temp_dir
from safe.datastore.folder import Folder
from safe.gis.vector.multi_buffering import multi_buffering
from safe.gui.tools.help.multi_buffer_help import multi_buffer_help
from safe.gui.tools.wizard.wizard_dialog import WizardDialog
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

    def __init__(self, parent=None, iface=None, dock_widget=None):
        """Constructor for the multi buffer dialog.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget
        """
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr('InaSAFE Multi Buffer Tool'))
        icon = resources_path('img', 'icons', 'show-multi-buffer.svg')
        self.setWindowIcon(QtGui.QIcon(icon))
        self.parent = parent
        self.iface = iface
        self.dock_widget = dock_widget
        self.keyword_wizard = None

        # output file properties initialisation
        self.data_store = None
        self.output_directory = None
        self.output_filename = None
        self.output_extension = None
        self.output_layer = None
        self.classification = []

        # set icon
        self.add_class_button.setIcon(
            QIcon(resources_path('img', 'icons', 'add.svg')))
        self.remove_class_button.setIcon(
            QIcon(resources_path('img', 'icons', 'remove.svg')))

        # prepare dialog initialisation
        self.layer.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.directory_button_status()
        self.add_class_button_status()
        self.ok_button_status()
        self.output_form.setPlaceholderText(
            self.tr('[Create a temporary layer]'))
        self.keyword_wizard_checkbox.setChecked(True)

        # set signal
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

        # Fix for issue 1699 - cancel button does nothing
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
        self.output_layer = multi_buffering(input_layer, radius)

        # save output layer to data store and check whether user
        # provide the output path.
        if output_path:
            self.output_directory, self.output_filename = (
                os.path.split(output_path))
            self.output_filename, self.output_extension = (
                os.path.splitext(self.output_filename))

        # if user do not provide the output path, create a temporary file.
        else:
            self.output_directory = temp_dir(sub_dir='work')
            self.output_filename = (
                unique_filename(
                    prefix='hazard_layer',
                    suffix='.geojson',
                    dir=self.output_directory))
            self.output_filename = os.path.split(self.output_filename)[1]
            self.output_filename, self.output_extension = (
                os.path.splitext(self.output_filename))

        self.data_store = Folder(self.output_directory)
        if self.output_extension == '.shp':
            self.data_store.default_vector_format = 'shp'
        elif self.output_extension == '.geojson':
            self.data_store.default_vector_format = 'geojson'
        self.data_store.add_layer(self.output_layer, self.output_filename)

        # add output layer to map canvas
        self.output_layer = self.data_store.layer(self.output_filename)

        QgsProject.instance().addMapLayers(
            [self.output_layer])
        self.iface.setActiveLayer(self.output_layer)
        self.iface.zoomToActiveLayer()
        self.done(QtGui.QDialog.Accepted)

        if self.keyword_wizard_checkbox.isChecked():
            self.launch_keyword_wizard()

    @pyqtSignature('')  # prevents actions being handled twice
    def on_directory_button_tool_clicked(self):
        """Autoconnect slot activated when directory button is clicked."""
        # noinspection PyCallByClass,PyTypeChecker
        # set up parameter from dialog
        input_path = self.layer.currentLayer().source()
        input_directory, self.output_filename = os.path.split(input_path)
        file_extension = os.path.splitext(self.output_filename)[1]
        self.output_filename = os.path.splitext(self.output_filename)[0]
        # show Qt file directory dialog
        output_path, __ = QFileDialog.getSaveFileName(
            self,
            self.tr('Output file'),
            '%s_multi_buffer%s' % (
                os.path.join(input_directory, self.output_filename),
                file_extension),
            'GeoJSON (*.geojson);;Shapefile (*.shp)')
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
        new_class = {
            'value': self.radius_form.value(),
            'name': self.class_form.text()}
        self.classification.append(new_class)
        self.classification = sorted(
            self.classification, key=itemgetter('value'))

        self.hazard_class_form.clear()
        for item in self.classification:
            new_item = '{value} - {name}'.format(
                value=item['value'], name=item['name'])
            self.hazard_class_form.addItem(new_item)

        self.radius_form.setValue(0)
        self.class_form.clear()
        self.ok_button_status()

    def remove_selected_classification(self):
        """Remove selected item on hazard class form."""
        removed_classes = self.hazard_class_form.selectedItems()
        current_item = self.hazard_class_form.currentItem()
        removed_index = self.hazard_class_form.indexFromItem(current_item)
        del self.classification[removed_index.row()]
        for item in removed_classes:
            self.hazard_class_form.takeItem(
                self.hazard_class_form.row(item))

    def get_classification(self):
        """Get all hazard class created by user.

        :return: Hazard class definition created by user.
        :rtype: OrderedDict
        """
        classification_dictionary = {}
        for item in self.classification:
            classification_dictionary[item['value']] = item['name']

        classification_dictionary = OrderedDict(
            sorted(classification_dictionary.items()))

        return classification_dictionary

    def directory_button_status(self):
        """Function to enable or disable directory button."""
        if self.layer.currentLayer():
            self.directory_button.setEnabled(True)
        else:
            self.directory_button.setEnabled(False)

    def add_class_button_status(self):
        """Function to enable or disable add class button."""
        if self.class_form.text() and self.radius_form >= 0:
            self.add_class_button.setEnabled(True)
        else:
            self.add_class_button.setEnabled(False)

    def ok_button_status(self):
        """Function to enable or disable OK button."""
        if not self.layer.currentLayer():
            self.button_box.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        elif (self.hazard_class_form.count() > 0 and
                self.layer.currentLayer().name() and
                len(self.output_form.text()) >= 0):
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

    def launch_keyword_wizard(self):
        """Launch keyword creation wizard."""
        # make sure selected layer is the output layer
        if self.iface.activeLayer() != self.output_layer:
            return

        # launch wizard dialog
        self.keyword_wizard = WizardDialog(
            self.iface.mainWindow(),
            self.iface,
            self.dock_widget)
        self.keyword_wizard.set_keywords_creation_mode(self.output_layer)
        self.keyword_wizard.exec_()  # modal
