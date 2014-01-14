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
        self.template_path = os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            'resources',
            'qgis-composer-templates',
            'merged_report.qpt')

        # Safe Logo Path
        self.safe_logo_path = os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            'resources',
            'img',
            'logos',
            'inasafe-logo-url.png')

        # Organisation Logo Path
        self.oganisation_logo_path = os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            'resources',
            'img',
            'logos',
            'supporters.png')

        # All the chosen layers to be processed
        self.first_impact_layer = None
        self.second_impact_layer = None
        self.chosen_aggregation_layer = None

        # Title of used hazard
        self.hazard_title = ''

        # The output directory
        self.out_dir = None

        # The html reports and its file path
        self.html_reports = {}

        # A boolean flag whether to merge entire area or aggregated
        self.entire_area_mode = False

        # The attribute name to be aggregated in chosen aggregation layer
        self.aggregation_attribute = None

        # Report from first and second impact layer keywords:
        self.first_postprocessing_report = None
        self.second_postprocessing_report = None

        # Get all current project layers for combo box
        self.get_project_layers()

        # Set up context help
        help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        help_button.clicked.connect(self.show_help)

        # Show usafe info
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
        """ Show a dialog to choose directory """
        # noinspection PyCallByClass,PyTypeChecker
        self.output_directory.setText(QFileDialog.getExistingDirectory(
            self, self.tr("Select output directory")))

    def accept(self):
        """Do merging two impact layers."""
        # Store the current state to configuration file
        self.save_state()

        # Prepare all the input from dialog, validate, and store it
        try:
            self.prepare_input()
        except (InvalidLayerError, EmptyDirectoryError) as ex:
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
        self.first_impact_layer = self.first_layer.itemData(
            self.first_layer.currentIndex(), QtCore.Qt.UserRole)
        self.second_impact_layer = self.second_layer.itemData(
            self.second_layer.currentIndex(), QtCore.Qt.UserRole)
        self.chosen_aggregation_layer = self.aggregation_layer.itemData(
            self.aggregation_layer.currentIndex(), QtCore.Qt.UserRole)

        # Validate the output directory
        self.require_directory()

        # Get output directory
        self.out_dir = self.output_directory.text()

        # Flag whether to merge entire area or based on aggregation unit
        if self.chosen_aggregation_layer is None:
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
        """Validate all layers based on the keywords."""
        # 1st impact layer should have postprocessing_report keywords
        try:
            self.first_postprocessing_report = \
                self.keyword_io.read_keywords(
                    self.first_impact_layer, 'postprocessing_report')
        except NoKeywordsFoundError:
            raise NoKeywordsFoundError(
                self.tr('No keywords found for first impact layer.'))
        except KeywordNotFoundError:
            raise KeywordNotFoundError(
                self.tr('Keyword postprocessing_report not found for first '
                        'layer.'))

        # 2nd impact layer should have postprocessing_report keywords
        try:
            self.second_postprocessing_report = \
                self.keyword_io.read_keywords(
                    self.second_impact_layer, 'postprocessing_report')
        except NoKeywordsFoundError:
            raise NoKeywordsFoundError(
                self.tr('No keywords found in second impact layer.'))
        except KeywordNotFoundError:
            raise KeywordNotFoundError(
                self.tr('Keyword postprocessing_report not found for second '
                        'layer.'))

        # 1st and 2nd layer should be generated from the same hazard
        # layer. It is indicated from 'hazard_title' keywords
        try:
            first_hazard_title = \
                self.keyword_io.read_keywords(
                    self.first_impact_layer, 'hazard_title')
        except NoKeywordsFoundError:
            raise NoKeywordsFoundError(
                self.tr('No keywords found for first impact layer.'))
        except KeywordNotFoundError:
            raise KeywordNotFoundError(
                self.tr('Keyword hazard_title not found for first '
                        'layer.'))

        try:
            second_hazard_title = \
                self.keyword_io.read_keywords(
                    self.second_impact_layer, 'hazard_title')
        except NoKeywordsFoundError:
            raise NoKeywordsFoundError(
                self.tr('No keywords found for second impact layer.'))
        except KeywordNotFoundError:
            raise KeywordNotFoundError(
                self.tr('Keyword hazard_title not found for second '
                        'layer.'))

        if first_hazard_title == second_hazard_title:
            self.hazard_title = first_hazard_title
        else:
            raise InvalidLayerError(
                self.tr('First impact layer and second impact layer do not '
                        'use the same hazard layer.'))

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
                        'Keyword aggregation attribute not found for '
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

        # Generate html reports file from merged dictionary
        self.generate_html_reports(merged_report_dict)

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

    def generate_html_reports(self, merged_report_dict):
        """Generate html file for each aggregation units.

        It also saves the path of the each aggregation unit in
        self.html_reports.
        Ex. {"jakarta barat": "/home/jakarta barat.html",
             "jakarta timur": "/home/jakarta timur.html"}

        :param merged_report_dict: A dictionary of merged report.
        :type merged_report_dict: dict
        """
        for aggregation_area in merged_report_dict:
            html = html_header()
            html += ('<table style="margin:0px auto;" '
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

            file_path = '%s.html' % aggregation_area
            path = os.path.join(self.out_dir, file_path)
            html_to_file(html, path)
            self.html_reports[aggregation_area.lower()] = path

    def generate_reports(self):
        """Generate PDF reports for each aggregation unit using map composer.

        .. First the report template is loaded with the renderer from two
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
            fit_min_x = center_x - (new_width / 2.0)
            fit_max_x = center_x + (new_width / 2.0)
            fit_min_y = center_y - (new_height / 2.0)
            fit_max_y = center_y + (new_height / 2.0)

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

            # Set Aggregation Area Label
            area_label = composition.getComposerItemById('aggregation-area')
            area_label.setText(area_title.upper())

            html_report_path = self.html_reports[area_title]
            #noinspection PyArgumentList
            html_frame_url = QUrl.fromLocalFile(html_report_path)
            html_report_frame.setUrl(html_frame_url)

            file_name = '_'.join(area_title.split())
            file_path = '%s.pdf' % file_name
            path = os.path.join(self.out_dir, file_path)
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
                file_name = '_'.join(current_filename.split())
                file_path = '%s.pdf' % file_name
                path = os.path.join(self.out_dir, file_path)

                # Only print the area that has the report
                area_title = current_filename.lower()
                if area_title in self.html_reports:
                    # Set Aggregation Area Label
                    area_label = composition.getComposerItemById(
                        'aggregation-area')
                    area_label.setText(area_title.upper())

                    html_report_path = self.html_reports[area_title]
                    #noinspection PyArgumentList
                    html_frame_url = QUrl.fromLocalFile(html_report_path)
                    html_report_frame.setUrl(html_frame_url)
                    composition.exportAsPDF(path)

            # End of rendering
            atlas.endRender()

    #noinspection PyArgumentList
    def load_template(self, renderer):
        """Load composer template for merged report.

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
        #noinspection PyTypeChecker,PyCallByClass
        safe_logo_path = QUrl.fromLocalFile(str(self.safe_logo_path))
        #noinspection PyTypeChecker,PyCallByClass
        organisation_logo_path = QUrl.fromLocalFile(
            str(self.oganisation_logo_path))
        substitution_map = {
            'impact-title': self.get_impact_title(),
            'hazard-title': self.hazard_title,
            'inasafe-logo': safe_logo_path.toString(),
            'organisation-logo': organisation_logo_path.toString()
        }

        # Load template
        load_status = composition.loadFromTemplate(document, substitution_map)
        if not load_status:
            raise ReportCreationError(
                self.tr('Error loading template %s') %
                self.template_path)

        # Set Map Legend
        legend = composition.getComposerItemById('impact-legend')
        if legend is not None:
            legend.updateLegend()
        else:
            raise ReportCreationError(
                self.tr('Legend "impact-legend" could not be found'))

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
