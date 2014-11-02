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

from PyQt4 import QtGui, QtCore
# noinspection PyPackageRequirements
from PyQt4.QtCore import (
    QObject,
    QSettings,
    pyqtSignal)
# noinspection PyPackageRequirements
from PyQt4.QtGui import QColor

from qgis.core import (
    QgsMapLayerRegistry,
    QgsMapLayer,
    QgsPoint,
    QgsRectangle,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QGis)
from qgis.gui import QgsRubberBand

from third_party.pydispatch import dispatcher

from safe.api import ImpactFunctionManager
from safe.api import metadata  # pylint: disable=W0612

from safe_qgis.safe_interface import messaging as m
from safe_qgis.safe_interface import (
    temp_dir,
    styles,
    DEFAULTS,
    DYNAMIC_MESSAGE_SIGNAL,
    STATIC_MESSAGE_SIGNAL,
    ERROR_MESSAGE_SIGNAL,
    BUSY_SIGNAL,
    NOT_BUSY_SIGNAL,
    ANALYSIS_DONE_SIGNAL)

from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.utilities.analysis import Analysis

from safe_qgis.utilities.utilities import (
    get_error_message,
    impact_attribution,
    read_impact_layer)
from safe_qgis.utilities.styling import (
    setRasterStyle,
    set_vector_graduated_style,
    set_vector_categorized_style)
from safe_qgis.exceptions import (
    HashNotFoundError,
    NoKeywordsFoundError,
    KeywordNotFoundError,
    InvalidParameterError,
    InsufficientOverlapError,
    #InvalidAggregationKeywords,
    #InsufficientMemoryWarning,
    UnsupportedProviderError)

from safe_qgis.report.map import Map
from safe_qgis.report.html_renderer import HtmlRenderer

from safe_qgis.tools.impact_report_dialog import ImpactReportDialog

PROGRESS_UPDATE_STYLE = styles.PROGRESS_UPDATE_STYLE
INFO_STYLE = styles.INFO_STYLE
WARNING_STYLE = styles.WARNING_STYLE
LOGO_ELEMENT = m.Image('qrc:/plugins/inasafe/inasafe-logo.png', 'InaSAFE Logo')
LOGGER = logging.getLogger('InaSAFE')

class WizardAnalysisHandler(QObject):
    """Analysis handler for the InaSAFE wizard."""

    analysisDone = pyqtSignal(bool)

    def __init__(self, parent):
        """Constructor for the class.

        :param parent: Parent widget i.e. the wizard dialog.
        :type parent: QWidget
        """

        QtCore.QObject.__init__(self)
        self.parent = parent
        self.iface = parent.iface
        self.keyword_io = KeywordIO()

        # Values for settings these get set in read_settings.
        self.run_in_thread_flag = None
        self.zoom_to_impact_flag = None
        self.hide_exposure_flag = None
        self.clip_hard = None
        self.clip_to_viewport = None
        self.show_intermediate_layers = None
        self.show_rubber_bands = False

        self.last_analysis_rubberband = None
        # This is a rubber band to show what the AOI of the
        # next analysis will be. Also added in 2.1.0
        self.next_analysis_rubberband = None

        self.read_settings()

    def read_settings(self):
        """Set the dock state from QSettings.

        Do this on init and after changing options in the options dialog.
        """

        settings = QtCore.QSettings()

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

        # whether to clip hazard and exposure layers to the view port
        self.clip_to_viewport = settings.value(
            'inasafe/clip_to_viewport', True, type=bool)

        # whether to show or not postprocessing generated layers
        self.show_intermediate_layers = settings.value(
            'inasafe/show_intermediate_layers', False, type=bool)

        # 2hether to show rubber band of last and next scenario
        flag = bool(settings.value(
            'inasafe/showRubberBands', False, type=bool))
        self.show_rubber_bands = flag

    def setup_and_run_analysis(self):
        """Setup and execute the analysis"""
        self.enable_signal_receiver()

        #TODO: TRY...CATCH HERE! (see: dock)

        # TODO: In dock, the keywords dialog is displayed here
        #       for the aggregation layer. Why?
        self.show_busy()

        self.setup_analysis()
        self.show_next_analysis_extent()
        extent = self.analysis.clip_parameters[1]
        self.show_extent(extent)
        # Start the analysis
        self.analysis.run_analysis()

        self.disable_signal_receiver()

    def setup_analysis(self):
        """Setup analysis to make it ready to work.

        .. note:: Copied or adapted from the dock
        """
        self.analysis = Analysis()
        # Layers
        self.analysis.hazard_layer = self.parent.hazard_layer
        self.analysis.exposure_layer = self.parent.exposure_layer
        self.analysis.aggregation_layer = self.parent.aggregation_layer
        #TODO test if the implement aggregation layer works!

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
        self.analysis.impact_function_id = self.parent.selected_function()['id']
        self.analysis.impact_function_parameters = self.parent.if_params

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

        # noinspection PyArgumentEqualDefault
        dispatcher.connect(
            self.parent.wvResults.static_message_event,
            signal=STATIC_MESSAGE_SIGNAL,
            sender=dispatcher.Any)

        # noinspection PyArgumentEqualDefault
        dispatcher.connect(
            self.parent.wvResults.error_message_event,
            signal=ERROR_MESSAGE_SIGNAL,
            sender=dispatcher.Any)

    def disable_signal_receiver(self):
        """Remove dispatcher for all available signal from Analysis.

        .. note:: Copied from the dock
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

    def show_busy(self):
        """Lock buttons and enable the busy cursor."""
        self.parent.pbnNext.setEnabled(False)
        self.parent.pbnBack.setEnabled(False)
        self.parent.pbnCancel.setEnabled(False)
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.parent.repaint()
        QtGui.qApp.processEvents()

    def hide_busy(self):
        """A helper function to indicate processing is done."""
        self.parent.pbnNext.setEnabled(True)
        self.parent.pbnBack.setEnabled(True)
        self.parent.pbnCancel.setEnabled(True)
        self.parent.repaint()
        QtGui.qApp.restoreOverrideCursor()

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
        #TODO Hardcoded step - may overflow, if the number of messages increase
        self.parent.pbProgress.setValue( self.parent.pbProgress.value() + 15 )
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

    def show_analysis_results(self, qgis_impact_layer, engine_impact_layer):
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
            exposure_layer = self.parent.get_exposure_layer()
            legend = self.iface.legendInterface()
            legend.setLayerVisible(exposure_layer, False)

        # append postprocessing report
        report.add(output.to_html())
        # Layer attribution comes last
        report.add(impact_attribution(keywords).to_html(True))
        # Return text to display in report panel
        return report

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
            engine_impact_layer = self.analysis.get_impact_layer()

            # Load impact layer into QGIS
            qgis_impact_layer = read_impact_layer(engine_impact_layer)

            report = self.show_analysis_results(
                qgis_impact_layer, engine_impact_layer)

        except Exception, e:  # pylint: disable=W0703
            # FIXME (Ole): This branch is not covered by the tests
            self.analysis_error(e, self.tr('Error loading impact layer.'))
        else:
            # On success, display generated report
            impact_path = qgis_impact_layer.source()
            message = m.Message(report)
            message.add(m.Heading(self.tr('View processing log as HTML'),
                                  **INFO_STYLE))
            message.add(m.Link('file://%s' % self.parent.wvResults.log_path))
            self.show_static_message(message)
            self.parent.wvResults.impact_path = impact_path

        self.parent.pbProgress.hide()
        self.parent.lblAnalysisStatus.setText('Analysis done.')
        self.parent.pbnReportWeb.show()
        self.parent.pbnReportPDF.show()
        self.parent.pbnReportComposer.show()
        self.hide_busy()
        self.analysisDone.emit(True)


    def print_map(self, mode="pdf"):
        """Slot to open impact report dialog that used to tune report
        when print map button pressed."""
        print_dialog = ImpactReportDialog(self.iface)

        print_dialog.button_ok = QtGui.QPushButton(self.tr('OK'))
        print_dialog.buttonBox.addButton(
            print_dialog.button_ok,
            QtGui.QDialogButtonBox.ActionRole)

        print_dialog.button_ok.clicked.connect(print_dialog.accept)

        print_dialog.button_save_pdf.hide()
        print_dialog.button_open_composer.hide()

        if not print_dialog.exec_() == QtGui.QDialog.Accepted:
            self.show_dynamic_message(
                self,
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

        create_pdf = bool(mode == 'pdf')

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
            self,
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
                self.parent, self.tr('Write to PDF'),
                os.path.join(temp_dir(), default_file_name),
                self.tr('Pdf File (*.pdf)'))
            map_pdf_path = str(map_pdf_path)

            if map_pdf_path is None or map_pdf_path == '':
                self.show_dynamic_message(
                    self,
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
            self.show_dynamic_message(self,status)
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