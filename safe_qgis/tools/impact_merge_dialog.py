# coding=utf-8
"""
Impact Layer Merge Dialog.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '06/05/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
from collections import OrderedDict
from xml.dom import minidom

#noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore, QtXml
#noinspection PyPackageRequirements
from PyQt4.QtCore import QSettings, pyqtSignature, QUrl
#noinspection PyPackageRequirements
from PyQt4.QtGui import QDialog, QMessageBox, QFileDialog, QDesktopServices
from qgis.core import (
    QgsMapLayerRegistry,
    QgsMapRenderer,
    QgsComposition,
    QgsRectangle,
    QgsAtlasComposition)

from safe_qgis.ui.impact_merge_dialog_base import Ui_ImpactMergeDialogBase
from safe_qgis.exceptions import (
    InvalidLayerError,
    EmptyDirectoryError,
    FileNotFoundError,
    CanceledImportDialogError,
    NoKeywordsFoundError,
    KeywordNotFoundError,
    InvalidParameterError,
    ReportCreationError,
    UnsupportedProviderError)
from safe_qgis.safe_interface import (
    messaging as m,
    styles,
    temp_dir)
from safe_qgis.utilities.defaults import disclaimer
from safe_qgis.utilities.utilities import (
    html_header,
    html_footer,
    html_to_file,
    add_ordered_combo_item)
from safe_qgis.utilities.help import show_context_help
from safe_qgis.utilities.keyword_io import KeywordIO

INFO_STYLE = styles.INFO_STYLE


#noinspection PyArgumentList
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

        # Template Path for composer
        self.template_path = ':/plugins/inasafe/merged_report.qpt'

        # Safe Logo Path
        self.safe_logo_path = ':/plugins/inasafe/inasafe-logo-url.png'

        # Organisation Logo Path
        self.organisation_logo_path = ':/plugins/inasafe/supporters.png'

        # Disclaimer text
        self.disclaimer = disclaimer()

        # The output directory
        self.out_dir = None

        # Stored information from first impact layer
        self.first_impact = {
            'layer': None,
            'map_title': None,
            'hazard_title': None,
            'exposure_title': None,
            'postprocessing_report': None,
        }

        # Stored information from second impact layer
        self.second_impact = {
            'layer': None,
            'map_title': None,
            'hazard_title': None,
            'exposure_title': None,
            'postprocessing_report': None,
        }

        # Stored information from aggregation layer
        self.aggregation = {
            'layer': None,
            'aggregation_attribute': None
        }

        # The summary report, contains report for each aggregation area
        self.summary_report = {}

        # The html reports and its file path
        self.html_reports = {}

        # A boolean flag whether to merge entire area or aggregated
        self.entire_area_mode = False

        # Get the global settings and override some variable if exist
        self.read_settings()

        # Get all current project layers for combo box
        self.get_project_layers()

        # Set up context help
        help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        help_button.clicked.connect(self.show_help)

        # Show usage info
        self.show_info()
        self.restore_state()

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
            'areas and same hazard. To use:'
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
            'Select the aggregation layer that was used to generate the '
            'first and second impact layer.'))
        tips.add(self.tr(
            'Select an output directory.'))
        tips.add(self.tr(
            'Check "Use customized report template" checkbox and select the '
            'report template file if you want to use your own template. Note '
            'that all the map composer components that are needed must be '
            'fulfilled.'))
        tips.add(self.tr(
            'Click OK to generate the per aggregation area combined '
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
        try:
            last_path = settings.value('directory', type=str)
        except TypeError:
            last_path = ''
        self.output_directory.setText(last_path)

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
        """Show a dialog to choose directory."""
        # noinspection PyCallByClass,PyTypeChecker
        self.output_directory.setText(QFileDialog.getExistingDirectory(
            self, self.tr("Select Output Directory")))

    @pyqtSignature('')  # prevents actions being handled twice
    def on_report_template_chooser_clicked(self):
        """Show a dialog to choose directory"""
        # noinspection PyCallByClass,PyTypeChecker
        report_template_path = QtGui.QFileDialog.getOpenFileName(
            self,
            self.tr('Select Report Template'),
            self.template_path,
            self.tr('QPT File (*.qpt)'))

        # noinspection PyCallByClass,PyTypeChecker
        self.report_template_le.setText(report_template_path)

    def accept(self):
        """Do merging two impact layers."""
        # Store the current state to configuration file
        self.save_state()

        # Prepare all the input from dialog, validate, and store it
        try:
            self.prepare_input()
        except (InvalidLayerError,
                EmptyDirectoryError,
                FileNotFoundError) as ex:
            # noinspection PyCallByClass,PyTypeChecker, PyArgumentList
            QMessageBox.information(
                self,
                self.tr("InaSAFE Merge Impact Tool Information"),
                str(ex))
            return
        except CanceledImportDialogError:
            return

        # Validate all the layers logically
        try:
            self.validate_all_layers()
        except (NoKeywordsFoundError,
                KeywordNotFoundError,
                InvalidLayerError) as ex:
            # noinspection PyCallByClass,PyTypeChecker, PyArgumentList
            QMessageBox.information(
                self,
                self.tr("InaSAFE Merge Impact Tools Information"),
                str(ex))
            return

        # The input is valid, do the merging
        # Set cursor to wait cursor
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        #pylint: disable=W0703
        try:
            self.merge()
        except Exception as ex:
            # End wait cursor
            QtGui.qApp.restoreOverrideCursor()
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QMessageBox.warning(
                self,
                self.tr("InaSAFE Merge Impact Tools Error"),
                str(ex))
            return
            #pylint: enable=W0703

        # Finish doing it. End wait cursor
        QtGui.qApp.restoreOverrideCursor()

        # Give user successful information!
        # noinspection PyCallByClass,PyTypeChecker, PyArgumentList
        QMessageBox.information(
            self,
            self.tr('InaSAFE Merge Impact Tool Information'),
            self.tr(
                'Report from merging two impact layers was generated '
                'successfully.'))

        # Open output directory on file explorer
        output_directory_url = QUrl.fromLocalFile(self.out_dir)
        #noinspection PyTypeChecker,PyCallByClass
        QDesktopServices.openUrl(output_directory_url)

    def read_settings(self):
        """Set some variables from global settings on inasafe options dialog.
        """
        settings = QtCore.QSettings()

        # Organisation logo
        organisation_logo_path = settings.value(
            'inasafe/organisation_logo_path', '', type=str)
        if organisation_logo_path != '':
            self.organisation_logo_path = organisation_logo_path

        # Disclaimer text
        customised_disclaimer = settings.value(
            'inasafe/reportDisclaimer', '', type=str)
        if customised_disclaimer != '':
            self.disclaimer = customised_disclaimer

    def get_project_layers(self):
        """Get impact layers and aggregation layer currently loaded in QGIS."""
        #noinspection PyArgumentList
        registry = QgsMapLayerRegistry.instance()

        # MapLayers returns a QMap<QString id, QgsMapLayer layer>
        layers = registry.mapLayers().values()

        if len(layers) == 0:
            return

        # Clear the combo box first
        self.first_layer.clear()
        self.second_layer.clear()
        self.aggregation_layer.clear()

        for layer in layers:
            try:
                self.keyword_io.read_keywords(layer, 'impact_summary')
            except (NoKeywordsFoundError, KeywordNotFoundError):
                # Check if it has aggregation keyword
                try:
                    self.keyword_io.read_keywords(
                        layer, 'aggregation attribute')
                except (NoKeywordsFoundError, KeywordNotFoundError):
                    # Skip if there are no keywords at all
                    continue
                add_ordered_combo_item(
                    self.aggregation_layer,
                    layer.name(),
                    layer)
                continue
            except (UnsupportedProviderError, InvalidParameterError):
                # UnsupportedProviderError:
                #   Encounter unsupported provider layer, e.g Open Layer
                # InvalidParameterError:
                #   Encounter invalid layer source,
                #   see https://github.com/AIFDR/inasafe/issues/754
                continue

            add_ordered_combo_item(self.first_layer, layer.name(), layer)
            add_ordered_combo_item(self.second_layer, layer.name(), layer)

        # Add Entire Area Option to Aggregated Layer:
        self.aggregation_layer.insertItem(
            0,
            self.tr('Entire Area'),
            None
        )
        self.aggregation_layer.setCurrentIndex(0)

    def prepare_input(self):
        """Fetch all the input from dialog, validate, and store it.

        Consider this as a bridge between dialog interface and our logical
        stored data in this class

        :raises: InvalidLayerError, CanceledImportDialogError
        """
        # Validate The combobox impact layers (they should be different)
        first_layer_index = self.first_layer.currentIndex()
        second_layer_index = self.second_layer.currentIndex()

        if first_layer_index < 0:
            raise InvalidLayerError(self.tr('First layer is not valid.'))

        if second_layer_index < 0:
            raise InvalidLayerError(self.tr('Second layer is not valid.'))

        if first_layer_index == second_layer_index:
            raise InvalidLayerError(
                self.tr('First layer must be different to second layer''.'))

        # Get All Chosen Layer
        self.first_impact['layer'] = self.first_layer.itemData(
            self.first_layer.currentIndex(), QtCore.Qt.UserRole)
        self.second_impact['layer'] = self.second_layer.itemData(
            self.second_layer.currentIndex(), QtCore.Qt.UserRole)
        self.aggregation['layer'] = self.aggregation_layer.itemData(
            self.aggregation_layer.currentIndex(), QtCore.Qt.UserRole)

        # Validate the output directory
        self.require_directory()

        # Get output directory
        self.out_dir = self.output_directory.text()

        # Whether to use own report template:
        if self.report_template_checkbox.isChecked():
            own_template_path = self.report_template_le.text()
            if os.path.isfile(own_template_path):
                self.template_path = own_template_path
            else:
                raise FileNotFoundError(
                    self.tr('Template file does not exist.'))

        # Flag whether to merge entire area or based on aggregation unit
        if self.aggregation['layer'] is None:
            self.entire_area_mode = True

    def require_directory(self):
        """Ensure directory path entered in dialog exist.

        When the path does not exist, this function will ask the user if he
        wants to create it or not.

        :raises: CanceledImportDialogError - when user chooses 'No' in
            the question dialog for creating directory, or 'Yes' but the output
            directory path is empty
        """
        path = str(self.output_directory.text())

        if os.path.exists(path):
            return

        title = self.tr("Directory %s does not exist") % path
        question = self.tr(
            "Directory %s does not exist. Do you want to create it?"
        ) % path
        # noinspection PyCallByClass,PyTypeChecker
        answer = QMessageBox.question(
            self, title,
            question, QMessageBox.Yes | QMessageBox.No)

        if answer == QMessageBox.Yes:
            if len(path) != 0:
                os.makedirs(path)
            else:
                raise EmptyDirectoryError(
                    self.tr('Output directory cannot be empty.'))
        else:
            raise CanceledImportDialogError()

    def validate_all_layers(self):
        """Validate all layers based on the keywords.

        When we do the validation, we also fetch the information we need:

        1. 'map_title' from each impact layer
        2. 'exposure_title' from each impact layer
        3. 'postprocessing_report' from each impact layer
        4. 'aggregation_attribute' on aggregation layer, if user runs merging
           tools with aggregation layer chosen

        The things that we validate are:

        1. 'map_title' keyword must exist on each impact layer
        2. 'exposure_title' keyword must exist on each impact layer
        3. 'postprocessing_report' keyword must exist on each impact layer
        4. 'hazard_title' keyword must exist on each impact layer. Hazard title
           from first impact layer must be the same with second impact layer
           to indicate that both are generated from the same hazard layer.
        5. 'aggregation attribute' must exist when user wants to run merging
           tools with aggregation layer chosen.

        """
        required_attribute = ['map_title', 'exposure_title', 'hazard_title',
                              'postprocessing_report']
        # Fetch for first impact layer
        for attribute in required_attribute:
            try:
                #noinspection PyTypeChecker
                self.first_impact[attribute] = self.keyword_io.read_keywords(
                    self.first_impact['layer'], attribute)
            except NoKeywordsFoundError:
                raise NoKeywordsFoundError(
                    self.tr('No keywords found for first impact layer.'))
            except KeywordNotFoundError:
                raise KeywordNotFoundError(
                    self.tr(
                        'Keyword %s not found for first layer.' % attribute))

        # Fetch for second impact layer
        for attribute in required_attribute:
            try:
                #noinspection PyTypeChecker
                self.second_impact[attribute] = self.keyword_io.read_keywords(
                    self.second_impact['layer'], attribute)
            except NoKeywordsFoundError:
                raise NoKeywordsFoundError(
                    self.tr('No keywords found for second impact layer.'))
            except KeywordNotFoundError:
                raise KeywordNotFoundError(
                    self.tr(
                        'Keyword %s not found for second layer.' % attribute))

        # Validate that two impact layers are obtained from the same hazard.
        # Indicated by the same 'hazard_title' (to be fixed later by using
        # more reliable method)
        if (self.first_impact['hazard_title'] !=
                self.second_impact['hazard_title']):
            raise InvalidLayerError(
                self.tr('First impact layer and second impact layer do not '
                        'use the same hazard layer.'))

        # Fetch 'aggregation_attribute'
        # If the chosen aggregation layer not Entire Area, it should have
        # aggregation attribute keywords
        if not self.entire_area_mode:
            try:
                #noinspection PyTypeChecker
                self.aggregation['aggregation_attribute'] = \
                    self.keyword_io.read_keywords(
                        self.aggregation['layer'], 'aggregation attribute')
            except NoKeywordsFoundError:
                raise NoKeywordsFoundError(
                    self.tr('No keywords exist in aggregation layer.'))
            except KeywordNotFoundError:
                raise KeywordNotFoundError(
                    self.tr(
                        'Keyword aggregation attribute not found for '
                        'aggregation layer.'))

    def merge(self):
        """Merge the postprocessing_report from each impact."""
        # Ensure there is always only a single root element or minidom moans
        first_postprocessing_report = \
            self.first_impact['postprocessing_report']
        second_postprocessing_report = \
            self.second_impact['postprocessing_report']
        #noinspection PyTypeChecker
        first_report = '<body>' + first_postprocessing_report + '</body>'
        #noinspection PyTypeChecker
        second_report = '<body>' + second_postprocessing_report + '</body>'

        # Now create a dom document for each
        first_document = minidom.parseString(first_report)
        second_document = minidom.parseString(second_report)
        first_impact_tables = first_document.getElementsByTagName('table')
        second_impact_tables = second_document.getElementsByTagName('table')

        # Now create dictionary report from DOM
        first_report_dict = self.generate_report_dictionary_from_dom(
            first_impact_tables)
        second_report_dict = self.generate_report_dictionary_from_dom(
            second_impact_tables)

        # Generate report summary for all aggregation unit
        self.generate_report_summary(first_report_dict, second_report_dict)

        # Generate html reports file from merged dictionary
        self.generate_html_reports(first_report_dict, second_report_dict)

        # Generate PDF Reports using composer and/or atlas generation:
        self.generate_reports()

        # Delete html report files:
        for area in self.html_reports:
            report_path = self.html_reports[area]
            if os.path.exists(report_path):
                os.remove(report_path)

    @staticmethod
    def generate_report_dictionary_from_dom(html_dom):
        """Generate dictionary representing report from html dom.

        :param html_dom: Input representing document dom as report from each
            impact layer report.
        :type html_dom: str

        :return: Dictionary representing html_dom.
        :rtype: dict

        Dictionary Structure::

            { Aggregation_Area:
                {Exposure Type:{
                    Exposure Detail}
                }
            }

        Example::

           {"Jakarta Barat":
               {"Detailed Building Type Report":
                   {"Total inundated":150,
                    "Places of Worship": "No data"
                   }
               }
           }

        """
        merged_report_dict = OrderedDict()
        for table in html_dom:
            #noinspection PyUnresolvedReferences
            caption = table.getElementsByTagName('caption')[0].firstChild.data
            #noinspection PyUnresolvedReferences
            rows = table.getElementsByTagName('tr')
            header = rows[0]
            contains = rows[1:]
            for contain in contains:
                data = contain.getElementsByTagName('td')
                aggregation_area = data[0].firstChild.nodeValue
                exposure_dict = OrderedDict()
                if aggregation_area in merged_report_dict:
                    exposure_dict = merged_report_dict[aggregation_area]
                data_contain = data[1:]
                exposure_detail_dict = OrderedDict()
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

    def generate_report_summary(self, first_report_dict, second_report_dict):
        """Generate report summary for each aggregation area from merged
        report dictionary.

        For each exposure, search for the total only. Report dictionary looks
        like this:

        :param first_report_dict: Dictionary report from the first impact.
        :type first_report_dict: dict

        :param second_report_dict: Dictionary report from the second impact.
        :type second_report_dict: dict

        Dictionary structure::

            { aggregation_area:
                {exposure_type:{
                   exposure_detail}
                }
            }

        Example::

            {"Jakarta Barat":
                {"Detailed Building Type Report":
                    {"Total inundated":150,
                     "Places of Worship": "No data"
                    }
                }
            }

        """
        for aggregation_area in first_report_dict:
            html = ''
            html += '<table style="margin:0px auto">'

            # Summary total from first report
            html += '<tr><td><b>%s</b></td><td></td></tr>' % \
                    self.first_impact['exposure_title'].title()
            first_exposure_type_dict = first_report_dict[aggregation_area]
            first_exposure_type = first_exposure_type_dict.keys()[0]
            first_exposure_detail_dict = \
                first_exposure_type_dict[first_exposure_type]
            for datum in first_exposure_detail_dict:
                if self.tr('Total').lower() in datum.lower():
                    html += ('<tr>'
                             '<td>%s</td>'
                             '<td>%s</td>'
                             '</tr>') % \
                            (datum, first_exposure_detail_dict[datum])
                    break

            # Catch fallback for aggregation_area not exist in second_report
            if aggregation_area in second_report_dict:
                second_exposure_report_dict = second_report_dict[
                    aggregation_area]
                # Summary total from second report
                html += '<tr><td><b>%s</b></td><td></td></tr>' % \
                        self.second_impact['exposure_title'].title()
                second_exposure = second_exposure_report_dict.keys()[0]
                second_exposure_detail_dict = \
                    second_exposure_report_dict[second_exposure]
                for datum in second_exposure_detail_dict:
                    if self.tr('Total').lower() in datum.lower():
                        html += ('<tr>'
                                 '<td>%s</td>'
                                 '<td>%s</td>'
                                 '</tr>') % \
                                (datum, second_exposure_detail_dict[datum])
                        break

            html += '</table>'
            self.summary_report[aggregation_area.lower()] = html

    def generate_html_reports(self, first_report_dict, second_report_dict):
        """Generate html file for each aggregation units.

        It also saves the path of the each aggregation unit in
        self.html_reports.
        ::

            Ex. {"jakarta barat": "/home/jakarta barat.html",
                 "jakarta timur": "/home/jakarta timur.html"}

        :param first_report_dict: Dictionary report from first impact.
        :type first_report_dict: dict

        :param second_report_dict: Dictionary report from second impact.
        :type second_report_dict: dict
        """
        for aggregation_area in first_report_dict:
            html = html_header()
            html += ('<table width="100%" style="position:absolute;left:0px;"'
                     'class="table table-condensed table-striped">')
            html += '<caption><h4>%s</h4></caption>' % \
                    aggregation_area.title()

            html += '<tr>'

            # First impact on the left side
            html += '<td width="48%">'
            html += '<table width="100%">'
            html += '<thead><th>%s</th></thead>' % \
                    self.first_impact['exposure_title'].upper()
            first_exposure_report_dict = first_report_dict[aggregation_area]
            for first_exposure in first_exposure_report_dict:
                first_exposure_detail_dict = \
                    first_exposure_report_dict[first_exposure]
                html += '<tr><th><i>%s</i></th><th></th></tr>' % \
                        first_exposure.title()
                for datum in first_exposure_detail_dict:
                    html += ('<tr>'
                             '<td>%s</td>'
                             '<td>%s</td>'
                             '</tr>') % (datum,
                                         first_exposure_detail_dict[datum])
            html += '</table>'
            html += '</td>'

            # Second impact on the right side
            if aggregation_area in second_report_dict:
                # Add spaces between
                html += '<td width="4%">'
                html += '</td>'

                # Second impact report
                html += '<td width="48%">'
                html += '<table width="100%">'
                html += '<thead><th>%s</th></thead>' % \
                        self.second_impact['exposure_title'].upper()
                second_exposure_report_dict = \
                    second_report_dict[aggregation_area]
                for second_exposure in second_exposure_report_dict:
                    second_exposure_detail_dict = \
                        second_exposure_report_dict[second_exposure]
                    html += '<tr><th><i>%s</i></th><th></th></tr>' % \
                            second_exposure.title()
                    for datum in second_exposure_detail_dict:
                        html += ('<tr>'
                                 '<td>%s</td>'
                                 '<td>%s</td>'
                                 '</tr>') % \
                                (datum,
                                 second_exposure_detail_dict[datum])
                html += '</table>'
                html += '</td>'

            html += '</tr>'
            html += '</table>'
            html += html_footer()

            file_path = '%s.html' % aggregation_area
            path = os.path.join(temp_dir(), file_path)
            html_to_file(html, path)
            self.html_reports[aggregation_area.lower()] = path

    def generate_reports(self):
        """Generate PDF reports for each aggregation unit using map composer.

        First the report template is loaded with the renderer from two
        impact layers. After it's loaded, if it is not aggregated then
        we just use composition to produce report. Since there are two
        impact maps here, we need to set a new extent for these impact maps
        by a simple calculation.

        If it is not aggregated then we use a powerful QGIS atlas generation
        on composition. Since we save each report table representing each
        aggregated area on self.html_report (which is a dictionary with the
        aggregation area name as a key and its path as a value), and we set
        the aggregation area name as current filename on atlas generation,
        we can match these two so that we have the right report table for
        each report.

        For those two cases, we use the same template. The report table is
        basically an HTML frame. Of course after the merging process is done,
        we delete each report table on self.html_reports physically on disk.
        """
        # Setup Map Renderer and set all the layer
        renderer = QgsMapRenderer()
        layer_set = [self.first_impact['layer'].id(),
                     self.second_impact['layer'].id()]

        # If aggregated, append chosen aggregation layer
        if not self.entire_area_mode:
            layer_set.append(self.aggregation['layer'].id())

        # Set Layer set to renderer
        renderer.setLayerSet(layer_set)

        # Create composition
        composition = self.load_template(renderer)

        # Get Map
        composer_map = composition.getComposerItemById('impact-map')

        # Get HTML Report Frame
        html_report_item = \
            composition.getComposerItemById('merged-report-table')
        html_report_frame = composition.getComposerHtmlByItem(html_report_item)

        if self.entire_area_mode:
            # Get composer map size
            composer_map_width = composer_map.boundingRect().width()
            composer_map_height = composer_map.boundingRect().height()

            # Set the extent from two impact layers to fit into composer map
            composer_size_ratio = float(
                composer_map_height / composer_map_width)

            # The extent of two impact layers
            min_x = min(self.first_impact['layer'].extent().xMinimum(),
                        self.second_impact['layer'].extent().xMinimum())
            min_y = min(self.first_impact['layer'].extent().yMinimum(),
                        self.second_impact['layer'].extent().yMinimum())
            max_x = max(self.first_impact['layer'].extent().xMaximum(),
                        self.second_impact['layer'].extent().xMaximum())
            max_y = max(self.first_impact['layer'].extent().yMaximum(),
                        self.second_impact['layer'].extent().yMaximum())
            max_width = max_x - min_x
            max_height = max_y - min_y
            layers_size_ratio = float(max_height / max_width)
            center_x = min_x + float(max_width / 2.0)
            center_y = min_y + float(max_height / 2.0)

            # The extent should fit the composer map size
            new_width = max_width
            new_height = max_height

            # QgsComposerMap only overflows to height, so if it overflows,
            # the extent of the width should be widened
            if layers_size_ratio > composer_size_ratio:
                new_width = max_height / composer_size_ratio

            # Set new extent
            fit_min_x = center_x - (new_width / 2.0)
            fit_max_x = center_x + (new_width / 2.0)
            fit_min_y = center_y - (new_height / 2.0)
            fit_max_y = center_y + (new_height / 2.0)

            # Create the extent and set it to the map
            map_extent = QgsRectangle(
                fit_min_x, fit_min_y, fit_max_x, fit_max_y)
            composer_map.setNewExtent(map_extent)

            # Add grid to composer map
            split_count = 5
            x_interval = new_width / split_count
            composer_map.setGridIntervalX(x_interval)
            y_interval = new_height / split_count
            composer_map.setGridIntervalY(y_interval)

            # Self.html_reports must have only 1 key value pair
            area_title = list(self.html_reports.keys())[0]

            # Set Report Summary
            summary_report = composition.getComposerItemById('summary-report')
            summary_report.setText(self.summary_report[area_title])

            # Set Aggregation Area Label
            area_label = composition.getComposerItemById('aggregation-area')
            area_label.setText(area_title.title())

            # Set merged-report-table
            html_report_path = self.html_reports[area_title]
            #noinspection PyArgumentList
            html_frame_url = QUrl.fromLocalFile(html_report_path)
            html_report_frame.setUrl(html_frame_url)

            # Export composition to PDF file
            file_name = '_'.join(area_title.split())
            file_path = '%s.pdf' % file_name
            path = os.path.join(self.out_dir, file_path)
            composition.exportAsPDF(path)
        else:
            # Create atlas composition:
            atlas = QgsAtlasComposition(composition)

            # Set coverage layer
            # Map will be clipped by features from this layer:
            atlas.setCoverageLayer(self.aggregation['layer'])

            # Add grid to composer map from coverage layer
            split_count = 5
            map_width = self.aggregation['layer'].extent().width()
            map_height = self.aggregation['layer'].extent().height()
            x_interval = map_width / split_count
            composer_map.setGridIntervalX(x_interval)
            y_interval = map_height / split_count
            composer_map.setGridIntervalY(y_interval)

            # Set composer map that will be used for printing atlas
            atlas.setComposerMap(composer_map)

            # set output filename pattern
            atlas.setFilenamePattern(
                self.aggregation['aggregation_attribute'])

            # Start rendering
            atlas.beginRender()

            # Iterate all aggregation unit in aggregation layer
            for i in range(0, atlas.numFeatures()):
                atlas.prepareForFeature(i)

                current_filename = atlas.currentFilename()
                file_name = '_'.join(current_filename.split())
                file_path = '%s.pdf' % file_name
                path = os.path.join(self.out_dir, file_path)

                # Only print the area that has the report
                area_title = current_filename.lower()
                if area_title in self.summary_report:
                    # Set Report Summary
                    summary_report = composition.getComposerItemById(
                        'summary-report')
                    summary_report.setText(self.summary_report[area_title])

                    # Set Aggregation Area Label
                    area_label = composition.getComposerItemById(
                        'aggregation-area')
                    area_label.setText(area_title.title())

                    # Set merged-report-table
                    html_report_path = self.html_reports[area_title]
                    #noinspection PyArgumentList
                    html_frame_url = QUrl.fromLocalFile(html_report_path)
                    html_report_frame.setUrl(html_frame_url)

                    # Export composition to PDF file
                    composition.exportAsPDF(path)

            # End of rendering
            atlas.endRender()

    #noinspection PyArgumentList
    def load_template(self, renderer):
        """Load composer template for merged report.

        Validate it as well. The template needs to have:
        1. QgsComposerMap with id 'impact-map' for merged impact map.
        2. QgsComposerPicture with id 'safe-logo' for InaSAFE logo.
        3. QgsComposerLabel with id 'summary-report' for a summary of two
        impacts.
        4. QgsComposerLabel with id 'aggregation-area' to indicate the area
        of aggregation.
        5. QgsComposerScaleBar with id 'map-scale' for impact map scale.
        6. QgsComposerLegend with id 'map-legend' for impact map legend.
        7. QgsComposerPicture with id 'organisation-logo' for organisation
        logo.
        8. QgsComposerLegend with id 'impact-legend' for map legend.
        9. QgsComposerHTML with id 'merged-report-table' for the merged report.

        :param renderer: Map renderer
        :type renderer: QgsMapRenderer

        """
        # Create Composition
        composition = QgsComposition(renderer)

        template_file = QtCore.QFile(self.template_path)
        template_file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
        template_content = template_file.readAll()
        template_file.close()

        # Create a dom document containing template content
        document = QtXml.QDomDocument()
        document.setContent(template_content)

        # Prepare Map Substitution
        impact_title = '%s and %s' % (
            self.first_impact['map_title'],
            self.second_impact['map_title'])
        substitution_map = {
            'impact-title': impact_title,
            'hazard-title': self.first_impact['hazard_title'],
            'disclaimer': self.disclaimer
        }

        # Load template
        load_status = composition.loadFromTemplate(document, substitution_map)
        if not load_status:
            raise ReportCreationError(
                self.tr('Error loading template %s') %
                self.template_path)

        # Validate all needed composer components
        component_ids = ['impact-map', 'safe-logo', 'summary-report',
                         'aggregation-area', 'map-scale', 'map-legend',
                         'organisation-logo', 'merged-report-table']
        for component_id in component_ids:
            component = composition.getComposerItemById(component_id)
            if component is None:
                raise ReportCreationError(self.tr(
                    'Component %s could not be found' % component_id))

        # Set InaSAFE logo
        safe_logo = composition.getComposerItemById('safe-logo')
        safe_logo.setPictureFile(self.safe_logo_path)

        # set organisation logo
        org_logo = composition.getComposerItemById('organisation-logo')
        org_logo.setPictureFile(self.organisation_logo_path)

        # Set Map Legend
        legend = composition.getComposerItemById('map-legend')
        legend.updateLegend()

        return composition
