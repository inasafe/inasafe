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
__author__ = 'oscar mbita (mgwetam@gmail.com)'
__date__ = '8/2/2016'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import json
import os
import logging

# noinspection PyUnresolvedReferences
# pylint: disable=unused-import
from qgis.core import QGis, QgsRectangle, QgsVectorLayer  # force sip2 api
from qgis.gui import QgsMapToolPan

from PyQt4 import QtGui
# noinspection PyPackageRequirements
from PyQt4.QtCore import QSettings, pyqtSignature, QRegExp, pyqtSlot
# noinspection PyPackageRequirements
from PyQt4.QtGui import (
    QDialog, QProgressDialog, QMessageBox, QFileDialog, QRegExpValidator)

from safe.common.exceptions import (
    CanceledImportDialogError,
    FileMissingError)
from safe.utilities.population_downloader import download
from safe.utilities.gis import (
    viewport_geo_array,
    rectangle_geo_array,
    validate_geo_array)
from safe.utilities.resources import (
    html_footer, html_header, get_ui_class)

from safe.utilities.qgis_utilities import (
    display_warning_message_box)

from safe.gui.tools.rectangle_map_tool import RectangleMapTool
from safe.gui.tools.help.population_downloader_help import \
    population_downloader_help

LOGGER = logging.getLogger('InaSAFE')

FORM_CLASS = get_ui_class('population_downloader_dialog_base.ui')


class PopulationDownloaderDialog(QDialog, FORM_CLASS):
    """Downloader for World Population data."""

    def __init__(self, parent=None, iface=None):
        """Constructor for import dialog.
        :param parent: Optional widget to use as parent
        :type parent: QWidget
        :param iface: An instance of QGisInterface
        :type iface: QGisInterface
        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        self.setWindowTitle(self.tr('InaSAFE World Population Downloader'))

        self.iface = iface

        self.help_context = 'population_downloader'
        # creating progress dialog for download
        self.progress_dialog = QProgressDialog(self)
        self.progress_dialog.setAutoClose(False)
        title = self.tr('InaSAFE World Population Downloader')
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

        # Setup the rectangle map tool
        self.canvas = iface.mapCanvas()
        self.rectangle_map_tool = \
            RectangleMapTool(self.canvas)
        self.rectangle_map_tool.rectangle_created.connect(
            self.update_extent_from_rectangle)
        self.capture_button.clicked.connect(
            self.drag_rectangle_on_map_canvas)

        # Setup pan tool
        self.pan_tool = QgsMapToolPan(self.canvas)
        self.canvas.setMapTool(self.pan_tool)

    @pyqtSlot()
    @pyqtSignature('bool')  # prevents actions being handled twice
    def help_toggled(self, flag):
        """Show or hide the help tab in the stacked widget.
        .. versionadded: 3.2
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
        .. versionadded:: 3.2
        """
        self.main_stacked_widget.setCurrentIndex(1)

    def show_help(self):
        """Show usage info to the user."""
        # Read the header and footer html snippets
        self.main_stacked_widget.setCurrentIndex(0)
        header = html_header()
        footer = html_footer()

        string = header

        message = population_downloader_help()
        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)

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

    def update_extent(self, extent):
        """Update extent value in GUI based from an extent.
        :param extent: A list in the form [xmin, ymin, xmax, ymax] where all
            coordinates provided are in Geographic / EPSG:4326.
        :type extent: list
        """
        self.x_minimum.setValue(extent[0])
        self.y_minimum.setValue(extent[1])
        self.x_maximum.setValue(extent[2])
        self.y_maximum.setValue(extent[3])

    def update_extent_from_map_canvas(self):
        """Update extent value in GUI based from value in map.
        .. note:: Delegates to update_extent()
        """

        self.bounding_box_group.setTitle(
            self.tr('Bounding box from the map canvas'))
        # Get the extent as [xmin, ymin, xmax, ymax]
        extent = viewport_geo_array(self.iface.mapCanvas())
        self.update_extent(extent)

    def update_extent_from_rectangle(self):
        """Update extent value in GUI based from the QgsMapTool rectangle.
        .. note:: Delegates to update_extent()
        """

        self.show()
        self.canvas.unsetMapTool(self.rectangle_map_tool)
        self.canvas.setMapTool(self.pan_tool)

        rectangle = self.rectangle_map_tool.rectangle()
        if rectangle:
            self.bounding_box_group.setTitle(
                self.tr('Bounding box from rectangle'))
            extent = rectangle_geo_array(rectangle, self.iface.mapCanvas())
            self.update_extent(extent)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_directory_button_clicked(self):
        """Show a dialog to choose directory."""
        # noinspection PyCallByClass,PyTypeChecker
        self.output_directory.setText(QFileDialog.getExistingDirectory(
            self, self.tr('Select download directory')))

    def drag_rectangle_on_map_canvas(self):
        """Hide the dialog and allow the user to draw a rectangle."""

        self.hide()
        self.rectangle_map_tool.reset()
        self.canvas.unsetMapTool(self.pan_tool)
        self.canvas.setMapTool(self.rectangle_map_tool)

    def accept(self):
        """Do population download and display it in QGIS."""
        error_dialog_title = self.tr('InaSAFE worldpop Downloader Error')

        # Lock the bounding_box_group
        self.bounding_box_group.setDisabled(True)

        # Get the extent
        y_minimum = self.y_minimum.value()
        y_maximum = self.y_maximum.value()
        x_minimum = self.x_minimum.value()
        x_maximum = self.x_maximum.value()
        extent = [x_minimum, y_minimum, x_maximum, y_maximum]

        # Validate extent
        valid_flag = validate_geo_array(extent)
        if not valid_flag:
            message = self.tr(
                'The bounding box is not valid. Please make sure it is '
                'valid or check your projection!')
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            display_warning_message_box(self, error_dialog_title, message)
            # Unlock the bounding_box_group
            self.bounding_box_group.setEnabled(True)
            return

        try:
            self.save_state()
            self.require_directory()
            rectangle = self.rectangle_map_tool.rectangle()

            output_directory = self.output_directory.text()
            output_prefix = self.filename_prefix.text()
            overwrite = self.overwrite_flag.isChecked()
            output_base_file_path = self.get_output_base_path(
                output_directory, output_prefix, overwrite)

            download(
                output_base_file_path,
                extent,
                rectangle,
                self.progress_dialog)

            try:
                self.load_file(output_prefix, output_base_file_path)
            except FileMissingError as exception:
                display_warning_message_box(
                    self,
                    error_dialog_title,
                    exception.message)
            self.done(QDialog.Accepted)
            self.rectangle_map_tool.reset()

        except CanceledImportDialogError:
            # don't show anything because this exception raised
            # when user canceling the import process directly
            pass
        except Exception as exception:  # pylint: disable=broad-except
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            display_warning_message_box(
                self, error_dialog_title, exception.message)

            self.progress_dialog.cancel()

        finally:
            # Unlock the bounding_box_group
            self.bounding_box_group.setEnabled(True)

    def get_output_base_path(
            self,
            output_directory,
            output_prefix,
            overwrite):
        """Get a full base name path to save the geojson.
        :param output_directory: The directory where to put results.
        :type output_directory: str

        :param output_prefix: The prefix to add for the file.
        :type output_prefix: str

        :param overwrite: Boolean to know if we can overwrite existing files.
        :type overwrite: bool

        :return: The base path.
        :rtype: str
        """
        path = os.path.join(
            output_directory, '%s' % output_prefix)

        if overwrite:

            # If a file exists, we must remove it (only the .geojson)
            geojson = '%s.geojson' % path
            if os.path.isfile(json):
                os.remove(geojson)

        else:
            separator = '-'
            suffix = self.get_unique_file_path_suffix(
                '%s.geojson' % path, separator)

            if suffix:
                path = os.path.join(output_directory, '%s%s%s%s' % (
                    output_prefix, separator, suffix))

        return path

    @staticmethod
    def get_unique_file_path_suffix(file_path, separator='-', i=0):
        """Return the minimum number to suffix the file to not overwrite one.
        Example : /tmp/a.txt exists.
            - With file_path='/tmp/b.txt' will return 0.
            - With file_path='/tmp/a.txt' will return 1 (/tmp/a-1.txt)
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
            return PopulationDownloaderDialog.get_unique_file_path_suffix(
                file_path, separator, i + 1)
        else:
            return i

    def require_directory(self):
        """Ensure directory path entered in dialog exist.
        When the path does not exist, this function will ask the user if he
        want to create it or not.
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

    def load_file(self, base_name, base_path):
        """Load downloaded file to QGIS Main Window.

        :param base_path: The base path of the shape file (without extension).
        :type base_path: str

        :raises: FileMissingError - when geojson file does not exist
        """

        path = '%s.geojson' % base_path

    def reject(self):
        """Redefinition of the reject() method
        to remove the rectangle selection tool.
        It will call the super method.
        """

        self.canvas.unsetMapTool(self.rectangle_map_tool)
        self.rectangle_map_tool.reset()

        super(PopulationDownloaderDialog, self).reject()
