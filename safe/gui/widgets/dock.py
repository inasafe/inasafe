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
__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import shutil
import logging
import json
from collections import OrderedDict
from datetime import datetime

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
from PyQt4.QtCore import Qt, pyqtSlot, QSettings, pyqtSignal

from safe.utilities.keyword_io import KeywordIO
from safe.utilities.utilities import (
    get_error_message,
    impact_attribution,
    add_ordered_combo_item,
    is_keyword_version_supported)
from safe.defaults import (
    disclaimer,
    default_north_arrow_path)
from safe.utilities.gis import (
    viewport_geo_array,
    extent_string_to_array,
    read_impact_layer,
    vector_geometry_string)
from safe.utilities.resources import (
    resources_path,
    get_ui_class)
from safe.utilities.qgis_utilities import (
    display_critical_message_bar,
    display_warning_message_bar,
    display_information_message_bar)
from safe.defaults import (
    limitations,
    supporters_logo_path)
from safe.utilities.styling import (
    setRasterStyle,
    set_vector_graduated_style,
    set_vector_categorized_style)
from safe.gui.tools.function_options_dialog import (
    FunctionOptionsDialog)
from safe.common.utilities import temp_dir
from safe.common.exceptions import ReadLayerError, TemplateLoadingError
from safe.common.version import get_version
from safe.common.signals import (
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    ERROR_MESSAGE_SIGNAL,
    BUSY_SIGNAL,
    NOT_BUSY_SIGNAL,
    ANALYSIS_DONE_SIGNAL,
    send_static_message,
    send_error_message,
    send_dynamic_message)
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
    MissingImpactReport,
    MetadataReadError
)
from safe.report.impact_report import ImpactReport
from safe.gui.tools.about_dialog import AboutDialog
from safe.gui.tools.help_dialog import HelpDialog
from safe.gui.tools.impact_report_dialog import ImpactReportDialog
from safe_extras.pydispatch import dispatcher
from safe.utilities.extent import Extent
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.utilities.unicode import get_unicode
from safe.impact_template.utilities import get_report_template

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

    analysis_done = pyqtSignal(bool)

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
        self.pbnShowQuestion.setVisible(False)
        self.enable_messaging()
        self.inasafe_version = get_version()

        self.set_dock_title()

        # Save reference to the QGIS interface
        self.iface = iface

        # Impact Function Manager to deal with IF needs
        self.impact_function_manager = ImpactFunctionManager()

        self.impact_function = None
        self.keyword_io = KeywordIO()
        self.active_impact_function = None
        self.impact_function_parameters = None
        self.state = None
        self.last_used_function = ''
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
        self.run_in_thread_flag = None
        self.show_only_visible_layers_flag = None
        self.set_layer_from_title_flag = None
        self.zoom_to_impact_flag = None
        self.hide_exposure_flag = None
        self.clip_hard = None
        self.map_canvas = None
        self.show_intermediate_layers = None
        self.developer_mode = None
        self.organisation_logo_path = None

        self.pbnPrint.setEnabled(False)
        self.runtime_keywords_dialog = None

        self.setup_button_connectors()

        if QGis.QGIS_VERSION_INT >= 20700:
            self.iface.layerSavedAs.connect(self.save_auxiliary_files)

        canvas = self.iface.mapCanvas()

        # Enable on the fly projection by default
        canvas.setCrsTransformEnabled(True)
        self.connect_layer_listener()
        self.grpQuestion.setEnabled(False)
        self.grpQuestion.setVisible(False)
        self.set_run_button_status()

        self.read_settings()  # get_project_layers called by this

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

    def getting_started_message(self):
        """Generate a message for initial application state.

        :returns: Information for the user on how to get started.
        :rtype: safe.messaging.Message
        """
        message = m.Message()
        message.add(LOGO_ELEMENT)
        message.add(m.Heading(self.tr('Getting started'), **INFO_STYLE))
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
                'exposure layers. You can do this using the '
                'keywords creation wizard '),
            m.Image(
                'file:///%s/img/icons/show-keyword-wizard.svg' %
                (resources_path()), **SMALL_ICON_STYLE),
            self.tr(' in the toolbar.')))
        basics_list.add(m.Paragraph(
            self.tr('Click on the '),
            m.ImportantText(self.tr('Run'), **KEYWORD_STYLE),
            self.tr(' button below.')))
        message.add(basics_list)

        message.add(m.Heading(self.tr('Limitations'), **WARNING_STYLE))
        caveat_list = m.NumberedList()
        for limitation in limitations():
            caveat_list.add(limitation)
        message.add(caveat_list)

        message.add(m.Heading(self.tr('Disclaimer'), **WARNING_STYLE))
        message.add(m.Paragraph(disclaimer()))

        return message

    def ready_message(self):
        """Helper to create a message indicating inasafe is ready.

        :returns Message: A localised message indicating we are ready to run.
        """
        title = m.Heading(
            self.tr('Ready'), **PROGRESS_UPDATE_STYLE)
        notes = m.Paragraph(
            self.tr(
                'You can now proceed to run your analysis by clicking the '),
            m.EmphasizedText(self.tr('Run'), **KEYWORD_STYLE),
            self.tr('button.'))
        message = m.Message(LOGO_ELEMENT, title, notes)
        return message

    def not_ready_message(self):
        """Help to create a message indicating inasafe is NOT ready.

        .. note:: Assumes a valid hazard and exposure layer are loaded.

        :returns: A localised message indicating we are not ready.
        :rtype: safe.messaging.Message
        """
        heading = m.Heading(
            self.tr('No valid functions'), **WARNING_STYLE)
        notes = m.Paragraph(self.tr(
            'No functions are available for the inputs you have specified. '
            'Try selecting a different combination of inputs. Please '
            'consult the user manual for details on what constitute '
            'valid inputs for a given risk function.'))
        hazard_heading = m.Heading(
            self.tr('Hazard keywords'), **INFO_STYLE)
        hazard_keywords = KeywordIO(self.get_hazard_layer()).to_message(
            show_header=False)
        exposure_heading = m.Heading(
            self.tr('Exposure keywords'), **INFO_STYLE)
        exposure_keywords = KeywordIO(self.get_exposure_layer()).to_message(
            show_header=False)
        message = m.Message(
            heading,
            notes,
            exposure_heading,
            exposure_keywords,
            hazard_heading,
            hazard_keywords)
        return message

    def no_overlap_message(self):
        """Helper which returns a message indicating no valid overlap."""
        return self.tr(
            'Currently there are no overlapping extents between '
            'the hazard layer, the exposure layer and the user '
            'defined analysis area. Try zooming to the analysis '
            'area, clearing the analysis area or defining a new '
            'one using the analysis area definition tool.')

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
        hazard_index = self.cboHazard.currentIndex()
        exposure_index = self.cboExposure.currentIndex()
        if hazard_index == -1 or exposure_index == -1:
            message = self.getting_started_message()
            return False, message

        if self.cboFunction.currentIndex() == -1:
            message = self.not_ready_message()
            return False, message
        # Now check if extents are ok for #1811
        else:
            message = self.ready_message()
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
            self.disable_busy_cursor()

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
        self.set_run_button_status()
        self.draw_rubber_bands()

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
        self.set_run_button_status()
        self.draw_rubber_bands()

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

            function = self.impact_function_manager.get(function_id)
            self.active_impact_function = function
            self.impact_function_parameters = None
            if hasattr(self.active_impact_function, 'parameters'):
                self.impact_function_parameters = \
                    self.active_impact_function.parameters
            self.set_function_options_status()
        else:
            self.impact_function_parameters = None
            self.set_function_options_status()

        self.toggle_aggregation_combo()
        self.set_run_button_status()

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

    def set_run_button_status(self):
        """Helper function to set the run button status based on form validity.
        """
        button = self.pbnRunStop
        flag, message = self.validate()

        button.setEnabled(flag)
        if message is not None:
            send_static_message(self, message)

    def set_function_options_status(self):
        """Helper function to toggle the tool function button based on context.

        If there are function parameters to configure then enable it, otherwise
        disable it.
        """
        # Check if function_parameters initialized
        if self.impact_function_parameters is None:
            self.toolFunctionOptions.setEnabled(False)
        else:
            self.toolFunctionOptions.setEnabled(True)

    # noinspection PyPep8Naming
    @pyqtSlot()
    def on_toolFunctionOptions_clicked(self):
        """Automatic slot executed when toolFunctionOptions is clicked."""
        dialog = FunctionOptionsDialog(self)
        dialog.set_dialog_info(self.get_function_id())
        dialog.build_form(self.impact_function_parameters)

        if dialog.exec_():
            self.active_impact_function.parameters = dialog.result()
            self.impact_function_parameters = \
                self.active_impact_function.parameters

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

        # for arg in args:
        # LOGGER.debug('get_layer argument: %s' % arg)
        # Map registry may be invalid if QGIS is shutting down
        registry = QgsMapLayerRegistry.instance()
        canvas_layers = self.iface.mapCanvas().layers()
        # MapLayers returns a QMap<QString id, QgsMapLayer layer>
        layers = registry.mapLayers().values()

        # For issue #618
        if len(layers) == 0:
            send_static_message(self, self.getting_started_message())
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
            #     addComboItemInOrder(self.cboAggregation, title,
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
                add_ordered_combo_item(self.cboHazard, title, source)
            elif layer_purpose == 'exposure':
                add_ordered_combo_item(self.cboExposure, title, source)
            elif layer_purpose == 'aggregation':
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
        self.pbnShowQuestion.setVisible(False)
        # Note: Don't change the order of the next two lines otherwise there
        # will be a lot of unneeded looping around as the signal is handled
        self.connect_layer_listener()
        self.get_layers_lock = False
        # ensure the dock keywords info panel is updated
        # make sure to do this after the lock is released!
        self.layer_changed(self.iface.activeLayer())
        # Make sure to update the analysis area preview
        self.draw_rubber_bands()

    def get_functions(self):
        """Obtain a list of impact functions from the IF manager."""
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
            # noinspection PyTypeChecker
            hazard_keywords['layer_geometry'] = vector_geometry_string(
                hazard_layer)
        elif hazard_layer.type() == QgsMapLayer.RasterLayer:
            hazard_keywords['layer_geometry'] = 'raster'

        # noinspection PyTypeChecker
        exposure_keywords = self.keyword_io.read_keywords(exposure_layer)
        # We need to add the layer type to the returned keywords
        if exposure_layer.type() == QgsMapLayer.VectorLayer:
            # noinspection PyTypeChecker
            exposure_keywords['layer_geometry'] = vector_geometry_string(
                exposure_layer)
        elif exposure_layer.type() == QgsMapLayer.RasterLayer:
            exposure_keywords['layer_geometry'] = 'raster'

        # Find out which functions can be used with these layers
        try:
            # from pprint import pprint
            # pprint(hazard_keywords)
            # pprint(exposure_keywords)
            # print '---------------------------------------------------------'
            impact_functions = self.impact_function_manager.filter_by_keywords(
                hazard_keywords, exposure_keywords)
            # Populate the hazard combo with the available functions
            for impact_function in impact_functions:
                function_id = self.impact_function_manager.get_function_id(
                    impact_function)
                function_title = \
                    self.impact_function_manager.get_function_title(
                        impact_function)

                # Provide function title and ID to function combo:
                # function_title is the text displayed in the combo
                # function_name is the canonical identifier
                add_ordered_combo_item(
                    self.cboFunction,
                    function_title,
                    data=function_id)
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
        self.extent.show_rubber_bands = flag
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
                clip_parameters = self.impact_function.clip_parameters
                self.extent.show_last_analysis_extent(
                    clip_parameters['adjusted_geo_extent'])  # red
            except (AttributeError, TypeError):
                pass

    def accept(self):
        """Execute analysis when run button is clicked.

        .. todo:: FIXME (Tim) We may have to implement some polling logic
            because the button click accept() function and the updating
            of the web view after model completion are asynchronous (when
            threading mode is enabled especially)
        """
        self.enable_signal_receiver()
        try:
            self.enable_busy_cursor()
            self.show_next_analysis_extent()
            self.impact_function = self.prepare_impact_function()
            clip_parameters = self.impact_function.clip_parameters
            self.extent.show_last_analysis_extent(
                clip_parameters['adjusted_geo_extent'])

            # Start the analysis
            self.impact_function.run_analysis()
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
            self.disable_busy_cursor()
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
            # Set back analysis to not ignore memory warning
            if self.impact_function:
                self.impact_function.force_memory = False
            self.disable_signal_receiver()

    def accept_cancelled(self, old_keywords):
        """Deal with user cancelling post processing option dialog.

        :param old_keywords: A keywords dictionary that should be reinstated.
        :type old_keywords: dict
        """
        LOGGER.debug('Setting old dictionary: ' + str(old_keywords))
        self.keyword_io.write_keywords(
            self.impact_function.aggregator.layer, old_keywords)
        self.hide_busy()
        self.set_run_button_status()

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
        self.hide_busy()
        LOGGER.exception(message)
        message = get_error_message(exception, context=message)
        send_error_message(self, message)
        self.analysis_done.emit(False)

    def prepare_impact_function(self):
        """Create analysis as a representation of current situation of dock."""

        # Impact Functions
        impact_function = self.impact_function_manager.get(
            self.get_function_id())
        impact_function.parameters = self.impact_function_parameters

        # Layers
        impact_function.hazard = self.get_hazard_layer()
        impact_function.exposure = self.get_exposure_layer()
        impact_function.aggregation = self.get_aggregation_layer()

        # Variables
        impact_function.clip_hard = self.clip_hard
        impact_function.show_intermediate_layers = \
            self.show_intermediate_layers
        viewport = viewport_geo_array(self.iface.mapCanvas())
        impact_function.viewport_extent = viewport
        if self.extent.user_extent:
            impact_function.requested_extent = self.extent.user_extent
            impact_function.requested_extent_crs = self.extent.user_extent_crs

        return impact_function

    def add_above_layer(self, new_layer, *existing_layers):
        """Add a layer (e.g. impact layer) above another layer in the legend.

        .. versionadded:: 3.2

        .. note:: This method works in QGIS 2.4 and better only. In
            earlier versions it will just add the layer to the top of the
            layer stack.

        .. seealso:: issue #2322

        :param existing_layers: Layers which the new layer
            should be added above.
        :type existing_layers: QgsMapLayer

        :param new_layer: The new layer being added. An assumption is made
            that the newly added layer is not already loaded in the legend
            or the map registry.
        :type new_layer: QgsMapLayer

        """
        # Some existing layers might be None, ie the aggregation layer #2948.
        existing_layers = [l for l in existing_layers if l is not None]
        if not len(existing_layers) or new_layer is None:
            return

        registry = QgsMapLayerRegistry.instance()

        if QGis.QGIS_VERSION_INT < 20400:
            # True flag adds layer directly to legend
            registry.addMapLayer(existing_layer, True)
            return

        # False flag prevents layer being added to legend
        registry.addMapLayer(new_layer, False)
        minimum_index = len(QgsProject.instance().layerTreeRoot().children())
        for layer in existing_layers:
            index = self.layer_legend_index(layer)
            if index < minimum_index:
                minimum_index = index
        root = QgsProject.instance().layerTreeRoot()
        root.insertLayer(minimum_index, new_layer)

    @staticmethod
    def layer_legend_index(layer):
        """Find out where in the legend layer stack a layer is.

        .. note:: This function requires QGIS 2.4 or greater to work. In older
            versions it will simply return 0.

        .. version_added:: 3.2

        :param layer: A map layer currently loaded in the legend.
        :type layer: QgsMapLayer

        :returns: An integer representing the z-order of the given layer in
            the legend tree. If the layer cannot be found, or the QGIS version
            is < 2.4 it will return 0.
        :rtype: int
        """
        if QGis.QGIS_VERSION_INT < 20400:
            return 0

        root = QgsProject.instance().layerTreeRoot()
        layer_id = layer.id()
        current_index = 0
        nodes = root.children()
        for node in nodes:
            # check if the node is a layer as opposed to a group
            if isinstance(node, QgsLayerTreeLayer):
                if layer_id == node.layerId():
                    return current_index
            current_index += 1
        return current_index

    def completed(self):
        """Slot activated when the process is done.
        """
        # save the ID of the function that just ran
        self.last_used_function = self.get_function_id()

        # Try to run completion code
        try:
            LOGGER.debug(datetime.now())
            LOGGER.debug(self.impact_function is None)
            report = self.show_results()
        except Exception, e:  # pylint: disable=W0703

            # FIXME (Ole): This branch is not covered by the tests
            self.analysis_error(e, self.tr('Error loading impact layer.'))
        else:
            # On success, display generated report
            # impact_path = qgis_impact_layer.source()
            message = m.Message(report)
            send_static_message(self, message)
            # self.wvResults.impact_path = impact_path

        self.save_state()
        self.hide_busy()
        self.analysis_done.emit(True)

    def show_results(self):
        """Helper function for slot activated when the process is done.

        .. versionchanged:: 3.2 - removed parameters.

        :returns: Provides a report for writing to the dock.
        :rtype: str
        """
        safe_impact_layer = self.impact_function.impact
        qgis_impact_layer = read_impact_layer(safe_impact_layer)
        # self.layer_changed(qgis_impact_layer)
        keywords = self.keyword_io.read_keywords(qgis_impact_layer)
        json_path = os.path.splitext(qgis_impact_layer.source())[0] + '.json'

        # write postprocessing report to keyword
        postprocessor_data = self.impact_function.postprocessor_manager.\
            get_json_data(self.impact_function.aggregator.aoi_mode)
        post_processing_report = m.Message()
        if os.path.exists(json_path):
            with open(json_path) as json_file:
                impact_data = json.load(
                    json_file, object_pairs_hook=OrderedDict)
                impact_data['post processing'] = postprocessor_data
                with open(json_path, 'w') as json_file_2:
                    json.dump(impact_data, json_file_2, indent=2)
        else:
            post_processing_report = self.impact_function.\
                postprocessor_manager.get_output(
                    self.impact_function.aggregator.aoi_mode)
            keywords['postprocessing_report'] = post_processing_report.to_html(
                suppress_newlines=True)
            self.keyword_io.write_keywords(qgis_impact_layer, keywords)

        # Get tabular information from impact layer
        report = m.Message()
        report.add(LOGO_ELEMENT)
        report.add(m.Heading(self.tr('Analysis Results'), **INFO_STYLE))
        # If JSON Impact Data Exist, use JSON
        json_path = qgis_impact_layer.source()[:-3] + 'json'
        LOGGER.debug('JSON Path %s' % json_path)
        if os.path.exists(json_path):
            impact_template = get_report_template(json_file=json_path)
            impact_report = impact_template.generate_message_report()
            report.add(impact_report)
        else:
            report.add(self.keyword_io.read_keywords(
                qgis_impact_layer, 'impact_summary'))
            # append postprocessing report
            report.add(post_processing_report.to_html())

        # Layer attribution comes last
        report.add(impact_attribution(keywords).to_html(True))

        # Get requested style for impact layer of either kind
        style = safe_impact_layer.get_style_info()
        style_type = safe_impact_layer.get_style_type()

        # Determine styling for QGIS layer
        if safe_impact_layer.is_vector:
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

        elif safe_impact_layer.is_raster:
            LOGGER.debug('myEngineImpactLayer.is_raster')
            if not style:
                qgis_impact_layer.setDrawingStyle("SingleBandPseudoColor")
            else:
                setRasterStyle(qgis_impact_layer, style)

        else:
            message = self.tr(
                'Impact layer %s was neither a raster or a vector layer') % (
                    qgis_impact_layer.source())
            # noinspection PyExceptionInherit
            raise ReadLayerError(message)

        legend = self.iface.legendInterface()

        # Insert the aggregation output above the input aggregation layer
        if self.show_intermediate_layers:
            self.add_above_layer(
                self.impact_function.aggregator.layer,
                self.get_aggregation_layer())
            legend.setLayerVisible(self.impact_function.aggregator.layer, True)

        if self.hide_exposure_flag:
            # Insert the impact always above the hazard
            self.add_above_layer(qgis_impact_layer, self.get_hazard_layer())
        else:
            # Insert the impact above the hazard and the exposure if
            # we don't hide the exposure. See #2899
            self.add_above_layer(
                qgis_impact_layer,
                self.get_exposure_layer(),
                self.get_hazard_layer())

        active_function = self.active_impact_function
        self.active_impact_function = active_function
        self.impact_function_parameters = \
            self.active_impact_function.parameters

        # In QGIS 2.14.2 and GDAL 1.11.3, if the exposure is in 3857,
        # the impact layer is in 54004, we need to change it. See issue #2790.
        if self.get_exposure_layer().crs().authid() == 'EPSG:3857':
            if qgis_impact_layer.crs().authid() != 'EPSG:3857':
                epsg_3857 = QgsCoordinateReferenceSystem(3857)
                qgis_impact_layer.setCrs(epsg_3857)

        # make sure it is active in the legend - needed since QGIS 2.4
        self.iface.setActiveLayer(qgis_impact_layer)
        # then zoom to it
        if self.zoom_to_impact_flag:
            self.iface.zoomToActiveLayer()
        if self.hide_exposure_flag:
            exposure_layer = self.get_exposure_layer()
            legend.setLayerVisible(exposure_layer, False)

        # Make the layer visible. Might be hidden by default. See #2925
        legend.setLayerVisible(qgis_impact_layer, True)

        self.restore_state()

        # Return text to display in report panel
        return report

    def show_help(self):
        """Open the About dialog."""
        # noinspection PyTypeChecker
        dialog = HelpDialog(self)
        dialog.show()

    def hide_busy(self):
        """A helper function to indicate processing is done."""
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
        while QtGui.qApp.overrideCursor() is not None and \
                QtGui.qApp.overrideCursor().shape() == QtCore.Qt.WaitCursor:
            QtGui.qApp.restoreOverrideCursor()

    def show_impact_report(self, layer, keywords):
        """Show the report for an impact layer.

        .. versionadded: 3.4

        .. note:: The print button will be enabled if this method is called.
            Also, the question group box will be hidden and the 'show
            question' button will be shown.

        :param layer: QgsMapLayer instance that is now active
        :type layer: QgsMapLayer, QgsRasterLayer, QgsVectorLayer

        :param keywords: A keywords dictionary.
        :type keywords: dict
        """
        LOGGER.debug('Showing Impact Report')
        # Init report
        report = m.Message()
        report.add(LOGO_ELEMENT)
        report.add(m.Heading(self.tr('Analysis Results'), **INFO_STYLE))

        impact_template = get_report_template(impact_layer_path=layer.source())
        impact_report = impact_template.generate_message_report()
        report.add(impact_report)

        if 'postprocessing_report' in keywords:
            report.add(keywords['postprocessing_report'])
        report.add(impact_attribution(keywords))
        self.pbnPrint.setEnabled(True)
        send_static_message(self, report)
        # also hide the question and show the show question button
        self.pbnShowQuestion.setVisible(True)
        self.grpQuestion.setEnabled(True)
        self.grpQuestion.setVisible(False)

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
        send_static_message(self, report)
        # also hide the question and show the show question button
        self.pbnShowQuestion.setVisible(True)
        self.grpQuestion.setEnabled(True)
        self.grpQuestion.setVisible(False)

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
        self.pbnPrint.setEnabled(False)
        message = keywords.to_message()
        send_static_message(self, message)

    def show_no_keywords_message(self):
        """Show a message indicating that no keywords are defined.

        .. note:: The print button will be disabled if this method is called.
        """
        LOGGER.debug('Showing No Keywords Message')
        report = m.Message()
        report.add(LOGO_ELEMENT)
        report.add(m.Heading(self.tr(
            'Layer keywords missing:'), **WARNING_STYLE))
        context = m.Paragraph(
            self.tr(
                'No keywords have been defined for this layer yet or there is '
                'an issue with the currently defined keywords and they need '
                'to be reviewed. If you wish to use this layer as an '
                'exposure, hazard, or aggregation layer in an analysis, '
                'please use the keyword wizard to update the keywords. You '
                'can open the wizard by clicking on the '),
            m.Image(
                'file:///%s/img/icons/'
                'show-keyword-wizard.svg' % resources_path(),
                **SMALL_ICON_STYLE),
            self.tr(
                ' icon in the toolbar.'))
        report.add(context)
        self.pbnPrint.setEnabled(False)
        send_static_message(self, report)

    def show_keyword_version_message(
            self, keyword_version, inasafe_version):
        """Show a message indicating that the keywords version is mismatch

        .. versionadded: 3.2

        :param keyword_version: The version of the layer's keywords
        :type keyword_version: str

        :param inasafe_version: The version of the InaSAFE
        :type inasafe_version: str

        .. note:: The print button will be disabled if this method is called.
        """
        LOGGER.debug('Showing Mismatch Version Message')
        report = m.Message()
        report.add(LOGO_ELEMENT)
        report.add(m.Heading(self.tr(
            'Layer Keyword\'s Version Mismatch:'), **WARNING_STYLE))
        context = m.Paragraph(
            self.tr(
                'Your layer\'s keyword\'s version (%s) does not match with '
                'your InaSAFE version (%s). If you wish to use it as an '
                'exposure, hazard, or aggregation layer in an analysis, '
                'please use the keyword wizard to update the keywords. You '
                'can open the wizard by clicking on the ' % (
                    keyword_version, inasafe_version)),
            m.Image(
                'file:///%s/img/icons/'
                'show-keyword-wizard.svg' % resources_path(),
                **SMALL_ICON_STYLE),
            self.tr(
                ' icon in the toolbar.'))
        report.add(context)
        self.pbnPrint.setEnabled(False)
        send_static_message(self, report)

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
            send_static_message(self, self.getting_started_message())

        # Now try to read the keywords and show them in the dock
        try:
            keywords = self.keyword_io.read_keywords(layer)

            if keywords.get('layer_purpose') == 'impact':
                try:
                    self.show_impact_report(layer, keywords)
                except MissingImpactReport:
                    self.show_impact_keywords(keywords)
            else:
                if 'keyword_version' not in keywords.keys():
                    self.show_keyword_version_message(
                        'No Version', self.inasafe_version)
                else:
                    keyword_version = str(keywords.get('keyword_version'))
                    supported = is_keyword_version_supported(
                        keyword_version)
                    if supported:
                        self.show_generic_keywords(layer)
                    else:
                        # Layer version is not supported
                        self.show_keyword_version_message(
                            keyword_version, self.inasafe_version)

        # TODO: maybe we need to split these apart more to give mode
        # TODO: granular error messages TS
        except (KeywordNotFoundError,
                HashNotFoundError,
                InvalidParameterError,
                NoKeywordsFoundError,
                AttributeError):
            # LOGGER.info(e.message)
            # Added this check in 3.2 for #1861
            active_layer = self.iface.activeLayer()
            if active_layer is None:
                send_static_message(self, self.getting_started_message())
            else:
                self.show_no_keywords_message()
            # Append the error message.
            # error_message = get_error_message(e)
            # send_error_message(self, error_message)
            return
        except Exception, e:  # pylint: disable=broad-except
            error_message = get_error_message(e)
            send_error_message(self, error_message)
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
        """Open impact report dialog used to tune report when printing."""
        # Check if selected layer is valid
        impact_layer = self.iface.activeLayer()
        if impact_layer is None:
            # noinspection PyCallByClass,PyTypeChecker
            QtGui.QMessageBox.warning(
                self,
                self.tr('InaSAFE'),
                self.tr('Please select a valid impact layer before '
                        'trying to print.'))
            return

        # Open Impact Report Dialog
        print_dialog = ImpactReportDialog(self.iface)
        if not print_dialog.exec_() == QtGui.QDialog.Accepted:
            send_dynamic_message(
                self,
                m.Message(
                    m.Heading(self.tr('Map Creator'), **WARNING_STYLE),
                    m.Text(self.tr('Report generation cancelled!'))))
            return

        # Get the extent of the map for report
        use_full_extent = print_dialog.analysis_extent_radio.isChecked()
        if use_full_extent:
            map_crs = self.iface.mapCanvas().mapRenderer().destinationCrs()
            layer_crs = self.iface.activeLayer().crs()
            layer_extent = self.iface.activeLayer().extent()
            if map_crs != layer_crs:
                # noinspection PyCallingNonCallable
                transform = QgsCoordinateTransform(layer_crs, map_crs)
                layer_extent = transform.transformBoundingBox(layer_extent)
            area_extent = layer_extent
        else:
            area_extent = self.iface.mapCanvas().extent()

        # Get selected template path to use
        if print_dialog.default_template_radio.isChecked():
            template_path = print_dialog.template_combo.itemData(
                print_dialog.template_combo.currentIndex())
        else:
            template_path = print_dialog.template_path.text()
            if not os.path.exists(template_path):
                # noinspection PyCallByClass,PyTypeChecker
                QtGui.QMessageBox.warning(
                    self,
                    self.tr('InaSAFE'),
                    self.tr('Please select a valid template before printing. '
                            'The template you choose does not exist.'))
                return

        # Open in PDF or Open in Composer Flag
        create_pdf_flag = print_dialog.create_pdf

        # Instantiate and prepare Report
        send_dynamic_message(
            self,
            m.Message(
                m.Heading(self.tr('Map Creator'), **PROGRESS_UPDATE_STYLE),
                m.Text(self.tr('Preparing map and report'))))

        impact_report = ImpactReport(self.iface, template_path, impact_layer)
        impact_report.extent = area_extent

        # Get other setting
        settings = QSettings()
        logo_path = settings.value(
            'inasafe/organisation_logo_path', '', type=str)
        impact_report.organisation_logo = logo_path

        disclaimer_text = settings.value(
            'inasafe/reportDisclaimer', '', type=str)
        impact_report.disclaimer = disclaimer_text

        north_arrow_path = settings.value(
            'inasafe/north_arrow_path', '', type=str)
        impact_report.north_arrow = north_arrow_path

        template_warning_verbose = bool(settings.value(
            'inasafe/template_warning_verbose', True, type=bool))

        # Check if there's missing elements needed in the template
        component_ids = ['safe-logo', 'north-arrow', 'organisation-logo',
                         'impact-map', 'impact-legend']
        impact_report.component_ids = component_ids
        length = len(impact_report.missing_elements)
        if template_warning_verbose and length != 0:
            title = self.tr('Template is missing some elements')
            question = self.tr(
                'The composer template you are printing to is missing '
                'these elements: %s. Do you still want to continue') % (
                    ', '.join(impact_report.missing_elements))
            # noinspection PyCallByClass,PyTypeChecker
            answer = QtGui.QMessageBox.question(
                self,
                title,
                question,
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if answer == QtGui.QMessageBox.No:
                return

        self.enable_busy_cursor()
        if create_pdf_flag:
            self.print_map_to_pdf(impact_report)
        else:
            self.open_map_in_composer(impact_report)

        self.disable_busy_cursor()

    def print_map_to_pdf(self, impact_report):
        """Print map to PDF given MapReport instance.

        :param impact_report: Impact Report instance that is ready to print
        :type impact_report: ImpactReport
        """
        impact_report.setup_composition()

        # Get Filename
        map_title = impact_report.map_title
        if map_title is not None:
            default_file_name = map_title + '.pdf'
            default_file_name = default_file_name.replace(' ', '_')
        else:
            send_error_message(
                self,
                self.tr('Keyword "map_title" not found.'))
            return

        # Get output path
        # noinspection PyCallByClass,PyTypeChecker
        output_path = QtGui.QFileDialog.getSaveFileName(
            self,
            self.tr('Write to PDF'),
            os.path.join(temp_dir(), default_file_name),
            self.tr('Pdf File (*.pdf)'))
        output_path = get_unicode(output_path)

        if output_path is None or output_path == '':
            # noinspection PyTypeChecker
            send_dynamic_message(
                self,
                m.Message(
                    m.Heading(self.tr('Map Creator'), **WARNING_STYLE),
                    m.Text(self.tr('Printing cancelled!'))))
            return

        try:
            map_pdf_path, table_pdf_path = impact_report.print_to_pdf(
                output_path)

            # Make sure the file paths can wrap nicely:
            wrapped_map_path = map_pdf_path.replace(os.sep, '<wbr>' + os.sep)
            wrapped_table_path = table_pdf_path.replace(
                os.sep, '<wbr>' + os.sep)
            status = m.Message(
                m.Heading(self.tr('Map Creator'), **INFO_STYLE),
                m.Paragraph(self.tr(
                    'Your PDF was created....opening using the default PDF '
                    'viewer on your system. The generated pdfs were saved '
                    'as:')),
                m.Paragraph(wrapped_map_path),
                m.Paragraph(self.tr('and')),
                m.Paragraph(wrapped_table_path))

            # noinspection PyCallByClass,PyTypeChecker,PyTypeChecker
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl.fromLocalFile(table_pdf_path))
            # noinspection PyCallByClass,PyTypeChecker,PyTypeChecker
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl.fromLocalFile(map_pdf_path))

            send_dynamic_message(self, status)
        except TemplateLoadingError, e:
            send_error_message(self, get_error_message(e))
        except Exception, e:  # pylint: disable=broad-except
            send_error_message(self, get_error_message(e))

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
            self.pbnRunStop.setEnabled(False)
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
            self.pbnRunStop.setEnabled(True)
        else:
            # For issue #618, #1811
            if self.show_only_visible_layers_flag:
                layer_count = self._visible_layers_count()
            else:
                layer_count = self._layer_count()

            if layer_count == 0:
                send_static_message(self, self.getting_started_message())
            else:
                show_warnings = settings.value(
                    'inasafe/show_extent_warnings',
                    True,
                    type=bool)
                if show_warnings:
                    message = self.no_overlap_message()
                    display_warning_message_bar(
                        self.tr('InaSAFE'),
                        self.tr('No overlapping extents'),
                        message)
            self.pbnRunStop.setEnabled(False)
            # For #2077 somewhat kludgy hack to prevent positive
            # message when we cant actually run
            match = self.tr(
                'You can now proceed to run your analysis by clicking the ')
            current_text = self.wvResults.page_to_text()
            if match in current_text:
                message = m.Message()
                message.add(LOGO_ELEMENT)
                message.add(m.Heading(self.tr(
                    'Insufficient overlap'), **WARNING_STYLE))
                message.add(self.no_overlap_message())
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
        :rtype: (bool, QgisRectangle)
        """

        try:
            # Temporary only, for checking the user extent
            impact_function = self.prepare_impact_function()
            clip_parameters = impact_function.clip_parameters
            return True, clip_parameters['adjusted_geo_extent']
        except (AttributeError, InsufficientOverlapError):
            return False, None
