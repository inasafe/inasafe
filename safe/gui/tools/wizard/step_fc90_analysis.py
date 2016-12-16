# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Function Centric Wizard Step: Analysis

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import logging
# noinspection PyPackageRequirements
from PyQt4 import QtGui
# noinspection PyPackageRequirements
from PyQt4.QtCore import pyqtSignature
# noinspection PyPackageRequirements
from safe_extras.pydispatch import dispatcher

from safe.utilities.i18n import tr
from safe.definitionsv4.constants import (
    ANALYSIS_FAILED_BAD_INPUT,
    ANALYSIS_FAILED_BAD_CODE,
    PREPARE_FAILED_BAD_INPUT,
    PREPARE_FAILED_BAD_CODE
)
from safe.common.signals import (
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    ERROR_MESSAGE_SIGNAL,
    send_static_message,
    send_error_message,
)
from safe.utilities.qt import enable_busy_cursor, disable_busy_cursor
from safe.impact_function_v4.impact_function import ImpactFunction
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.analysis_utilities import (
    generate_impact_report, add_impact_layer_to_QGIS)
from safe import messaging as m
from safe.messaging import styles

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')
PROGRESS_UPDATE_STYLE = styles.PROGRESS_UPDATE_STYLE
INFO_STYLE = styles.INFO_STYLE
WARNING_STYLE = styles.WARNING_STYLE
KEYWORD_STYLE = styles.KEYWORD_STYLE
SUGGESTION_STYLE = styles.SUGGESTION_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE
LOGO_ELEMENT = m.Brand()
FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcAnalysis(WizardStep, FORM_CLASS):
    """Function Centric Wizard Step: Analysis"""

    def __init__(self, parent):
        """Init method"""
        WizardStep.__init__(self, parent)

        self.enable_messaging()

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_fc_summary
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        return None

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnReportWeb_released(self):
        """Handle the Open Report in Web Browser button release.

        .. note:: This is an automatic Qt slot
           executed when the Next button is released.
        """
        self.results_webview.open_current_in_browser()

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnReportPDF_released(self):
        """Handle the Generate PDF button release.

        .. note:: This is an automatic Qt slot
           executed when the Next button is released.
        """
        LOGGER.debug('Generate PDF Button is not implemented')

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnReportComposer_released(self):
        """Handle the Open in composer button release.

        .. note:: This is an automatic Qt slot
           executed when the Next button is released.
        """
        LOGGER.debug('Open in composer Button is not implemented')

    def setup_and_run_analysis(self):
        """Execute analysis after the tab is displayed"""
        # IFCW 4.0:

        # Show busy
        self.show_busy()
        # show next analysis extent
        # Prepare impact function from wizard dialog user input
        self.impact_function = self.prepare_impact_function()
        # Prepare impact function
        status, message = self.impact_function.prepare()
        # Check status
        if status == PREPARE_FAILED_BAD_INPUT:
            self.hide_busy()
            LOGGER.info(tr(
                'The impact function will not be able to run because of the '
                'inputs.'))
            send_error_message(self, message)
            return
        if status == PREPARE_FAILED_BAD_CODE:
            self.hide_busy()
            LOGGER.exception(tr(
                'The impact function will not be able to run because of a '
                'bug.'))
            send_error_message(self, message)
            return
        # Start the analysis
        status, message = self.impact_function.run()
        # Check status
        if status == ANALYSIS_FAILED_BAD_INPUT:
            self.hide_busy()
            LOGGER.info(tr(
                'The impact function could not run because of the inputs.'))
            send_error_message(self, message)
            return
        elif status == ANALYSIS_FAILED_BAD_CODE:
            self.hide_busy()
            LOGGER.exception(tr(
                'The impact function could not run because of a bug.'))
            send_error_message(self, message)
            return

        LOGGER.info(tr('The impact function could run without errors.'))

        # Generate impact report
        generate_impact_report(self.impact_function, self.parent.iface)
        # Add result layer to QGIS
        add_impact_layer_to_QGIS(self.impact_function, self.parent.iface)

        # Some if-s i.e. zoom, debug, hide exposure
        # Hide busy
        self.hide_busy()
        # Setup gui if analysis is done
        self.setup_gui_analysis_done()

    def set_widgets(self):
        """Set widgets on the Progress tab"""
        self.progress_bar.setValue(0)
        self.results_webview.setHtml('')
        self.pbnReportWeb.hide()
        self.pbnReportPDF.hide()
        self.pbnReportComposer.hide()
        self.lblAnalysisStatus.setText(self.tr('Running analysis...'))

    # Notes(IS): Copied from dock. We should move this to more common place.
    # With the web view as the argument
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
            self.results_webview.static_message_event,
            signal=ERROR_MESSAGE_SIGNAL,
            sender=dispatcher.Any)

    def prepare_impact_function(self):
        """Create analysis as a representation of current situation of IFCW."""

        # Impact Functions
        impact_function = ImpactFunction()
        impact_function.callback = self.progress_callback

        # Layers
        impact_function.hazard = self.parent.hazard_layer
        impact_function.exposure = self.parent.exposure_layer
        aggregation = self.parent.aggregation_layer

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

        # Notes (IS): Always et debug as True for development.
        impact_function.debug_mode = True

        return impact_function

    def setup_gui_analysis_done(self):
        """Helper method to setup gui if analysis is done."""
        self.progress_bar.hide()
        self.lblAnalysisStatus.setText(tr('Analysis done.'))
        self.pbnReportWeb.show()
        self.pbnReportPDF.show()
        self.pbnReportComposer.show()

    def show_busy(self):
        """Lock buttons and enable the busy cursor."""
        self.progress_bar.show()
        self.parent.pbnNext.setEnabled(False)
        self.parent.pbnBack.setEnabled(False)
        self.parent.pbnCancel.setEnabled(False)
        self.parent.repaint()
        enable_busy_cursor()
        QtGui.qApp.processEvents()

    def hide_busy(self):
        """Unlock buttons A helper function to indicate processing is done."""
        self.progress_bar.hide()
        self.parent.pbnNext.setEnabled(True)
        self.parent.pbnBack.setEnabled(True)
        self.parent.pbnCancel.setEnabled(True)
        self.parent.repaint()
        disable_busy_cursor()

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
