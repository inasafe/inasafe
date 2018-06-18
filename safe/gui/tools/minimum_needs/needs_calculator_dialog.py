# coding=utf-8
"""Minimum Needs Implementation.

.. tip:: Provides minimum needs assessment for a polygon layer containing
    counts of people affected per polygon.
"""

import logging
import os

from qgis.PyQt import QtGui, QtWidgets
from qgis.PyQt.QtCore import pyqtSlot, QSettings
from qgis.core import QgsProject, QgsFieldProxyModel, QgsMapLayerProxyModel

from safe.common.utilities import temp_dir, unique_filename
from safe.common.version import get_version
from safe.datastore.folder import Folder
from safe.definitions.fields import displaced_field, aggregation_name_field
from safe.definitions.layer_purposes import layer_purpose_aggregation
from safe.gis.vector.prepare_vector_layer import (
    clean_inasafe_fields)
from safe.gis.vector.tools import (
    create_memory_layer, copy_layer)
from safe.gui.tools.help.needs_calculator_help import needs_calculator_help
from safe.impact_function.postprocessors import run_single_post_processor
from safe.messaging import styles
from safe.processors.minimum_needs_post_processors import (
    minimum_needs_post_processors)
from safe.utilities.qgis_utilities import display_critical_message_box
from safe.utilities.resources import (
    html_footer, html_header, get_ui_class, resources_path, )
from safe.utilities.utilities import humanise_exception

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
LOGGER = logging.getLogger('InaSAFE')
FORM_CLASS = get_ui_class('needs_calculator_dialog_base.ui')


class NeedsCalculatorDialog(QtWidgets.QDialog, FORM_CLASS):
    """Dialog implementation class for the InaSAFE minimum needs calculator.
    """

    def __init__(self, parent=None):
        """Constructor for the minimum needs dialog.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr(
            'InaSAFE %s Minimum Needs Calculator' % get_version()))
        icon = resources_path('img', 'icons', 'show-minimum-needs.svg')
        self.setWindowIcon(QtGui.QIcon(icon))

        self.result_layer = None
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

        # get qgis map layer combobox object
        self.layer.setFilters(QgsMapLayerProxyModel.VectorLayer)

        # get field that represent displaced count(population)
        self.displaced.setFilters(QgsFieldProxyModel.Numeric)

        # get field that represent aggregation name
        self.aggregation_name.setFilters(QgsFieldProxyModel.String)

        # set field to the current selected layer
        self.displaced.setLayer(self.layer.currentLayer())
        self.aggregation_name.setLayer(self.layer.currentLayer())
        self.aggregation_id.setLayer(self.layer.currentLayer())

        # link map layer and field combobox
        self.layer.layerChanged.connect(self.displaced.setLayer)
        self.layer.layerChanged.connect(self.aggregation_name.setLayer)
        self.layer.layerChanged.connect(self.aggregation_id.setLayer)

        # enable/disable ok button
        self.update_button_status()
        self.displaced.fieldChanged.connect(self.update_button_status)

        # Set up things for context help
        self.help_button = self.button_box.button(
            QtWidgets.QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)

        # Fix for issue 1699 - cancel button does nothing
        cancel_button = self.button_box.button(
            QtWidgets.QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(self.reject)
        # Fix ends
        ok_button = self.button_box.button(QtWidgets.QDialogButtonBox.Ok)
        ok_button.clicked.connect(self.accept)

    def update_button_status(self):
        """Function to enable or disable the Ok button.
        """
        # enable/disable ok button
        if len(self.displaced.currentField()) > 0:
            self.button_box.button(
                QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.button_box.button(
                QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

    def minimum_needs(self, input_layer):
        """Compute minimum needs given a layer and a column containing pop.

        :param input_layer: Vector layer assumed to contain
            population counts.
        :type input_layer: QgsVectorLayer

        :returns: A tuple containing True and the vector layer if
                  post processor success. Or False and an error message
                  if something went wrong.
        :rtype: tuple(bool,QgsVectorLayer or basetring)
        """
        # Create a new layer for output layer
        output_layer = self.prepare_new_layer(input_layer)

        # count each minimum needs for every features
        for needs in minimum_needs_post_processors:
            is_success, message = run_single_post_processor(
                output_layer, needs)
            # check if post processor not running successfully
            if not is_success:
                LOGGER.debug(message)
                display_critical_message_box(
                    title=self.tr('Error while running post processor'),
                    message=message)

                return False, None

        return True, output_layer

    def prepare_new_layer(self, input_layer):
        """Prepare new layer for the output layer.

        :param input_layer: Vector layer.
        :type input_layer: QgsVectorLayer

        :return: New memory layer duplicated from input_layer.
        :rtype: QgsVectorLayer
        """
        # create memory layer
        output_layer_name = os.path.splitext(input_layer.name())[0]
        output_layer_name = unique_filename(
            prefix=('%s_minimum_needs_' % output_layer_name),
            dir='minimum_needs_calculator')
        output_layer = create_memory_layer(
            output_layer_name,
            input_layer.geometryType(),
            input_layer.crs(),
            input_layer.fields())

        # monkey patching input layer to make it work with
        # prepare vector layer function
        temp_layer = input_layer
        temp_layer.keywords = {
            'layer_purpose': layer_purpose_aggregation['key']}

        # copy features to output layer
        copy_layer(temp_layer, output_layer)

        # Monkey patching output layer to make it work with
        # minimum needs calculator
        output_layer.keywords['layer_purpose'] = (
            layer_purpose_aggregation['key'])
        output_layer.keywords['inasafe_fields'] = {
            displaced_field['key']: self.displaced.currentField()
        }
        if self.aggregation_name.currentField():
            output_layer.keywords['inasafe_fields'][
                aggregation_name_field['key']] = (
                    self.aggregation_name.currentField())

        # remove unnecessary fields & rename inasafe fields
        clean_inasafe_fields(output_layer)

        return output_layer

    def accept(self):
        """Process the layer and field and generate a new layer.

        .. note:: This is called on OK click.

        """
        # run minimum needs calculator
        try:
            success, self.result_layer = (
                self.minimum_needs(self.layer.currentLayer()))
            if not success:
                return
        except Exception as e:
            error_name, traceback = humanise_exception(e)
            message = (
                'Problem(s) occured. \n%s \nDiagnosis: \n%s' % (
                    error_name, traceback))
            display_critical_message_box(
                title=self.tr('Error while calculating minimum needs'),
                message=message)
            return

        # remove monkey patching keywords
        del self.result_layer.keywords

        # write memory layer to file system
        settings = QSettings()
        default_user_directory = settings.value(
            'inasafe/defaultUserDirectory', defaultValue='')

        if default_user_directory:
            output_directory = os.path.join(
                default_user_directory, 'minimum_needs_calculator')
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
        else:
            output_directory = temp_dir(sub_dir='minimum_needs_calculator')

        output_layer_name = os.path.split(self.result_layer.name())[1]

        # If normal filename doesn't exist, then use normal filename
        random_string_length = len(output_layer_name.split('_')[-1])
        normal_filename = output_layer_name[:-(random_string_length + 1)]
        if not os.path.exists(os.path.join(output_directory, normal_filename)):
            output_layer_name = normal_filename

        data_store = Folder(output_directory)
        data_store.default_vector_format = 'geojson'
        data_store.add_layer(self.result_layer, output_layer_name)

        self.result_layer = data_store.layer(output_layer_name)

        # noinspection PyArgumentList
        QgsProject.instance().addMapLayers(
            [data_store.layer(self.result_layer.name())])
        self.done(QtWidgets.QDialog.Accepted)

    @pyqtSlot(bool)  # prevents actions being handled twice
    def help_toggled(self, flag):
        """Show or hide the help tab in the stacked widget.

        .. versionadded: 3.2.1

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
        """Hide the usage info from the user.

        .. versionadded: 3.2.1
        """
        self.main_stacked_widget.setCurrentIndex(1)

    def show_help(self):
        """Show usage info to the user."""
        # Read the header and footer html snippets
        self.main_stacked_widget.setCurrentIndex(0)
        header = html_header()
        footer = html_footer()

        string = header

        message = needs_calculator_help()

        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)
