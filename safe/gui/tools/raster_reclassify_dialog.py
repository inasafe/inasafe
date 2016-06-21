# coding=utf-8
import logging

from PyQt4 import (QtGui, QtCore)
from PyQt4.QtCore import (pyqtSlot, pyqtSignature)

from PyQt4.QtGui import (QDialog, QLabel)
from qgis.core import (
    QgsMapLayerRegistry,
    QgsRasterLayer,
    QgsVectorLayer)

from safe.gis.reclassify_gdal import reclassify_polygonize
from safe.gui.tools.help.raster_reclassify_help import raster_reclassify_help
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.resources import get_ui_class, html_header, html_footer
from safe.utilities.utilities import add_ordered_combo_item, \
    ranges_according_thresholds_list
from safe.impact_functions.registry import Registry
from safe_extras.parameters.qt_widgets.parameter_container import \
    ParameterContainer


LOGGER = logging.getLogger('InaSAFE')
FORM_CLASS = get_ui_class('raster_reclassify_dialog_base.ui')

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '5/30/16'


class RasterReclassifyDialog(QDialog, FORM_CLASS):

    def __init__(self, parent=None, iface=None):
        """Constructor for Raster Reclassification to Vector Polygon.

        .. versionadded: 3.4

        :param parent: Optional widget to use as parent
        :type parent: QWidget

        :param iface: An instance of QGisInterface
        :type iface: QGisInterface
        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        self.setWindowTitle(self.tr('Raster Reclassification'))

        self.iface = iface

        self.if_registry = Registry()
        self.keyword_io = KeywordIO()

        # populate raster input
        self.cbo_raster_input.clear()
        registry = QgsMapLayerRegistry.instance()
        # MapLayers returns a QMap<QString id, QgsMapLayer layer>
        layers = registry.mapLayers().values()
        for layer in layers:
            try:
                name = layer.name()
                source = layer.id()
                layer_purpose = self.keyword_io.read_keywords(
                    layer, 'layer_purpose')
                if (isinstance(layer, QgsRasterLayer) and
                            layer_purpose == 'hazard'):
                    add_ordered_combo_item(
                        self.cbo_raster_input, self.tr(name), source)

            except Exception as e:
                raise e

        # self.input_list_parameter = InputListParameter()
        # self.input_list_parameter.name = 'Thresholds'
        # self.input_list_parameter.description = (
        #     'List of thresholds of values used in reclassification.')
        # self.input_list_parameter.help_text = 'list of thresholds used'
        # self.input_list_parameter.maximum_item_count = 100
        # self.input_list_parameter.minimum_item_count = 1
        # self.input_list_parameter.element_type = float
        # self.input_list_parameter.value = [0.0, 1.0]
        # self.input_list_parameter.ordering = \
        #     InputListParameter.AscendingOrder
        # self.thresholds_widget = InputListParameterWidget(
        #     self.input_list_parameter)

        # self.threshold_editor.layout().addWidget(self.thresholds_widget)

        # Set up context help
        self.help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        self.ok_button = self.button_box.button(QtGui.QDialogButtonBox.Ok)
        # self.cancel_button = self.button_box.button(
        #     QtGui.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)
        # adapt layer changed
        self.cbo_raster_input.currentIndexChanged.connect(self.raster_changed)
        self.raster_changed(self.cbo_raster_input.currentIndex())

    # noinspection PyPep8Naming
    @pyqtSlot(int)
    def raster_changed(self, index):
        """Executed when raster is changed

        :param index: index of the selected raster
        :return:
        """
        registry = QgsMapLayerRegistry.instance()
        layer_id = self.cbo_raster_input.itemData(
            index, QtCore.Qt.UserRole)
        layer = registry.mapLayer(layer_id)
        layer_purpose = self.keyword_io.read_keywords(layer, 'layer_purpose')
        if layer_purpose == 'hazard':
            impact_function = self.if_registry.filter_by_hazard(
                self.if_registry.impact_functions,
                self.keyword_io.read_keywords(layer)
            )
        elif layer_purpose == 'exposure':
            impact_function = self.if_registry.filter_by_exposure(
                self.if_registry.impact_functions,
                self.keyword_io.read_keywords(layer)
            )
        else:
            impact_function = []

        if impact_function:
            parameters_dict = impact_function[0].parameters
            threshold_list = []
            for param_key, param_value in parameters_dict.iteritems():
                if 'threshold' in param_key:
                    threshold_list.append(param_value)

            if threshold_list:
                param_container = ParameterContainer(threshold_list)
                param_container.setup_ui(must_scroll=False)

                self.threshold_editor.layout().addWidget(param_container)
            else:
                empty_threshold_label = QLabel(
                    self.tr('No threshold configuration available '
                            'for this layer'))
                self.threshold_editor.layout().addWidget(
                    empty_threshold_label)

    @pyqtSlot()
    @pyqtSignature('bool')  # prevents actions being handled twice
    def help_toggled(self, flag):
        """Show or hide the help tab in the stacked widget.

        .. versionadded: 3.4

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

        .. versionadded:: 3.4
        """
        self.main_stacked_widget.setCurrentIndex(1)

    def show_help(self):
        """Show usage info to the user.

        .. versionadded: 3.4
        """
        # Read the header and footer html snippets
        self.main_stacked_widget.setCurrentIndex(0)
        header = html_header()
        footer = html_footer()

        string = header

        message = raster_reclassify_help()
        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)

    def validate(self):
        if self.cbo_raster_input.currentIndex() < 0:
            self.ok_button.setEnabled(False)
        else:
            self.ok_button.setEnabled(True)

    def accept(self):
        """Do raster reclassification and display it in QGIS

        .. versionadded: 3.4

        :return:
        """
        registry = QgsMapLayerRegistry.instance()
        try:
            index = self.cbo_raster_input.currentIndex()
            layer_id = self.cbo_raster_input.itemData(
                index, QtCore.Qt.UserRole)
            layer = registry.mapLayer(layer_id)
            class_attribute = 'class'
            # extract thresholds
            thresholds_list = self.thresholds_widget.get_parameter().value
            thresholds_list.append(None)
            ranges = ranges_according_thresholds_list(thresholds_list)

            path = reclassify_polygonize(
                layer.source(), ranges, name_field=class_attribute)

            # load layer to QGIS
            title = self.tr('%s classified') % self.tr(layer.name())
            layer = QgsVectorLayer(path, title, 'ogr')
            registry.addMapLayer(layer)
        except Exception as e:
            LOGGER.exception(e)

        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.disable_busy_cursor()
        self.done(QDialog.Accepted)

    @staticmethod
    def disable_busy_cursor():
        """Disable the hourglass cursor.

        TODO: this is duplicated from dock.py
        """
        while QtGui.qApp.overrideCursor() is not None and \
                        QtGui.qApp.overrideCursor().shape() == \
                        QtCore.Qt.WaitCursor:
            QtGui.qApp.restoreOverrideCursor()

    def reject(self):
        """Redefinition of the reject() method.

        It will call the super method.
        """
        # add our own logic here...

        super(RasterReclassifyDialog, self).reject()
