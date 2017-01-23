# coding=utf-8
"""**Minimum Needs Implementation.**

.. tip:: Provides minimum needs assessment for a polygon layer containing
    counts of people affected per polygon.

"""

__author__ = 'tim@kartoza.com, ole.moller.nielsen@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '20/1/2013'
__license__ = "GPL"
__copyright__ = 'Copyright 2013, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import logging
from qgis.core import QgsMapLayerRegistry
from qgis.gui import (
    QgsFieldComboBox,
    QgsMapLayerComboBox,
    QgsMapLayerProxyModel,
    QgsFieldProxyModel)
from PyQt4 import QtGui

from PyQt4.QtCore import pyqtSignature, pyqtSlot

from safe.common.version import get_version
from safe.utilities.resources import html_footer, html_header, get_ui_class
from safe.messaging import styles
from safe.gui.tools.help.needs_calculator_help import needs_calculator_help
from safe.impact_function.postprocessors import run_single_post_processor
from safe.definitions.post_processors import minimum_needs_post_processors
from safe.definitions.fields import displaced_field, aggregation_name_field
from safe.definitions.layer_purposes import layer_purpose_aggregation
from safe.gis.vector.tools import (
    create_memory_layer, copy_layer)
from safe.gis.vector.prepare_vector_layer import (
    rename_remove_inasafe_fields)

INFO_STYLE = styles.INFO_STYLE
LOGGER = logging.getLogger('InaSAFE')
FORM_CLASS = get_ui_class('needs_calculator_dialog_base.ui')


class NeedsCalculatorDialog(QtGui.QDialog, FORM_CLASS):
    """Dialog implementation class for the InaSAFE minimum needs calculator.
    """

    def __init__(self, parent=None):
        """Constructor for the minimum needs dialog.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget
        """
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr(
            'InaSAFE %s Minimum Needs Calculator' % get_version()))

        self.button_box.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

        # get qgis map layer combobox object
        self.layer = QgsMapLayerComboBox()
        self.layer.setFilters(QgsMapLayerProxyModel.VectorLayer)

        # get field that represent displaced count(population)
        self.displaced = QgsFieldComboBox()
        self.displaced.setFilters(QgsFieldProxyModel.Numeric)

        # get field that represent aggregation name
        self.aggregation_name = QgsFieldComboBox()
        self.aggregation_name.setFilters(QgsFieldProxyModel.String)

        # get field that represent aggregation id
        self.aggregation_id = QgsFieldComboBox()

        # add Qgis combo box to window
        self.gridLayout_2.addWidget(self.layer, 3, 1)
        self.gridLayout_2.addWidget(self.displaced, 5, 1)
        self.gridLayout_2.addWidget(self.aggregation_name, 7, 1)
        self.gridLayout_2.addWidget(self.aggregation_id, 9, 1)

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

    def update_button_status(self):
        """
        """
        # enable/disable ok button
        if len(self.displaced.currentField()) > 0:
            self.button_box.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.button_box.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

    def minimum_needs(self, input_layer):
        """Compute minimum needs given a layer and a column containing pop.

        :param input_layer: Vector layer assumed to contain
            population counts
        :type input_layer: QgsVectorLayer

        :returns: Layer with attributes for minimum needs as per Perka 7
        :rtype: read_layer
        """
        # count each minimum needs for every features
        for needs in minimum_needs_post_processors:
            run_single_post_processor(input_layer, needs)

    def prepare_new_layer(self, input_layer):
        """Prepare new layer for the output layer.

        :param input_layer: Vector layer
        :type input_layer: QgsVectorLayer

        :return: New memory layer duplicated from input_layer
        :rtype: QgsVectorLayer
        """
        # create memory layer
        output_layer = (
            '%s_minimum_needs' % input_layer.name())
        output_layer = create_memory_layer(
            output_layer,
            input_layer.geometryType(),
            input_layer.crs(),
            input_layer.fields())

        # monkey patching input layer to make it work with
        # prepare vector layer function
        temp_layer = input_layer
        temp_layer.keywords = {'layer_purpose':
                                   layer_purpose_aggregation['key']}

        # add keywords to output layer
        copy_layer(temp_layer, output_layer)

        return output_layer

    def accept(self):
        """Process the layer and field and generate a new layer.

        .. note:: This is called on OK click.

        """
        # Create a new layer for output layer
        output_layer = self.prepare_new_layer(self.layer.currentLayer())

        # Monkey patching output layer to make it work with
        # minimum needs calculator
        output_layer.keywords['layer_purpose'] = (
            layer_purpose_aggregation['key'])
        output_layer.keywords['inasafe_fields'] = (
            {displaced_field['key']: self.displaced.currentField(),
             aggregation_name_field['key']:
                 self.aggregation_name.currentField()})

        # remove unnecessary fields & rename inasafe fields
        rename_remove_inasafe_fields(output_layer)

        try:
            self.minimum_needs(output_layer)
        except Exception as e:
            LOGGER.debug(e)
            return

        # write layer to geopackage file

        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([output_layer])
        self.done(QtGui.QDialog.Accepted)

    @pyqtSlot()
    @pyqtSignature('bool')  # prevents actions being handled twice
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
