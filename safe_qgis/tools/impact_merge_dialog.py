# coding=utf-8
"""
Layer Merge Dialog.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '23/10/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
from xml.dom import minidom

#noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
#noinspection PyPackageRequirements
from PyQt4.QtCore import QSettings, pyqtSignature
#noinspection PyPackageRequirements
from PyQt4.QtGui import QDialog, QMessageBox, QFileDialog
from qgis.core import QgsMapLayerRegistry

from safe_qgis.ui.impact_merge_dialog_base import Ui_ImpactMergeDialogBase

from safe_qgis.exceptions import (
    CanceledImportDialogError, NoKeywordsFoundError, KeywordNotFoundError)
from safe_qgis.safe_interface import messaging as m
from safe_qgis.utilities.utilities import (
    html_footer, html_header, add_ordered_combo_item)
from safe_qgis.utilities.help import show_context_help
from safe_qgis.safe_interface import styles
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.report.html_renderer import HtmlRenderer

#from pydev import pydevd  # pylint: disable=F0401

INFO_STYLE = styles.INFO_STYLE


class ImpactMergeDialog(QDialog, Ui_ImpactMergeDialogBase):
    """Tools for merging 2 impact layer based on different exposure."""

    def __init__(self, parent=None, iface=None):
        """Constructor for dialog.

        :param parent: Optional widget to use as parent
        :type parent: QWidget

        :param iface: An instance of QGisInterface
        :type iface: QGisInterface
        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        self.setWindowTitle(self.tr('InaSAFE Impact Layer Merge Tool'))

        self.iface = iface
        self.keyword_io = KeywordIO()

        # Set up context help
        help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        QtCore.QObject.connect(
            help_button, QtCore.SIGNAL('clicked()'), self.show_help)

        self.show_info()
        self.restore_state()
        # Enable remote debugging - should normally be commented out.
        #pydevd.settrace(
        #    'localhost', port=5678, stdoutToServer=True, stderrToServer=True)
        self.get_layers()

    def show_info(self):
        """Show usage info to the user."""
        # Read the header and footer html snippets
        header = html_header()
        footer = html_footer()

        string = header

        heading = m.Heading(self.tr('Impact Layer Merge Tool'), **INFO_STYLE)
        body = self.tr(
            'This tool will merge the outputs from two impact maps for the '
            'same area. The maps must be created using the same aggregation '
            'areas. To use:'
        )
        tips = m.BulletedList()
        tips.add(self.tr(
            'Run an impact assessment for an area using aggregation. e.g.'
            'Flood Impact on Buildings aggregated by municipal boundaries.'))
        tips.add(self.tr(
            'Run a second impact assessment for the same area using the same '
            'aggregation. e.g. Flood Impact on People aggregated by '
            'municipal boundaries.'))
        tips.add(self.tr(
            'Open this tool and select each impact layer from the pick lists '
            'provided below.'))
        tips.add(self.tr(
            'Select an output directory.'))
        tips.add(self.tr(
            'Click Run to generate the per aggregation area combined '
            'summaries.'))
        message = m.Message()
        message.add(heading)
        message.add(body)
        message.add(tips)
        string += message.to_html()
        string += footer

        self.web_view.setHtml(string)

    def restore_state(self):
        """ Read last state of GUI from configuration file."""
        settings = QSettings()
        self.output_directory.setText(settings.value('directory'))

    def save_state(self):
        """ Store current state of GUI to configuration file """
        settings = QSettings()
        settings.setValue('directory', self.output_directory.text())

    @staticmethod
    def show_help():
        """Load the help text for the dialog."""
        show_context_help('impact_layer_merge_tool')

    @pyqtSignature('')  # prevents actions being handled twice
    def on_directory_chooser_clicked(self):
        """ Show a dialog to choose directory """
        # noinspection PyCallByClass,PyTypeChecker
        self.output_directory.setText(QFileDialog.getExistingDirectory(
            self, self.tr("Select output directory")))

    def accept(self):
        """Do merging two impact layers."""
        try:
            self.save_state()
            self.require_directory()
            if not self.validate():
                #noinspection PyCallByClass,PyArgumentList,PyTypeChecker
                QMessageBox.warning(
                    self,
                    self.tr('InaSAFE error'),
                    self.tr(
                        'Please choose two different impact layers to continue.'
                    ))
                return
            self.merge()
            self.done(QDialog.Accepted)
        except CanceledImportDialogError:
            # don't show anything because this exception raised
            # when user canceling the import process directly
            pass
        except Exception as myEx:
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QMessageBox.warning(
                self,
                self.tr("InaSAFE Merge Impact Tools error"),
                str(myEx))

    def validate(self):
        """Verify that there are two layers and they are different."""

        if self.first_layer.currentIndex() < 0:
            return False

        if self.second_layer.currentIndex() < 0:
            return False

        first_layer = self.first_layer.itemData(
            self.first_layer.currentIndex(), QtCore.Qt.UserRole)
        second_layer = self.second_layer.itemData(
            self.second_layer.currentIndex(), QtCore.Qt.UserRole)

        if first_layer.id() == second_layer.id():
            return False

        return True

    def require_directory(self):
        """Ensure directory path entered in dialog exist.

        When the path does not exist, this function will ask the user if he
        want to create it or not.

        :raises: CanceledImportDialogError - when user choose 'No' in
            the question dialog for creating directory, or 'Yes' but the output
            directory path is empty
        """
        path = str(self.output_directory.text())

        if os.path.exists(path):
            return

        title = self.tr("Directory %s not exist") % path
        question = self.tr(
            "Directory %s not exist. Do you want to create it?"
        ) % path
        # noinspection PyCallByClass,PyTypeChecker
        answer = QMessageBox.question(
            self, title,
            question, QMessageBox.Yes | QMessageBox.No)

        if answer == QMessageBox.Yes:
            if len(path) != 0:
                os.makedirs(path)
            else:
            # noinspection PyCallByClass,PyTypeChecker
                QMessageBox.warning(
                    self,
                    self.tr('InaSAFE error'),
                    self.tr('Output directory can not be empty.'))
                raise CanceledImportDialogError()

        else:
            raise CanceledImportDialogError()

    def merge(self):
        """Merge the postprocessing_report from each impact."""
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        first_layer = self.first_layer.itemData(
            self.first_layer.currentIndex(), QtCore.Qt.UserRole)
        second_layer = self.second_layer.itemData(
            self.second_layer.currentIndex(), QtCore.Qt.UserRole)
        try:
            first_report = self.keyword_io.read_keywords(
                first_layer, 'postprocessing_report')
            second_report = self.keyword_io.read_keywords(
                second_layer, 'postprocessing_report')
        except (NoKeywordsFoundError, KeywordNotFoundError):
            # Skip if there are no keywords at all
            # Skip if the impact_summary keyword is missing
            raise

        # Ensure there is always only a single root element or minidom moans
        first_report = '<body>' + first_report + '</body>'
        second_report = '<body>' + second_report + '</body>'

        # Now create a dom document for each
        first_document = minidom.parseString(first_report)
        second_document = minidom.parseString(second_report)
        tables = first_document.getElementsByTagName('table')
        tables += second_document.getElementsByTagName('table')

        # Now create dictionary report from DOM
        merged_report_dict = self.generate_report_dictionary_from_dom(tables)

        # Generate html reports from merged dictionary
        html_reports = self.generate_html_from_merged_report(merged_report_dict)

        # Now Generate image from html reports. Each image will be generated
        # for each html report
        html_renderer = HtmlRenderer(300)
        for html_report in html_reports:
            aggregation_area = html_report[0]
            html = html_report[1]
            image_report = html_renderer.html_to_image(html, 100)
            path = '%s/%s.png' % (
                str(self.output_directory.text()),
                aggregation_area)
            image_report.save(path)

        QtGui.qApp.restoreOverrideCursor()

        # Give user success information
        # noinspection PyCallByClass,PyTypeChecker
        QMessageBox.information(
            self,
            self.tr('InaSAFE Information'),
            self.tr(
                'Reports from merging two impact layers is generated '
                'successfully.'))

    @staticmethod
    def generate_report_dictionary_from_dom(html_dom):
        """Generate dictionary representing report from html dom.

        :param html_dom: Input representing document dom as report from each
        impact layer report.
        :type html_dom: str
        :return: Dictionary representing html_dom
        :rtype: dict

        # DICT STRUCTURE:
         { Aggregation_Area:
            {Exposure Type:{
                Exposure Detail}}}
        # EXAMPLE
           {"Jakarta Barat":
               {"Buildings":
                   {"Total":150,
                    "Places of Worship: No data
                   }
               }
           }
        """
        merged_report_dict = {}
        for table in html_dom:
            caption = table.getElementsByTagName('caption')[0].firstChild.data
            rows = table.getElementsByTagName('tr')
            header = rows[0]
            contains = rows[1:]
            for contain in contains:
                data = contain.getElementsByTagName('td')
                aggregation_area = data[0].firstChild.nodeValue
                exposure_dict = {}
                if aggregation_area in merged_report_dict:
                    exposure_dict = merged_report_dict[aggregation_area]
                data_contain = data[1:]
                exposure_detail_dict = {}
                for datum in data_contain:
                    index_datum = data.index(datum)
                    datum_header = \
                        header.getElementsByTagName('td')[index_datum]
                    datum_caption = datum_header.firstChild.nodeValue
                    exposure_detail_dict[datum_caption] = \
                        datum.firstChild.nodeValue
                exposure_dict[caption] = exposure_detail_dict
                merged_report_dict[aggregation_area] = exposure_dict
        return merged_report_dict

    @staticmethod
    def generate_html_from_merged_report(merged_report_dict):
        """Generate html format of all aggregation units from a dictionary
        representing merged report.

        :param merged_report_dict: a dictionary of merged report
        :type merged_report_dict: dict

        :return: HTML for each aggregation unit report
        :rtype: list
        """
        html_reports = []
        for aggregation_area in merged_report_dict:
            html = ''
            html += '<table class="table table-condensed table-striped">'
            html += '<caption>%s</caption>' % aggregation_area
            exposure_report_dict = merged_report_dict[aggregation_area]
            for exposure in exposure_report_dict:
                exposure_detail_dict = exposure_report_dict[exposure]
                html += '<tr><th>%s</th></tr>' % exposure
                # Print rows containing 'total'
                for datum in exposure_detail_dict:
                    if 'total' in str(datum).lower():
                        html += ('<tr>'
                                 '<td>%s</td>'
                                 '<td>%s</td>'
                                 '</tr>') % (datum, exposure_detail_dict[datum])
                # Print rows other than above
                for datum in exposure_detail_dict:
                    if 'total' not in str(datum).lower():
                        html += ('<tr>'
                                 '<td>%s</td>'
                                 '<td>%s</td>'
                                 '</tr>') % (datum, exposure_detail_dict[datum])

            html += '</table>'
            html_report = (aggregation_area, html)
            html_reports.append(html_report)

        return html_reports

    def get_layers(self):
        """Obtain a list of impact layers currently loaded in QGIS.
        """
        registry = QgsMapLayerRegistry.instance()
        # MapLayers returns a QMap<QString id, QgsMapLayer layer>
        layers = registry.mapLayers().values()

        # For issue #618
        if len(layers) == 0:
            return

        self.first_layer.clear()
        self.second_layer.clear()

        for layer in layers:
            try:
                self.keyword_io.read_keywords(layer, 'impact_summary')
            except (NoKeywordsFoundError, KeywordNotFoundError):
                # Skip if there are no keywords at all
                # Skip if the impact_summary keyword is missing
                continue

            add_ordered_combo_item(self.first_layer, layer.name(), layer)
            add_ordered_combo_item(self.second_layer, layer.name(), layer)
