# coding=utf-8

"""Multi Exposure Tool."""

import logging

from PyQt4.QtCore import (
    Qt,
)
from PyQt4.QtGui import (
    QDialog,
    QComboBox,
    QLabel,
    QDialogButtonBox,
    QApplication,
    QSizePolicy,
    QTreeWidgetItem,
    QListWidgetItem,
)
from qgis.core import QgsMapLayerRegistry, QgsProject
from qgis.utils import iface

from safe import messaging as m
from safe.common.exceptions import (
    NoKeywordsFoundError,
    KeywordNotFoundError,
    MetadataReadError,
)
from safe.common.signals import send_error_message
from safe.definitions.constants import (
    inasafe_keyword_version_key,
    ANALYSIS_FAILED_BAD_INPUT,
    PREPARE_SUCCESS,
    entire_area_item_aggregation,
)
from safe.definitions.exposure import exposure_all
from safe.definitions.font import bold_font
from safe.definitions.layer_purposes import (
    layer_purpose_hazard,
    layer_purpose_exposure,
    layer_purpose_aggregation,
)
from safe.definitions.utilities import definition
from safe.gui.analysis_utilities import add_impact_layers_to_canvas
from safe.gui.gui_utilities import layer_from_combo, add_ordered_combo_item
from safe.gui.widgets.message import (
    enable_messaging,
    send_static_message,
    ready_message,
)
from safe.impact_function.multi_exposure_wrapper import (
    MultiExposureImpactFunction)
from safe.messaging import styles
from safe.utilities.gis import qgis_version
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.qt import disable_busy_cursor, enable_busy_cursor
from safe.utilities.resources import (
    get_ui_class,
)
from safe.utilities.settings import setting
from safe.utilities.utilities import (
    is_keyword_version_supported,
    get_error_message,
)

LOGGER = logging.getLogger('InaSAFE')
FORM_CLASS = get_ui_class('multi_exposure_dialog_base.ui')

INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
LOGO_ELEMENT = m.Brand()

LAYER_ORIGIN_ROLE = Qt.UserRole  # Value defined with the following dict.
FROM_CANVAS = {
    'key': 'FromCanvas',
    'name': tr('Layers from Canvas'),
}
FROM_ANALYSIS = {
    'key': 'FromAnalysis',
    'name': tr('Layers from Analysis'),
}

LAYER_PARENT_ANALYSIS_ROLE = LAYER_ORIGIN_ROLE + 1  # Name of the parent IF
LAYER_PURPOSE_KEY_OR_ID_ROLE = LAYER_PARENT_ANALYSIS_ROLE + 1  # Layer purpose


class MultiExposureDialog(QDialog, FORM_CLASS):

    """Dialog for multi exposure tool."""

    def __init__(self, parent=None):
        """Constructor for the multi exposure dialog.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget
        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.tab_widget.setCurrentIndex(0)
        self.combos_exposures = {}
        self.keyword_io = KeywordIO()
        self._create_exposure_combos()
        self._multi_exposure_if = None

        enable_messaging(self.message_viewer, self)

        # Fix for issue 1699 - cancel button does nothing
        cancel_button = self.button_box.button(QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(self.reject)
        self.ok_button = self.button_box.button(QDialogButtonBox.Ok)
        self.ok_button.clicked.connect(self.accept)
        self.validate_impact_function()
        self.tab_widget.currentChanged.connect(self._tab_changed)
        self.tree.itemSelectionChanged.connect(self._tree_selection_changed)
        self.list_layers_in_map_report.itemSelectionChanged.connect(
            self._list_selection_changed)
        self.add_layer.clicked.connect(self._add_layer_clicked)
        self.remove_layer.clicked.connect(self._remove_layer_clicked)
        self.move_up.clicked.connect(self.move_layer_up)
        self.move_down.clicked.connect(self.move_layer_down)

    def _tab_changed(self):
        """Triggered when the current tab is changed."""
        if self.tab_widget.currentWidget() == self.reportingTab:
            self._populate_reporting_tab()

    def ordered_expected_layers(self):
        """Get an ordered list of layers according to users input.

        From top to bottom in the legend:
        [
            (FromCanvas, layer id, layer name),
            (FromAnalysis, layer purpose, layer group),
            ...
        ]

        :return: An ordered list of layers
        :rtype: list
        """
        layers = []
        count = self.list_layers_in_map_report.count()
        for i in range(0, count):
            layer = self.list_layers_in_map_report.item(i)
            origin = layer.data(LAYER_ORIGIN_ROLE)
            if origin == FROM_ANALYSIS['key']:
                key = layer.data(LAYER_PURPOSE_KEY_OR_ID_ROLE)
                layers.append(
                    (FROM_ANALYSIS['key'], definition(key)['name'], key))
            else:
                layer_id = layer.data(LAYER_PURPOSE_KEY_OR_ID_ROLE)
                layers.append((FROM_CANVAS['key'], layer.text(), layer_id))
        return layers

    def _add_layer_clicked(self):
        """Add layer clicked."""
        layer = self.tree.selectedItems()[0]
        origin = layer.data(0, LAYER_ORIGIN_ROLE)
        if origin == FROM_ANALYSIS['key']:
            parent = layer.data(0, LAYER_PARENT_ANALYSIS_ROLE)
            key = layer.data(0, LAYER_PURPOSE_KEY_OR_ID_ROLE)
            item = QListWidgetItem('%s - %s' % (layer.text(0), parent))
            item.setData(LAYER_PARENT_ANALYSIS_ROLE, parent)
            item.setData(LAYER_PURPOSE_KEY_OR_ID_ROLE, key)
        else:
            item = QListWidgetItem(layer.text(0))
            layer_id = layer.data(0, LAYER_PURPOSE_KEY_OR_ID_ROLE)
            item.setData(LAYER_PURPOSE_KEY_OR_ID_ROLE, layer_id)
        item.setData(LAYER_ORIGIN_ROLE, origin)
        self.list_layers_in_map_report.addItem(item)
        self.tree.invisibleRootItem().removeChild(layer)
        self.tree.clearSelection()

    def _remove_layer_clicked(self):
        """Remove layer clicked."""
        layer = self.list_layers_in_map_report.selectedItems()[0]
        origin = layer.data(LAYER_ORIGIN_ROLE)
        if origin == FROM_ANALYSIS['key']:
            key = layer.data(LAYER_PURPOSE_KEY_OR_ID_ROLE)
            parent = layer.data(LAYER_PARENT_ANALYSIS_ROLE)
            parent_item = self.tree.findItems(
                parent, Qt.MatchContains | Qt.MatchRecursive, 0)[0]
            item = QTreeWidgetItem(parent_item, [definition(key)['name']])
            item.setData(0, LAYER_PARENT_ANALYSIS_ROLE, parent)
        else:
            parent_item = self.tree.findItems(
                FROM_CANVAS['name'],
                Qt.MatchContains | Qt.MatchRecursive, 0)[0]
            item = QTreeWidgetItem(parent_item, [layer.text()])
            layer_id = layer.data(LAYER_PURPOSE_KEY_OR_ID_ROLE)
            item.setData(0, LAYER_PURPOSE_KEY_OR_ID_ROLE, layer_id)
        item.setData(0, LAYER_ORIGIN_ROLE, origin)
        index = self.list_layers_in_map_report.indexFromItem(layer)
        self.list_layers_in_map_report.takeItem(index.row())
        self.list_layers_in_map_report.clearSelection()

    def move_layer_up(self):
        """Move the layer up."""
        layer = self.list_layers_in_map_report.selectedItems()[0]
        index = self.list_layers_in_map_report.indexFromItem(layer).row()
        item = self.list_layers_in_map_report.takeItem(index)
        self.list_layers_in_map_report.insertItem(index - 1, item)
        self.list_layers_in_map_report.item(index - 1).setSelected(True)

    def move_layer_down(self):
        """Move the layer down."""
        layer = self.list_layers_in_map_report.selectedItems()[0]
        index = self.list_layers_in_map_report.indexFromItem(layer).row()
        item = self.list_layers_in_map_report.takeItem(index)
        self.list_layers_in_map_report.insertItem(index + 1, item)
        self.list_layers_in_map_report.item(index + 1).setSelected(True)

    def _list_selection_changed(self):
        """Selection has changed in the list."""
        items = self.list_layers_in_map_report.selectedItems()
        self.remove_layer.setEnabled(len(items) >= 1)
        if len(items) == 1 and self.list_layers_in_map_report.count() >= 2:
            index = self.list_layers_in_map_report.indexFromItem(items[0])
            index = index.row()
            if index == 0:
                self.move_up.setEnabled(False)
                self.move_down.setEnabled(True)
            elif index == self.list_layers_in_map_report.count() - 1:
                self.move_up.setEnabled(True)
                self.move_down.setEnabled(False)
            else:
                self.move_up.setEnabled(True)
                self.move_down.setEnabled(True)
        else:
            self.move_up.setEnabled(False)
            self.move_down.setEnabled(False)

    def _tree_selection_changed(self):
        """Selection has changed in the tree."""
        self.add_layer.setEnabled(len(self.tree.selectedItems()) >= 1)

    def _populate_reporting_tab(self):
        """Populate trees about layers."""
        self.tree.clear()
        self.add_layer.setEnabled(False)
        self.remove_layer.setEnabled(False)
        self.move_up.setEnabled(False)
        self.move_down.setEnabled(False)
        self.tree.setColumnCount(1)
        self.tree.setRootIsDecorated(False)
        self.tree.setHeaderHidden(True)

        analysis_branch = QTreeWidgetItem(
            self.tree.invisibleRootItem(), [FROM_ANALYSIS['name']])
        analysis_branch.setFont(0, bold_font)
        analysis_branch.setExpanded(True)
        analysis_branch.setFlags(Qt.ItemIsEnabled)

        if self._multi_exposure_if:
            expected = self._multi_exposure_if.output_layers_expected()
            for group, layers in expected.iteritems():
                group_branch = QTreeWidgetItem(analysis_branch, [group])
                group_branch.setFont(0, bold_font)
                group_branch.setExpanded(True)
                group_branch.setFlags(Qt.ItemIsEnabled)

                for layer in layers:
                    layer = definition(layer)
                    if layer.get('allowed_geometries', None):
                        item = QTreeWidgetItem(
                            group_branch, [layer.get('name')])
                        item.setData(
                            0, LAYER_ORIGIN_ROLE, FROM_ANALYSIS['key'])
                        item.setData(0, LAYER_PARENT_ANALYSIS_ROLE, group)
                        item.setData(
                            0, LAYER_PURPOSE_KEY_OR_ID_ROLE, layer['key'])
                        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

        canvas_branch = QTreeWidgetItem(
            self.tree.invisibleRootItem(), [FROM_CANVAS['name']])
        canvas_branch.setFont(0, bold_font)
        canvas_branch.setExpanded(True)
        canvas_branch.setFlags(Qt.ItemIsEnabled)

        # List layers from the canvas
        loaded_layers = QgsMapLayerRegistry.instance().mapLayers().values()
        canvas_layers = iface.mapCanvas().layers()
        flag = setting('visibleLayersOnlyFlag', True, bool)
        for loaded_layer in loaded_layers:
            if flag and loaded_layer not in canvas_layers:
                continue

            if qgis_version() >= 21800:
                title = loaded_layer.name()
            else:
                # QGIS 2.14
                title = loaded_layer.layerName()
            item = QTreeWidgetItem(canvas_branch, [title])
            item.setData(0, LAYER_ORIGIN_ROLE, FROM_CANVAS['key'])
            item.setData(0, LAYER_PURPOSE_KEY_OR_ID_ROLE, loaded_layer.id())
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

        self.tree.resizeColumnToContents(0)

    def _create_exposure_combos(self):
        """Create one combobox for each exposure and insert them in the UI."""
        # Map registry may be invalid if QGIS is shutting down
        registry = QgsMapLayerRegistry.instance()
        canvas_layers = iface.mapCanvas().layers()
        # MapLayers returns a QMap<QString id, QgsMapLayer layer>
        layers = registry.mapLayers().values()

        show_only_visible_layers = setting('visibleLayersOnlyFlag', True, bool)

        # For issue #618
        if len(layers) == 0:
            # self.message_viewer.setHtml(getting_started_message())
            return

        for one_exposure in exposure_all:
            label = QLabel(one_exposure['name'])
            combo = QComboBox()
            combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            combo.addItem(tr('Do not use'), None)
            self.form_layout.addRow(label, combo)
            self.combos_exposures[one_exposure['key']] = combo

        for layer in layers:
            if (show_only_visible_layers and
                    (layer not in canvas_layers)):
                continue

            try:
                layer_purpose = self.keyword_io.read_keywords(
                    layer, 'layer_purpose')
                keyword_version = str(self.keyword_io.read_keywords(
                    layer, inasafe_keyword_version_key))
                if not is_keyword_version_supported(keyword_version):
                    continue
            except:  # pylint: disable=W0702
                # continue ignoring this layer
                continue

            # See if there is a title for this layer, if not,
            # fallback to the layer's filename
            # noinspection PyBroadException
            try:
                title = self.keyword_io.read_keywords(layer, 'title')
            except (NoKeywordsFoundError,
                    KeywordNotFoundError, MetadataReadError):
                # Skip if there are no keywords at all, or missing keyword
                continue
            except:  # pylint: disable=W0702
                pass
            else:
                # Lookup internationalised title if available
                title = self.tr(title)

            # Register title with layer
            set_layer_from_title = setting(
                'set_layer_from_title_flag', True, bool)
            if title and set_layer_from_title:
                if qgis_version() >= 21800:
                    layer.setName(title)
                else:
                    # QGIS 2.14
                    layer.setLayerName(title)

            source = layer.id()

            if layer_purpose == layer_purpose_hazard['key']:
                add_ordered_combo_item(
                    self.cbx_hazard, title, source)
            elif layer_purpose == layer_purpose_aggregation['key']:
                add_ordered_combo_item(
                    self.cbx_aggregation, title, source)
            elif layer_purpose == layer_purpose_exposure['key']:

                # fetching the exposure
                try:
                    exposure_type = self.keyword_io.read_keywords(
                        layer, layer_purpose_exposure['key'])
                except:  # pylint: disable=W0702
                    # continue ignoring this layer
                    continue

                for key, combo in self.combos_exposures.iteritems():
                    if key == exposure_type:
                        add_ordered_combo_item(
                            combo, title, source)

        self.cbx_aggregation.addItem(entire_area_item_aggregation, None)
        for combo in self.combos_exposures.itervalues():
            combo.currentIndexChanged.connect(self.validate_impact_function)

    def progress_callback(self, current_value, maximum_value, message=None):
        """GUI based callback implementation for showing progress.

        :param current_value: Current progress.
        :type current_value: int

        :param maximum_value: Maximum range (point at which task is complete.
        :type maximum_value: int

        :param message: Optional message dictionary to containing content
            we can display to the user. See safe.definitions.analysis_steps
            for an example of the expected format
        :type message: dict
        """
        report = m.Message()
        report.add(LOGO_ELEMENT)
        report.add(m.Heading(
            self.tr('Analysis status'), **INFO_STYLE))
        if message is not None:
            report.add(m.ImportantText(message['name']))
            report.add(m.Paragraph(message['description']))
        report.add(
            self._multi_exposure_if
                .current_impact_function.performance_log_message())
        send_static_message(self, report)
        self.progress_bar.setMaximum(maximum_value)
        self.progress_bar.setValue(current_value)
        QApplication.processEvents()

    def validate_impact_function(self):
        """Check validity of the current impact function."""
        # Always set it to False
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

        use_selected_only = setting('useSelectedFeaturesOnly', True, bool)

        for combo in self.combos_exposures.itervalues():
            # if combo.count() > 1 and self.cbx_hazard.count():
            #     self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
            if combo.count() == 1:
                combo.setEnabled(False)

        hazard = layer_from_combo(self.cbx_hazard)
        aggregation = layer_from_combo(self.cbx_aggregation)
        exposures = []
        for combo in self.combos_exposures.itervalues():
            exposures.append(layer_from_combo(combo))
        exposures = [layer for layer in exposures if layer]

        multi_exposure_if = MultiExposureImpactFunction()
        multi_exposure_if.hazard = hazard
        multi_exposure_if.exposures = exposures
        if aggregation:
            multi_exposure_if.use_selected_features_only = use_selected_only
            multi_exposure_if.aggregation = aggregation
        else:
            # TODO
            pass

        status, message = multi_exposure_if.prepare()
        if status == PREPARE_SUCCESS:
            self._multi_exposure_if = multi_exposure_if
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
            send_static_message(self, ready_message())
            self.tab_widget.setTabEnabled(1, True)
            return
        else:
            self.tab_widget.setTabEnabled(1, False)
            disable_busy_cursor()
            LOGGER.info(
                'The impact function could not run because of the inputs.')
            send_error_message(self, message)
            LOGGER.info(message.to_text())

        self._multi_exposure_if = None
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

    def accept(self):
        """Launch the multi exposure analysis."""
        enable_busy_cursor()
        try:
            hazard = layer_from_combo(self.cbx_hazard)
            aggregation = layer_from_combo(self.cbx_aggregation)
            exposures = []
            for combo in self.combos_exposures.itervalues():
                exposures.append(layer_from_combo(combo))
            exposures = [layer for layer in exposures if layer]

            self._multi_exposure_if = MultiExposureImpactFunction()
            self._multi_exposure_if.hazard = hazard
            self._multi_exposure_if.exposures = exposures
            self._multi_exposure_if.aggregation = aggregation
            self._multi_exposure_if.debug = False
            self._multi_exposure_if.callback = self.progress_callback

            status, message = self._multi_exposure_if.prepare()
            # self.assertEqual(code, PREPARE_MULTI_SUCCESS, message)
            if status == ANALYSIS_FAILED_BAD_INPUT:
                self.hide_busy()
                LOGGER.info(
                    'The impact function could not run because of the inputs.')
                send_error_message(self, message)
                LOGGER.info(message.to_text())
            else:
                code, message = self._multi_exposure_if.run()
                # self.assertEqual(code, ANALYSIS_MULTI_SUCCESS, message)

                root = QgsProject.instance().layerTreeRoot()
                group_analysis = root.insertGroup(
                    0, self._multi_exposure_if.name)
                group_analysis.setVisible(Qt.Checked)

                for layer in self._multi_exposure_if.outputs:
                    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
                    layer_node = group_analysis.addLayer(layer)
                    layer_node.setVisible(Qt.Unchecked)

                for analysis in self._multi_exposure_if.impact_functions:
                    detailed_group = group_analysis.insertGroup(
                        0, analysis.name)
                    detailed_group.setVisible(Qt.Checked)
                    add_impact_layers_to_canvas(analysis, group=detailed_group)
                self.done(QDialog.Accepted)

        except Exception as e:
            error_message = get_error_message(e)
            send_error_message(self, error_message)
            LOGGER.exception(e)
            LOGGER.debug(error_message.to_text())
        finally:
            disable_busy_cursor()

    def reject(self):
        """Redefinition of the reject method."""
        super(MultiExposureDialog, self).reject()
