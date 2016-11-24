# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid **GUI InaSAFE Wizard Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""


import os
import json
import logging
from collections import OrderedDict

# noinspection PyPackageRequirements
from qgis.core import (
    QgsCoordinateTransform,
    QgsProject,
    QgsMapLayerRegistry,
    QgsMapLayer,
    QGis,
    QgsRectangle,
    QgsCoordinateReferenceSystem)
# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
# noinspection PyPackageRequirements
from PyQt4.QtCore import QObject, QSettings, pyqtSignal, Qt, QDir

from safe.definitionsv4.fields import hazard_class_field
from safe.definitionsv4.utilities import definition
from safe.impact_function_v4.style import hazard_class_style
from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe.reportv4.report_metadata import ReportMetadata
from safe.reportv4.impact_report import ImpactReport as ImpactReportV4
from safe.definitionsv4.report import standard_impact_report_metadata

from safe.utilities.keyword_io import KeywordIO
from safe.utilities.utilities import (
    get_error_message,
    impact_attribution,
    write_json
)
from safe.utilities.gis import (
    extent_string_to_array,
    read_impact_layer,
    viewport_geo_array)
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
    send_static_message,
    send_error_message,
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
from safe.utilities.extent import Extent
from safe.utilities.qgis_utilities import add_above_layer
from safe.impact_template.utilities import get_report_template
from safe.impact_function_v4.impact_function import ImpactFunction

__author__ = 'qgis@borysjurgiel.pl'
__revision__ = '$Format:%H$'
__date__ = '21/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

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
        self.extent = Extent(self.iface)
        self.impact_function = None
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
            self.parent.step_fc_analysis.wvResults.static_message_event,
            signal=STATIC_MESSAGE_SIGNAL,
            sender=dispatcher.Any)

        # noinspection PyArgumentEqualDefault,PyUnresolvedReferences
        dispatcher.connect(
            self.parent.step_fc_analysis.wvResults.error_message_event,
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

    def show_dynamic_message(self, sender, message):
        """Send a dynamic message to the message viewer.

        Dynamic messages are appended to any existing content in the
        MessageViewer.

        .. note:: Modified from the dock

        :param sender: The object that sent the message.
        :type sender: Object, None

        :param message: An instance of our rich message class.
        :type message: safe.messaging.Message

        """
        # TODO Hardcoded step - may overflow, if number of messages increase
        # noinspection PyUnresolvedReferences
        self.parent.step_fc_analysis.pbProgress.setValue(
            self.parent.step_fc_analysis.pbProgress.value() + 15)
        # noinspection PyUnresolvedReferences
        self.parent.step_fc_analysis.wvResults.dynamic_message_event(
            sender, message)

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
        send_error_message(self, message)
        self.analysisDone.emit(False)

    def setup_and_run_analysis(self):
        """Setup and execute the analysis"""
        self.enable_signal_receiver()

        try:
            self.show_busy()
            self.impact_function = self.prepare_impact_function()

            self.impact_function.run()
            self.generate_impact_report(self.impact_function)

        except InsufficientOverlapError as e:
            raise e
        finally:
            if self.impact_function:
                self.impact_function.force_memory = False

                layers = self.impact_function.outputs

                name = self.impact_function.name
                root = QgsProject.instance().layerTreeRoot()
                group_analysis = root.insertGroup(0, name)
                group_analysis.setVisible(Qt.Checked)
                for layer in layers:
                    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
                    layer_node = group_analysis.addLayer(layer)

                    # Let's enable only the more detailed layer.
                    if layer.id() == self.impact_function.impact.id():
                        layer_node.setVisible(Qt.Checked)
                    else:
                        layer_node.setVisible(Qt.Unchecked)

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

            self.disable_signal_receiver()
            self.hide_busy()

        # self.disable_signal_receiver()

    # noinspection PyUnresolvedReferences
    def prepare_impact_function(self):
        """Setup analysis to make it ready to work.

        .. note:: Copied or adapted from the dock
        """
        # Impact Function
        impact_function = ImpactFunction()

        # Layers
        impact_function.hazard = self.parent.hazard_layer
        impact_function.exposure = self.parent.exposure_layer
        aggregation = self.parent.aggregation_layer
        # TODO test if the implement aggregation layer works!
        if aggregation:
            impact_function.aggregation = aggregation
        else:
            map_settings = self.iface.mapCanvas().mapSettings()
            impact_function.viewport_extent = map_settings.fullExtent()
            impact_function._viewport_extent_crs = (
                map_settings.destinationCrs())

        # impact_function.debug_mode = self.debug_mode.isChecked()

        return impact_function

    # noinspection PyUnresolvedReferences
    def completed(self, zero_impact):
        """Slot activated when the process is done.

        :param zero_impact: Flag for zero impact.
        :type zero_impact: bool

        .. note:: Adapted from the dock
        """

        # Try to run completion code
        # Show the result in the dock from layer if there is an impact.
        if not zero_impact:
            try:
                from datetime import datetime
                LOGGER.debug(datetime.now())
                LOGGER.debug('get engine impact layer')
                LOGGER.debug(self.impact_function is None)

                # Load impact layer into QGIS
                qgis_impact_layer = read_impact_layer(
                    self.impact_function.impact)
                report = self.show_results()

            except Exception, e:  # pylint: disable=W0703
                # FIXME (Ole): This branch is not covered by the tests
                self.analysis_error(e, self.tr('Error loading impact layer.'))
            else:
                # On success, display generated report
                impact_path = qgis_impact_layer.source()
                message = m.Message(report)
                # noinspection PyTypeChecker
                send_static_message(self, message)
                self.parent.step_fc_analysis.wvResults.impact_path = \
                    impact_path

        self.parent.step_fc_analysis.pbProgress.hide()
        self.parent.step_fc_analysis.lblAnalysisStatus.setText(
            'Analysis done.')
        self.parent.step_fc_analysis.pbnReportWeb.show()
        self.parent.step_fc_analysis.pbnReportPDF.show()
        self.parent.step_fc_analysis.pbnReportComposer.show()
        self.hide_busy()
        self.analysisDone.emit(True)

    def show_impact_report(self, qgis_impact_layer):
        pass

    def show_results(self):
        """Helper function for slot activated when the process is done.

        .. versionchanged:: 3.4 - removed parameters.

        .. note:: If you update this function, please report your change to
            safe.gui.widgets.dock.show_results too.

        :returns: Provides a report for writing to the dock.
        :rtype: str
        """
        qgis_exposure = self.impact_function.exposure.qgis_layer()
        qgis_hazard = self.impact_function.hazard.qgis_layer()
        qgis_aggregation = self.impact_function.aggregation.qgis_layer()

        safe_impact_layer = self.impact_function.impact
        qgis_impact_layer = read_impact_layer(safe_impact_layer)

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
                write_json(impact_data, json_path)
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
            add_above_layer(
                self.impact_function.aggregator.layer,
                qgis_aggregation)
            legend.setLayerVisible(self.impact_function.aggregator.layer, True)

        if self.hide_exposure_flag:
            # Insert the impact always above the hazard
            add_above_layer(
                qgis_impact_layer,
                qgis_hazard)
        else:
            # Insert the impact above the hazard and the exposure if
            # we don't hide the exposure. See #2899
            add_above_layer(
                qgis_impact_layer,
                qgis_exposure,
                qgis_hazard)

        # In QGIS 2.14.2 and GDAL 1.11.3, if the exposure is in 3857,
        # the impact layer is in 54004, we need to change it. See issue #2790.
        if qgis_exposure.crs().authid() == 'EPSG:3857':
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
            send_error_message(
                self, self.tr('Keyword "map_title" not found.'))
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

    def generate_impact_report(self, impact_function):
        """

        :param impact_function:
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
