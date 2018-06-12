# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Import Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import logging
import os
import time
from shutil import copy

# noinspection PyUnresolvedReferences
# pylint: disable=unused-import
from qgis.core import (QgsApplication, QgsCoordinateTransform, QgsExpression,
                       QgsExpressionContext, QgsField, QgsProject,
                       QgsVectorFileWriter, QgsVectorLayer)
# noinspection PyPackageRequirements
from qgis.PyQt import QtCore, QtGui, QtWidgets
# noinspection PyPackageRequirements
from qgis.PyQt.QtCore import QRegExp, QSettings, Qt, QVariant, pyqtSlot
from qgis.PyQt.QtNetwork import QNetworkReply
# noinspection PyPackageRequirements
from qgis.PyQt.QtWidgets import (QButtonGroup, QDialog, QFileDialog,
                                 QMessageBox, QProgressDialog)
from safe.common.exceptions import CanceledImportDialogError, FileMissingError
from safe.definitions.peta_bencana import development_api, production_api
from safe.gui.tools.help.peta_bencana_help import peta_bencana_help
from safe.utilities.file_downloader import FileDownloader
from safe.utilities.qgis_utilities import display_warning_message_box
from safe.utilities.qt import disable_busy_cursor
from safe.utilities.resources import (get_ui_class, html_footer, html_header,
                                      resources_path)
from safe.utilities.settings import setting

# pylint: enable=unused-import


LOGGER = logging.getLogger('InaSAFE')

FORM_CLASS = get_ui_class('peta_bencana_dialog_base.ui')

__copyright__ = "Copyright 2015, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class PetaBencanaDialog(QDialog, FORM_CLASS):

    """Downloader for PetaBencana data.

    .. versionadded: 3.3
    """

    def __init__(self, parent=None, iface=None):
        """Constructor for import dialog.

        .. versionadded: 3.3

        :param parent: Optional widget to use as parent.
        :type parent: QWidget

        :param iface: An instance of QgisInterface.
        :type iface: QgisInterface
        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        title = self.tr('PetaBencana Downloader')
        self.setWindowTitle(title)
        icon = resources_path('img', 'icons', 'add-petabencana-layer.svg')
        self.setWindowIcon(QtGui.QIcon(icon))

        self.iface = iface

        self.source = None

        self.radio_button_group = QButtonGroup()
        self.radio_button_group.addButton(self.radio_button_production)
        self.radio_button_group.addButton(self.radio_button_development)

        self.radio_button_group.setExclusive(True)
        self.radio_button_production.setChecked(True)
        self.populate_combo_box()

        developer_mode = setting('developer_mode', False, bool)
        if not developer_mode:
            self.radio_button_widget.hide()
            self.source_label.hide()
            self.output_group.adjustSize()

        # signals
        self.radio_button_production.clicked.connect(self.populate_combo_box)
        self.radio_button_development.clicked.connect(self.populate_combo_box)

        # Set up things for context help
        self.help_button = self.button_box.button(
            QtWidgets.QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)

        # set up the validator for the file name prefix
        expression = QRegExp('^[A-Za-z0-9-_]*$')
        validator = QtGui.QRegExpValidator(expression, self.filename_prefix)
        self.filename_prefix.setValidator(validator)
        self.time_stamp = None
        self.restore_state()

    @pyqtSlot(bool)  # prevents actions being handled twice
    def help_toggled(self, flag):
        """Show or hide the help tab in the stacked widget.

        .. versionadded: 3.3

        :param flag: Flag indicating whether help should be shown or hidden.
        :type flag: bool
        """
        if flag:
            self.help_button.setText(self.tr('Hide Help'))
            self.show_help()
        else:
            self.help_button.setText(self.tr('Show Help'))
            self.hide_help()

    def hide_help(self):
        """Hide the usage info from the user.

        .. versionadded:: 3.3
        """
        self.main_stacked_widget.setCurrentIndex(1)

    def show_help(self):
        """Show usage info to the user.

        .. versionadded: 3.3
        """
        # Read the header and footer html snippets
        self.main_stacked_widget.setCurrentIndex(0)
        header = html_header()
        footer = html_footer()

        string = header

        message = peta_bencana_help()
        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)

    def restore_state(self):
        """Read last state of GUI from configuration file.

        .. versionadded: 3.3
        """
        settings = QSettings()
        try:
            last_path = settings.value('directory', type=str)
        except TypeError:
            last_path = ''
        self.output_directory.setText(last_path)

    def save_state(self):
        """Store current state of GUI to configuration file.

        .. versionadded: 3.3
        """
        settings = QSettings()
        settings.setValue('directory', self.output_directory.text())

    @pyqtSlot()  # prevents actions being handled twice
    def on_directory_button_clicked(self):
        """Show a dialog to choose directory.

        .. versionadded: 3.3
        """
        # noinspection PyCallByClass,PyTypeChecker
        self.output_directory.setText(QFileDialog.getExistingDirectory(
            self, self.tr('Select download directory')))

    def accept(self):
        """Do PetaBencana download and display it in QGIS.

        .. versionadded: 3.3
        """

        self.save_state()
        try:
            self.require_directory()
        except CanceledImportDialogError:
            return

        QgsApplication.instance().setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        source = self.define_url()
        # save the file as json first
        name = 'jakarta_flood.json'
        output_directory = self.output_directory.text()
        output_prefix = self.filename_prefix.text()
        overwrite = self.overwrite_flag.isChecked()
        date_stamp_flag = self.include_date_flag.isChecked()
        output_base_file_path = self.get_output_base_path(
            output_directory,
            output_prefix,
            date_stamp_flag,
            name,
            overwrite)

        title = self.tr("Can't access API")

        try:
            self.download(source, output_base_file_path)

            # Open downloaded file as QgsMapLayer
            options = QgsVectorLayer.LayerOptions(False)
            layer = QgsVectorLayer(
                output_base_file_path, 'flood', 'ogr', options)
        except Exception as e:
            disable_busy_cursor()
            QMessageBox.critical(self, title, str(e))
            return

        self.time_stamp = time.strftime('%d-%b-%Y %H:%M:%S')
        # Now save as shp
        name = 'jakarta_flood.shp'
        output_base_file_path = self.get_output_base_path(
            output_directory,
            output_prefix,
            date_stamp_flag,
            name,
            overwrite)
        QgsVectorFileWriter.writeAsVectorFormat(
            layer,
            output_base_file_path,
            'CP1250',
            QgsCoordinateTransform(),
            'ESRI Shapefile')
        # Get rid of the GeoJSON layer and rather use local shp
        del layer

        self.copy_style(output_base_file_path)

        self.copy_keywords(output_base_file_path)
        layer = self.add_flooded_field(output_base_file_path)

        # check if the layer has feature or not
        if layer.featureCount() <= 0:
            city = self.city_combo_box.currentText()
            message = self.tr(
                'There are no floods data available on {city} '
                'at this time.').format(city=city)
            display_warning_message_box(
                self,
                self.tr('No data'),
                message)
            disable_busy_cursor()
        else:
            # add the layer to the map
            project = QgsProject.instance()
            project.addMapLayer(layer)
            disable_busy_cursor()
            self.done(QDialog.Accepted)

    def add_flooded_field(self, shapefile_path):
        """Create the layer from the local shp adding the flooded field.

        .. versionadded:: 3.3

        Use this method to add a calculated field to a shapefile. The shapefile
        should have a field called 'count' containing the number of flood
        reports for the field. The field values will be set to 0 if the count
        field is < 1, otherwise it will be set to 1.

        :param shapefile_path: Path to the shapefile that will have the flooded
            field added.
        :type shapefile_path: basestring

        :return: A vector layer with the flooded field added.
        :rtype: QgsVectorLayer
        """
        layer = QgsVectorLayer(
            shapefile_path, self.tr('Jakarta Floods'), 'ogr')
        # Add a calculated field indicating if a poly is flooded or not
        # from qgis.PyQt.QtCore import QVariant
        layer.startEditing()
        # Add field with integer from 0 to 4 which represents the flood
        # class. Its the same as 'state' field except that is being treated
        # as a string.
        # This is used for cartography
        flood_class_field = QgsField('floodclass', QVariant.Int)
        layer.addAttribute(flood_class_field)
        layer.commitChanges()
        layer.startEditing()
        flood_class_idx = layer.fields().lookupField('floodclass')
        flood_class_expression = QgsExpression('to_int(state)')
        context = QgsExpressionContext()
        context.setFields(layer.fields())
        flood_class_expression.prepare(context)

        # Add field with boolean flag to say if the area is flooded
        # This is used by the impact function
        flooded_field = QgsField('flooded', QVariant.Int)
        layer.dataProvider().addAttributes([flooded_field])
        layer.commitChanges()
        layer.startEditing()
        flooded_idx = layer.fields().lookupField('flooded')
        flood_flag_expression = QgsExpression('state > 0')
        flood_flag_expression.prepare(context)
        for feature in layer.getFeatures():
            context.setFeature(feature)
            feature[flood_class_idx] = flood_class_expression.evaluate(context)
            feature[flooded_idx] = flood_flag_expression.evaluate(context)
            layer.updateFeature(feature)
        layer.commitChanges()
        return layer

    def copy_keywords(self, shapefile_path):
        """Copy keywords from the OSM resource directory to the output path.

        .. versionadded: 3.3

        In addition to copying the template, tokens within the template will
        be replaced with new values for the date token and title token.

        :param shapefile_path: Path to the shapefile that will have the flooded
            field added.
        :type shapefile_path: basestring
        """
        source_xml_path = resources_path('petabencana', 'flood-keywords.xml')
        output_xml_path = shapefile_path.replace('shp', 'xml')
        LOGGER.info('Copying xml to: %s' % output_xml_path)

        title_token = '[TITLE]'
        new_title = self.tr('Jakarta Floods - %s' % self.time_stamp)

        date_token = '[DATE]'
        new_date = self.time_stamp
        with open(source_xml_path) as source_file, \
                open(output_xml_path, 'w') as output_file:
            for line in source_file:
                line = line.replace(date_token, new_date)
                line = line.replace(title_token, new_title)
                output_file.write(line)

    @staticmethod
    def copy_style(shapefile_path):
        """Copy style from the OSM resource directory to the output path.

        .. versionadded: 3.3

        :param shapefile_path: Path to the shapefile that should get the path
            added.
        :type shapefile_path: basestring
        """
        source_qml_path = resources_path('petabencana', 'flood-style.qml')
        output_qml_path = shapefile_path.replace('shp', 'qml')
        LOGGER.info('Copying qml to: %s' % output_qml_path)
        copy(source_qml_path, output_qml_path)

    def get_output_base_path(
            self,
            output_directory,
            output_prefix,
            with_date_stamp,
            feature_type,
            overwrite):
        """Get a full base name path to save the shapefile.

        TODO: This is cut & paste from OSM - refactor to have one method

        :param output_directory: The directory where to put results.
        :type output_directory: str

        :param output_prefix: The prefix to add for the shapefile.
        :type output_prefix: str

        :param with_date_stamp: Whether to add a datestamp in between the
            file prefix and the feature_type for the shapefile name.
        :type output_prefix: str

        :param feature_type: What kind of data will be downloaded. Will be
            used for the shapefile name.
        :type feature_type: str

        :param overwrite: Boolean to know if we can overwrite existing files.
        :type overwrite: bool

        :return: The base path.
        :rtype: str
        """
        if with_date_stamp and self.time_stamp is not None:
            time_stamp = self.time_stamp.replace(' ', '-')
            time_stamp = time_stamp.replace(':', '-')
            time_stamp += '-'
            feature_type = time_stamp + feature_type

        path = os.path.join(
            output_directory, '%s%s' % (output_prefix, feature_type))

        if overwrite:

            # If a shapefile exists, we must remove it (only the .shp)
            shp = '%s.shp' % path
            if os.path.isfile(shp):
                os.remove(shp)

        else:
            separator = '-'
            suffix = self.get_unique_file_path_suffix(
                '%s.shp' % path, separator)

            if suffix:
                path = os.path.join(output_directory, '%s%s%s%s' % (
                    output_prefix, feature_type, separator, suffix))

        return path

    @staticmethod
    def get_unique_file_path_suffix(file_path, separator='-', i=0):
        """Return the minimum number to suffix the file to not overwrite one.
        Example : /tmp/a.txt exists.
            - With file_path='/tmp/b.txt' will return 0.
            - With file_path='/tmp/a.txt' will return 1 (/tmp/a-1.txt)

        TODO: This is cut & paste from OSM - refactor to have one method

        :param file_path: The file to check.
        :type file_path: str

        :param separator: The separator to add before the prefix.
        :type separator: str

        :param i: The minimum prefix to check.
        :type i: int

        :return: The minimum prefix you should add to not overwrite a file.
        :rtype: int
        """
        basename = os.path.splitext(file_path)
        if i != 0:
            file_path_test = os.path.join(
                '%s%s%s%s' % (basename[0], separator, i, basename[1]))
        else:
            file_path_test = file_path

        if os.path.isfile(file_path_test):
            return PetaBencanaDialog.get_unique_file_path_suffix(
                file_path, separator, i + 1)
        else:
            return i

    def require_directory(self):
        """Ensure directory path entered in dialog exist.

        When the path does not exist, this function will ask the user if he
        want to create it or not.

        TODO: This is cut & paste from OSM - refactor to have one method

        :raises: CanceledImportDialogError - when user choose 'No' in
            the question dialog for creating directory.
        """
        path = self.output_directory.text()

        if os.path.exists(path):
            return

        title = self.tr('Directory %s not exist') % path
        question = self.tr(
            'Directory %s not exist. Do you want to create it?') % path
        # noinspection PyCallByClass,PyTypeChecker
        answer = QMessageBox.question(
            self, title, question, QMessageBox.Yes | QMessageBox.No)

        if answer == QMessageBox.Yes:
            if len(path) != 0:
                os.makedirs(path)
            else:
                # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                display_warning_message_box(
                    self,
                    self.tr('InaSAFE error'),
                    self.tr('Output directory can not be empty.'))
                raise CanceledImportDialogError()
        else:
            raise CanceledImportDialogError()

    def load_shapefile(self, feature_type, base_path):
        """Load downloaded shape file to QGIS Main Window.

        TODO: This is cut & paste from OSM - refactor to have one method

        :param feature_type: What kind of features should be downloaded.
            Currently 'buildings', 'building-points' or 'roads' are supported.
        :type feature_type: str

        :param base_path: The base path of the shape file (without extension).
        :type base_path: str

        :raises: FileMissingError - when buildings.shp not exist
        """

        path = '%s.shp' % base_path

        if not os.path.exists(path):
            message = self.tr(
                '%s does not exist. The server does not have any data for '
                'this extent.' % path)
            raise FileMissingError(message)

        self.iface.addVectorLayer(path, feature_type, 'ogr')

    def reject(self):
        """Redefinition of the method.

        It will call the super method.
        """
        super(PetaBencanaDialog, self).reject()

    def download(self, url, output_path):
        """Download file from API url and write to output path.

        :param url: URL of the API.
        :type url: str

        :param output_path: Path of output file,
        :type output_path: str
        """
        request_failed_message = self.tr(
            "Can't access PetaBencana API: {source}").format(
            source=url)
        downloader = FileDownloader(url, output_path)
        result, message = downloader.download()
        if not result:
            display_warning_message_box(
                self,
                self.tr('Download error'),
                self.tr(request_failed_message + '\n' + message))

        if result == QNetworkReply.OperationCanceledError:
            display_warning_message_box(
                self,
                self.tr('Download error'),
                self.tr(message))

    # The function below might be usefull for future usage.

    # def get_available_area(self):
    #     """Function to automatically get the available area on API.
    #        *still cannot get string data from QByteArray*
    #     """
    #     available_area = []
    #     network_manager = QgsNetworkAccessManager.instance()
    #     api_url = QUrl('https://data.petabencana.id/cities')
    #     api_request = QNetworkRequest(api_url)
    #     api_response = network_manager.get(api_request)
    #     data = api_response.readAll()
    #     json_response = QScriptEngine().evaluate(data)
    #     geometries = json_response.property('output').property('geometries')
    #     iterator = QScriptValueIterator(geometries)
    #     while iterator.hasNext():
    #         iterator.next()
    #         geometry = iterator.value()
    #         geometry_code = (
    #             geometry.property('properties').property('code').toString())
    #         available_area.append(geometry_code)

    def populate_combo_box(self):
        """Populate combobox for selecting city."""
        if self.radio_button_production.isChecked():
            self.source = production_api['url']
            available_data = production_api['available_data']

        else:
            self.source = development_api['url']
            available_data = development_api['available_data']

        self.city_combo_box.clear()
        for index, data in enumerate(available_data):
            self.city_combo_box.addItem(data['name'])
            self.city_combo_box.setItemData(
                index, data['code'], Qt.UserRole)

    def define_url(self):
        """Define API url based on which source is selected.

        :return: Valid url of selected source.
        :rtype: str
        """
        current_index = self.city_combo_box.currentIndex()
        city_code = self.city_combo_box.itemData(current_index, Qt.UserRole)
        source = (self.source).format(city_code=city_code)
        return source
