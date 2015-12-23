# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid **GUI InaSAFE Wizard Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'qgis@borysjurgiel.pl'
__revision__ = '$Format:%H$'
__date__ = '21/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import logging

# noinspection PyPackageRequirements
from qgis.core import (
    QgsCoordinateTransform,
    QgsRectangle,
    QgsMapLayerRegistry,
    QgsCoordinateReferenceSystem)
# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
# noinspection PyPackageRequirements
from PyQt4.QtCore import QObject, QSettings, pyqtSignal

from safe.utilities.keyword_io import KeywordIO
from safe.utilities.utilities import (
    get_error_message,
    impact_attribution)
from safe.utilities.gis import extent_string_to_array, read_impact_layer
from safe.utilities.resources import (
    resources_path,
    resource_url)
from safe.defaults import (
    supporters_logo_path)
from safe.utilities.styling import (
    setRasterStyle,
    set_vector_graduated_style,
    set_vector_categorized_style)
from safe.common.utilities import temp_dir
from safe.common.exceptions import ReadLayerError
from safe.common.signals import (
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    ERROR_MESSAGE_SIGNAL,
    BUSY_SIGNAL,
    NOT_BUSY_SIGNAL,
    ANALYSIS_DONE_SIGNAL)
from safe import messaging as m
from safe.messaging import styles
from safe.common.exceptions import (
    InsufficientOverlapError, TemplateLoadingError)
from safe.report.impact_report import ImpactReport
from safe.gui.tools.impact_report_dialog import ImpactReportDialog
from safe_extras.pydispatch import dispatcher
from safe.utilities.analysis import Analysis
from safe.utilities.extent import Extent
from safe.impact_functions.impact_function_manager import ImpactFunctionManager

PROGRESS_UPDATE_STYLE = styles.PROGRESS_UPDATE_STYLE
INFO_STYLE = styles.INFO_STYLE
WARNING_STYLE = styles.WARNING_STYLE

LOGO_ELEMENT = m.Image(
    resource_url(
        resources_path('img', 'logos', 'inasafe-logo.png')),
    'InaSAFE Logo')
LOGGER = logging.getLogger('InaSAFE')


class AnalysisHandler(QObject):

    """Analysis handler for the dock and the wizard."""

    analysisDone = pyqtSignal(bool)

    # noinspection PyUnresolvedReferences
    def __init__(self, parent):
        """Constructor for the class.

        :param parent: Parent widget i.e. the wizard dialog.
        :type parent: QWidget
        """

        QtCore.QObject.__init__(self)
        self.parent = parent
        # Do not delete this
        self.iface = parent.iface
        self.keyword_io = KeywordIO()
        self.impact_function_manager = ImpactFunctionManager()
        self.extent = Extent(self.iface)
        self.analysis = None
        self.composer = None

        # Values for settings these get set in read_settings.
        self.run_in_thread_flag = None
        self.zoom_to_impact_flag = None
        self.hide_exposure_flag = None
        self.clip_hard = None
        self.show_intermediate_layers = None
        self.show_rubber_bands = False

        self.last_analysis_rubberband = None
        # This is a rubber band to show what the AOI of the
        # next analysis will be. Also added in 2.1.0
        self.next_analysis_rubberband = None

        self.read_settings()

    def enable_signal_receiver(self):
        """Setup dispatcher for all available signal from Analysis.

        .. note:: Adapted from the dock
        """
        dispatcher.connect(
            self.show_busy,
            signal=BUSY_SIGNAL)

        dispatcher.connect(
            self.hide_busy,
            signal=NOT_BUSY_SIGNAL)

        dispatcher.connect(
            self.completed,
            signal=ANALYSIS_DONE_SIGNAL)

        # noinspection PyArgumentEqualDefault
        dispatcher.connect(
            self.show_dynamic_message,
            signal=DYNAMIC_MESSAGE_SIGNAL)

        # noinspection PyArgumentEqualDefault,PyUnresolvedReferences
        dispatcher.connect(
            self.parent.wvResults.static_message_event,
            signal=STATIC_MESSAGE_SIGNAL,
            sender=dispatcher.Any)

        # noinspection PyArgumentEqualDefault,PyUnresolvedReferences
        dispatcher.connect(
            self.parent.wvResults.error_message_event,
            signal=ERROR_MESSAGE_SIGNAL,
            sender=dispatcher.Any)

    def disable_signal_receiver(self):
        """Remove dispatcher for all available signal from Analysis.

        .. note:: Adapted from the dock
        """
        dispatcher.disconnect(
            self.show_busy,
            signal=BUSY_SIGNAL)

        dispatcher.disconnect(
            self.hide_busy,
            signal=NOT_BUSY_SIGNAL)

        dispatcher.disconnect(
            self.completed,
            signal=ANALYSIS_DONE_SIGNAL)

        dispatcher.disconnect(
            self.show_dynamic_message,
            signal=DYNAMIC_MESSAGE_SIGNAL)

    def show_static_message(self, message):
        """Send a static message to the message viewer.

        Static messages cause any previous content in the MessageViewer to be
        replaced with new content.

        .. note:: Copied from the dock

        :param message: An instance of our rich message class.
        :type message: Message

        """
        dispatcher.send(
            signal=STATIC_MESSAGE_SIGNAL,
            sender=self,
            message=message)

    def show_dynamic_message(self, sender, message):
        """Send a dynamic message to the message viewer.

        Dynamic messages are appended to any existing content in the
        MessageViewer.

        .. note:: Modified from the dock

        :param sender: The object that sent the message.
        :type sender: Object, None

        :param message: An instance of our rich message class.
        :type message: Message

        """
        # TODO Hardcoded step - may overflow, if number of messages increase
        # noinspection PyUnresolvedReferences
        self.parent.pbProgress.setValue(self.parent.pbProgress.value() + 15)
        # noinspection PyUnresolvedReferences
        self.parent.wvResults.dynamic_message_event(sender, message)

    def show_error_message(self, error_message):
        """Send an error message to the message viewer.

        Error messages cause any previous content in the MessageViewer to be
        replaced with new content.

        .. note:: Copied from the dock

        :param error_message: An instance of our rich error message class.
        :type error_message: ErrorMessage
        """
        dispatcher.send(
            signal=ERROR_MESSAGE_SIGNAL,
            sender=self,
            message=error_message)
        self.hide_busy()

    def read_settings(self):
        """Restore settings from QSettings.

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
                self.extent.user_extent = QgsRectangle(*extent)
                self.extent.user_extent_crs = QgsCoordinateReferenceSystem(crs)
                self.extent.show_user_analysis_extent()
            except TypeError:
                self.extent.user_extent = None
                self.extent.user_extent_crs = None

        flag = settings.value(
            'inasafe/useThreadingFlag', False, type=bool)
        self.run_in_thread_flag = flag

        flag = settings.value(
            'inasafe/setZoomToImpactFlag', True, type=bool)
        self.zoom_to_impact_flag = flag

        # whether exposure layer should be hidden after model completes
        flag = settings.value(
            'inasafe/setHideExposureFlag', False, type=bool)
        self.hide_exposure_flag = flag

        # whether to 'hard clip' layers (e.g. cut buildings in half if they
        # lie partially in the AOI
        self.clip_hard = settings.value('inasafe/clip_hard', False, type=bool)

        # whether to show or not postprocessing generated layers
        self.show_intermediate_layers = settings.value(
            'inasafe/show_intermediate_layers', False, type=bool)

        # whether to show or not dev only options
        # noinspection PyAttributeOutsideInit
        self.developer_mode = settings.value(
            'inasafe/developer_mode', False, type=bool)

        # whether to show or not a custom Logo
        # noinspection PyAttributeOutsideInit
        self.organisation_logo_path = settings.value(
            'inasafe/organisation_logo_path',
            supporters_logo_path(),
            type=str)

    # noinspection PyUnresolvedReferences
    def show_busy(self):
        """Lock buttons and enable the busy cursor."""
        self.parent.pbnNext.setEnabled(False)
        self.parent.pbnBack.setEnabled(False)
        self.parent.pbnCancel.setEnabled(False)
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.parent.repaint()
        QtGui.qApp.processEvents()

    # noinspection PyUnresolvedReferences
    def hide_busy(self):
        """Unlock buttons A helper function to indicate processing is done."""
        self.parent.pbnNext.setEnabled(True)
        self.parent.pbnBack.setEnabled(True)
        self.parent.pbnCancel.setEnabled(True)
        self.parent.repaint()
        QtGui.qApp.restoreOverrideCursor()

    def analysis_error(self, exception, message):
        """A helper to spawn an error and halt processing.

        An exception will be logged, busy status removed and a message
        displayed.

        .. note:: Copied from the dock

        :param message: an ErrorMessage to display
        :type message: ErrorMessage, Message

        :param exception: An exception that was raised
        :type exception: Exception
        """
        self.hide_busy()
        LOGGER.exception(message)
        message = get_error_message(exception, context=message)
        self.show_error_message(message)
        self.analysisDone.emit(False)

    def setup_and_run_analysis(self):
        """Setup and execute the analysis"""
        self.enable_signal_receiver()

        self.show_busy()
        self.init_analysis()
        try:
            self.analysis.setup_analysis()
        except InsufficientOverlapError as e:
            raise e

        self.extent.show_last_analysis_extent(
            self.analysis.clip_parameters[1])

        # Start the analysis
        self.analysis.run_analysis()

        self.disable_signal_receiver()

    # noinspection PyUnresolvedReferences
    def init_analysis(self):
        """Setup analysis to make it ready to work.

        .. note:: Copied or adapted from the dock
        """
        self.analysis = Analysis()
        # Layers
        self.analysis.hazard_layer = self.parent.hazard_layer
        self.analysis.exposure_layer = self.parent.exposure_layer
        self.analysis.aggregation_layer = self.parent.aggregation_layer
        # TODO test if the implement aggregation layer works!

        # noinspection PyTypeChecker
        self.analysis.hazard_keyword = self.keyword_io.read_keywords(
            self.parent.hazard_layer)
        self.analysis.exposure_keyword = self.keyword_io.read_keywords(
            self.parent.exposure_layer)
        # Need to check since aggregation layer is not mandatory
        if self.analysis.aggregation_layer:
            self.analysis.aggregation_keyword = self.keyword_io.read_keywords(
                self.parent.aggregation_layer)

        # Impact Function
        impact_function = self.impact_function_manager.get(
            self.parent.selected_function()['id'])
        impact_function.parameters = self.parent.if_params
        self.analysis.impact_function = impact_function

        # Variables
        self.analysis.clip_hard = self.clip_hard
        self.analysis.show_intermediate_layers = self.show_intermediate_layers
        self.analysis.run_in_thread_flag = self.run_in_thread_flag
        self.analysis.map_canvas = self.iface.mapCanvas()

        # Extent
        self.analysis.user_extent = self.extent.user_extent
        self.analysis.user_extent_crs = self.extent.user_extent_crs

    # noinspection PyUnresolvedReferences
    def completed(self):
        """Slot activated when the process is done.

        .. note:: Adapted from the dock
        """

        # Try to run completion code
        try:
            from datetime import datetime
            LOGGER.debug(datetime.now())
            LOGGER.debug('get engine impact layer')
            LOGGER.debug(self.analysis is None)
            engine_impact_layer = self.analysis.impact_layer

            # Load impact layer into QGIS
            qgis_impact_layer = read_impact_layer(engine_impact_layer)

            report = self.show_results(
                qgis_impact_layer, engine_impact_layer)

        except Exception, e:  # pylint: disable=W0703
            # FIXME (Ole): This branch is not covered by the tests
            self.analysis_error(e, self.tr('Error loading impact layer.'))
        else:
            # On success, display generated report
            impact_path = qgis_impact_layer.source()
            message = m.Message(report)
            # message.add(m.Heading(self.tr('View processing log as HTML'),
            #                      **INFO_STYLE))
            # message.add(m.Link('file://%s' % self.parent.wvResults.log_path))
            # noinspection PyTypeChecker
            self.show_static_message(message)
            self.parent.wvResults.impact_path = impact_path

        self.parent.pbProgress.hide()
        self.parent.lblAnalysisStatus.setText('Analysis done.')
        self.parent.pbnReportWeb.show()
        self.parent.pbnReportPDF.show()
        self.parent.pbnReportComposer.show()
        self.hide_busy()
        self.analysisDone.emit(True)

    def show_results(self, qgis_impact_layer, engine_impact_layer):
        """Helper function for slot activated when the process is done.

        .. note:: Adapted from the dock

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
                # qgis_impact_layer.setColorShadingAlgorithm(
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
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers(layers_to_add)
        # make sure it is active in the legend - needed since QGIS 2.4
        self.iface.setActiveLayer(qgis_impact_layer)
        # then zoom to it
        if self.zoom_to_impact_flag:
            self.iface.zoomToActiveLayer()
        if self.hide_exposure_flag:
            exposure_layer = self.analysis.exposure_layer
            legend = self.iface.legendInterface()
            legend.setLayerVisible(exposure_layer, False)

        # append postprocessing report
        report.add(output.to_html())
        # Layer attribution comes last
        report.add(impact_attribution(keywords).to_html(True))
        # Return text to display in report panel
        return report

    def print_map(self, mode='pdf'):
        """Open impact report dialog that used define report options.

        :param mode: Mode for report - defaults to PDF.
        :type mode:
        """
        # Check if selected layer is valid
        impact_layer = self.iface.activeLayer()
        if impact_layer is None:
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QtGui.QMessageBox.warning(
                self.parent,
                self.tr('InaSAFE'),
                self.tr(
                    'Please select a valid impact layer before trying to '
                    'print.'))
            return

        # Open Impact Report Dialog
        print_dialog = ImpactReportDialog(self.iface)
        print_dialog.button_ok = QtGui.QPushButton(self.tr('OK'))
        print_dialog.button_box.addButton(
            print_dialog.button_ok,
            QtGui.QDialogButtonBox.ActionRole)

        # noinspection PyUnresolvedReferences
        print_dialog.button_ok.clicked.connect(print_dialog.accept)

        print_dialog.button_save_pdf.hide()
        print_dialog.button_open_composer.hide()

        if not print_dialog.exec_() == QtGui.QDialog.Accepted:
            # noinspection PyTypeChecker
            self.show_dynamic_message(
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
                # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                QtGui.QMessageBox.warning(
                    self.parent,
                    self.tr('InaSAFE'),
                    self.tr('Please select a valid template before printing. '
                            'The template you choose does not exist.'))
                return

        # Instantiate and prepare Report
        # noinspection PyTypeChecker
        self.show_dynamic_message(
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
        if template_warning_verbose and \
                len(impact_report.missing_elements) != 0:
            title = self.tr('Template is missing some elements')
            question = self.tr(
                'The composer template you are printing to is missing '
                'these elements: %s. Do you still want to continue') % (
                    ', '.join(impact_report.missing_elements))
            # noinspection PyCallByClass,PyTypeChecker
            answer = QtGui.QMessageBox.question(
                self.parent,
                title,
                question,
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if answer == QtGui.QMessageBox.No:
                return

        create_pdf_flag = bool(mode == 'pdf')
        self.show_busy()
        if create_pdf_flag:
            self.print_map_to_pdf(impact_report)
        else:
            self.open_map_in_composer(impact_report)

        self.hide_busy()

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
            self.show_error_message(
                self.tr('Keyword "map_title" not found.'))
            return

        # Get output path
        # noinspection PyCallByClass,PyTypeChecker
        output_path = QtGui.QFileDialog.getSaveFileName(
            self.parent,
            self.tr('Write to PDF'),
            os.path.join(temp_dir(), default_file_name),
            self.tr('Pdf File (*.pdf)'))
        output_path = str(output_path)

        if output_path is None or output_path == '':
            # noinspection PyTypeChecker
            self.show_dynamic_message(
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
                m.Paragraph(self.tr('Your PDF was created....')),
                m.Paragraph(self.tr(
                    'Opening using the default PDF viewer on your system. '
                    'The generated pdfs were saved as:')),
                m.Paragraph(wrapped_map_path),
                m.Paragraph(self.tr('and')),
                m.Paragraph(wrapped_table_path))

            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl.fromLocalFile(table_pdf_path))
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl.fromLocalFile(map_pdf_path))

            # noinspection PyTypeChecker
            self.show_dynamic_message(self, status)
        except TemplateLoadingError, e:
            self.show_error_message(get_error_message(e))
        except Exception, e:  # pylint: disable=broad-except
            self.show_error_message(get_error_message(e))

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
