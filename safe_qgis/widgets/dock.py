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
__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import logging
from functools import partial

# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
# noinspection PyPackageRequirements
from PyQt4.QtCore import pyqtSlot, QSettings, pyqtSignal
# noinspection PyPackageRequirements
from PyQt4.QtGui import QColor
from qgis.core import (
    QgsCoordinateTransform,
    QgsRectangle,
    QgsPoint,
    QgsMapLayer,
    QgsMapLayerRegistry,
    QgsCoordinateReferenceSystem,
    QGis)
from qgis.gui import QgsRubberBand
from third_party.pydispatch import dispatcher
from safe_qgis.ui.dock_base import Ui_DockBase
from safe_qgis.utilities.help import show_context_help
from safe_qgis.utilities.utilities import (
    get_error_message,
    impact_attribution,
    add_ordered_combo_item,
    read_impact_layer)
from safe_qgis.utilities.defaults import (
    limitations,
    disclaimer,
    default_organisation_logo_path)
from safe_qgis.utilities.styling import (
    setRasterStyle,
    set_vector_graduated_style,
    set_vector_categorized_style)
from safe_qgis.utilities.impact_calculator import ImpactCalculator
from safe_qgis.safe_interface import (
    load_plugins,
    available_functions,
    get_function_title,
    get_safe_impact_function,
    safeTr,
    get_version,
    temp_dir,
    ReadLayerError)
from safe_qgis.safe_interface import messaging as m
from safe_qgis.safe_interface import (
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    ERROR_MESSAGE_SIGNAL,
    BUSY_SIGNAL,
    NOT_BUSY_SIGNAL,
    ANALYSIS_DONE_SIGNAL)
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.exceptions import (
    KeywordNotFoundError,
    NoKeywordsFoundError,
    InsufficientOverlapError,
    InvalidParameterError,
    HashNotFoundError,
    UnsupportedProviderError,
    InvalidAggregationKeywords,
    InsufficientMemoryWarning)
from safe_qgis.report.map import Map
from safe_qgis.report.html_renderer import HtmlRenderer
from safe_qgis.impact_statistics.function_options_dialog import (
    FunctionOptionsDialog)
from safe_qgis.tools.about_dialog import AboutDialog
from safe_qgis.tools.keywords_dialog import KeywordsDialog
from safe_qgis.tools.impact_report_dialog import ImpactReportDialog
from safe_qgis.safe_interface import styles

from safe_qgis.utilities.analysis import Analysis

PROGRESS_UPDATE_STYLE = styles.PROGRESS_UPDATE_STYLE
INFO_STYLE = styles.INFO_STYLE
WARNING_STYLE = styles.WARNING_STYLE
KEYWORD_STYLE = styles.KEYWORD_STYLE
SUGGESTION_STYLE = styles.SUGGESTION_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE
LOGO_ELEMENT = m.Image('qrc:/plugins/inasafe/inasafe-logo.png', 'InaSAFE Logo')
LOGGER = logging.getLogger('InaSAFE')

# from pydev import pydevd  # pylint: disable=F0401


#noinspection PyArgumentList
# noinspection PyUnresolvedReferences
class Dock(QtGui.QDockWidget, Ui_DockBase):
    """Dock implementation class for the inaSAFE plugin."""

    analysisDone = pyqtSignal(bool)

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
        # Enable remote debugging - should normally be commented out.
        # pydevd.settrace(
        #    'localhost', port=5678, stdoutToServer=True,
        #    stderrToServer=True)

        QtGui.QDockWidget.__init__(self, None)
        self.setupUi(self)

        # Ensure that all impact functions are loaded
        load_plugins()
        self.pbnShowQuestion.setVisible(False)
        self.enable_messaging()

        self.set_dock_title()

        # Save reference to the QGIS interface
        self.iface = iface

        self.calculator = ImpactCalculator()
        self.keyword_io = KeywordIO()
        self.runner = None
        self.state = None
        self.last_used_function = ''

        self.composer = None
        self.composition = None

        # Flag used to prevent recursion and allow bulk loads of layers to
        # trigger a single event only
        self.get_layers_lock = False
        # Flag so we can see if the dock is busy processing
        self.busy = False

        # Values for settings these get set in read_settings.
        self.run_in_thread_flag = None
        self.show_only_visible_layers_flag = None
        self.set_layer_from_title_flag = None
        self.zoom_to_impact_flag = None
        self.hide_exposure_flag = None
        self.clip_to_viewport = None
        self.clip_hard = None
        self.show_intermediate_layers = None
        self.developer_mode = None
        self.organisation_logo_path = None

        self.function_parameters = None
        self.analysis = None

        self.pbnPrint.setEnabled(False)
        # used by configurable function options button
        self.active_function = None
        self.runtime_keywords_dialog = None

        self.setup_button_connectors()

        canvas = self.iface.mapCanvas()

        # Enable on the fly projection by default
        canvas.mapRenderer().setProjectionsEnabled(True)
        self.connect_layer_listener()
        self.grpQuestion.setEnabled(False)
        self.grpQuestion.setVisible(False)
        self.set_ok_button_status()
        # Rubber band for showing analysis extent etc.
        # Added by Tim in version 2.1.0
        self.last_analysis_rubberband = None
        # This is a rubber band to show what the AOI of the
        # next analysis will be. Also added in 2.1.0
        self.next_analysis_rubberband = None
        # Whether to show rubber band of last and next scenario
        self.show_rubber_bands = False

        self.read_settings()  # get_project_layers called by this

    def set_dock_title(self):
        """Set the title of the dock using the current version of InaSAFE."""
        long_version = get_version()
        LOGGER.debug('Version: %s' % long_version)
        tokens = long_version.split('.')
        version = '%s.%s.%s' % (tokens[0], tokens[1], tokens[2])
        try:
            version_type = tokens[3].split('2')[0]
        except IndexError:
            version_type = 'final'
            # Allowed version names: ('alpha', 'beta', 'rc', 'final')
        self.setWindowTitle(self.tr('InaSAFE %s %s' % (version, version_type)))

    def enable_signal_receiver(self):
        """Setup dispatcher for all available signal from Analysis."""
        dispatcher.connect(
            self.show_busy,
            signal=BUSY_SIGNAL)

        dispatcher.connect(
            self.hide_busy,
            signal=NOT_BUSY_SIGNAL)

        dispatcher.connect(
            self.completed,
            signal=ANALYSIS_DONE_SIGNAL)

    def disable_signal_receiver(self):
        """Remove dispatcher for all available signal from Analysis."""
        dispatcher.disconnect(
            self.show_busy,
            signal=BUSY_SIGNAL)

        dispatcher.disconnect(
            self.hide_busy,
            signal=NOT_BUSY_SIGNAL)

        dispatcher.disconnect(
            self.completed,
            signal=ANALYSIS_DONE_SIGNAL)

    def enable_messaging(self):
        """Set up the dispatcher for messaging."""
        # Set up dispatcher for dynamic messages
        # Dynamic messages will not clear the message queue so will be appended
        # to existing user messages
        # noinspection PyArgumentEqualDefault
        dispatcher.connect(
            self.wvResults.dynamic_message_event,
            signal=DYNAMIC_MESSAGE_SIGNAL,
            sender=dispatcher.Any)
        # Set up dispatcher for static messages
        # Static messages clear the message queue and so the display is 'reset'
        # noinspection PyArgumentEqualDefault
        dispatcher.connect(
            self.wvResults.static_message_event,
            signal=STATIC_MESSAGE_SIGNAL,
            sender=dispatcher.Any)
        # Set up dispatcher for error messages
        # Error messages clear the message queue and so the display is 'reset'
        # noinspection PyArgumentEqualDefault
        dispatcher.connect(
            self.wvResults.error_message_event,
            signal=ERROR_MESSAGE_SIGNAL,
            sender=dispatcher.Any)

    def setup_button_connectors(self):
        """Setup signal/slot mechanisms for dock buttons."""
        self.pbnHelp.clicked.connect(self.show_help)
        self.pbnPrint.clicked.connect(self.print_map)
        self.pbnRunStop.clicked.connect(self.accept)
        self.about_button.clicked.connect(self.about)

    def about(self):
        """Open the About dialog."""
        # noinspection PyTypeChecker
        dialog = AboutDialog(self)
        dialog.show()

    def show_static_message(self, message):
        """Send a static message to the message viewer.

        Static messages cause any previous content in the MessageViewer to be
        replaced with new content.

        :param message: An instance of our rich message class.
        :type message: Message

        """
        dispatcher.send(
            signal=STATIC_MESSAGE_SIGNAL,
            sender=self,
            message=message)

    def show_dynamic_message(self, message):
        """Send a dynamic message to the message viewer.

        Dynamic messages are appended to any existing content in the
        MessageViewer.

        :param message: An instance of our rich message class.
        :type message: Message

        """
        dispatcher.send(
            signal=DYNAMIC_MESSAGE_SIGNAL,
            sender=self,
            message=message)

    def show_error_message(self, error_message):
        """Send an error message to the message viewer.

        Error messages cause any previous content in the MessageViewer to be
        replaced with new content.

        :param error_message: An instance of our rich error message class.
        :type error_message: ErrorMessage
        """
        dispatcher.send(
            signal=ERROR_MESSAGE_SIGNAL,
            sender=self,
            message=error_message)
        self.hide_busy()

    def read_settings(self):
        """Set the dock state from QSettings.

        Do this on init and after changing options in the options dialog.
        """

        settings = QtCore.QSettings()
        flag = settings.value(
            'inasafe/useThreadingFlag', False, type=bool)
        self.run_in_thread_flag = flag

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

        # whether to clip hazard and exposure layers to the view port
        self.clip_to_viewport = settings.value(
            'inasafe/clip_to_viewport', True, type=bool)

        # whether to 'hard clip' layers (e.g. cut buildings in half if they
        # lie partially in the AOI
        self.clip_hard = settings.value(
            'inasafe/clip_hard', False, type=bool)

        # whether to show or not postprocessing generated layers
        self.show_intermediate_layers = settings.value(
            'inasafe/show_intermediate_layers', False, type=bool)

        # whether to show or not dev only options
        self.developer_mode = settings.value(
            'inasafe/developer_mode', False, type=bool)

        # whether to show or not a custom Logo
        self.organisation_logo_path = settings.value(
            'inasafe/organisation_logo_path',
            default_organisation_logo_path(),
            type=str)
        flag = bool(settings.value(
            'inasafe/showOrganisationLogoInDockFlag', True, type=bool))

        if self.organisation_logo_path and flag:
            dock_width = self.width()
            self.organisation_logo.setMaximumWidth(dock_width)
            self.organisation_logo.setPixmap(
                QtGui.QPixmap(self.organisation_logo_path))
            self.organisation_logo.show()
        else:
            self.organisation_logo.hide()

        flag = bool(settings.value(
            'inasafe/showRubberBands', False, type=bool))
        self.show_rubber_bands = flag

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
        self.iface.mapCanvas().extentsChanged.connect(
            self.show_next_analysis_extent)

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
            self.show_next_analysis_extent)

    def getting_started_message(self):
        """Generate a message for initial application state.

        :returns: Information for the user on how to get started.
        :rtype: Message
        """
        message = m.Message()
        message.add(LOGO_ELEMENT)
        message.add(m.Heading('Getting started', **INFO_STYLE))
        notes = m.Paragraph(
            self.tr(
                'These are the minimum steps you need to follow in order '
                'to use InaSAFE:'))
        message.add(notes)
        basics_list = m.NumberedList()
        basics_list.add(m.Paragraph(
            self.tr('Add at least one '),
            m.ImportantText(self.tr('hazard'), **KEYWORD_STYLE),
            self.tr(' layer (e.g. earthquake MMI) to QGIS.')))
        basics_list.add(m.Paragraph(
            self.tr('Add at least one '),
            m.ImportantText(self.tr('exposure'), **KEYWORD_STYLE),
            self.tr(' layer (e.g. structures) to QGIS.')))
        basics_list.add(m.Paragraph(
            self.tr(
                'Make sure you have defined keywords for your hazard and '
                'exposure layers. You can do this using the keywords icon '),
            m.Image(
                'qrc:/plugins/inasafe/show-keyword-editor.svg',
                **SMALL_ICON_STYLE),
            self.tr(' in the InaSAFE toolbar.')))
        basics_list.add(m.Paragraph(
            self.tr('Click on the '),
            m.ImportantText(self.tr('Run'), **KEYWORD_STYLE),
            self.tr(' button below.')))
        message.add(basics_list)

        message.add(m.Heading('Limitations', **WARNING_STYLE))
        caveat_list = m.NumberedList()
        for limitation in limitations():
            caveat_list.add(limitation)
        message.add(caveat_list)

        message.add(m.Heading('Disclaimer', **WARNING_STYLE))
        message.add(m.Paragraph(disclaimer()))

        return message

    def ready_message(self):
        """Helper to create a message indicating inasafe is ready.

        :returns Message: A localised message indicating we are ready to run.
        """
        # What does this todo mean? TS
        # TODO refactor impact_functions so it is accessible and user here
        title = m.Heading(
            self.tr('Ready'), **PROGRESS_UPDATE_STYLE)
        notes = m.Paragraph(self.tr(
            'You can now proceed to run your model by clicking the'),
            m.EmphasizedText(self.tr('Run'), **KEYWORD_STYLE),
            self.tr('button.'))
        message = m.Message(LOGO_ELEMENT, title, notes)
        return message

    def not_ready_message(self):
        """Help to create a message indicating inasafe is NOT ready.

        .. note:: Assumes a valid hazard and exposure layer are loaded.

        :returns Message: A localised message indicating we are not ready.
        """
        #myHazardFilename = self.getHazardLayer().source()
        # noinspection PyTypeChecker
        hazard_keywords = str(
            self.keyword_io.read_keywords(self.get_hazard_layer()))
        #myExposureFilename = self.getExposureLayer().source()
        # noinspection PyTypeChecker
        exposure_keywords = str(
            self.keyword_io.read_keywords(self.get_exposure_layer()))
        heading = m.Heading(
            self.tr('No valid functions:'), **WARNING_STYLE)
        notes = m.Paragraph(self.tr(
            'No functions are available for the inputs you have specified. '
            'Try selecting a different combination of inputs. Please '
            'consult the user manual for details on what constitute '
            'valid inputs for a given risk function.'))
        hazard_heading = m.Heading(
            self.tr('Hazard keywords:'), **INFO_STYLE)
        hazard_keywords = m.Paragraph(hazard_keywords)
        exposure_heading = m.Heading(
            self.tr('Exposure keywords:'), **INFO_STYLE)
        exposure_keywords = m.Paragraph(exposure_keywords)
        message = m.Message(
            heading,
            notes,
            exposure_heading,
            exposure_keywords,
            hazard_heading,
            hazard_keywords)
        return message

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
        :rtype: (Boolean, Message)

        Example::

            flag,message = self.validate()
        """
        if self.busy:
            return False, None
        hazard_index = self.cboHazard.currentIndex()
        exposure_index = self.cboExposure.currentIndex()
        if hazard_index == -1 or exposure_index == -1:
            message = self.getting_started_message()
            return False, message

        if self.cboFunction.currentIndex() == -1:
            message = self.not_ready_message()
            return False, message
        else:
            message = self.ready_message()
            return True, message

    # noinspection PyPep8Naming
    @pyqtSlot(int)
    def on_cboHazard_currentIndexChanged(self, index):
        """Automatic slot executed when the Hazard combo is changed.

        This is here so that we can see if the ok button should be enabled.

        :param index: The index number of the selected hazard layer.

        """
        # Add any other logic you might like here...
        del index
        self.get_functions()
        self.toggle_aggregation_combo()
        self.set_ok_button_status()
        self.show_next_analysis_extent()

    # noinspection PyPep8Naming
    @pyqtSlot(int)
    def on_cboExposure_currentIndexChanged(self, index):
        """Automatic slot executed when the Exposure combo is changed.

        This is here so that we can see if the ok button should be enabled.

        :param index: The index number of the selected exposure layer.

        """
        # Add any other logic you might like here...
        del index
        self.get_functions()
        self.toggle_aggregation_combo()
        self.set_ok_button_status()
        self.show_next_analysis_extent()

    # noinspection PyPep8Naming
    @pyqtSlot(int)
    def on_cboFunction_currentIndexChanged(self, index):
        """Automatic slot executed when the Function combo is changed.

        This is here so that we can see if the ok button should be enabled.

        :param index: The index number of the selected function.
        """
        # Add any other logic you might like here...
        if index > -1:
            function_id = self.get_function_id()

            functions = get_safe_impact_function(function_id)
            self.active_function = functions[0][function_id]
            self.function_parameters = None
            if hasattr(self.active_function, 'parameters'):
                self.function_parameters = self.active_function.parameters
            self.set_function_options_status()
        else:
            self.function_parameters = None
            self.set_function_options_status()

        self.toggle_aggregation_combo()
        self.set_ok_button_status()

    def toggle_aggregation_combo(self):
        """Toggle the aggregation combo enabled status.

        Whether the combo is toggled on or off will depend on the current dock
        status.
        """
        selected_hazard_layer = self.get_hazard_layer()
        selected_exposure_layer = self.get_exposure_layer()

        # more than 1 because No aggregation is always there
        if ((self.cboAggregation.count() > 1) and
                (selected_hazard_layer is not None) and
                (selected_exposure_layer is not None)):
            self.cboAggregation.setEnabled(True)
        else:
            self.cboAggregation.setCurrentIndex(0)
            self.cboAggregation.setEnabled(False)

    def set_ok_button_status(self):
        """Helper function to set the ok button status based on form validity.
        """
        button = self.pbnRunStop
        flag, message = self.validate()

        button.setEnabled(flag)
        if message is not None:
            self.show_static_message(message)

    def set_function_options_status(self):
        """Helper function to toggle the tool function button based on context.

        If there are function parameters to configure then enable it, otherwise
        disable it.
        """
        # Check if function_parameters initialized
        if self.function_parameters is None:
            self.toolFunctionOptions.setEnabled(False)
        else:
            self.toolFunctionOptions.setEnabled(True)

    # noinspection PyPep8Naming
    @pyqtSlot()
    def on_toolFunctionOptions_clicked(self):
        """Automatic slot executed when toolFunctionOptions is clicked."""
        dialog = FunctionOptionsDialog(self)
        dialog.set_dialog_info(self.get_function_id())
        dialog.build_form(self.function_parameters)

        if dialog.exec_():
            self.active_function.parameters = dialog.result()
            self.function_parameters = self.active_function.parameters

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
        self.cboAggregation.blockSignals(False)
        self.cboExposure.blockSignals(False)
        self.cboHazard.blockSignals(False)

    def block_signals(self):
        """Prevent the combos and dock listening for event changes."""
        self.disconnect_layer_listener()
        self.cboAggregation.blockSignals(True)
        self.cboExposure.blockSignals(True)
        self.cboHazard.blockSignals(True)

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

        On invocation, this method will populate cboHazard, cboExposure and
        cboAggregation on the dialog with a list of available layers.

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

        #for arg in args:
        #    LOGGER.debug('get_layer argument: %s' % arg)
        # Map registry may be invalid if QGIS is shutting down
        registry = QgsMapLayerRegistry.instance()
        canvas_layers = self.iface.mapCanvas().layers()
        # MapLayers returns a QMap<QString id, QgsMapLayer layer>
        layers = registry.mapLayers().values()

        # For issue #618
        if len(layers) == 0:
            self.show_static_message(self.getting_started_message())
            return

        self.get_layers_lock = True

        # Make sure this comes after the checks above to prevent signal
        # disconnection without reconnection
        self.block_signals()
        self.save_state()
        self.cboHazard.clear()
        self.cboExposure.clear()
        self.cboAggregation.clear()

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
            source = str(layer.id())
            # See if there is a title for this layer, if not,
            # fallback to the layer's filename

            # noinspection PyBroadException
            try:
                title = self.keyword_io.read_keywords(layer, 'title')
            except NoKeywordsFoundError:
                # Skip if there are no keywords at all
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
                title = safeTr(title)
            # Register title with layer
            if title and self.set_layer_from_title_flag:
                layer.setLayerName(title)

            # NOTE : I commented out this due to
            # https://github.com/AIFDR/inasafe/issues/528
            # check if layer is a vector polygon layer
            # if isPolygonLayer(layer):
            #     addComboItemInOrder(self.cboAggregation, title,
            #                         source)
            #     self.aggregationLayers.append(layer)

            # Find out if the layer is a hazard or an exposure
            # layer by querying its keywords. If the query fails,
            # the layer will be ignored.
            # noinspection PyBroadException
            try:
                category = self.keyword_io.read_keywords(layer, 'category')
            except:  # pylint: disable=W0702
                # continue ignoring this layer
                continue

            if category == 'hazard':
                add_ordered_combo_item(self.cboHazard, title, source)
            elif category == 'exposure':
                add_ordered_combo_item(self.cboExposure, title, source)
            elif category == 'postprocessing':
                add_ordered_combo_item(self.cboAggregation, title, source)

        self.unblock_signals()
        # handle the cboAggregation combo
        self.cboAggregation.insertItem(0, self.tr('Entire area'))
        self.cboAggregation.setCurrentIndex(0)
        self.toggle_aggregation_combo()

        # Now populate the functions list based on the layers loaded
        self.get_functions()
        self.restore_state()
        self.grpQuestion.setEnabled(True)
        self.grpQuestion.setVisible(True)
        # Note: Don't change the order of the next two lines otherwise there
        # will be a lot of unneeded looping around as the signal is handled
        self.connect_layer_listener()
        self.get_layers_lock = False
        #ensure the dock keywords info panel is updated
        #make sure to do this after the lock is released!
        self.layer_changed(self.iface.activeLayer())
        # Make sure to update the analysis area preview
        self.show_next_analysis_extent()

    def get_functions(self):
        """Obtain a list of impact functions from the impact calculator.
        """
        # remember what the current function is
        original_function = self.cboFunction.currentText()
        self.cboFunction.clear()

        # Get the keyword dictionaries for hazard and exposure
        hazard_layer = self.get_hazard_layer()
        if hazard_layer is None:
            return
        exposure_layer = self.get_exposure_layer()
        if exposure_layer is None:
            return
        # noinspection PyTypeChecker
        hazard_keywords = self.keyword_io.read_keywords(hazard_layer)
        # We need to add the layer type to the returned keywords
        if hazard_layer.type() == QgsMapLayer.VectorLayer:
            hazard_keywords['layertype'] = 'vector'
        elif hazard_layer.type() == QgsMapLayer.RasterLayer:
            hazard_keywords['layertype'] = 'raster'

        # noinspection PyTypeChecker
        exposure_keywords = self.keyword_io.read_keywords(exposure_layer)
        # We need to add the layer type to the returned keywords
        if exposure_layer.type() == QgsMapLayer.VectorLayer:
            exposure_keywords['layertype'] = 'vector'
        elif exposure_layer.type() == QgsMapLayer.RasterLayer:
            exposure_keywords['layertype'] = 'raster'

        # Find out which functions can be used with these layers
        func_list = [hazard_keywords, exposure_keywords]
        try:
            func_dict = available_functions(func_list)
            # Populate the hazard combo with the available functions
            for myFunctionID in func_dict:
                function = func_dict[myFunctionID]
                function_title = get_function_title(function)

                # KEEPING THESE STATEMENTS FOR DEBUGGING UNTIL SETTLED
                #print
                #print 'function (ID)', myFunctionID
                #print 'function', function
                #print 'Function title:', function_title

                # Provide function title and ID to function combo:
                # function_title is the text displayed in the combo
                # myFunctionID is the canonical identifier
                add_ordered_combo_item(
                    self.cboFunction,
                    function_title,
                    data=myFunctionID)
        except Exception, e:
            raise e

        self.restore_function_state(original_function)

    def get_hazard_layer(self):
        """Get the QgsMapLayer currently selected in the hazard combo.

        Obtain QgsMapLayer id from the userrole of the QtCombo for hazard
        and return it as a QgsMapLayer.

        :returns: The currently selected map layer in the hazard combo.
        :rtype: QgsMapLayer

        """
        index = self.cboHazard.currentIndex()
        if index < 0:
            return None
        layer_id = self.cboHazard.itemData(
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

        index = self.cboExposure.currentIndex()
        if index < 0:
            return None
        layer_id = self.cboExposure.itemData(
            index, QtCore.Qt.UserRole)
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    def get_aggregation_layer(self):

        """Get the QgsMapLayer currently selected in the post processing combo.

        Obtain QgsMapLayer id from the userrole of the QtCombo for post
        processing combo return it as a QgsMapLayer.

        :returns: None if no aggregation is selected or cboAggregation is
                disabled, otherwise a polygon layer.
        :rtype: QgsMapLayer, QgsVectorLayer or None
        """

        no_selection_value = 0
        index = self.cboAggregation.currentIndex()
        if index <= no_selection_value:
            return None
        layer_id = self.cboAggregation.itemData(
            index, QtCore.Qt.UserRole)
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    @pyqtSlot('bool')
    def toggle_rubber_bands(self, flag):
        """Disabled/enable the rendering of rubber bands.

        :param flag: Flag to indicate if drawing of bands is active.
        :type flag: bool
        """
        self.show_rubber_bands = flag
        settings = QSettings()
        settings.setValue('inasafe/showRubberBands', flag)
        if not flag:
            self.hide_extent()
            self.hide_next_analysis_extent()
        else:
            self.show_next_analysis_extent()

    def hide_next_analysis_extent(self):
        """Hide the rubber band showing extent of the next analysis."""
        if self.next_analysis_rubberband is not None:
            self.next_analysis_rubberband.reset(QGis.Polygon)
            self.next_analysis_rubberband = None

    def show_next_analysis_extent(self):
        """Update the rubber band showing where the next analysis extent is.

        Primary purpose of this slot is to draw a rubber band of where the
        analysis will be carried out based on valid intersection between
        layers.

        This slot is called on pan, zoom, layer visibility changes and

        .. versionadded:: 2.1.0
        """
        if not self.show_rubber_bands:
            return

        self.hide_next_analysis_extent()
        try:
            # Temporary only, it will be rewrite if we run an analysis
            if not self.analysis.clip_parameters:
                self.setup_analysis()
            extent = self.analysis.clip_parameters[1]

        except (AttributeError, InsufficientOverlapError):
            # No layers loaded etc.
            return

        if not (isinstance(extent, list) or isinstance(extent, QgsRectangle)):
            return
        if isinstance(extent, list):
            # noinspection PyBroadException
            try:
                extent = QgsRectangle(
                    extent[0],
                    extent[1],
                    extent[2],
                    extent[3])
            except:  # yes we want to catch all exception types here
                return

        extent = self._geo_extent_to_canvas_crs(extent)
        self.next_analysis_rubberband = QgsRubberBand(
            self.iface.mapCanvas(), True)
        self.next_analysis_rubberband.setColor(QColor(0, 255, 0, 100))
        self.next_analysis_rubberband.setWidth(1)
        update_display_flag = False
        point = QgsPoint(extent.xMinimum(), extent.yMinimum())
        self.next_analysis_rubberband.addPoint(point, update_display_flag)
        point = QgsPoint(extent.xMaximum(), extent.yMinimum())
        self.next_analysis_rubberband.addPoint(point, update_display_flag)
        point = QgsPoint(extent.xMaximum(), extent.yMaximum())
        self.next_analysis_rubberband.addPoint(point, update_display_flag)
        point = QgsPoint(extent.xMinimum(), extent.yMaximum())
        self.next_analysis_rubberband.addPoint(point, update_display_flag)
        point = QgsPoint(extent.xMinimum(), extent.yMinimum())
        update_display_flag = True
        self.next_analysis_rubberband.addPoint(point, update_display_flag)

    def hide_extent(self):
        """Clear extent rubber band if any.

        This method can safely be called even if there is no rubber band set.

        .. versionadded:: 2.1.0
        """
        if self.last_analysis_rubberband is not None:
            self.last_analysis_rubberband.reset(QGis.Polygon)
            self.last_analysis_rubberband = None

    def _geo_extent_to_canvas_crs(self, extent):
        """Transform a bounding box into the CRS of the canvas.

        :param extent: An extent in geographic coordinates.
        :type extent: QgsRectangle

        :returns: The extent in CRS of the canvas.
        :rtype: QgsRectangle
        """

        # make sure the extent is in the same crs as the canvas
        dest_crs = self.iface.mapCanvas().mapRenderer().destinationCrs()
        source_crs = QgsCoordinateReferenceSystem()
        source_crs.createFromSrid(4326)
        transform = QgsCoordinateTransform(source_crs, dest_crs)
        extent = transform.transformBoundingBox(extent)
        return extent

    def show_extent(self, extent):
        """Show an extent as a rubber band on the canvas.

        .. seealso:: hide_extent()

        .. versionadded:: 2.1.0

        :param extent: A rectangle to display on the canvas. If parameter is
            a list it should be in the form of [xmin, ymin, xmax, ymax]
            otherwise it will be silently ignored and this method will
            do nothing.
        :type extent: QgsRectangle, list
        """
        if not self.show_rubber_bands:
            return

        if not (isinstance(extent, list) or isinstance(extent, QgsRectangle)):
            return
        if isinstance(extent, list):
            # noinspection PyBroadException
            try:
                extent = QgsRectangle(
                    extent[0],
                    extent[1],
                    extent[2],
                    extent[3])
            except:  # yes we want to catch all exception types here
                return

        self.hide_extent()
        extent = self._geo_extent_to_canvas_crs(extent)

        self.last_analysis_rubberband = QgsRubberBand(
            self.iface.mapCanvas(), True)
        self.last_analysis_rubberband.setColor(QColor(255, 0, 0, 100))
        self.last_analysis_rubberband.setWidth(2)
        update_display_flag = False
        point = QgsPoint(extent.xMinimum(), extent.yMinimum())
        self.last_analysis_rubberband.addPoint(point, update_display_flag)
        point = QgsPoint(extent.xMaximum(), extent.yMinimum())
        self.last_analysis_rubberband.addPoint(point, update_display_flag)
        point = QgsPoint(extent.xMaximum(), extent.yMaximum())
        self.last_analysis_rubberband.addPoint(point, update_display_flag)
        point = QgsPoint(extent.xMinimum(), extent.yMaximum())
        self.last_analysis_rubberband.addPoint(point, update_display_flag)
        point = QgsPoint(extent.xMinimum(), extent.yMinimum())
        update_display_flag = True
        self.last_analysis_rubberband.addPoint(point, update_display_flag)

    def accept(self):
        """Execute analysis when run button is clicked.

        .. todo:: FIXME (Tim) We may have to implement some polling logic
            because the button click accept() function and the updating
            of the web view after model completion are asynchronous (when
            threading mode is enabled especially)
        """
        self.enable_signal_receiver()
        try:
            if self.get_aggregation_layer():
                original_keywords = self.keyword_io.read_keywords(
                    self.get_aggregation_layer())
                self.runtime_keywords_dialog = KeywordsDialog(
                    self.iface.mainWindow(),
                    self.iface,
                    self,
                    self.get_aggregation_layer())
                self.runtime_keywords_dialog.accepted.connect(self.accept)
                self.runtime_keywords_dialog.rejected.connect(
                    partial(self.accept_cancelled, original_keywords))

            self.enable_busy_cursor()
            self.setup_analysis()
            self.show_next_analysis_extent()
            extent = self.analysis.clip_parameters[1]
            self.show_extent(extent)
            # Start the analysis
            self.analysis.run_analysis()
        except InsufficientOverlapError:
            return  # Will abort the analysis if there is exception
        except InvalidAggregationKeywords:
            self.runtime_keywords_dialog.set_layer(
                self.get_aggregation_layer())
            # disable gui elements that should not be applicable for this
            self.runtime_keywords_dialog.radExposure.setEnabled(False)
            self.runtime_keywords_dialog.radHazard.setEnabled(False)
            self.runtime_keywords_dialog.setModal(True)
            self.runtime_keywords_dialog.show()
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
                self.analysis.force_memory = True
                self.accept()

        # Set back analysis to not ignore memory warning
        self.analysis.force_memory = False
        self.disable_signal_receiver()

    def accept_cancelled(self, old_keywords):
        """Deal with user cancelling post processing option dialog.

        :param old_keywords: A keywords dictionary that should be reinstated.
        :type old_keywords: dict
        """
        LOGGER.debug('Setting old dictionary: ' + str(old_keywords))
        self.keyword_io.write_keywords(
            self.analysis.aggregator.layer, old_keywords)
        self.hide_busy()
        self.set_ok_button_status()

    def show_busy(self):
        """Hide the question group box and enable the busy cursor."""
        self.grpQuestion.setEnabled(False)
        self.grpQuestion.setVisible(False)
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.repaint()
        QtGui.qApp.processEvents()
        self.busy = True

    def analysis_error(self, exception, message):
        """A helper to spawn an error and halt processing.

        An exception will be logged, busy status removed and a message
        displayed.

        :param message: an ErrorMessage to display
        :type message: ErrorMessage, Message

        :param exception: An exception that was raised
        :type exception: Exception
        """
        QtGui.qApp.restoreOverrideCursor()
        self.hide_busy()
        LOGGER.exception(message)
        message = get_error_message(exception, context=message)
        self.show_error_message(message)
        self.analysisDone.emit(False)

    def setup_analysis(self):
        """Setup analysis to make it ready to work."""
        self.analysis = Analysis()
        # Layers
        self.analysis.hazard_layer = self.get_hazard_layer()
        self.analysis.exposure_layer = self.get_exposure_layer()
        self.analysis.aggregation_layer = self.get_aggregation_layer()

        # noinspection PyTypeChecker
        self.analysis.hazard_keyword = self.keyword_io.read_keywords(
            self.get_hazard_layer())
        # noinspection PyTypeChecker
        self.analysis.exposure_keyword = self.keyword_io.read_keywords(
            self.get_exposure_layer())
        # Need to check since aggregation layer is not mandatory
        if self.analysis.aggregation_layer:
            self.analysis.aggregation_keyword = self.keyword_io.read_keywords(
                self.get_aggregation_layer())

        # Impact Functions
        self.analysis.impact_function_id = self.get_function_id()
        self.analysis.impact_function_parameters = self.function_parameters

        # Variables
        self.analysis.clip_hard = self.clip_hard
        self.analysis.show_intermediate_layers = self.show_intermediate_layers
        self.analysis.run_in_thread_flag = self.run_in_thread_flag
        self.analysis.map_canvas = self.iface.mapCanvas()
        self.analysis.clip_to_viewport = self.clip_to_viewport

        try:
            self.analysis.setup_analysis()
        except InsufficientOverlapError as e:
            raise e

    def completed(self):
        """Slot activated when the process is done.
        """
        # save the ID of the function that just ran
        self.last_used_function = self.get_function_id()

        # Try to run completion code
        try:
            from datetime import datetime
            LOGGER.debug(datetime.now())
            LOGGER.debug('get engine impact layer')
            LOGGER.debug(self.analysis is None)
            engine_impact_layer = self.analysis.get_impact_layer()

            # Load impact layer into QGIS
            qgis_impact_layer = read_impact_layer(engine_impact_layer)
            self.layer_changed(qgis_impact_layer)
            report = self.show_results(
                qgis_impact_layer, engine_impact_layer)
        except Exception, e:  # pylint: disable=W0703

            # FIXME (Ole): This branch is not covered by the tests
            self.analysis_error(e, self.tr('Error loading impact layer.'))
        else:
            # On success, display generated report
            impact_path = qgis_impact_layer.source()
            message = m.Message(report)
            #message.add(m.Heading(self.tr('View processing log as HTML'),
            #                      **INFO_STYLE))
            #message.add(m.Link('file://%s' % self.wvResults.log_path))
            self.show_static_message(message)
            self.wvResults.impact_path = impact_path

        self.save_state()
        self.hide_busy()
        self.analysisDone.emit(True)

    def show_results(self, qgis_impact_layer, engine_impact_layer):
        """Helper function for slot activated when the process is done.

        :param qgis_impact_layer: A QGIS layer representing the impact.
        :type qgis_impact_layer: QgsMapLayer, QgsVectorLayer, QgsRasterLayer

        :param engine_impact_layer: A safe_layer representing the impact.
        :type engine_impact_layer: ReadLayer

        :returns: Provides a report for writing to the dock.
        :rtype: str
        """
        keywords = self.keyword_io.read_keywords(qgis_impact_layer)

        # write postprocessing report to keyword
        output = self.analysis.postprocessor_manager.get_output(
            self.analysis.aggregator.aoi_mode)
        keywords['postprocessing_report'] = output.to_html(
            suppress_newlines=True)
        self.keyword_io.write_keywords(qgis_impact_layer, keywords)

        # Get tabular information from impact layer
        report = m.Message()
        report.add(LOGO_ELEMENT)
        report.add(m.Heading(self.tr(
            'Analysis Results'), **INFO_STYLE))
        report.add(self.keyword_io.read_keywords(
            qgis_impact_layer, 'impact_summary'))

        # Get requested style for impact layer of either kind
        style = engine_impact_layer.get_style_info()
        style_type = engine_impact_layer.get_style_type()

        # Determine styling for QGIS layer
        if engine_impact_layer.is_vector:
            LOGGER.debug('myEngineImpactLayer.is_vector')
            if not style:
                # Set default style if possible
                pass
            elif style_type == 'categorizedSymbol':
                LOGGER.debug('use categorized')
                set_vector_categorized_style(qgis_impact_layer, style)
            elif style_type == 'graduatedSymbol':
                LOGGER.debug('use graduated')
                set_vector_graduated_style(qgis_impact_layer, style)

        elif engine_impact_layer.is_raster:
            LOGGER.debug('myEngineImpactLayer.is_raster')
            if not style:
                qgis_impact_layer.setDrawingStyle("SingleBandPseudoColor")
                #qgis_impact_layer.setColorShadingAlgorithm(
                #    QgsRasterLayer.PseudoColorShader)
            else:
                setRasterStyle(qgis_impact_layer, style)

        else:
            message = self.tr(
                'Impact layer %s was neither a raster or a vector layer') % (
                    qgis_impact_layer.source())
            # noinspection PyExceptionInherit
            raise ReadLayerError(message)

        # Add layers to QGIS
        layers_to_add = []
        if self.show_intermediate_layers:
            layers_to_add.append(self.analysis.aggregator.layer)
        layers_to_add.append(qgis_impact_layer)
        QgsMapLayerRegistry.instance().addMapLayers(layers_to_add)
        # make sure it is active in the legend - needed since QGIS 2.4
        self.iface.setActiveLayer(qgis_impact_layer)
        # then zoom to it
        if self.zoom_to_impact_flag:
            self.iface.zoomToActiveLayer()
        if self.hide_exposure_flag:
            exposure_layer = self.get_exposure_layer()
            legend = self.iface.legendInterface()
            legend.setLayerVisible(exposure_layer, False)

        self.restore_state()

        # append postprocessing report
        report.add(output.to_html())
        # Layer attribution comes last
        report.add(impact_attribution(keywords).to_html(True))
        # Return text to display in report panel
        return report

    @staticmethod
    def show_help():
        """Load the help text into the system browser."""
        show_context_help(context='dock')

    def hide_busy(self):
        """A helper function to indicate processing is done."""
        #self.pbnRunStop.setText('Run')
        if self.runner:
            try:
                self.runner.done.disconnect(self.aggregate)
            except TypeError:
                # happens when object is not connected - see #621
                pass
        self.pbnShowQuestion.setVisible(True)
        self.grpQuestion.setEnabled(True)
        self.grpQuestion.setVisible(False)
        # for #706 - if the exposure is hidden
        # due to self.hide_exposure_flag being enabled
        # we may have no exposure layers left
        # so we handle that here and disable run
        if self.cboExposure.count() == 0:
            self.pbnRunStop.setEnabled(False)
        else:
            self.pbnRunStop.setEnabled(True)
        self.repaint()
        self.disable_busy_cursor()
        self.busy = False

    @staticmethod
    def enable_busy_cursor():
        """Set the hourglass enabled and stop listening for layer changes."""
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

    @staticmethod
    def disable_busy_cursor():
        """Disable the hourglass cursor and listen for layer changes."""
        QtGui.qApp.restoreOverrideCursor()

    def show_impact_keywords(self, keywords):
        """Show the keywords for an impact layer.

        .. note:: The print button will be enabled if this method is called.
            Also, the question group box will be hidden and the 'show
            question' button will be shown.

        :param keywords: A keywords dictionary.
        :type keywords: dict
        """
        LOGGER.debug('Showing Impact Keywords')
        if 'impact_summary' not in keywords:
            return

        report = m.Message()
        report.add(LOGO_ELEMENT)
        report.add(m.Heading(self.tr(
            'Analysis Results'), **INFO_STYLE))
        report.add(m.Text(keywords['impact_summary']))
        if 'postprocessing_report' in keywords:
            report.add(keywords['postprocessing_report'])
        report.add(impact_attribution(keywords))
        self.pbnPrint.setEnabled(True)
        self.show_static_message(report)
        # also hide the question and show the show question button
        self.pbnShowQuestion.setVisible(True)
        self.grpQuestion.setEnabled(True)
        self.grpQuestion.setVisible(False)

    def show_generic_keywords(self, keywords):
        """Show the keywords defined for the active layer.

        .. note:: The print button will be disabled if this method is called.

        :param keywords: A keywords dictionary.
        :type keywords: dict
        """
        LOGGER.debug('Showing Generic Keywords')
        report = m.Message()
        report.add(LOGO_ELEMENT)
        report.add(m.Heading(self.tr(
            'Layer keywords:'), **INFO_STYLE))
        report.add(m.Text(self.tr(
            'The following keywords are defined for the active layer:')))
        self.pbnPrint.setEnabled(False)
        keywords_list = m.BulletedList()
        for keyword in keywords:
            value = keywords[keyword]

            # Translate titles explicitly if possible
            if keyword == 'title':
                value = safeTr(value)
                # Add this keyword to report
            key = m.ImportantText(
                self.tr(keyword.capitalize()))
            value = str(value)
            keywords_list.add(m.Text(key, value))

        report.add(keywords_list)
        self.pbnPrint.setEnabled(False)
        self.show_static_message(report)

    def show_no_keywords_message(self):
        """Show a message indicating that no keywords are defined.

        .. note:: The print button will be disabled if this method is called.
        """
        LOGGER.debug('Showing No Keywords Message')
        report = m.Message()
        report.add(LOGO_ELEMENT)
        report.add(m.Heading(self.tr(
            'Layer keywords missing:'), **WARNING_STYLE))
        context = m.Message(
            m.Text(self.tr(
                'No keywords have been defined for this layer yet. If '
                'you wish to use it as an impact or hazard layer in a '
                'scenario, please use the keyword editor. You can open'
                ' the keyword editor by clicking on the ')),
            m.Image('qrc:/plugins/inasafe/show-keyword-editor.svg',
                    attributes='width=24 height=24'),
            m.Text(self.tr(
                ' icon in the toolbar, or choosing Plugins -> InaSAFE '
                '-> Keyword Editor from the menu bar.')))
        report.add(context)
        self.pbnPrint.setEnabled(False)
        self.show_static_message(report)

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

        if layer is None:
            LOGGER.debug('Layer is None')
            return

        try:
            keywords = self.keyword_io.read_keywords(layer)

            if 'impact_summary' in keywords:
                self.show_impact_keywords(keywords)
            else:
                self.show_generic_keywords(keywords)

        except (KeywordNotFoundError,
                HashNotFoundError,
                InvalidParameterError,
                NoKeywordsFoundError):
            self.show_no_keywords_message()
            # Append the error message.
            # error_message = get_error_message(e)
            # self.show_error_message(error_message)
            return
        except Exception, e:
            error_message = get_error_message(e)
            self.show_error_message(error_message)
            return

    def save_state(self):
        """Save the current state of the ui to an internal class member.

        The saved state can be restored again easily using
        :func:`restore_state`
        """
        state = {
            'hazard': self.cboHazard.currentText(),
            'exposure': self.cboExposure.currentText(),
            'function': self.cboFunction.currentText(),
            'aggregation': self.cboAggregation.currentText(),
            'report': self.wvResults.page().currentFrame().toHtml()}
        self.state = state

    def restore_state(self):
        """Restore the state of the dock to the last known state."""
        if self.state is None:
            return
        for myCount in range(0, self.cboExposure.count()):
            item_text = self.cboExposure.itemText(myCount)
            if item_text == self.state['exposure']:
                self.cboExposure.setCurrentIndex(myCount)
                break
        for myCount in range(0, self.cboHazard.count()):
            item_text = self.cboHazard.itemText(myCount)
            if item_text == self.state['hazard']:
                self.cboHazard.setCurrentIndex(myCount)
                break
        for myCount in range(0, self.cboAggregation.count()):
            item_text = self.cboAggregation.itemText(myCount)
            if item_text == self.state['aggregation']:
                self.cboAggregation.setCurrentIndex(myCount)
                break
        self.restore_function_state(self.state['function'])
        self.wvResults.setHtml(self.state['report'])

    def restore_function_state(self, original_function):
        """Restore the function combo to a known state.

        :param original_function: Name of function that should be selected.
        :type original_function: str

        """
        # Restore previous state of combo
        for count in range(0, self.cboFunction.count()):
            item_text = self.cboFunction.itemText(count)
            if item_text == original_function:
                self.cboFunction.setCurrentIndex(count)
                break

    def print_map(self):
        """Slot to open impact report dialog that used to tune report
        when print map button pressed."""
        print_dialog = ImpactReportDialog(self.iface)
        if not print_dialog.exec_() == QtGui.QDialog.Accepted:
            self.show_dynamic_message(
                m.Message(
                    m.Heading(self.tr('Map Creator'), **WARNING_STYLE),
                    m.Text(self.tr('Report generation cancelled!'))))
            return

        use_full_extent = print_dialog.analysis_extent_radio.isChecked()
        create_pdf = print_dialog.create_pdf
        if print_dialog.default_template_radio.isChecked():
            template_path = print_dialog.template_combo.itemData(
                print_dialog.template_combo.currentIndex())
        else:
            template_path = print_dialog.template_path.text()

        print_map = Map(self.iface)
        if self.iface.activeLayer() is None:
            # noinspection PyCallByClass,PyTypeChecker
            QtGui.QMessageBox.warning(
                self,
                self.tr('InaSAFE'),
                self.tr('Please select a valid impact layer before '
                        'trying to print.'))
            return

        self.show_dynamic_message(
            m.Message(
                m.Heading(self.tr('Map Creator'), **PROGRESS_UPDATE_STYLE),
                m.Text(self.tr('Preparing map and report'))))

        # Set all the map components
        print_map.set_impact_layer(self.iface.activeLayer())
        if use_full_extent:
            map_crs = self.iface.mapCanvas().mapRenderer().destinationCrs()
            layer_crs = self.iface.activeLayer().crs()
            layer_extent = self.iface.activeLayer().extent()
            if map_crs != layer_crs:
                transform = QgsCoordinateTransform(layer_crs, map_crs)
                layer_extent = transform.transformBoundingBox(layer_extent)
            print_map.set_extent(layer_extent)
        else:
            print_map.set_extent(self.iface.mapCanvas().extent())

        settings = QSettings()
        logo_path = settings.value(
            'inasafe/organisation_logo_path', '', type=str)
        if logo_path != '':
            print_map.set_organisation_logo(logo_path)

        disclaimer_text = settings.value(
            'inasafe/reportDisclaimer', '', type=str)
        if disclaimer_text != '':
            print_map.set_disclaimer(disclaimer_text)

        north_arrow_path = settings.value(
            'inasafe/north_arrow_path', '', type=str)
        if north_arrow_path != '':
            print_map.set_north_arrow_image(north_arrow_path)

        template_warning_verbose = bool(settings.value(
            'inasafe/template_warning_verbose', True, type=bool))

        print_map.set_template(template_path)

        # Get missing elements on template
        # AG: This is a quick fix to adapt with QGIS >= 2.4
        # https://github.com/AIFDR/inasafe/issues/911
        # We'll need to refactor report modules
        component_ids = ['safe-logo', 'north-arrow', 'organisation-logo',
                         'impact-map', 'impact-legend']
        missing_elements = []
        template_file = QtCore.QFile(template_path)
        template_file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
        template_content = template_file.readAll()
        for component_id in component_ids:
            if component_id not in template_content:
                missing_elements.append(component_id)

        if template_warning_verbose and len(missing_elements) != 0:
            title = self.tr('Template is missing some elements')
            question = self.tr(
                'The composer template you are printing to is missing '
                'these elements: %s. Do you still want to continue') % (
                    ', '.join(missing_elements))
            # noinspection PyCallByClass,PyTypeChecker
            answer = QtGui.QMessageBox.question(
                self,
                title,
                question,
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

            if answer == QtGui.QMessageBox.No:
                return

        LOGGER.debug('Map Title: %s' % print_map.map_title())
        if create_pdf:
            print_map.setup_composition()
            print_map.load_template()
            if print_map.map_title() is not None:
                default_file_name = print_map.map_title() + '.pdf'
            else:
                self.show_error_message(
                    self.tr('Keyword "map_title" not found.'))
                return

            default_file_name = default_file_name.replace(' ', '_')
            # noinspection PyCallByClass,PyTypeChecker
            map_pdf_path = QtGui.QFileDialog.getSaveFileName(
                self, self.tr('Write to PDF'),
                os.path.join(temp_dir(), default_file_name),
                self.tr('Pdf File (*.pdf)'))
            map_pdf_path = str(map_pdf_path)

            if map_pdf_path is None or map_pdf_path == '':
                self.show_dynamic_message(
                    m.Message(
                        m.Heading(self.tr('Map Creator'), **WARNING_STYLE),
                        m.Text(self.tr('Printing cancelled!'))))
                return

            table_file_name = os.path.splitext(map_pdf_path)[0] + '_table.pdf'
            html_renderer = HtmlRenderer(page_dpi=print_map.page_dpi)
            keywords = self.keyword_io.read_keywords(self.iface.activeLayer())
            html_pdf_path = html_renderer.print_impact_table(
                keywords, filename=table_file_name)

            try:
                print_map.make_pdf(map_pdf_path)
            except Exception, e:  # pylint: disable=W0703
                # FIXME (Ole): This branch is not covered by the tests
                report = get_error_message(e)
                self.show_error_message(report)

            # Make sure the file paths can wrap nicely:
            wrapped_map_path = map_pdf_path.replace(os.sep, '<wbr>' + os.sep)
            wrapped_html_path = html_pdf_path.replace(os.sep, '<wbr>' + os.sep)
            status = m.Message(
                m.Heading(self.tr('Map Creator'), **INFO_STYLE),
                m.Paragraph(self.tr(
                    'Your PDF was created....opening using the default PDF '
                    'viewer on your system. The generated pdfs were saved '
                    'as:')),
                m.Paragraph(wrapped_map_path),
                m.Paragraph(self.tr('and')),
                m.Paragraph(wrapped_html_path))

            # noinspection PyCallByClass,PyTypeChecker,PyTypeChecker
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl('file:///' + html_pdf_path,
                            QtCore.QUrl.TolerantMode))
            # noinspection PyCallByClass,PyTypeChecker,PyTypeChecker
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl('file:///' + map_pdf_path,
                            QtCore.QUrl.TolerantMode))
            self.show_dynamic_message(status)
        else:
            # AG:
            # See https://github.com/AIFDR/inasafe/issues/911
            # We need to set the composition to the composer before loading
            # the template
            print_map.setup_composition()
            self.composer = self.iface.createNewComposer()
            self.composer.setComposition(print_map.composition)
            print_map.load_template()

            # Zoom to Full Extent
            number_pages = print_map.composition.numPages()
            if number_pages > 0:
                height = \
                    print_map.composition.paperHeight() * number_pages + \
                    print_map.composition.spaceBetweenPages() * \
                    (number_pages - 1)
                self.composer.fitInView(
                    0, 0,
                    print_map.composition.paperWidth() + 1,
                    height + 1,
                    QtCore.Qt.KeepAspectRatio)

        self.hide_busy()

    def get_function_id(self, index=None):
        """Get the canonical impact function ID for the currently selected
           function (or the specified combo entry if theIndex is supplied.

        :param index: Optional index position in the combo that you
            want the function id for. Defaults to None. If not set / None
            the currently selected combo item's function id will be
            returned.
        :type index: int

        :returns: Id of the currently selected function.
        :rtype: str
        """
        if index is None:
            index = self.cboFunction.currentIndex()
        item_data = self.cboFunction.itemData(index, QtCore.Qt.UserRole)
        function_id = '' if item_data is None else str(item_data)
        return function_id
