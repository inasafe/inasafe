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
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer
from PyQt4 import QtGui, QtCore

from PyQt4.QtCore import pyqtSignature, pyqtSlot

from safe.common.version import get_version
from safe.storage.core import read_layer as safe_read_layer
from safe.storage.vector import Vector
from safe.utilities.gis import is_point_layer, is_polygon_layer
from safe.utilities.resources import html_footer, html_header, get_ui_class
from safe.utilities.utilities import add_ordered_combo_item
from safe.impact_functions.core import evacuated_population_weekly_needs
from safe import messaging as m
from safe.messaging import styles
from safe.gui.tools.help.needs_calculator_help import needs_calculator_help

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
        self.polygon_layers_to_combo()

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

    def minimum_needs(self, input_layer, population_name):
        """Compute minimum needs given a layer and a column containing pop.

        :param input_layer: InaSAFE layer object assumed to contain
            population counts
        :type input_layer: read_layer

        :param population_name: Attribute name that holds population count
        :type population_name: str

        :returns: Layer with attributes for minimum needs as per Perka 7
        :rtype: read_layer
        """

        all_attributes = []
        for attributes in input_layer.get_data():
            # Get population count
            population = attributes[population_name]
            # Clean up and turn into integer
            if population in ['-', None]:
                displaced = 0
            else:
                if isinstance(population, basestring):
                    population = str(population).replace(',', '')

                try:
                    displaced = int(population)
                except ValueError:
                    # noinspection PyTypeChecker,PyArgumentList
                    QtGui.QMessageBox.information(
                        None,
                        self.tr('Format error'),
                        self.tr(
                            'Please change the value of %1 in attribute '
                            '%s to integer format') % (
                                population, population_name))
                    raise ValueError

            # Calculate estimated needs based on BNPB Perka 7/2008
            # minimum needs
            # weekly_needs = {
            #     'rice': int(ceil(population * min_rice)),
            #     'drinking_water': int(ceil(population * min_drinking_water)),
            #     'water': int(ceil(population * min_water)),
            #     'family_kits': int(ceil(population * min_family_kits)),
            #     'toilets': int(ceil(population * min_toilets))}

            # Add to attributes
            weekly_needs = evacuated_population_weekly_needs(displaced)

            # Record attributes for this feature
            all_attributes.append(weekly_needs)

        output_layer = Vector(
            geometry=input_layer.get_geometry(),
            data=all_attributes,
            projection=input_layer.get_projection())
        return output_layer

    def polygon_layers_to_combo(self):
        """Populate the combo with all polygon layers loaded in QGIS."""

        # noinspection PyArgumentList
        registry = QgsMapLayerRegistry.instance()
        layers = registry.mapLayers().values()
        found_flag = False
        for layer in layers:
            name = layer.name()
            source = layer.id()
            # check if layer is a vector polygon layer
            if is_polygon_layer(layer) or is_point_layer(layer):
                found_flag = True
                add_ordered_combo_item(self.cboPolygonLayers, name, source)
        # Now disable the run button if no suitable layers were found
        # see #2206
        ok_button = self.button_box.button(QtGui.QDialogButtonBox.Ok)
        if found_flag:
            self.cboPolygonLayers.setCurrentIndex(0)
            ok_button.setEnabled(True)
        else:
            ok_button.setEnabled(False)

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('int')
    def on_cboPolygonLayers_currentIndexChanged(self, index):
        """Automatic slot executed when the layer is changed to update fields.

        :param index: Passed by the signal that triggers this slot.
        :type index: int
        """
        layer_id = self.cboPolygonLayers.itemData(
            index, QtCore.Qt.UserRole)
        # noinspection PyArgumentList
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        fields = layer.pendingFields()
        self.cboFields.clear()
        has_fields = False
        for field in fields:
            LOGGER.info(field.typeName())
            # TODO exclude dates too? TS
            if field.typeName() != 'String':
                has_fields = True
                add_ordered_combo_item(
                    self.cboFields, field.name(), field.name())

        # Now disable the run button if no suitable fields were found
        # see #2206
        ok_button = self.button_box.button(QtGui.QDialogButtonBox.Ok)
        if not has_fields:
            ok_button.setEnabled(False)
        else:
            ok_button.setEnabled(True)

    def accept(self):
        """Process the layer and field and generate a new layer.

        .. note:: This is called on OK click.

        """
        index = self.cboFields.currentIndex()
        field_name = self.cboFields.itemData(
            index, QtCore.Qt.UserRole)

        index = self.cboPolygonLayers.currentIndex()
        layer_id = self.cboPolygonLayers.itemData(
            index, QtCore.Qt.UserRole)
        # noinspection PyArgumentList
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)

        file_name = layer.source()

        input_layer = safe_read_layer(file_name)

        try:
            output_layer = self.minimum_needs(input_layer, field_name)
        except ValueError:
            return

        new_file = file_name[:-4] + '_perka7' + '.shp'

        output_layer.write_to_file(new_file)

        new_layer = QgsVectorLayer(new_file, 'Minimum Needs', 'ogr')
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers([new_layer])
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
