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
from PyQt4.QtCore import QSettings, pyqtSignature, QVariant
#noinspection PyPackageRequirements
from PyQt4.QtGui import QDialog, QMessageBox, QFileDialog
from qgis.core import (QgsMapLayerRegistry,
                       QgsMapRenderer,
                       QgsComposition,
                       QgsVectorDataProvider,
                       QgsField,
                       QgsAtlasComposition)

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

        # The image table reports
        # Ex. {"jakarta barat": "/home/jakarta barat.png",
        #      "jakarta timur": "/home/jakarta timur.png"}
        self.image_reports = {}

        # Template Path for composer
        self.aggregated_template_path = (
            ':/plugins/inasafe/aggregated_merged_report.qpt'
        )
        self.entire_area_template_path = (
            ':/plugins/inasafe/entire_area_merged_report.qpt'
        )

        # Temporary attribute name for atlas generation
        self.temp_attribute_name = 'IMG_PATH'

        # The composition instance to be used for atlas generation
        self.composition = None

        # All the chosen layers to be processed
        self.first_impact_layer = None
        self.second_impact_layer = None
        self.chosen_aggregation_layer = None

        # Get all current project layers for combo box
        self.get_project_layers()

        # Add Entire Area Option to Aggregated Layer:
        add_ordered_combo_item(
            self.aggregation_layer,
            self.tr('Entire Area'),
            None
        )

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
            # Process Merging
            self.merge()

            # Process is Done
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
        """Verify that there are two impact layers and they are different."""
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
            # noinspection PyCallByClass,PyTypeChecker, PyArgumentList
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

        # Get all the chosen layer
        self.first_impact_layer = self.first_layer.itemData(
            self.first_layer.currentIndex(), QtCore.Qt.UserRole)
        self.second_impact_layer = self.second_layer.itemData(
            self.second_layer.currentIndex(), QtCore.Qt.UserRole)
        self.chosen_aggregation_layer = self.aggregation_layer.itemData(
            self.aggregation_layer.currentIndex(), QtCore.Qt.UserRole)

        # Validate all the layer
        # 1st and 2nd layer should have postprocessing_report keywords
        # If Aggregation layer not Entire Area, it should have aggregation
        # attribute keywords
        try:
            first_report = self.keyword_io.read_keywords(
                self.first_impact_layer, 'postprocessing_report')
            second_report = self.keyword_io.read_keywords(
                self.second_impact_layer, 'postprocessing_report')
            if self.chosen_aggregation_layer is not None:
                self.keyword_io.read_keywords(
                    self.chosen_aggregation_layer,
                    'aggregation attribute')
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
            image_report = html_renderer.html_to_image(html, 50)
            path = '%s/%s.png' % (
                str(self.output_directory.text()),
                aggregation_area)
            image_report.save(path)
            self.image_reports[aggregation_area.lower()] = path

        # If it is aggregated by aggregation layer, then generate atlas report
        if self.chosen_aggregation_layer is not None:
            # Add attribute image report path to aggregation layer
            self.add_image_path_to_aggregation_layer()

        # Generate Reports:
        self.generate_reports()

        # If it is aggregated by aggregation layer, clean some works
        if self.chosen_aggregation_layer is not None:
            # Delete attribute image report from aggregation layer
            self.delete_image_path_from_aggregation_layer()

        # Hohoho finish doing it!
        QtGui.qApp.restoreOverrideCursor()

        # Give user success information
        # noinspection PyCallByClass,PyTypeChecker, PyArgumentList
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
            html += '<caption><h4>%s</h4></caption>' % aggregation_area.upper()
            exposure_report_dict = merged_report_dict[aggregation_area]
            for exposure in exposure_report_dict:
                exposure_detail_dict = exposure_report_dict[exposure]
                html += '<tr><th>%s</th></tr>' % exposure.upper()
                for datum in exposure_detail_dict:
                    html += ('<tr>'
                             '<td>%s</td>'
                             '<td>%s</td>'
                             '</tr>') % (datum, exposure_detail_dict[datum])
            html += '</table>'
            html_report = (aggregation_area, html)
            html_reports.append(html_report)

        return html_reports

    def get_project_layers(self):
        """Obtain a list of impact layers and aggregation layer currently
        loaded in QGIS."""
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
                    self.keyword_io.read_keywords(layer,
                                                  'aggregation attribute')
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
        """
        # Setup Map Renderer and set all the layer
        renderer = QgsMapRenderer()
        layer_set = [self.first_impact_layer.id(),
                     self.second_impact_layer.id()]

        if self.chosen_aggregation_layer is not None:
            layer_set.append(self.chosen_aggregation_layer.id())

        renderer.setLayerSet(layer_set)

        # Create composition
        composition = self.load_template(renderer)

        # Get Map
        atlas_map = composition.getComposerItemById('impact-map')

        if self.chosen_aggregation_layer is None:
            table_image_report = composition.\
                getComposerItemById('report_image')

            # Self.image_reports must have only 1 key value pair
            area_title = self.image_reports.keys()[0]
            image_path = self.image_reports[area_title]
            table_image_report.setPictureFile(image_path)
            path = '%s/%s.pdf' % (
                str(self.output_directory.text()),
                area_title)
            composition.exportAsPDF(path)
        else:
            # Create atlas composition:
            atlas = QgsAtlasComposition(composition)

            # Set coverage layer
            # Map will be clipped by features from this layer:
            atlas.setCoverageLayer(self.chosen_aggregation_layer)

            # set which composer map will be used for printing atlas
            atlas.setComposerMap(atlas_map)

            # set output filename pattern
            atlas.setFilenamePattern("KAB_NAME")

            # Start rendering
            atlas.beginRender()

            # Iterate all aggregation unit in aggregation layer
            for i in range(0, atlas.numFeatures()):
                atlas.prepareForFeature(i)
                path = '%s/%s.pdf' % (
                    str(self.output_directory.text()),
                    atlas.currentFilename())
                composition.exportAsPDF(path)

            # End of rendering
            atlas.endRender()

    def load_template(self, renderer):
        """Load composer template for merged report.

        There are 2 templates. The template that is choosen based on
        aggregated or not

        :param renderer: Map renderer
        :type renderer: QgsMapRenderer
        """
        # Create Composition
        composition = QgsComposition(renderer)

        # Read template content
        if self.chosen_aggregation_layer is not None:
            template_file = QtCore.QFile(self.aggregated_template_path)
        else:
            template_file = QtCore.QFile(self.entire_area_template_path)

        template_file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
        template_content = template_file.readAll()
        template_file.close()

        # Create a dom document containing template content
        document = QtXml.QDomDocument()
        document.setContent(template_content)

        # Load template
        composition.loadFromTemplate(document)

        return composition

    def add_image_path_to_aggregation_layer(self):
        """Add an attribute containing image path to aggregation layer."""
        self.chosen_aggregation_layer.startEditing()

        provider = self.chosen_aggregation_layer.dataProvider()
        capabilities = provider.capabilities()
        # Check if the attribute is already there. Delete it first!
        index = provider.fieldNameIndex(self.temp_attribute_name)
        if index != -1:
            if capabilities & QgsVectorDataProvider.DeleteAttributes:
                result = provider.deleteAttributes([index])
                if not result:
                    raise Exception('Error deleting attribute: %s.'
                                    % self.temp_attribute_name)
        # Add Attribute
        if capabilities & QgsVectorDataProvider.AddAttributes:
            result = provider.addAttributes(
                [QgsField(self.temp_attribute_name, QVariant.String)])
            if not result:
                raise Exception('Error adding attribute:%s.'
                                % self.temp_attribute_name)

        aggregation_attribute = 'KAB_NAME'
        aggregation_attribute_index = \
            provider.fieldNameIndex(aggregation_attribute)

        # Modify the attribute of img_path
        img_path_attribute_index = self.chosen_aggregation_layer\
            .dataProvider().fieldNameIndex(self.temp_attribute_name)
        if capabilities & QgsVectorDataProvider.ChangeAttributeValues:
            features = self.chosen_aggregation_layer.getFeatures()
            for feature in features:
                feature_id = feature.id()
                aggregation_area = \
                    feature.attributes()[aggregation_attribute_index].lower()
                image_path = str(self.image_reports[aggregation_area])
                attributes = {img_path_attribute_index: image_path}
                self.chosen_aggregation_layer.\
                    dataProvider().\
                    changeAttributeValues({feature_id: attributes})
                print 'test'

        else:
            raise Exception('Attribute %s can not be modified.'
                            % self.temp_attribute_name)

        self.chosen_aggregation_layer.commitChanges()

    def delete_image_path_from_aggregation_layer(self):
        """Delete an attribute containing image path from aggregation layer."""
        self.chosen_aggregation_layer.startEditing()

        provider = self.chosen_aggregation_layer.dataProvider()
        capabilities = provider.capabilities()
        # Check if the attribute is already there. Delete it first!
        index = provider.fieldNameIndex(self.temp_attribute_name)
        if index != -1:
            if capabilities & QgsVectorDataProvider.DeleteAttributes:
                result = provider.deleteAttributes([index])
                if not result:
                    raise Exception('Error deleting attribute: %s.'
                                    % self.temp_attribute_name)
