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
from collections import OrderedDict
from xml.dom import minidom

#noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore, QtXml
#noinspection PyPackageRequirements
from PyQt4.QtCore import QSettings, pyqtSignature, QUrl
#noinspection PyPackageRequirements
from PyQt4.QtGui import QDialog, QMessageBox, QFileDialog
from qgis.core import (
    QgsMapLayerRegistry,
    QgsMapRenderer,
    QgsComposition,
    QgsRectangle,
    QgsAtlasComposition)

from safe_qgis.ui.impact_merge_dialog_base import Ui_ImpactMergeDialogBase

from safe_qgis.exceptions import (
    InvalidLayerError,
    CanceledImportDialogError,
    NoKeywordsFoundError,
    KeywordNotFoundError,
    ReportCreationError)
from safe_qgis.safe_interface import messaging as m
from safe_qgis.utilities.utilities import (
    html_header,
    html_footer,
    html_to_file,
    add_ordered_combo_item)
from safe_qgis.utilities.help import show_context_help
from safe_qgis.safe_interface import styles
from safe_qgis.utilities.keyword_io import KeywordIO

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
        help_button.clicked.connect(self.show_help)

        # Show usafe info
        self.show_info()
        self.restore_state()

        # Template Path for composer
        self.template_path = (
            ':/plugins/inasafe/merged_report.qpt'
        )

        # Safe Logo Path
        self.safe_logo_path = ':/plugins/inasafe/bnpb_logo.png'

        # All the chosen layers to be processed
        self.first_impact_layer = None
        self.second_impact_layer = None
        self.chosen_aggregation_layer = None

        # The output directory
        self.out_dir = None

        # The html reports and its file path
        # Ex. {"jakarta barat": "/home/jakarta barat.html",
        #      "jakarta timur": "/home/jakarta timur.html"}
        self.html_reports = {}

        # Whether to merge entire area or aggregated
        self.entire_area_mode = False

        # The attribute name to aggregate in chosen aggregation layer
        self.aggregation_attribute = None

        # Report from first and second impact layer keywords:
        self.first_postprocessing_report = None
        self.second_postprocessing_report = None

        # Get all current project layers for combo box
        self.get_project_layers()

        # Add Entire Area Option to Aggregated Layer:
        self.aggregation_layer.insertItem(
            0,
            self.tr('Entire Area'),
            None
        )
        self.aggregation_layer.setCurrentIndex(0)

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
        # Store the current state to configuration file
        self.save_state()

        # Validate the directory
        try:
            self.require_directory()
        except CanceledImportDialogError:
            # Don't show anything because this exception raised
            # when user canceling the import process directly
            pass

        # Get All Chosen Layer
        self.get_all_chosen_layers()

        # Get output directory
        self.out_dir = self.output_directory.text()

        # Flag whether to merge entire area or based on aggregation unit
        if self.chosen_aggregation_layer is None:
            self.entire_area_mode = True

        # Validate all the layers
        try:
            self.validate()
        except (InvalidLayerError,
                NoKeywordsFoundError,
                KeywordNotFoundError) as ex:
            # noinspection PyCallByClass,PyTypeChecker, PyArgumentList
            QMessageBox.information(
                self,
                self.tr("InaSAFE Merge Impact Tools Information"),
                str(ex))
            return

        # Merging Process
        # Set cursor to wait cursor
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
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

        # Hohoho finish doing it. End wait cursor
        QtGui.qApp.restoreOverrideCursor()

        # Give user successful information!
        # noinspection PyCallByClass,PyTypeChecker, PyArgumentList
        QMessageBox.information(
            self,
            self.tr('InaSAFE Merge Impact Tools Information'),
            self.tr(
                'Report from merging two impact layers is generated '
                'successfully.'))

        # Process is Done
        self.done(QDialog.Accepted)

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
            # noinspection PyCallByClass,PyTypeChecker, PyArgumentList
                QMessageBox.information(
                    self,
                    self.tr('InaSAFE Merge Impact Tools Error'),
                    self.tr('Output directory cannot be empty.'))
                raise CanceledImportDialogError()

        else:
            raise CanceledImportDialogError()

    def get_all_chosen_layers(self):
        """Get all chosen layers after user clicks merge."""
        self.first_impact_layer = self.first_layer.itemData(
            self.first_layer.currentIndex(), QtCore.Qt.UserRole)
        self.second_impact_layer = self.second_layer.itemData(
            self.second_layer.currentIndex(), QtCore.Qt.UserRole)
        self.chosen_aggregation_layer = self.aggregation_layer.itemData(
            self.aggregation_layer.currentIndex(), QtCore.Qt.UserRole)

    def validate(self):
        """Verify that there are two impact layers and they are different."""
        if self.first_layer.currentIndex() < 0:
            raise InvalidLayerError(self.tr('First layer is not valid.'))

        if self.second_layer.currentIndex() < 0:
            raise InvalidLayerError(self.tr('Second layer is not valid.'))

        if self.first_impact_layer.id() == self.second_impact_layer.id():
            raise InvalidLayerError(
                self.tr('First layer must be different with second layer''.'))

        # 1st impact layer should have postprocessing_report keywords
        try:
            self.first_postprocessing_report = \
                self.keyword_io.read_keywords(
                    self.first_impact_layer, 'postprocessing_report')
        except NoKeywordsFoundError:
            raise NoKeywordsFoundError(
                self.tr('No keywords found in first impact layer.'))
        except KeywordNotFoundError:
            raise KeywordNotFoundError(
                self.tr('Keyword postprocessing_report is not found in first '
                        'layer.'))

        # 2nd impact layer should have postprocessing_report keywords
        try:
            self.second_postprocessing_report = \
                self.keyword_io.read_keywords(
                    self.second_impact_layer, 'postprocessing_report')
        except NoKeywordsFoundError:
            raise NoKeywordsFoundError(
                self.tr('No keywords exist in second impact layer.'))
        except KeywordNotFoundError:
            raise KeywordNotFoundError(
                self.tr('Keyword postprocessing_report is not found in second '
                        'layer.'))

        # If the chosen aggregation layer not Entire Area, it should have
        # aggregation attribute keywords
        if not self.entire_area_mode:
            try:
                self.aggregation_attribute = \
                    self.keyword_io.read_keywords(
                        self.chosen_aggregation_layer,
                        'aggregation attribute')
            except NoKeywordsFoundError:
                raise NoKeywordsFoundError(
                    self.tr('No keywords exist in aggregation layer.'))
            except KeywordNotFoundError:
                raise KeywordNotFoundError(
                    self.tr(
                        'Keyword aggregation attribute is not found in '
                        'aggregation layer.'))

    def merge(self):
        """Merge the postprocessing_report from each impact."""
        # Ensure there is always only a single root element or minidom moans
        first_report = '<body>' + self.first_postprocessing_report + '</body>'
        second_report = (
            '<body>' + self.second_postprocessing_report + '</body>')

        # Now create a dom document for each
        first_document = minidom.parseString(first_report)
        second_document = minidom.parseString(second_report)
        tables = first_document.getElementsByTagName('table')
        tables += second_document.getElementsByTagName('table')

        # Now create dictionary report from DOM
        merged_report_dict = self.generate_report_dictionary_from_dom(tables)

        # Generate html reports from merged dictionary
        html_reports = self.generate_html_from_merged_report(
            merged_report_dict)

        # Now Generate html file from html reports.
        # Each file will be generated for each html report
        for html_report in html_reports:
            aggregation_area = html_report[0]
            html = html_report[1]
            path = '%s/%s.html' % (
                str(self.out_dir),
                aggregation_area)
            html_to_file(html, path)
            self.html_reports[aggregation_area.lower()] = path

        # Generate Reports:
        self.generate_reports()

        # Delete report files:
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

    @staticmethod
    def generate_html_from_merged_report(merged_report_dict):
        """Generate html for aggregation units from merged report.

        :param merged_report_dict: A dictionary of merged report.
        :type merged_report_dict: dict

        :return: HTML for each aggregation unit report.
        :rtype: list
        """
        html_reports = []
        for aggregation_area in merged_report_dict:
            html = html_header()
            html += ('<table style="width: auto" '
                     'class="table table-condensed table-striped">')
            html += '<caption><h4>%s</h4></caption>' % aggregation_area.upper()
            exposure_report_dict = merged_report_dict[aggregation_area]
            for exposure in exposure_report_dict:
                exposure_detail_dict = exposure_report_dict[exposure]
                html += '<tr><th>%s</th><th></th></tr>' % exposure.upper()
                for datum in exposure_detail_dict:
                    html += ('<tr>'
                             '<td>%s</td>'
                             '<td>%s</td>'
                             '</tr>') % (datum, exposure_detail_dict[datum])
            html += '</table>'
            html += html_footer()
            html_report = (aggregation_area, html)
            html_reports.append(html_report)

        return html_reports

    def get_project_layers(self):
        """Get impact layers and aggregation layer currently loaded in QGIS."""
        #noinspection PyArgumentList
        registry = QgsMapLayerRegistry.instance()

        # MapLayers returns a QMap<QString id, QgsMapLayer layer>
        layers = registry.mapLayers().values()

        # For issue #618
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

            add_ordered_combo_item(self.first_layer, layer.name(), layer)
            add_ordered_combo_item(self.second_layer, layer.name(), layer)

    def generate_reports(self):
        """Generate reports for each aggregation unit.

        If it is aggregated then use atlas generation.
        If it is not (entire area) then just use composition.

        .. note:: Akbar I think we should add a more verbose description of
            how the logic works here - how the html report makes its way in
            the composer map html and so on...
        """
        # Setup Map Renderer and set all the layer
        renderer = QgsMapRenderer()
        layer_set = [self.first_impact_layer.id(),
                     self.second_impact_layer.id()]

        # If aggregated, append chosen aggregation layer
        if not self.entire_area_mode:
            layer_set.append(self.chosen_aggregation_layer.id())

        # Set Layer set to renderer
        renderer.setLayerSet(layer_set)

        # Create composition
        composition = self.load_template(renderer)

        # Get Map
        composer_map = composition.getComposerItemById('impact-map')

        # Get HTML Report Frame
        html_report_item = composition.getComposerItemById('merged-report')
        html_report_frame = composition.getComposerHtmlByItem(html_report_item)

        if self.entire_area_mode:
            # Get composer map size
            composer_map_width = composer_map.boundingRect().width()
            composer_map_height = composer_map.boundingRect().height()

            # Set the extent from two impact layers to fit into composer map
            composer_size_ratio = float(
                composer_map_height / composer_map_width)

            # The extent of two impact layers
            min_x = min(self.first_impact_layer.extent().xMinimum(),
                        self.second_impact_layer.extent().xMinimum())
            min_y = min(self.first_impact_layer.extent().yMinimum(),
                        self.second_impact_layer.extent().yMinimum())
            max_x = max(self.first_impact_layer.extent().xMaximum(),
                        self.second_impact_layer.extent().xMaximum())
            max_y = max(self.first_impact_layer.extent().yMaximum(),
                        self.second_impact_layer.extent().yMaximum())
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
            fit_min_x = center_x - (new_width/2.0)
            fit_max_x = center_x + (new_width/2.0)
            fit_min_y = center_y - (new_height/2.0)
            fit_max_y = center_y + (new_height/2.0)

            # Create the extent and set it to the map
            map_extent = QgsRectangle(
                fit_min_x,
                fit_min_y,
                fit_max_x,
                fit_max_y)
            composer_map.setNewExtent(map_extent)

            # Add grid to composer map
            split_count = 5
            x_interval = new_width / split_count
            composer_map.setGridIntervalX(x_interval)
            y_interval = new_height / split_count
            composer_map.setGridIntervalY(y_interval)

            # Self.html_reports must have only 1 key value pair
            area_title = list(self.html_reports.keys())[0]
            html_report_path = self.html_reports[area_title]
            html_report_frame.setUrl(QUrl('file://%s' % html_report_path))

            path = '%s/%s.pdf' % (
                str(self.out_dir),
                area_title)
            composition.exportAsPDF(path)
        else:
            # Create atlas composition:
            atlas = QgsAtlasComposition(composition)

            # Set coverage layer
            # Map will be clipped by features from this layer:
            atlas.setCoverageLayer(self.chosen_aggregation_layer)

            # Add grid to composer map from coverage layer
            split_count = 5
            map_width = self.chosen_aggregation_layer.extent().width()
            map_height = self.chosen_aggregation_layer.extent().height()
            x_interval = map_width / split_count
            composer_map.setGridIntervalX(x_interval)
            y_interval = map_height / split_count
            composer_map.setGridIntervalY(y_interval)

            # Set composer map that will be used for printing atlas
            atlas.setComposerMap(composer_map)

            # set output filename pattern
            atlas.setFilenamePattern(self.aggregation_attribute)

            # Start rendering
            atlas.beginRender()

            # Iterate all aggregation unit in aggregation layer
            for i in range(0, atlas.numFeatures()):
                atlas.prepareForFeature(i)

                current_filename = atlas.currentFilename()
                path = '%s/%s.pdf' % (
                    str(self.out_dir),
                    current_filename)

                # Only print the area that has the report
                area_title = current_filename.lower()
                if area_title in self.html_reports:
                    html_report_path = self.html_reports[area_title]
                    html_report_frame.setUrl(
                        QUrl('file://%s' % html_report_path))
                    composition.exportAsPDF(path)

            # End of rendering
            atlas.endRender()

    def load_template(self, renderer):
        """Load composer template for merged report.

        There are 2 templates. The template that is chosen based on
        whether it is aggregated or not

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

        # Map Substitution
        substitution_map = {
            'impact-title': self.get_impact_title()
        }

        # Load template
        load_status = composition.loadFromTemplate(document, substitution_map)
        if not load_status:
            raise ReportCreationError(
                self.tr('Error loading template %s') %
                self.template_path)

        # Set logo
        safe_logo = composition.getComposerItemById('safe-logo')
        if safe_logo is not None:
            safe_logo.setPictureFile(self.safe_logo_path)
        else:
            raise ReportCreationError(
                self.tr('Image "safe-logo" could not be found'))

        # Set Map Legend
        legend = composition.getComposerItemById('impact-legend')
        legend.setTitle(self.tr('Legend'))
        legend.updateLegend()

        return composition

    def get_impact_title(self):
        """Get the map title from the two impact layers.

        :returns: None on error, otherwise the title.
        :rtype: None, str
        """
        try:
            first_impact_title = self.keyword_io.read_keywords(
                self.first_impact_layer,
                'map_title')
            second_impact_title = self.keyword_io.read_keywords(
                self.second_impact_layer,
                'map_title')
            return '%s and %s' % (first_impact_title, second_impact_title)
        except KeywordNotFoundError:
            return None
        except Exception:
            return None
