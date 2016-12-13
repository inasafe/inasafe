# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **GUI Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

import os
import shutil
import logging
from collections import OrderedDict

# noinspection PyPackageRequirements
from qgis.core import (
    QgsCoordinateTransform,
    QgsRectangle,
    QgsMapLayer,
    QgsMapLayerRegistry,
    QgsCoordinateReferenceSystem,
    QGis,
    QgsProject,
    QgsLayerTreeLayer)
# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
# noinspection PyPackageRequirements
from PyQt4.QtCore import (
    Qt,
    pyqtSlot,
    QSettings,
    pyqtSignal,
    QDir)

from safe.definitionsv4.layer_purposes import layer_purpose_exposure_impacted
from safe.definitionsv4.report import standard_impact_report_metadata
from safe.definitionsv4.utilities import definition
from safe.definitionsv4.fields import hazard_class_field
from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe.reportv4.report_metadata import ReportMetadata
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.utilities import (
    get_error_message,
    impact_attribution,
    add_ordered_combo_item,
    is_keyword_version_supported,
)
from safe.defaults import default_north_arrow_path, supporters_logo_path
from safe.utilities.gis import (
    extent_string_to_array,
)
from safe.utilities.resources import (
    get_ui_class)
from safe.utilities.qgis_utilities import (
    display_critical_message_bar,
    display_warning_message_bar,
    display_information_message_bar)
from safe.utilities.memory_checker import memory_error
from safe.common.version import get_version
from safe.common.signals import (
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    ERROR_MESSAGE_SIGNAL,
    BUSY_SIGNAL,
    NOT_BUSY_SIGNAL,
    send_static_message,
    send_error_message,
)
from safe import messaging as m
from safe.messaging import styles
from safe.common.exceptions import (
    KeywordNotFoundError,
    NoKeywordsFoundError,
    InsufficientOverlapError,
    InvalidParameterError,
    HashNotFoundError,
    InvalidGeometryError,
    UnsupportedProviderError,
    InvalidAggregationKeywords,
    InsufficientMemoryWarning,
    MetadataReadError,
)
from safe.impact_function_v4.impact_function import ImpactFunction
from safe.impact_function_v4.style import hazard_class_style
from safe.report.impact_report import ImpactReport
from safe.gui.tools.about_dialog import AboutDialog
from safe.gui.tools.help_dialog import HelpDialog
from safe_extras.pydispatch import dispatcher
from safe.utilities.extent import Extent
from safe.utilities.qt import disable_busy_cursor, enable_busy_cursor
from safe.gui.widgets.message import (
    show_no_keywords_message,
    show_keyword_version_message,
    missing_keyword_message,
    getting_started_message,
    no_overlap_message,
    ready_message)
from safe.reportv4.impact_report import ImpactReport as ImpactReportV4

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

PROGRESS_UPDATE_STYLE = styles.PROGRESS_UPDATE_STYLE
INFO_STYLE = styles.INFO_STYLE
WARNING_STYLE = styles.WARNING_STYLE
KEYWORD_STYLE = styles.KEYWORD_STYLE
SUGGESTION_STYLE = styles.SUGGESTION_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE
LOGO_ELEMENT = m.Brand()

FORM_CLASS = get_ui_class('dock_base.ui')

LOGGER = logging.getLogger('InaSAFE')


# noinspection PyArgumentList
# noinspection PyUnresolvedReferences
class Dock(QtGui.QDockWidget, FORM_CLASS):
    """Dock implementation class for the inaSAFE plugin."""

    def __init__(self, iface):
        """Constructor for the dialog.

        This dialog will allow the user to select layers and scenario details
        and subsequently run their model.

        :param iface: A QGisAppInterface instance we use to access QGIS via.
        :type iface: QgsAppInterface

        .. note:: We use the multiple inheritance approach from Qt4 so that
            for elements are directly accessible in the form context and we can
            use autoconnect to set up slots. See article below:
            http://doc.qt.nokia.com/4.7-snapshot/designer-using-a-ui-file.html
        """
        QtGui.QDockWidget.__init__(self, None)
        self.setupUi(self)
        self.show_question_button.setVisible(False)
        self.progress_bar.hide()
        self.enable_messaging()
        self.inasafe_version = get_version()

        self.set_dock_title()

        # Save reference to the QGIS interface
        self.iface = iface

        self.impact_function = None
        self.keyword_io = KeywordIO()
        self.state = None
        self.extent = Extent(self.iface)
        self.composer = None
        self.composition = None
        self.map_canvas = None

        # Flag used to prevent recursion and allow bulk loads of layers to
        # trigger a single event only
        self.get_layers_lock = False
        # Flag so we can see if the dock is busy processing
        self.busy = False

        # Values for settings these get set in read_settings.
        self.show_only_visible_layers_flag = None
        self.set_layer_from_title_flag = None
        self.zoom_to_impact_flag = None
        self.hide_exposure_flag = None
        self.map_canvas = None
        self.developer_mode = None
        self.organisation_logo_path = None

        self.print_button.setEnabled(False)
        self.runtime_keywords_dialog = None

        self.setup_button_connectors()

        self.iface.layerSavedAs.connect(self.save_auxiliary_files)

        canvas = self.iface.mapCanvas()

        # Enable on the fly projection by default
        canvas.setCrsTransformEnabled(True)
        self.connect_layer_listener()
        self.question_group.setEnabled(False)
        self.question_group.setVisible(False)
        self.set_run_button_status()

        self.read_settings()  # get_project_layers called by this

        # debug_mode is a check box to know if we run the IF with debug mode.
        self.debug_mode.setVisible(self.developer_mode)
        self.debug_mode.setChecked(False)

    def set_dock_title(self):
        """Set the title of the dock using the current version of InaSAFE."""
        self.setWindowTitle(self.tr('InaSAFE %s' % self.inasafe_version))

    def enable_signal_receiver(self):
        """Setup dispatcher for all available signal from Analysis."""
        dispatcher.connect(
            self.show_busy,
            signal=BUSY_SIGNAL)

        dispatcher.connect(
            self.hide_busy,
            signal=NOT_BUSY_SIGNAL)

    def disable_signal_receiver(self):
        """Remove dispatcher for all available signal from Analysis."""
        dispatcher.disconnect(
            self.show_busy,
            signal=BUSY_SIGNAL)

        dispatcher.disconnect(
            self.hide_busy,
            signal=NOT_BUSY_SIGNAL)

    def enable_messaging(self):
        """Set up the dispatcher for messaging."""
        # Set up dispatcher for dynamic messages
        # Dynamic messages will not clear the message queue so will be appended
        # to existing user messages
        # noinspection PyArgumentEqualDefault
        dispatcher.connect(
            self.results_webview.dynamic_message_event,
            signal=DYNAMIC_MESSAGE_SIGNAL,
            sender=dispatcher.Any)
        # Set up dispatcher for static messages
        # Static messages clear the message queue and so the display is 'reset'
        # noinspection PyArgumentEqualDefault
        dispatcher.connect(
            self.results_webview.static_message_event,
            signal=STATIC_MESSAGE_SIGNAL,
            sender=dispatcher.Any)
        # Set up dispatcher for error messages
        # Error messages clear the message queue and so the display is 'reset'
        # noinspection PyArgumentEqualDefault
        dispatcher.connect(
            self.results_webview.error_message_event,
            signal=ERROR_MESSAGE_SIGNAL,
            sender=dispatcher.Any)

    def setup_button_connectors(self):
        """Setup signal/slot mechanisms for dock buttons."""
        self.help_button.clicked.connect(self.show_help)
        self.run_button.clicked.connect(self.accept)
        self.about_button.clicked.connect(self.about)

    def about(self):
        """Open the About dialog."""
        # noinspection PyTypeChecker
        dialog = AboutDialog(self)
        dialog.show()

    def _show_organisation_logo(self):
        """Show the organisation logo in the dock if possible."""
        dock_width = float(self.width())
        # Don't let the image be more tha 100px height
        maximum_height = 100.0  # px
        pixmap = QtGui.QPixmap(self.organisation_logo_path)
        if pixmap.height() < 1 or pixmap.width() < 1:
            return

        height_ratio = maximum_height / pixmap.height()
        maximum_width = int(pixmap.width() * height_ratio)
        # Don't let the image be more than the dock width wide
        if maximum_width > dock_width:
            width_ratio = dock_width / float(pixmap.width())
            maximum_height = int(pixmap.height() * width_ratio)
            maximum_width = dock_width
        too_high = pixmap.height() > maximum_height
        too_wide = pixmap.width() > dock_width
        if too_wide or too_high:
            pixmap = pixmap.scaled(
                maximum_width, maximum_height, Qt.KeepAspectRatio)
        self.organisation_logo.setMaximumWidth(maximum_width)
        # We have manually scaled using logic above
        self.organisation_logo.setScaledContents(False)
        self.organisation_logo.setPixmap(pixmap)
        self.organisation_logo.show()

    def read_settings(self):
        """Set the dock state from QSettings.

        Do this on init and after changing options in the options dialog.
        """

        settings = QSettings()

        flag = bool(settings.value(
            'inasafe/showRubberBands', False, type=bool))
        self.extent.show_rubber_bands = flag
        try:
            extent = settings.value('inasafe/analysis_extent', '', type=str)
            crs = settings.value('inasafe/analysis_extent_crs', '', type=str)
        except TypeError:
            # Any bogus stuff in settings and we just clear them
            extent = ''
            crs = ''

        if extent != '' and crs != '':
            extent = extent_string_to_array(extent)
            try:
                # noinspection PyCallingNonCallable
                self.extent.user_extent = QgsRectangle(*extent)
                # noinspection PyCallingNonCallable
                self.extent.user_extent_crs = QgsCoordinateReferenceSystem(crs)
                self.extent.show_user_analysis_extent()
            except TypeError:
                self.extent.user_extent = None
                self.extent.user_extent_crs = None

        self.draw_rubber_bands()

        flag = settings.value(
            'inasafe/visibleLayersOnlyFlag', True, type=bool)
        self.show_only_visible_layers_flag = flag

        flag = settings.value(
            'inasafe/set_layer_from_title_flag', True, type=bool)
        self.set_layer_from_title_flag = flag

        flag = settings.value(
            'inasafe/setZoomToImpactFlag', True, type=bool)
        self.zoom_to_impact_flag = flag
        # whether exposure layer should be hidden after model completes
        flag = settings.value(
            'inasafe/setHideExposureFlag', False, type=bool)
        self.hide_exposure_flag = flag

        # whether to show or not dev only options
        self.developer_mode = settings.value(
            'inasafe/developer_mode', False, type=bool)

        # whether to show or not a custom Logo
        self.organisation_logo_path = settings.value(
            'inasafe/organisation_logo_path',
            supporters_logo_path(),
            type=str)
        # This is a fix for 3.0.0 change where we no longer provide Qt4
        # Qt4 resource bundles, so if the path points into a resource
        # bundle we clear it and overwrite the setting
        invalid_path_flag = False
        if self.organisation_logo_path.startswith(':/'):
            self.organisation_logo_path = None
            invalid_path_flag = True
            settings.setValue(
                'inasafe/organisation_logo_path',
                supporters_logo_path())

        # Changed default to False for new users in 3.2 - see #2171
        show_logos_flag = bool(settings.value(
            'inasafe/showOrganisationLogoInDockFlag', False, type=bool))

        # Flag to check valid organization logo
        invalid_logo_size = False
        logo_not_exist = False

        if self.organisation_logo_path:
            dock_width = float(self.width())

            # Dont let the image be more tha 100px hight
            maximum_height = 100.0  # px
            pixmap = QtGui.QPixmap(self.organisation_logo_path)
            # it will throw Overflow Error if pixmap.height() == 0
            if pixmap.height() > 0:

                height_ratio = maximum_height / pixmap.height()
                maximum_width = int(pixmap.width() * height_ratio)

                # Don't let the image be more than the dock width wide
                if maximum_width > dock_width:
                    width_ratio = dock_width / float(pixmap.width())
                    maximum_height = int(pixmap.height() * width_ratio)
                    maximum_width = dock_width

                too_high = pixmap.height() > maximum_height
                too_wide = pixmap.width() > dock_width

                if too_wide or too_high:
                    pixmap = pixmap.scaled(
                        maximum_width, maximum_height, Qt.KeepAspectRatio)

                self.organisation_logo.setMaximumWidth(maximum_width)
                # We have manually scaled using logic above
                self.organisation_logo.setScaledContents(False)
                self.organisation_logo.setPixmap(pixmap)
            else:
                # handle zero pixmap height and or nonexistent files
                if not os.path.exists(self.organisation_logo_path):
                    logo_not_exist = True
                else:
                    invalid_logo_size = True

        if (self.organisation_logo_path and show_logos_flag and
                not invalid_logo_size and not logo_not_exist):
            self._show_organisation_logo()
        else:
            self.organisation_logo.hide()

        # This is a fix for 3.0.0 change where we no longer provide Qt4
        # Qt4 resource bundles, so if the path points into a resource
        # bundle we clear it and overwrite the setting
        north_arrow_path = settings.value(
            'inasafe/north_arrow_path',
            default_north_arrow_path(),
            type=str)
        if north_arrow_path.startswith(':/'):
            invalid_path_flag = True
            settings.setValue(
                'inasafe/north_arrow_path', default_north_arrow_path())

        if invalid_path_flag:
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(
                self, self.tr('InaSAFE %s' % self.inasafe_version),
                self.tr(
                    'Due to backwards incompatibility with InaSAFE 2.0.0, the '
                    'paths to your preferred organisation logo and north '
                    'arrow may have been reset to their default values. '
                    'Please check in Plugins -> InaSAFE -> Options that your '
                    'paths are still correct and update them if needed.'
                ), QtGui.QMessageBox.Ok)

        # RM: this is a fix for nonexistent organization logo or zero height
        if logo_not_exist:
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(
                self, self.tr('InaSAFE %s' % self.inasafe_version),
                self.tr(
                    'The file for organization logo in %s doesn\'t exists. '
                    'Please check in Plugins -> InaSAFE -> Options that your '
                    'paths are still correct and update them if needed.' %
                    self.organisation_logo_path
                ), QtGui.QMessageBox.Ok)
        if invalid_logo_size:
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(
                self,
                self.tr('InaSAFE %s' % self.inasafe_version),
                self.tr(
                    'The file for organization logo has zero height. Please '
                    'provide valid file for organization logo.'
                ), QtGui.QMessageBox.Ok)
        if logo_not_exist or invalid_logo_size:
            settings.setValue(
                'inasafe/organisation_logo_path',
                supporters_logo_path())

    def connect_layer_listener(self):
        """Establish a signal/slot to listen for layers loaded in QGIS.

        ..seealso:: disconnect_layer_listener
        """
        registry = QgsMapLayerRegistry.instance()
        registry.layersWillBeRemoved.connect(self.get_layers)
        registry.layersAdded.connect(self.get_layers)
        registry.layersRemoved.connect(self.get_layers)

        self.iface.mapCanvas().layersChanged.connect(self.get_layers)
        self.iface.currentLayerChanged.connect(self.layer_changed)
        self.iface.mapCanvas().extentsChanged.connect(self.draw_rubber_bands)

    # pylint: disable=W0702
    def disconnect_layer_listener(self):
        """Destroy the signal/slot to listen for layers loaded in QGIS.

        ..seealso:: connect_layer_listener
        """
        registry = QgsMapLayerRegistry.instance()
        registry.layersWillBeRemoved.disconnect(self.get_layers)
        registry.layersAdded.disconnect(self.get_layers)
        registry.layersRemoved.disconnect(self.get_layers)

        self.iface.mapCanvas().layersChanged.disconnect(self.get_layers)
        self.iface.currentLayerChanged.disconnect(self.layer_changed)
        self.iface.mapCanvas().extentsChanged.disconnect(
            self.draw_rubber_bands)

    def validate(self):
        """Helper method to evaluate the current state of the dialog.

        This function will determine if it is appropriate for the OK button to
        be enabled or not.

        .. note:: The enabled state of the OK button on the dialog will
           NOT be updated (set True or False) depending on the outcome of
           the UI readiness tests performed - **only** True or False
           will be returned by the function.

        :returns: A two-tuple where the first element is a Boolean reflecting
         the results of the validation tests and the second is a message
         indicating any reason why the validation may have failed.
        :rtype: (Boolean, safe.messaging.Message)

        Example::

            flag,message = self.validate()
        """
        if self.busy:
            return False, None
        hazard_index = self.hazard_layer_combo.currentIndex()
        exposure_index = self.exposure_layer_combo.currentIndex()
        if hazard_index == -1 or exposure_index == -1:
            message = getting_started_message()
            return False, message

        # Now check if extents are ok for #1811
        else:
            message = ready_message()
            return True, message

    @pyqtSlot(QgsMapLayer, str)
    def save_auxiliary_files(self, layer, destination):
        """Save auxiliary files when using the 'save as' function.

        If some auxiliary files (.xml) exist, this function will
        copy them when the 'save as' function is used on the layer.

        :param layer: The layer which has been saved as.
        :type layer: QgsMapLayer

        :param destination: The new filename of the layer.
        :type destination: str
        """

        source_basename = os.path.splitext(layer.source())[0]
        source_xml = "%s.xml" % source_basename

        destination_basename = os.path.splitext(destination)[0]
        destination_xml = "%s.xml" % destination_basename

        # noinspection PyBroadException,PyBroadException
        try:
            # XML
            if os.path.isfile(source_xml):
                shutil.copy(source_xml, destination_xml)

        except (OSError, IOError):
            display_critical_message_bar(
                title=self.tr('Error while saving'),
                message=self.tr("The destination location must be writable."))

        except Exception:  # pylint: disable=broad-except
            display_critical_message_bar(
                title=self.tr('Error while saving'),
                message=self.tr("Something went wrong."))
        finally:
            disable_busy_cursor()

    # noinspection PyPep8Naming
    @pyqtSlot(int)
    def on_hazard_layer_combo_currentIndexChanged(self, index):
        """Automatic slot executed when the Hazard combo is changed.

        This is here so that we can see if the ok button should be enabled.

        :param index: The index number of the selected hazard layer.
        """
        # Add any other logic you might like here...
        del index
        self.toggle_aggregation_layer_combo()
        self.set_run_button_status()
        self.draw_rubber_bands()

    # noinspection PyPep8Naming
    @pyqtSlot(int)
    def on_exposure_layer_combo_currentIndexChanged(self, index):
        """Automatic slot executed when the Exposure combo is changed.

        This is here so that we can see if the ok button should be enabled.

        :param index: The index number of the selected exposure layer.
        """
        # Add any other logic you might like here...
        del index
        self.toggle_aggregation_layer_combo()
        self.set_run_button_status()
        self.draw_rubber_bands()

    def toggle_aggregation_layer_combo(self):
        """Toggle the aggregation combo enabled status.

        Whether the combo is toggled on or off will depend on the current dock
        status.
        """
        selected_hazard_layer = self.get_hazard_layer()
        selected_exposure_layer = self.get_exposure_layer()

        # more than 1 because No aggregation is always there
        if ((self.aggregation_layer_combo.count() > 1) and
                (selected_hazard_layer is not None) and
                (selected_exposure_layer is not None)):
            self.aggregation_layer_combo.setEnabled(True)
        else:
            self.aggregation_layer_combo.setCurrentIndex(0)
            self.aggregation_layer_combo.setEnabled(False)

    def set_run_button_status(self):
        """Helper function to set the run button status based on form validity.
        """
        button = self.run_button
        flag, message = self.validate()

        # Hack until we fix the dock for InaSAFE V4
        # button.setEnabled(flag)
        button.setEnabled(True)
        if message is not None:
            send_static_message(self, message)

    @pyqtSlot()
    def canvas_layerset_changed(self):
        """A helper slot to update dock combos if canvas layerset changes.

        Activated when the layerset has been changed (e.g. one or more layer
        visibilities changed). If self.show_only_visible_layers_flag is set to
        False this method will simply return, doing nothing.
        """
        if self.show_only_visible_layers_flag:
            self.get_layers()

    def unblock_signals(self):
        """Let the combos listen for event changes again."""
        self.aggregation_layer_combo.blockSignals(False)
        self.exposure_layer_combo.blockSignals(False)
        self.hazard_layer_combo.blockSignals(False)

    def block_signals(self):
        """Prevent the combos and dock listening for event changes."""
        self.disconnect_layer_listener()
        self.aggregation_layer_combo.blockSignals(True)
        self.exposure_layer_combo.blockSignals(True)
        self.hazard_layer_combo.blockSignals(True)

    @pyqtSlot()
    def update_layer_name(self):
        """Writes the sender's new layer name into the layer's keywords"""
        layer = self.sender()
        name = layer.name()
        try:
            self.keyword_io.update_keywords(layer, {'title': name})
        except NoKeywordsFoundError:
            # the layer has no keyword file. we leave it alone.
            pass

    # noinspection PyUnusedLocal
    @pyqtSlot('QgsMapLayer')
    def get_layers(self, *args):
        r"""Obtain a list of layers currently loaded in QGIS.

        On invocation, this method will populate hazard_layer_combo,
        exposure_layer_combo and aggregation_layer_combo on the dialog
        with a list of available layers.

        Only **polygon vector** layers will be added to the aggregate list.

        :param args: Arguments that may have been passed to this slot.
            Typically a list of layers, but depends on which slot or function
            called this function.
        :type args: list

        ..note:: \*args is only used for debugging purposes.
        """
        _ = args
        # Prevent recursion
        if self.get_layers_lock:
            return

        # for arg in args:
        # LOGGER.debug('get_layer argument: %s' % arg)
        # Map registry may be invalid if QGIS is shutting down
        registry = QgsMapLayerRegistry.instance()
        canvas_layers = self.iface.mapCanvas().layers()
        # MapLayers returns a QMap<QString id, QgsMapLayer layer>
        layers = registry.mapLayers().values()

        # For issue #618
        if len(layers) == 0:
            send_static_message(self, getting_started_message())
            return

        self.get_layers_lock = True

        # Make sure this comes after the checks above to prevent signal
        # disconnection without reconnection
        self.block_signals()
        self.save_state()
        self.hazard_layer_combo.clear()
        self.exposure_layer_combo.clear()
        self.aggregation_layer_combo.clear()

        for layer in layers:

            try:
                # disconnect all connections
                layer.layerNameChanged.disconnect(self.update_layer_name)
            except TypeError:
                # disconnect() trows a TypeError if no connections are active
                pass
            finally:
                layer.layerNameChanged.connect(self.update_layer_name)

            if (self.show_only_visible_layers_flag and
                    (layer not in canvas_layers)):
                continue

            # .. todo:: check raster is single band
            #    store uuid in user property of list widget for layers

            name = layer.name()
            source = layer.id()
            # See if there is a title for this layer, if not,
            # fallback to the layer's filename

            # noinspection PyBroadException
            try:
                title = self.keyword_io.read_keywords(layer, 'title')
            except NoKeywordsFoundError:
                # Skip if there are no keywords at all
                continue
            except KeywordNotFoundError:
                # There is a missing mandatory keyword, ignore it
                continue
            except MetadataReadError:
                continue
            except:  # pylint: disable=W0702
                # automatically adding file name to title in keywords
                # See #575
                try:
                    self.keyword_io.update_keywords(layer, {'title': name})
                    title = name
                except UnsupportedProviderError:
                    continue
            else:
                # Lookup internationalised title if available
                title = self.tr(title)
            # Register title with layer
            if title and self.set_layer_from_title_flag:
                layer.setLayerName(title)

            # NOTE : I commented out this due to
            # https://github.com/AIFDR/inasafe/issues/528
            # check if layer is a vector polygon layer
            # if isPolygonLayer(layer):
            #     addComboItemInOrder(self.aggregation_layer_combo, title,
            #                         source)
            #     self.aggregationLayers.append(layer)

            # Find out if the layer is a hazard or an exposure
            # layer by querying its keywords. If the query fails,
            # the layer will be ignored.
            # noinspection PyBroadException
            try:
                layer_purpose = self.keyword_io.read_keywords(
                    layer, 'layer_purpose')
                keyword_version = str(self.keyword_io.read_keywords(
                    layer, 'keyword_version'))
                if not is_keyword_version_supported(keyword_version):
                    continue
            except:  # pylint: disable=W0702
                # continue ignoring this layer
                continue

            if layer_purpose == 'hazard':
                add_ordered_combo_item(
                    self.hazard_layer_combo, title, source)
            elif layer_purpose == 'exposure':
                add_ordered_combo_item(
                    self.exposure_layer_combo, title, source)
            elif layer_purpose == 'aggregation':
                add_ordered_combo_item(
                    self.aggregation_layer_combo, title, source)

        self.unblock_signals()
        # handle the aggregation_layer_combo combo
        self.aggregation_layer_combo.insertItem(0, self.tr('Entire area'))
        self.aggregation_layer_combo.setCurrentIndex(0)
        self.toggle_aggregation_layer_combo()

        self.restore_state()
        self.question_group.setEnabled(True)
        self.question_group.setVisible(True)
        self.show_question_button.setVisible(False)
        # Note: Don't change the order of the next two lines otherwise there
        # will be a lot of unneeded looping around as the signal is handled
        self.connect_layer_listener()
        self.get_layers_lock = False
        # ensure the dock keywords info panel is updated
        # make sure to do this after the lock is released!
        self.layer_changed(self.iface.activeLayer())
        # Make sure to update the analysis area preview
        self.draw_rubber_bands()

    def get_hazard_layer(self):
        """Get the QgsMapLayer currently selected in the hazard combo.

        Obtain QgsMapLayer id from the userrole of the QtCombo for hazard
        and return it as a QgsMapLayer.

        :returns: The currently selected map layer in the hazard combo.
        :rtype: QgsMapLayer

        """
        index = self.hazard_layer_combo.currentIndex()
        if index < 0:
            return None
        layer_id = self.hazard_layer_combo.itemData(
            index, QtCore.Qt.UserRole)
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    def get_exposure_layer(self):
        """Get the QgsMapLayer currently selected in the exposure combo.

        Obtain QgsMapLayer id from the userrole of the QtCombo for exposure
        and return it as a QgsMapLayer.

        :returns: Currently selected map layer in the exposure combo.
        :rtype: QgsMapLayer
        """

        index = self.exposure_layer_combo.currentIndex()
        if index < 0:
            return None
        layer_id = self.exposure_layer_combo.itemData(
            index, QtCore.Qt.UserRole)
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    def get_aggregation_layer(self):

        """Get the QgsMapLayer currently selected in the post processing combo.

        Obtain QgsMapLayer id from the userrole of the QtCombo for post
        processing combo return it as a QgsMapLayer.

        :returns: None if no aggregation is selected or aggregation_layer_combo
            is disabled, otherwise a polygon layer.
        :rtype: QgsMapLayer, QgsVectorLayer or None
        """

        no_selection_value = 0
        index = self.aggregation_layer_combo.currentIndex()
        if index <= no_selection_value:
            return None
        layer_id = self.aggregation_layer_combo.itemData(
            index, QtCore.Qt.UserRole)
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    @pyqtSlot('bool')
    def toggle_rubber_bands(self, flag):
        """Disabled/enable the rendering of rubber bands.

        :param flag: Flag to indicate if drawing of bands is active.
        :type flag: bool
        """
        self.extent.show_rubber_bands = flag
        # Temporary disable until we fix the dock in inasafe v4.
        self.extent.show_rubber_bands = False
        settings = QSettings()
        settings.setValue('inasafe/showRubberBands', flag)
        if not flag:
            self.extent.hide_last_analysis_extent()  # red
            self.extent.hide_next_analysis_extent()  # green
            self.extent.hide_user_analysis_extent()  # blue
        else:
            self.draw_rubber_bands()

    @pyqtSlot()
    def draw_rubber_bands(self):
        """Draw any rubber bands that are enabled."""
        settings = QSettings()
        try:
            flag = settings.value('inasafe/showRubberBands', type=bool)
        except TypeError:
            flag = False
        if flag:
            self.show_next_analysis_extent()  # green
            self.extent.show_user_analysis_extent()  # blue
            try:
                pass
                # clip_parameters = self.impact_function.clip_parameters
                # self.extent.show_last_analysis_extent(
                # clip_parameters['adjusted_geo_extent'])  # red
            except (AttributeError, TypeError):
                pass

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
        report.add(self.impact_function.performance_log_message())
        send_static_message(self, report)
        self.progress_bar.setMaximum(maximum_value)
        self.progress_bar.setValue(current_value)
        QtGui.QApplication.processEvents()

    def generate_impact_report(self, impact_function):
        """Generate the impact report from an impact function.

        :param impact_function: The impact function used.
        :type impact_function: ImpactFunction
        :return:
        """
        # get minimum needs profile
        minimum_needs = NeedsProfile()
        minimum_needs.load()

        # create impact report instance
        report_metadata = ReportMetadata(
            metadata_dict=standard_impact_report_metadata)
        impact_report = ImpactReportV4(
            self.iface,
            report_metadata,
            impact_function=impact_function,
            minimum_needs_profile=minimum_needs)

        # generate report folder

        # no other option for now
        # TODO: retrieve the information from data store
        if isinstance(impact_function.datastore.uri, QDir):
            layer_dir = impact_function.datastore.uri.absolutePath()
        else:
            # No other way for now
            return

        # We will generate it on the fly without storing it after datastore
        # supports
        impact_report.output_folder = os.path.join(layer_dir, 'output')
        impact_report.process_component()

    def accept(self):
        """Execute analysis when run button is clicked.

        .. todo:: FIXME (Tim) We may have to implement some polling logic
            because the button click accept() function and the updating
            of the web view after model completion are asynchronous (when
            threading mode is enabled especially)
        """
        self.enable_signal_receiver()
        self.show_busy()
        self.show_next_analysis_extent()
        self.impact_function = self.prepare_impact_function()
        # clip_parameters = self.impact_function.clip_parameters
        # self.extent.show_last_analysis_extent(
        #    clip_parameters['adjusted_geo_extent'])

        # Start the analysis
        status, message = self.impact_function.run()
        if status == 0:
            LOGGER.debug(self.tr(
                'The impact function could run without errors.'))
            self.generate_impact_report(self.impact_function)
        elif status == 1:
            LOGGER.debug(self.tr(
                'The impact function could not run because of the inputs.'))
        else:
            LOGGER.debug(self.tr(
                'The impact function could not run because of a bug.'))

        try:
            print 'toto'

        except KeywordNotFoundError as e:
            self.hide_busy()
            missing_keyword_message(self, e)
            return  # Will abort the analysis if there is exception
        except InsufficientOverlapError as e:
            context = self.tr(
                'A problem was encountered when trying to determine the '
                'analysis extents.'
            )
            self.analysis_error(e, context)
            return  # Will abort the analysis if there is exception
        except InvalidAggregationKeywords as e:
            # TODO: Launch keywords wizard
            # Show message box
            message = self.tr(
                'Your aggregation layer does not have valid keywords for '
                'aggregation. Please launch keyword wizard to assign keywords '
                'in this layer.'
            )
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, self.tr('InaSAFE'), message)
            context = self.tr(
                'A problem was encountered because the aggregation layer '
                'does not have proper keywords for aggregation layer.'
            )
            self.analysis_error(e, context)
            disable_busy_cursor()
            return
        except MemoryError:
            memory_error()
            disable_busy_cursor()
            return
        except InsufficientMemoryWarning:
            # noinspection PyCallByClass,PyTypeChecker
            result = QtGui.QMessageBox.warning(
                self, self.tr('InaSAFE'),
                self.tr('You may not have sufficient free system memory to '
                        'carry out this analysis. See the dock panel '
                        'message for more information. Would you like to '
                        'continue regardless?'), QtGui.QMessageBox.Yes |
                QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if result == QtGui.QMessageBox.No:
                # stop work here and return to QGIS
                self.hide_busy()
                return
            elif result == QtGui.QMessageBox.Yes:
                # Set analysis to ignore memory warning
                self.impact_function.force_memory = True
                self.accept()
        finally:
            if self.impact_function:

                layers = self.impact_function.outputs

                name = self.impact_function.name
                root = QgsProject.instance().layerTreeRoot()
                group_analysis = root.insertGroup(0, name)
                group_analysis.setVisible(Qt.Checked)
                for layer in layers:
                    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
                    layer_node = group_analysis.addLayer(layer)

                    # Let's enable only the more detailed layer. See #2925
                    if layer.id() == self.impact_function.impact.id():
                        layer_node.setVisible(Qt.Checked)
                        self.iface.setActiveLayer(layer)
                    else:
                        layer_node.setVisible(Qt.Unchecked)

                if self.zoom_to_impact_flag:
                    self.iface.zoomToActiveLayer()

                if self.impact_function.debug_mode:
                    name = 'DEBUG %s' % name
                    group_debug = root.insertGroup(0, name)
                    group_debug.setVisible(Qt.Unchecked)
                    group_debug.setExpanded(False)

                    # Let's style the hazard class in each layers.
                    classification = (
                        self.impact_function.hazard.keywords['classification'])
                    classification = definition(classification)

                    classes = OrderedDict()
                    for f in reversed(classification['classes']):
                        classes[f['key']] = (f['color'], f['name'])
                    hazard_class = hazard_class_field['key']

                    datastore = self.impact_function.datastore
                    for layer in datastore.layers():
                        qgis_layer = datastore.layer(layer)
                        QgsMapLayerRegistry.instance().addMapLayer(
                            qgis_layer, False)
                        layer_node = group_debug.insertLayer(0, qgis_layer)
                        layer_node.setVisible(Qt.Unchecked)
                        layer_node.setExpanded(False)

                        # Let's style layers which have a geometry and have
                        # hazard_class
                        if qgis_layer.type() == QgsMapLayer.VectorLayer:
                            if qgis_layer.geometryType() != QGis.NoGeometry:
                                if qgis_layer.keywords['inasafe_fields'].get(
                                        hazard_class):
                                    hazard_class_style(
                                        qgis_layer, classes, self.debug_mode)

                if self.hide_exposure_flag:
                    legend = self.iface.legendInterface()
                    qgis_exposure = self.get_exposure_layer()
                    legend.setLayerVisible(qgis_exposure, False)

            self.disable_signal_receiver()
            self.hide_busy()

    def analysis_error(self, exception, message):
        """A helper to spawn an error and halt processing.

        An exception will be logged, busy status removed and a message
        displayed.

        :param message: an ErrorMessage to display
        :type message: ErrorMessage, Message

        :param exception: An exception that was raised
        :type exception: Exception
        """
        self.hide_busy()
        LOGGER.exception(message)
        message = get_error_message(exception, context=message)
        send_error_message(self, message)

    def prepare_impact_function(self):
        """Create analysis as a representation of current situation of dock."""

        # Impact Functions
        impact_function = ImpactFunction()
        impact_function.callback = self.progress_callback

        # Layers
        impact_function.hazard = self.get_hazard_layer()
        impact_function.exposure = self.get_exposure_layer()
        aggregation = self.get_aggregation_layer()

        if aggregation:
            impact_function.aggregation = aggregation
        else:
            # We need to enable it again when we will fix the dock.
            # impact_function.requested_extent = self.extent.user_extent
            # impact_function.requested_extent = self.extent.user_extent_crs

            map_settings = self.iface.mapCanvas().mapSettings()
            impact_function.viewport_extent = map_settings.fullExtent()
            impact_function._viewport_extent_crs = (
                map_settings.destinationCrs())

        impact_function.debug_mode = self.debug_mode.isChecked()

        return impact_function

    def show_help(self):
        """Open the help dialog."""
        # noinspection PyTypeChecker
        dialog = HelpDialog(self)
        dialog.show()

    def show_busy(self):
        """Hide the question group box and enable the busy cursor."""
        self.progress_bar.show()
        self.question_group.setEnabled(False)
        self.question_group.setVisible(False)
        enable_busy_cursor()
        self.repaint()
        QtGui.qApp.processEvents()
        self.busy = True

    def hide_busy(self):
        """A helper function to indicate processing is done."""
        self.progress_bar.hide()
        self.show_question_button.setVisible(True)
        self.question_group.setEnabled(True)
        self.question_group.setVisible(False)
        # for #706 - if the exposure is hidden
        # due to self.hide_exposure_flag being enabled
        # we may have no exposure layers left
        # so we handle that here and disable run
        if self.exposure_layer_combo.count() == 0:
            self.run_button.setEnabled(False)
        else:
            self.run_button.setEnabled(True)
        self.repaint()
        disable_busy_cursor()
        self.busy = False

    def show_impact(self, layer):
        """Show the report or keywords from an impact layer.

        .. versionadded: 4.0

        :param layer: QgsMapLayer instance that is now active
        :type layer: QgsMapLayer, QgsRasterLayer, QgsVectorLayer
        """
        report_path = os.path.dirname(layer.source())
        report_path = os.path.join(
            report_path, 'output/impact-report-output.html')

        if os.path.exists(report_path):
            # We can display an impact report.
            LOGGER.debug('Showing Impact Report')

            with open(report_path) as report_file:
                report = report_file.read()

            self.print_button.setEnabled(True)
            # right now send the report as html texts, not message
            send_static_message(self, report)
            # also hide the question and show the show question button
            self.show_question_button.setVisible(True)
            self.question_group.setEnabled(True)
            self.question_group.setVisible(False)

        else:
            # TODO : ET 9/12/16, need to check this with V4.
            # There isn't report, we can display only keywords.
            LOGGER.debug('Showing Impact Keywords')
            keywords = self.keyword_io.read_keywords(layer)
            if 'impact_summary' not in keywords:
                return

            report = m.Message()
            report.add(LOGO_ELEMENT)
            report.add(m.Heading(self.tr(
                'Analysis Results'), **INFO_STYLE))
            report.add(m.Text(keywords['impact_summary']))
            report.add(impact_attribution(keywords))
            self.print_button.setEnabled(True)
            send_static_message(self, report)
            # also hide the question and show the show question button
            self.show_question_button.setVisible(True)
            self.question_group.setEnabled(True)
            self.question_group.setVisible(False)

    def show_generic_keywords(self, layer):
        """Show the keywords defined for the active layer.

        .. note:: The print button will be disabled if this method is called.

        .. versionchanged:: 3.3 - changed parameter from keywords object
            to a layer object so that we can show extra stuff like CRS and
            data source in the keywords.

        :param layer: A QGIS layer.
        :type layer: QgsMapLayer
        """
        keywords = KeywordIO(layer)
        self.print_button.setEnabled(False)
        message = keywords.to_message()
        send_static_message(self, message)

    @pyqtSlot('QgsMapLayer')
    def layer_changed(self, layer):
        """Handler for when the QGIS active layer is changed.

        If the active layer is changed and it has keywords and a report,
        show the report.

        :param layer: QgsMapLayer instance that is now active
        :type layer: QgsMapLayer, QgsRasterLayer, QgsVectorLayer

        """
        # Don't handle this event if we are already handling another layer
        # addition or removal event.
        if self.get_layers_lock:
            return

        # Do nothing if there is no active layer - see #1861
        if not self._has_active_layer():
            send_static_message(self, getting_started_message())

        # Now try to read the keywords and show them in the dock
        try:
            keywords = self.keyword_io.read_keywords(layer)

            # list of layer purpose to show impact report
            # TODO: make it referenced directly from definitions
            impacted_layer = [
                layer_purpose_exposure_impacted['key'],
                'aggregate_hazard_impacted',
                'aggregation_impacted',
                'analysis_impacted',
                'exposure_breakdown',
            ]

            if keywords.get('layer_purpose') in impacted_layer:
                self.show_impact(layer)
            else:
                if 'keyword_version' not in keywords.keys():
                    show_keyword_version_message(
                        self, 'No Version', self.inasafe_version)
                    self.print_button.setEnabled(False)
                else:
                    keyword_version = str(keywords.get('keyword_version'))
                    supported = is_keyword_version_supported(
                        keyword_version)
                    if supported:
                        self.show_generic_keywords(layer)
                    else:
                        # Layer version is not supported
                        show_keyword_version_message(
                            self, keyword_version, self.inasafe_version)
                    self.print_button.setEnabled(False)

        # TODO: maybe we need to split these apart more to give mode
        # TODO: granular error messages TS
        except (KeywordNotFoundError,
                HashNotFoundError,
                InvalidParameterError,
                NoKeywordsFoundError,
                MetadataReadError,
                AttributeError):
            # Added this check in 3.2 for #1861
            active_layer = self.iface.activeLayer()
            if active_layer is None:
                send_static_message(self, getting_started_message())
            else:
                show_no_keywords_message(self)
                self.print_button.setEnabled(False)
        except Exception as e:  # pylint: disable=broad-except
            error_message = get_error_message(e)
            send_error_message(self, error_message)

    def save_state(self):
        """Save the current state of the ui to an internal class member.

        The saved state can be restored again easily using
        :func:`restore_state`
        """
        state = {
            'hazard': self.hazard_layer_combo.currentText(),
            'exposure': self.exposure_layer_combo.currentText(),
            'aggregation': self.aggregation_layer_combo.currentText(),
            'report': self.results_webview.page().currentFrame().toHtml()}
        self.state = state

    def restore_state(self):
        """Restore the state of the dock to the last known state."""
        if self.state is None:
            return
        for myCount in range(0, self.exposure_layer_combo.count()):
            item_text = self.exposure_layer_combo.itemText(myCount)
            if item_text == self.state['exposure']:
                self.exposure_layer_combo.setCurrentIndex(myCount)
                break
        for myCount in range(0, self.hazard_layer_combo.count()):
            item_text = self.hazard_layer_combo.itemText(myCount)
            if item_text == self.state['hazard']:
                self.hazard_layer_combo.setCurrentIndex(myCount)
                break
        for myCount in range(0, self.aggregation_layer_combo.count()):
            item_text = self.aggregation_layer_combo.itemText(myCount)
            if item_text == self.state['aggregation']:
                self.aggregation_layer_combo.setCurrentIndex(myCount)
                break
        self.results_webview.setHtml(self.state['report'])

    def open_map_in_composer(self, impact_report):
        """Open map in composer given MapReport instance.

        ..note:: (AG) See https://github.com/AIFDR/inasafe/issues/911. We
            need to set the composition to the composer before loading the
            template.

        :param impact_report: Impact Report to be opened in composer.
        :type impact_report: ImpactReport
        """
        impact_report.setup_composition()
        self.composer = self.iface.createNewComposer()
        self.composer.setComposition(impact_report.composition)
        impact_report.load_template()
        impact_report.draw_composition()

        # Fit In View
        number_pages = impact_report.composition.numPages()
        paper_height = impact_report.composition.paperHeight()
        paper_width = impact_report.composition.paperWidth()
        space_between_pages = impact_report.composition.spaceBetweenPages()
        if number_pages > 0:
            height = (paper_height * number_pages) + (
                space_between_pages * (number_pages - 1))
            self.composer.fitInView(
                0, 0, paper_width + 1, height + 1, QtCore.Qt.KeepAspectRatio)

    @pyqtSlot('QgsRectangle', 'QgsCoordinateReferenceSystem')
    def define_user_analysis_extent(self, extent, crs):
        """Slot called when user has defined a custom analysis extent.

        .. versionadded: 2.2.0

        :param extent: Extent of the user's preferred analysis area.
        :type extent: QgsRectangle

        :param crs: Coordinate reference system for user defined analysis
            extent.
        :type crs: QgsCoordinateReferenceSystem
        """
        try:
            self.extent.define_user_analysis_extent(extent, crs)
            self.show_next_analysis_extent()
        except InvalidGeometryError:
            return

    def _has_active_layer(self):
        """Check if there is a layer active in the legend.

        .. versionadded:: 3.1

        :returns: True if there is a layer hightlighted in the legend.
        :rtype: bool
        """
        layer = self.iface.activeLayer()
        return layer is not None

    def _layer_count(self):
        """Return the count of layers in the legend.

        .. versionadded: 3.1

        :returns: Number of layers in the legend, regardless of their
            visibility status.
        :rtype: int
        """

        legend = self.iface.legendInterface()
        layers = legend.layers()
        count = len(layers)
        return count

    def _visible_layers_count(self):
        """Calculate the number of visible layers in the legend.

        .. versionadded: 3.1

        :returns: Count of layers that are actually visible.
        :rtype: int
        """
        legend = self.iface.legendInterface()
        layers = legend.layers()
        visible_count = 0
        for layer in layers:
            if legend.isLayerVisible(layer):
                visible_count += 1
        return visible_count

    def show_next_analysis_extent(self):
        """Update the rubber band showing where the next analysis extent is.

        Primary purpose of this slot is to draw a rubber band of where the
        analysis will be carried out based on valid intersection between
        layers.

        This slot is called on pan, zoom, layer visibility changes and

        .. versionadded:: 2.1.0
        """
        settings = QSettings()
        self.extent.hide_next_analysis_extent()
        # check if we actually have correct hazard, exposure and IF
        # if we don't we exit immediately to avoid cluttering up the display
        # with unneeded status messages...
        flag, _ = self.validate()
        if not flag:
            self.run_button.setEnabled(False)
            return

        # IF could potentially run - lets see if the extents will work well...
        valid, extents = self.validate_extents()
        if valid:
            self.extent.show_next_analysis_extent(extents)
            show_confirmations = settings.value(
                'inasafe/show_extent_confirmations',
                True,
                type=bool)

            if show_confirmations:
                message = self.tr(
                    'The hazard layer, exposure layer and your '
                    'defined analysis area extents all overlap. Press the '
                    'run button below to continue with the analysis.')

                display_information_message_bar(
                    self.tr('InaSAFE'),
                    self.tr('Analysis environment ready'),
                    message,
                    self.tr('More info ...'),
                    2)
            self.run_button.setEnabled(True)
        else:
            # For issue #618, #1811
            if self.show_only_visible_layers_flag:
                layer_count = self._visible_layers_count()
            else:
                layer_count = self._layer_count()

            if layer_count == 0:
                send_static_message(self, getting_started_message())
            else:
                show_warnings = settings.value(
                    'inasafe/show_extent_warnings',
                    True,
                    type=bool)
                if show_warnings:
                    message = no_overlap_message()
                    display_warning_message_bar(
                        self.tr('InaSAFE'),
                        self.tr('No overlapping extents'),
                        message)
            self.run_button.setEnabled(False)
            # For #2077 somewhat kludgy hack to prevent positive
            # message when we cant actually run
            match = self.tr(
                'You can now proceed to run your analysis by clicking the ')
            current_text = self.results_webview.page_to_text()
            if match in current_text:
                message = m.Message()
                message.add(LOGO_ELEMENT)
                message.add(m.Heading(self.tr(
                    'Insufficient overlap'), **WARNING_STYLE))
                message.add(no_overlap_message())
                send_static_message(self, message)

    def validate_extents(self):
        """Check if the current extents are valid.

        Look at the intersection between Hazard, exposure and user analysis
        area and see if they represent a valid, usable area for analysis.

        .. versionadded:: 3.1

        :returns: A two-tuple. The first element will be True if extents are
            usable, otherwise False. It will also return False if an invalid
            condition exists e.g. no hazard layer etc. The second element will
            be a rectangle for the analysis extent (if valid) or None.
        :rtype: (bool, QgsRectangle)
        """

        try:
            # Temporary only, for checking the user extent
            impact_function = self.prepare_impact_function()
            # clip_parameters = impact_function.clip_parameters
            # return True, clip_parameters['adjusted_geo_extent']
            return True, None
        except (AttributeError, InsufficientOverlapError):
            return False, None
