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
import os
import logging
from shutil import copy
from PyQt4 import QtCore
from PyQt4.QtCore import QVariant
# noinspection PyUnresolvedReferences
# pylint: disable=unused-import
from qgis.core import (
    QGis, # force sip2 api
    QgsRectangle,
    QgsMapLayerRegistry,
    QgsProject,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsField,
    QgsExpression,
    QgsFeature)
# pylint: enable=unused-import

# noinspection PyPackageRequirements
from PyQt4 import QtGui
# noinspection PyPackageRequirements
from PyQt4.QtCore import QSettings, pyqtSignature, QRegExp, pyqtSlot
# noinspection PyPackageRequirements
from PyQt4.QtGui import (
    QDialog, QProgressDialog, QMessageBox, QFileDialog, QRegExpValidator)

from safe.common.exceptions import (
    CanceledImportDialogError,
    FileMissingError)
from safe.utilities.resources import (
    html_footer, html_header, get_ui_class, resources_path)
from safe.utilities.qgis_utilities import (
    display_warning_message_box,
    display_warning_message_bar)
from safe.gui.tools.help.peta_jakarta_help import peta_jakarta_help


LOGGER = logging.getLogger('InaSAFE')

FORM_CLASS = get_ui_class('peta_jakarta_dialog_base.ui')

__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '23/11/2015'
__copyright__ = ('Copyright 2015, Australia Indonesia Facility for '
                 'Disaster Reduction')


class PetaJakartaDialog(QDialog, FORM_CLASS):
    """Downloader for petajakarta data.

    .. versionadded: 3.3
    """

    def __init__(self, parent=None, iface=None):
        """Constructor for import dialog.

        .. versionadded: 3.3

        :param parent: Optional widget to use as parent
        :type parent: QWidget

        :param iface: An instance of QGisInterface
        :type iface: QGisInterface
        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        self.setWindowTitle(self.tr('PetaJakarta Downloader'))

        self.iface = iface

        # creating progress dialog for download
        self.progress_dialog = QProgressDialog(self)
        self.progress_dialog.setAutoClose(False)
        title = self.tr('PetaJakarta Downloader')
        self.progress_dialog.setWindowTitle(title)

        # Set up things for context help
        self.help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)

        # set up the validator for the file name prefix
        expression = QRegExp('^[A-Za-z0-9-_]*$')
        validator = QRegExpValidator(expression, self.filename_prefix)
        self.filename_prefix.setValidator(validator)

        self.restore_state()

    @pyqtSlot()
    @pyqtSignature('bool')  # prevents actions being handled twice
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

        message = peta_jakarta_help()
        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)

    def restore_state(self):
        """ Read last state of GUI from configuration file.

        .. versionadded: 3.3
        """
        settings = QSettings()
        try:
            last_path = settings.value('directory', type=str)
        except TypeError:
            last_path = ''
        self.output_directory.setText(last_path)

    def save_state(self):
        """ Store current state of GUI to configuration file.

        .. versionadded: 3.3
        """
        settings = QSettings()
        settings.setValue('directory', self.output_directory.text())

    @pyqtSignature('')  # prevents actions being handled twice
    def on_directory_button_clicked(self):
        """Show a dialog to choose directory.

        .. versionadded: 3.3
        """
        # noinspection PyCallByClass,PyTypeChecker
        self.output_directory.setText(QFileDialog.getExistingDirectory(
            self, self.tr('Select download directory')))

    def accept(self):
        """Do petajakarta download and display it in QGIS.

        .. versionadded: 3.3
        """

        self.save_state()
        self.require_directory()
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

        if self.three_hours.isChecked():
            interval = 3
        elif self.one_hour.isChecked():
            interval = 1
        else:
            interval = 6

        if self.sub_districts.isChecked():
            area = 'subdistrict'
        elif self.villages.isChecked():
            area = 'village'
        else:
            area = 'rw'

        registry = QgsMapLayerRegistry.instance()
        source = (
            'https://petajakarta.org/banjir/data/api/v1/aggregates/live?'
            'level=%s&hours=%i&format=geojson') % (area, interval)
        layer = QgsVectorLayer(source, 'flood', 'ogr', False)
        # Now save as shp
        name = 'jakarta_flood.shp'
        output_directory = self.output_directory.text()
        output_prefix = self.filename_prefix.text()
        overwrite = self.overwrite_flag.isChecked()
        output_base_file_path = self.get_output_base_path(
            output_directory, output_prefix, name, overwrite)
        QgsVectorFileWriter.writeAsVectorFormat(
            layer, output_base_file_path, 'CP1250', None, 'ESRI Shapefile')
        # Get rid of the GeoJSON layer and rather use local shp
        del layer

        # copy style
        source_qml_path = resources_path('petajakarta', 'flood-style.qml')
        output_qml_path = output_base_file_path.replace('shp', 'qml')
        LOGGER.info('Copying qml to: %s' % output_qml_path)
        copy(source_qml_path, output_qml_path)

        # copy keywords
        source_xml_path = resources_path('petajakarta', 'flood-keywords.xml')
        output_xml_path = output_base_file_path.replace('shp', 'xml')
        LOGGER.info('Copying xml to: %s' % output_xml_path)
        copy(source_xml_path, output_xml_path)

        # create the layer from the local shp
        layer = QgsVectorLayer(
            output_base_file_path, self.tr('Jakarta Floods'), 'ogr')
        # Add a calculated field indicating if a poly is flooded or not
        # from PyQt4.QtCore import QVariant
        layer.startEditing()
        field = QgsField('flooded', QVariant.Int)
        layer.dataProvider().addAttributes([field])
        layer.commitChanges()
        idx = layer.fieldNameIndex('flooded')
        expression = QgsExpression('if("count" > 0, 1, 0 )')
        expression.prepare(layer.pendingFields())

        for feature in layer.getFeatures():
            feature[idx] = expression.evaluate(feature)
            layer.updateFeature(feature)

        layer.commitChanges()
        # add the layer to the map
        registry.addMapLayer(layer)
        self.disable_busy_cursor()
        self.done(QDialog.Accepted)

    @staticmethod
    def disable_busy_cursor():
        """Disable the hourglass cursor.

        TODO: this is duplicated from dock.py
        """
        while QtGui.qApp.overrideCursor() is not None and \
                QtGui.qApp.overrideCursor().shape() == QtCore.Qt.WaitCursor:
            QtGui.qApp.restoreOverrideCursor()

    def get_output_base_path(
            self,
            output_directory,
            output_prefix,
            feature_type,
            overwrite):
        """Get a full base name path to save the shapefile.

        TODO: This is cut & paste from OSM - refactor to have one method

        :param output_directory: The directory where to put results.
        :type output_directory: str

        :param output_prefix: The prefix to add for the shapefile.
        :type output_prefix: str

        :param feature_type: What kind of flooded should be downloaded.
        :type feature_type: str

        :param overwrite: Boolean to know if we can overwrite existing files.
        :type overwrite: bool

        :return: The base path.
        :rtype: str
        """
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
            return PetaJakartaDialog.get_unique_file_path_suffix(
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

        canvas_srid = self.canvas.mapRenderer().destinationCrs().srsid()
        on_the_fly_projection = self.canvas.hasCrsTransformEnabled()
        if canvas_srid != 4326 and not on_the_fly_projection:
            if QGis.QGIS_VERSION_INT >= 20400:
                self.canvas.setCrsTransformEnabled(True)
            else:
                display_warning_message_bar(
                    self.iface,
                    self.tr('Enable \'on the fly\''),
                    self.tr(
                        'Your current projection is different than EPSG:4326. '
                        'You should enable \'on the fly\' to display '
                        'correctly your layers')
                    )

    def reject(self):
        """Redefinition of the reject() method.

        It will call the super method.
        """
        # add our own logic here...

        super(PetaJakartaDialog, self).reject()
