# coding=utf-8
"""InaSAFE Wizard Step Analysis."""

import logging
import os

from qgis.PyQt import QtGui, QtCore
from qgis.PyQt.QtCore import pyqtSignature
from qgis.core import (
    QgsGeometry,
    QgsCoordinateReferenceSystem)

from safe import messaging as m
from safe.common.signals import send_static_message, send_error_message
from safe.definitions.constants import (
    ANALYSIS_FAILED_BAD_INPUT,
    ANALYSIS_FAILED_BAD_CODE,
    ANALYSIS_SUCCESS,
    PREPARE_FAILED_BAD_INPUT,
    PREPARE_FAILED_BAD_CODE,
    EXPOSURE,
    HAZARD_EXPOSURE_VIEW,
    HAZARD_EXPOSURE_BOUNDINGBOX
)
from safe.definitions.reports.components import (
    standard_impact_report_metadata_html)
from safe.gui.analysis_utilities import add_impact_layers_to_canvas
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.widgets.message import enable_messaging
from safe.impact_function.impact_function import ImpactFunction
from safe.messaging import styles
from safe.report.impact_report import ImpactReport
from safe.utilities.extent import Extent
from safe.utilities.gis import wkt_to_rectangle
from safe.utilities.i18n import tr
from safe.utilities.qt import enable_busy_cursor, disable_busy_cursor
from safe.utilities.settings import setting
from safe.utilities.utilities import basestring_to_message

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')
PROGRESS_UPDATE_STYLE = styles.PROGRESS_UPDATE_STYLE
INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
WARNING_STYLE = styles.RED_LEVEL_4_STYLE
KEYWORD_STYLE = styles.KEYWORD_STYLE
SUGGESTION_STYLE = styles.GREEN_LEVEL_4_STYLE
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE
LOGO_ELEMENT = m.Brand()
FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcAnalysis(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Analysis."""

    def __init__(self, parent):
        """Init method."""
        WizardStep.__init__(self, parent)

        enable_messaging(self.results_webview)
        self.iface = parent.iface
        self.impact_function = None
        self.extent = Extent(self.iface)
        self.zoom_to_impact_flag = None
        self.hide_exposure_flag = None

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

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
        """Execute analysis after the tab is displayed.

        Please check the code in dock.py accept(). It should follow
        approximately the same code.
        """
        self.show_busy()
        # Read user's settings
        self.read_settings()
        # Prepare impact function from wizard dialog user input
        self.impact_function = self.prepare_impact_function()

        # Prepare impact function
        status, message = self.impact_function.prepare()
        message = basestring_to_message(message)
        # Check status
        if status == PREPARE_FAILED_BAD_INPUT:
            self.hide_busy()
            LOGGER.warning(tr(
                'The impact function will not be able to run because of the '
                'inputs.'))
            LOGGER.warning(message.to_text())
            send_error_message(self, message)
            return status, message
        if status == PREPARE_FAILED_BAD_CODE:
            self.hide_busy()
            LOGGER.warning(tr(
                'The impact function was not able to be prepared because of a '
                'bug.'))
            LOGGER.exception(message.to_text())
            send_error_message(self, message)
            return status, message

        # Start the analysis
        status, message = self.impact_function.run()
        message = basestring_to_message(message)
        # Check status
        if status == ANALYSIS_FAILED_BAD_INPUT:
            self.hide_busy()
            LOGGER.warning(tr(
                'The impact function could not run because of the inputs.'))
            LOGGER.warning(message.to_text())
            send_error_message(self, message)
            return status, message
        elif status == ANALYSIS_FAILED_BAD_CODE:
            self.hide_busy()
            LOGGER.warning(tr(
                'The impact function could not run because of a bug.'))
            LOGGER.exception(message.to_text())
            send_error_message(self, message)
            return status, message

        LOGGER.info(tr('The impact function could run without errors.'))

        # Add result layer to QGIS
        add_impact_layers_to_canvas(
            self.impact_function, iface=self.parent.iface)

        # Some if-s i.e. zoom, debug, hide exposure
        if self.zoom_to_impact_flag:
            self.iface.zoomToActiveLayer()

        qgis_exposure = (
            QgsProject.instance().mapLayer(
                self.parent.exposure_layer.id()))
        if self.hide_exposure_flag:
            legend = self.iface.legendInterface()
            legend.setLayerVisible(qgis_exposure, False)

        # we only want to generate non pdf/qpt report
        html_components = [standard_impact_report_metadata_html]
        error_code, message = self.impact_function.generate_report(
            html_components)
        message = basestring_to_message(message)
        if error_code == ImpactReport.REPORT_GENERATION_FAILED:
            self.hide_busy()
            LOGGER.info(tr(
                'The impact report could not be generated.'))
            send_error_message(self, message)
            LOGGER.exception(message.to_text())
            return ANALYSIS_FAILED_BAD_CODE, message

        self.extent.set_last_analysis_extent(
            self.impact_function.analysis_extent,
            qgis_exposure.crs())

        # Hide busy
        self.hide_busy()
        # Setup gui if analysis is done
        self.setup_gui_analysis_done()
        return ANALYSIS_SUCCESS, None

    def set_widgets(self):
        """Set widgets on the Progress tab."""
        self.progress_bar.setValue(0)
        self.results_webview.setHtml('')
        self.pbnReportWeb.hide()
        self.pbnReportPDF.hide()
        self.pbnReportComposer.hide()
        self.lblAnalysisStatus.setText(tr('Running analysis...'))

    def read_settings(self):
        """Set the IF state from QSettings."""
        extent = setting('user_extent', None, str)
        if extent:
            extent = QgsGeometry.fromWkt(extent)
            if not extent.isGeosValid():
                extent = None

        crs = setting('user_extent_crs', None, str)
        if crs:
            crs = QgsCoordinateReferenceSystem(crs)
            if not crs.isValid():
                crs = None

        mode = setting('analysis_extents_mode', HAZARD_EXPOSURE_VIEW)
        if crs and extent and mode == HAZARD_EXPOSURE_BOUNDINGBOX:
            self.extent.set_user_extent(extent, crs)

        self.extent.show_rubber_bands = setting(
            'showRubberBands', False, bool)

        self.zoom_to_impact_flag = setting('setZoomToImpactFlag', True, bool)

        # whether exposure layer should be hidden after model completes
        self.hide_exposure_flag = setting('setHideExposureFlag', False, bool)

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
            impact_function.use_selected_features_only = (
                setting('useSelectedFeaturesOnly', False, bool))
        else:
            # self.extent.crs is the map canvas CRS.
            impact_function.crs = self.extent.crs
            mode = setting('analysis_extents_mode')
            if self.extent.user_extent:
                # This like a hack to transform a geometry to a rectangle.
                # self.extent.user_extent is a QgsGeometry.
                # impact_function.requested_extent needs a QgsRectangle.
                wkt = self.extent.user_extent.exportToWkt()
                impact_function.requested_extent = wkt_to_rectangle(wkt)

            elif mode == HAZARD_EXPOSURE_VIEW:
                impact_function.requested_extent = (
                    self.iface.mapCanvas().extent())

            elif mode == EXPOSURE:
                impact_function.use_exposure_view_only = True

        # We don't have any checkbox in the wizard for the debug mode.
        impact_function.debug_mode = False

        return impact_function

    def setup_gui_analysis_done(self):
        """Helper method to setup gui if analysis is done."""
        self.progress_bar.hide()
        self.lblAnalysisStatus.setText(tr('Analysis done.'))
        self.pbnReportWeb.show()
        self.pbnReportPDF.show()
        # self.pbnReportComposer.show()  # Hide until it works again.
        self.pbnReportPDF.clicked.connect(self.print_map)

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
            tr('Analysis status'), **INFO_STYLE))
        if message is not None:
            report.add(m.ImportantText(message['name']))
            report.add(m.Paragraph(message['description']))
        report.add(self.impact_function.performance_log_message())
        send_static_message(self, report)
        self.progress_bar.setMaximum(maximum_value)
        self.progress_bar.setValue(current_value)
        QtGui.QApplication.processEvents()

    def print_map(self):
        """Open impact report dialog used to tune report when printing."""
        # Check if selected layer is valid
        impact_layer = self.parent.iface.activeLayer()
        if impact_layer is None:
            # noinspection PyCallByClass,PyTypeChecker
            QtGui.QMessageBox.warning(
                self,
                'InaSAFE',
                tr(
                    'Please select a valid impact layer before trying to '
                    'print.'))
            return

        # Get output path from datastore
        # Fetch report for pdfs report
        report_path = os.path.dirname(impact_layer.source())
        output_paths = [
            os.path.join(
                report_path,
                'output/impact-report-output.pdf'),
            os.path.join(
                report_path,
                'output/inasafe-map-report-portrait.pdf'),
            os.path.join(
                report_path,
                'output/inasafe-map-report-landscape.pdf'),
        ]

        # Make sure the file paths can wrap nicely:
        wrapped_output_paths = [
            path.replace(os.sep, '<wbr>' + os.sep) for path in
            output_paths]

        # create message to user
        status = m.Message(
            m.Heading(tr('Map Creator'), **INFO_STYLE),
            m.Paragraph(tr(
                'Your PDF was created....opening using the default PDF '
                'viewer on your system. The generated pdfs were saved '
                'as:')))

        for path in wrapped_output_paths:
            status.add(m.Paragraph(path))

        send_static_message(self, status)

        for path in output_paths:
            # noinspection PyCallByClass,PyTypeChecker,PyTypeChecker
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl.fromLocalFile(path))

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        return tr('Analysis')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will see the summary of '
            'the analysis that you have run. You can get your PDF report or '
            'show the report in the web browser by clicking the <b>Generate '
            'PDF</b> and <b>Open in web browser</b> respectively. You can '
            'also click the <b>Finish</b> button to end the wizard session.'
        ).format(step_name=self.step_name)))
        return message
