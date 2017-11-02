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

    def _tab_changed(self):
        """Triggered when the current tab is changed."""
        if self.tab_widget.currentWidget() == self.reportingTab:
            self._populate_reporting_tab()

    def _populate_reporting_tab(self):
        """Populate trees about layers."""
        self.tree.clear()
        self.tree.setColumnCount(1)
        self.tree.setRootIsDecorated(False)
        self.tree.setHeaderHidden(True)

        analysis_branch = QTreeWidgetItem(
            self.tree.invisibleRootItem(), [tr('Layers from Analysis')])
        analysis_branch.setFont(0, bold_font)
        analysis_branch.setExpanded(True)

        if self._multi_exposure_if:
            expected = self._multi_exposure_if.output_layers_expected()
            for group, layers in expected.iteritems():
                group_branch = QTreeWidgetItem(analysis_branch, [group])
                group_branch.setFont(0, bold_font)
                group_branch.setExpanded(True)

                for layer in layers:
                    QTreeWidgetItem(group_branch, [layer])

        canvas_branch = QTreeWidgetItem(
            self.tree.invisibleRootItem(), [tr('Layers from Canvas')])
        # canvas_branch.setFlags(Qt.ItemIsDropEnabled | Qt.ItemIsEnabled)
        canvas_branch.setFont(0, bold_font)
        canvas_branch.setExpanded(True)

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
            QTreeWidgetItem(canvas_branch, [title])

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
