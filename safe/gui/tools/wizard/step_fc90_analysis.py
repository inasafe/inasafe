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

import os
import logging
# noinspection PyPackageRequirements
from PyQt4.QtCore import pyqtSignature, Qt, QDir
# noinspection PyPackageRequirements
from qgis.core import QgsMapLayerRegistry, QgsProject
from safe_extras.pydispatch import dispatcher
from safe.common.signals import (
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    ERROR_MESSAGE_SIGNAL,
    send_static_message,
    send_error_message,
)
from safe.utilities.i18n import tr
from safe.impact_function_v4.impact_function import ImpactFunction
from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe.reportv4.report_metadata import ReportMetadata
from safe.definitionsv4.report import standard_impact_report_metadata
from safe.reportv4.impact_report import ImpactReport as ImpactReportV4
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step import WizardStep

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')
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
        self.analysis_handler.print_map('pdf')

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnReportComposer_released(self):
        """Handle the Open Report in Web Broseer button release.

        .. note:: This is an automatic Qt slot
           executed when the Next button is released.
        """
        self.analysis_handler.print_map('composer')

    def setup_and_run_analysis(self):
        """Execute analysis after the tab is displayed"""
        # IFCW 4.0:

        # Show busy
        # show next analysis extent
        # Prepare impact function from wizard dialog user input
        self.impact_function = self.prepare_impact_function()
        # Prepare impact function
        status, message = self.impact_function.prepare()
        # Check status
        if status == 1:
            # self.hide_busy()
            LOGGER.info(tr(
                'The impact function will not be able to run because of the '
                'inputs.'))
            send_error_message(self, message)
            return
        if status == 2:
            # self.hide_busy()
            LOGGER.exception(tr(
                'The impact function will not be able to run because of a '
                'bug.'))
            send_error_message(self, message)
            return
        # Start the analysis
        status, message = self.impact_function.run()
        # Check status
        if status == 1:
            # self.hide_busy()
            LOGGER.info(tr(
                'The impact function could not run because of the inputs.'))
            send_error_message(self, message)
            return
        elif status == 2:
            # self.hide_busy()
            LOGGER.exception(tr(
                'The impact function could not run because of a bug.'))
            send_error_message(self, message)
            return

        LOGGER.info(tr('The impact function could run without errors.'))

        # Generate impact report
        self.generate_impact_report(self.impact_function)
        # Add layer to QGIS (perhaps create common method)
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
                self.parent.iface.setActiveLayer(layer)
            else:
                layer_node.setVisible(Qt.Unchecked)
        # Some if-s i.e. zoom, debug, hide exposure
        # Hide busy


    def set_widgets(self):
        """Set widgets on the Progress tab"""
        self.pbProgress.setValue(0)
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
        # impact_function.callback = self.progress_callback

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
            self.parent.iface,
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