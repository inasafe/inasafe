# coding=utf-8

"""Multi Exposure Tool."""


import logging
from collections import OrderedDict

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog,
    QComboBox,
    QLabel,
    QSizePolicy,
    QTreeWidgetItem,
    QListWidgetItem
)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import QgsProject, QgsApplication
from qgis.utils import iface as iface_object

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
    ANALYSIS_FAILED_BAD_CODE,
    entire_area_item_aggregation,
    MULTI_EXPOSURE_ANALYSIS_FLAG,
)
from safe.definitions.exposure import exposure_all
from safe.definitions.font import bold_font
from safe.definitions.layer_purposes import (
    layer_purpose_hazard,
    layer_purpose_exposure,
    layer_purpose_aggregation,
)
from safe.definitions.reports.components import (
    standard_impact_report_metadata_html,
    standard_multi_exposure_impact_report_metadata_html)
from safe.definitions.utilities import definition
from safe.gis.tools import full_layer_uri
from safe.gui.analysis_utilities import (
    add_impact_layers_to_canvas,
    add_layers_to_canvas_with_custom_orders,
)
from safe.gui.gui_utilities import layer_from_combo, add_ordered_combo_item
from safe.gui.widgets.message import (
    enable_messaging,
    send_static_message,
    ready_message,
)
from safe.impact_function.impact_function_utilities import (
    LAYER_ORIGIN_ROLE,
    FROM_CANVAS,
    FROM_ANALYSIS,
    LAYER_PARENT_ANALYSIS_ROLE,
    LAYER_PURPOSE_KEY_OR_ID_ROLE,
)
from safe.impact_function.multi_exposure_wrapper import (
    MultiExposureImpactFunction)
from safe.messaging import styles
from safe.report.impact_report import ImpactReport
from safe.utilities.extent import Extent
from safe.utilities.gis import qgis_version, layer_icon
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.qgis_utilities import display_warning_message_bar
from safe.utilities.qt import disable_busy_cursor, enable_busy_cursor
from safe.utilities.resources import (
    get_ui_class, resources_path,
)
from safe.utilities.settings import setting
from safe.utilities.utilities import (
    is_keyword_version_supported,
    basestring_to_message,
    get_error_message,
)

LOGGER = logging.getLogger('InaSAFE')
FORM_CLASS = get_ui_class('multi_exposure_dialog_base.ui')

INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
LOGO_ELEMENT = m.Brand()


class MultiExposureDialog(QDialog, FORM_CLASS):

    """Dialog for multi exposure tool."""

    def __init__(self, parent=None, iface=iface_object):
        """Constructor for the multi exposure dialog.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget

        :param iface: An instance of QgisInterface
        :type iface: QgisInterface
        """
        QDialog.__init__(self, parent)
        self.use_selected_only = setting(
            'useSelectedFeaturesOnly', expected_type=bool)
        self.parent = parent
        self.iface = iface
        self.setupUi(self)
        icon = resources_path('img', 'icons', 'show-multi-exposure.svg')
        self.setWindowIcon(QIcon(icon))
        self.tab_widget.setCurrentIndex(0)
        self.combos_exposures = OrderedDict()
        self.keyword_io = KeywordIO()
        self._create_exposure_combos()
        self._multi_exposure_if = None
        self._extent = Extent(iface)
        self._extent.show_rubber_bands = setting(
            'showRubberBands', False, bool)

        enable_messaging(self.message_viewer, self)

        self.btn_back.clicked.connect(self.back_clicked)
        self.btn_next.clicked.connect(self.next_clicked)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_run.clicked.connect(self.accept)
        self.validate_impact_function()
        self.tab_widget.currentChanged.connect(self._tab_changed)
        self.tree.itemSelectionChanged.connect(self._tree_selection_changed)
        self.list_layers_in_map_report.itemSelectionChanged.connect(
            self._list_selection_changed)
        self.add_layer.clicked.connect(self._add_layer_clicked)
        self.remove_layer.clicked.connect(self._remove_layer_clicked)
        self.move_up.clicked.connect(self.move_layer_up)
        self.move_down.clicked.connect(self.move_layer_down)
        self.cbx_hazard.currentIndexChanged.connect(
            self.validate_impact_function)
        self.cbx_aggregation.currentIndexChanged.connect(
            self.validate_impact_function)

        # Keep track of the current panel
        self._current_index = 0
        self.tab_widget.setCurrentIndex(self._current_index)

    def _tab_changed(self):
        """Triggered when the current tab is changed."""
        current = self.tab_widget.currentWidget()
        if current == self.analysisTab:
            self.btn_back.setEnabled(False)
            self.btn_next.setEnabled(True)
        elif current == self.reportingTab:
            if self._current_index == 0:
                # Only if the user is coming from the first tab
                self._populate_reporting_tab()
            self.reporting_options_layout.setEnabled(
                self._multi_exposure_if is not None)
            self.btn_back.setEnabled(True)
            self.btn_next.setEnabled(True)
        else:
            self.btn_back.setEnabled(True)
            self.btn_next.setEnabled(False)
        self._current_index = current

    def back_clicked(self):
        """Back button clicked."""
        self.tab_widget.setCurrentIndex(self.tab_widget.currentIndex() - 1)

    def next_clicked(self):
        """Next button clicked."""
        self.tab_widget.setCurrentIndex(self.tab_widget.currentIndex() + 1)

    def ordered_expected_layers(self):
        """Get an ordered list of layers according to users input.

        From top to bottom in the legend:
        [
            ('FromCanvas', layer name, full layer URI, QML),
            ('FromAnalysis', layer purpose, layer group, None),
            ...
        ]

        The full layer URI is coming from our helper.

        :return: An ordered list of layers following a structure.
        :rtype: list
        """
        registry = QgsProject.instance()
        layers = []
        count = self.list_layers_in_map_report.count()
        for i in range(count):
            layer = self.list_layers_in_map_report.item(i)
            origin = layer.data(LAYER_ORIGIN_ROLE)
            if origin == FROM_ANALYSIS['key']:
                key = layer.data(LAYER_PURPOSE_KEY_OR_ID_ROLE)
                parent = layer.data(LAYER_PARENT_ANALYSIS_ROLE)
                layers.append((
                    FROM_ANALYSIS['key'],
                    key,
                    parent,
                    None
                ))
            else:
                layer_id = layer.data(LAYER_PURPOSE_KEY_OR_ID_ROLE)
                layer = registry.mapLayer(layer_id)
                style_document = QDomDocument()
                error = ''
                layer.exportNamedStyle(style_document, error)

                layers.append((
                    FROM_CANVAS['key'],
                    layer.name(),
                    full_layer_uri(layer),
                    style_document.toString()
                ))
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
            for group, layers in list(expected.items()):
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
        loaded_layers = list(QgsProject.instance().mapLayers().values())
        canvas_layers = self.iface.mapCanvas().layers()
        flag = setting('visibleLayersOnlyFlag', expected_type=bool)
        for loaded_layer in loaded_layers:
            if flag and loaded_layer not in canvas_layers:
                continue

            title = loaded_layer.name()
            item = QTreeWidgetItem(canvas_branch, [title])
            item.setData(0, LAYER_ORIGIN_ROLE, FROM_CANVAS['key'])
            item.setData(0, LAYER_PURPOSE_KEY_OR_ID_ROLE, loaded_layer.id())
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

        self.tree.resizeColumnToContents(0)

    def _create_exposure_combos(self):
        """Create one combobox for each exposure and insert them in the UI."""
        # Map registry may be invalid if QGIS is shutting down
        project = QgsProject.instance()
        canvas_layers = self.iface.mapCanvas().layers()
        # MapLayers returns a QMap<QString id, QgsMapLayer layer>
        layers = list(project.mapLayers().values())
        # Sort by name for tests
        layers.sort(key=lambda x: x.name())

        show_only_visible_layers = setting(
            'visibleLayersOnlyFlag', expected_type=bool)

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
            except BaseException:  # pylint: disable=W0702
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
            except BaseException:  # pylint: disable=W0702
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

            icon = layer_icon(layer)

            if layer_purpose == layer_purpose_hazard['key']:
                add_ordered_combo_item(
                    self.cbx_hazard, title, source, icon=icon)
            elif layer_purpose == layer_purpose_aggregation['key']:
                if self.use_selected_only:
                    count_selected = layer.selectedFeatureCount()
                    if count_selected > 0:
                        add_ordered_combo_item(
                            self.cbx_aggregation,
                            title,
                            source,
                            count_selected,
                            icon=icon
                        )
                    else:
                        add_ordered_combo_item(
                            self.cbx_aggregation, title, source, None, icon)
                else:
                    add_ordered_combo_item(
                        self.cbx_aggregation, title, source, None, icon)
            elif layer_purpose == layer_purpose_exposure['key']:

                # fetching the exposure
                try:
                    exposure_type = self.keyword_io.read_keywords(
                        layer, layer_purpose_exposure['key'])
                except BaseException:  # pylint: disable=W0702
                    # continue ignoring this layer
                    continue

                for key, combo in list(self.combos_exposures.items()):
                    if key == exposure_type:
                        add_ordered_combo_item(
                            combo, title, source, icon=icon)

        self.cbx_aggregation.addItem(entire_area_item_aggregation, None)
        for combo in list(self.combos_exposures.values()):
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
        QgsApplication.processEvents()

    def validate_impact_function(self):
        """Check validity of the current impact function."""
        # Always set it to False
        self.btn_run.setEnabled(False)

        for combo in list(self.combos_exposures.values()):
            if combo.count() == 1:
                combo.setEnabled(False)

        hazard = layer_from_combo(self.cbx_hazard)
        aggregation = layer_from_combo(self.cbx_aggregation)
        exposures = []
        for combo in list(self.combos_exposures.values()):
            exposures.append(layer_from_combo(combo))
        exposures = [layer for layer in exposures if layer]

        multi_exposure_if = MultiExposureImpactFunction()
        multi_exposure_if.hazard = hazard
        multi_exposure_if.exposures = exposures
        multi_exposure_if.debug = False
        multi_exposure_if.callback = self.progress_callback
        if aggregation:
            multi_exposure_if.use_selected_features_only = (
                self.use_selected_only)
            multi_exposure_if.aggregation = aggregation
        else:
            multi_exposure_if.crs = (
                self.iface.mapCanvas().mapSettings().destinationCrs())
        if len(self.ordered_expected_layers()) != 0:
            self._multi_exposure_if.output_layers_ordered = (
                self.ordered_expected_layers())

        status, message = multi_exposure_if.prepare()
        if status == PREPARE_SUCCESS:
            self._multi_exposure_if = multi_exposure_if
            self.btn_run.setEnabled(True)
            send_static_message(self, ready_message())
            self.list_layers_in_map_report.clear()
            return
        else:
            disable_busy_cursor()
            send_error_message(self, message)
            self._multi_exposure_if = None

    def accept(self):
        """Launch the multi exposure analysis."""
        if not isinstance(
                self._multi_exposure_if, MultiExposureImpactFunction):
            # This should not happen as the "accept" button must be disabled if
            # the impact function is not ready.
            return ANALYSIS_FAILED_BAD_CODE, None

        self.tab_widget.setCurrentIndex(2)
        self.set_enabled_buttons(False)
        enable_busy_cursor()
        try:
            code, message, exposure = self._multi_exposure_if.run()
            message = basestring_to_message(message)
            if code == ANALYSIS_FAILED_BAD_INPUT:
                LOGGER.warning(tr(
                    'The impact function could not run because of the inputs.'
                ))
                send_error_message(self, message)
                LOGGER.warning(message.to_text())
                disable_busy_cursor()
                self.set_enabled_buttons(True)
                return code, message
            elif code == ANALYSIS_FAILED_BAD_CODE:
                LOGGER.warning(tr(
                    'The impact function could not run because of a bug.'))
                LOGGER.exception(message.to_text())
                send_error_message(self, message)
                disable_busy_cursor()
                self.set_enabled_buttons(True)
                return code, message

            if setting('generate_report', True, bool):
                LOGGER.info(
                    'Reports are going to be generated for the multiexposure.')
                # Report for the multi exposure
                report = [standard_multi_exposure_impact_report_metadata_html]
                error_code, message = (self._multi_exposure_if.generate_report(
                    report))
                message = basestring_to_message(message)
                if error_code == ImpactReport.REPORT_GENERATION_FAILED:
                    LOGGER.warning(
                        'The impact report could not be generated.')
                    send_error_message(self, message)
                    LOGGER.exception(message.to_text())
                    disable_busy_cursor()
                    self.set_enabled_buttons(True)
                    return error_code, message
            else:
                LOGGER.warning(
                    'Reports are not generated because of your settings.')
                display_warning_message_bar(
                    tr('Reports'),
                    tr('Reports are not going to be generated because of your '
                       'InaSAFE settings.'),
                    duration=10,
                    iface_object=self.iface
                )

            # We always create the multi exposure group because we need
            # reports to be generated.
            root = QgsProject.instance().layerTreeRoot()

            if len(self.ordered_expected_layers()) == 0:
                group_analysis = root.insertGroup(
                    0, self._multi_exposure_if.name)
                group_analysis.setItemVisibilityChecked(True)
                group_analysis.setCustomProperty(
                    MULTI_EXPOSURE_ANALYSIS_FLAG, True)

                for layer in self._multi_exposure_if.outputs:
                    QgsProject.instance().addMapLayer(layer, False)
                    layer_node = group_analysis.addLayer(layer)
                    layer_node.setItemVisibilityChecked(False)

                    # set layer title if any
                    try:
                        title = layer.keywords['title']
                        if qgis_version() >= 21800:
                            layer.setName(title)
                        else:
                            layer.setLayerName(title)
                    except KeyError:
                        pass

                for analysis in self._multi_exposure_if.impact_functions:
                    detailed_group = group_analysis.insertGroup(
                        0, analysis.name)
                    detailed_group.setItemVisibilityChecked(True)
                    add_impact_layers_to_canvas(analysis, group=detailed_group)

                if self.iface:
                    self.iface.setActiveLayer(
                        self._multi_exposure_if.analysis_impacted)
            else:
                add_layers_to_canvas_with_custom_orders(
                    self.ordered_expected_layers(),
                    self._multi_exposure_if,
                    self.iface)

            if setting('generate_report', True, bool):
                LOGGER.info(
                    'Reports are going to be generated for each single '
                    'exposure.')
                # Report for the single exposure with hazard
                for analysis in self._multi_exposure_if.impact_functions:
                    # we only want to generate non pdf/qpt report
                    html_components = [standard_impact_report_metadata_html]
                    error_code, message = (
                        analysis.generate_report(html_components))
                    message = basestring_to_message(message)
                    if error_code == (
                            ImpactReport.REPORT_GENERATION_FAILED):
                        LOGGER.info(
                            'The impact report could not be generated.')
                        send_error_message(self, message)
                        LOGGER.info(message.to_text())
                        disable_busy_cursor()
                        self.set_enabled_buttons(True)
                        return error_code, message
            else:
                LOGGER.info(
                    'Reports are not generated because of your settings.')
                display_warning_message_bar(
                    tr('Reports'),
                    tr('Reports are not going to be generated because of your '
                       'InaSAFE settings.'),
                    duration=10,
                    iface_object=self.iface
                )

            # If zoom to impact is enabled
            if setting(
                    'setZoomToImpactFlag', expected_type=bool):
                self.iface.zoomToActiveLayer()

            # If hide exposure layers
            if setting('setHideExposureFlag', expected_type=bool):
                treeroot = QgsProject.instance().layerTreeRoot()
                for combo in list(self.combos_exposures.values()):
                    layer = layer_from_combo(combo)
                    if layer is not None:
                        treelayer = treeroot.findLayer(layer.id())
                        if treelayer:
                            treelayer.setItemVisibilityChecked(False)

            # Set last analysis extent
            self._extent.set_last_analysis_extent(
                self._multi_exposure_if.analysis_extent,
                self._multi_exposure_if.crs)

            self.done(QDialog.Accepted)

        except Exception as e:
            error_message = get_error_message(e)
            send_error_message(self, error_message)
            LOGGER.exception(e)
            LOGGER.debug(error_message.to_text())
        finally:
            disable_busy_cursor()
            self.set_enabled_buttons(True)

    def reject(self):
        """Redefinition of the reject method."""
        self._populate_reporting_tab()
        super(MultiExposureDialog, self).reject()

    def set_enabled_buttons(self, enabled):
        self.btn_cancel.setEnabled(enabled)
        self.btn_back.setEnabled(enabled)
        self.btn_next.setEnabled(enabled)
        self.btn_run.setEnabled(enabled)
