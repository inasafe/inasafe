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



import json
import logging
import os

from qgis.PyQt import QtGui
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtWidgets import QDialog, QProgressDialog, QMessageBox, QFileDialog
from qgis.core import QgsRectangle, QgsExpressionContextUtils
from qgis.gui import QgsMapToolPan

from safe.common.exceptions import (
    CanceledImportDialogError,
    FileMissingError)
from safe.common.utilities import temp_dir
from safe.definitions.osm_downloader import STAGING_SERVER, PRODUCTION_SERVER
from safe.gui.tools.help.osm_downloader_help import osm_downloader_help
from safe.gui.tools.rectangle_map_tool import RectangleMapTool
from safe.utilities.gis import (
    viewport_geo_array,
    rectangle_geo_array,
    validate_geo_array)
from safe.utilities.osm_downloader import download
from safe.utilities.qgis_utilities import (
    display_warning_message_box,
)
from safe.utilities.resources import (
    html_footer, html_header, get_ui_class, resources_path)
from safe.utilities.settings import setting, set_setting

__copyright__ = "Copyright 2012, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')

FORM_CLASS = get_ui_class('osm_downloader_dialog_base.ui')


class OsmDownloaderDialog(QDialog, FORM_CLASS):
    """Downloader for OSM data."""

    def __init__(self, parent=None, iface=None):
        """Constructor for import dialog.

        :param parent: Optional widget to use as parent.
        :type parent: QWidget

        :param iface: An instance of QGisInterface.
        :type iface: QGisInterface
        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        icon = resources_path('img', 'icons', 'show-osm-download.svg')
        self.setWindowIcon(QtGui.QIcon(icon))
        title = self.tr('InaSAFE OpenStreetMap Downloader')
        self.setWindowTitle(title)

        self.iface = iface

        # creating progress dialog for download
        self.progress_dialog = QProgressDialog(self)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setWindowTitle(title)

        # Set up things for context help
        self.help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)

        # Output directory
        self.directory_button.clicked.connect(self.directory_button_clicked)
        self.output_directory.setPlaceholderText(
            self.tr('[Create a temporary layer]'))

        # Disable boundaries group box until boundary checkbox is ticked
        self.boundary_group.setEnabled(False)

        # set up the validator for the file name prefix
        expression = QRegExp('^[A-Za-z0-9-_]*$')
        validator = QRegExpValidator(expression, self.filename_prefix)
        self.filename_prefix.setValidator(validator)

        # Advanced panel
        self.line_edit_custom.setPlaceholderText(STAGING_SERVER)
        developer_mode = setting('developer_mode', expected_type=bool)
        self.group_box_advanced.setVisible(developer_mode)

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

        # Setup helper for admin_level
        json_file_path = resources_path('osm', 'admin_level_per_country.json')
        if os.path.isfile(json_file_path):
            self.countries = json.load(open(json_file_path))
            self.bbox_countries = None
            self.populate_countries()
            # connect
            self.country_comboBox.currentIndexChanged.connect(
                self.update_helper_political_level)
            self.admin_level_comboBox.currentIndexChanged.connect(
                self.update_helper_political_level)

        self.update_extent_from_map_canvas()

    def update_helper_political_level(self):
        """To update the helper about the country and the admin_level."""
        current_country = self.country_comboBox.currentText()
        index = self.admin_level_comboBox.currentIndex()
        current_level = self.admin_level_comboBox.itemData(index)
        content = None
        try:
            content = \
                self.countries[current_country]['levels'][str(current_level)]
            if content == 'N/A' or content == 'fixme' or content == '':
                raise KeyError
        except KeyError:
            content = self.tr('undefined')
        finally:
            text = self.tr('which represents %s in') % content
            self.boundary_helper.setText(text)

    def populate_countries(self):
        """Populate the combobox about countries and levels."""
        for i in range(1, 12):
            self.admin_level_comboBox.addItem(self.tr('Level %s') % i, i)

        # Set current index to admin_level 8, the most common one
        self.admin_level_comboBox.setCurrentIndex(7)

        list_countries = [
            self.tr(country) for country in list(self.countries.keys())]
        list_countries.sort()
        for country in list_countries:
            self.country_comboBox.addItem(country)

        self.bbox_countries = {}
        for country in list_countries:
            multipolygons = self.countries[country]['bbox']
            self.bbox_countries[country] = []
            for coords in multipolygons:
                bbox = QgsRectangle(coords[0], coords[3], coords[2], coords[1])
                self.bbox_countries[country].append(bbox)

        self.update_helper_political_level()

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

        message = osm_downloader_help()
        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)

    def restore_state(self):
        """Read last state of GUI from configuration file."""
        last_path = setting('directory', '', expected_type=str)
        self.output_directory.setText(last_path)

    def save_state(self):
        """Store current state of GUI to configuration file."""
        set_setting('directory', self.output_directory.text())

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

        # Updating the country if possible.
        rectangle = QgsRectangle(extent[0], extent[1], extent[2], extent[3])
        center = rectangle.center()

        for country in self.bbox_countries:
            for polygon in self.bbox_countries[country]:
                if polygon.contains(center):
                    index = self.country_comboBox.findText(country)
                    self.country_comboBox.setCurrentIndex(index)
                    break
            else:
                # Continue if the inner loop wasn't broken.
                continue
            # Inner loop was broken, break the outer.
            break
        else:
            self.country_comboBox.setCurrentIndex(0)

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

    def directory_button_clicked(self):
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

    def get_checked_features(self):
        """Create a tab with all checked features.

        :return A list with all features which are checked in the UI.
        :rtype list
        """
        feature_types = []
        if self.roads_flag.isChecked():
            feature_types.append('roads')
        if self.buildings_flag.isChecked():
            feature_types.append('buildings')
        if self.building_points_flag.isChecked():
            feature_types.append('building-points')
        if self.flood_prone_flag.isChecked():
            feature_types.append('flood-prone')
        if self.evacuation_centers_flag.isChecked():
            feature_types.append('evacuation-centers')
        if self.boundary_flag.isChecked():
            level = self.admin_level_comboBox.currentIndex() + 1
            feature_types.append('boundary-%s' % level)
        return feature_types

    def accept(self):
        """Do osm download and display it in QGIS."""
        error_dialog_title = self.tr('InaSAFE OpenStreetMap Downloader Error')

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

        # Validate features
        feature_types = self.get_checked_features()
        if len(feature_types) < 1:
            message = self.tr(
                'No feature selected. '
                'Please make sure you have checked one feature.')
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            display_warning_message_box(self, error_dialog_title, message)
            # Unlock the bounding_box_group
            self.bounding_box_group.setEnabled(True)
            return

        if self.radio_custom.isChecked():
            server_url = self.line_edit_custom.text()
            if not server_url:
                # It's the place holder.
                server_url = STAGING_SERVER
        else:
            server_url = PRODUCTION_SERVER

        try:
            self.save_state()
            self.require_directory()
            for feature_type in feature_types:

                output_directory = self.output_directory.text()
                if output_directory == '':
                    output_directory = temp_dir(sub_dir='work')
                output_prefix = self.filename_prefix.text()
                overwrite = self.overwrite_flag.isChecked()
                output_base_file_path = self.get_output_base_path(
                    output_directory, output_prefix, feature_type, overwrite)

                # noinspection PyTypeChecker
                download(
                    feature_type,
                    output_base_file_path,
                    extent,
                    self.progress_dialog,
                    server_url
                )

                try:
                    self.load_shapefile(feature_type, output_base_file_path)
                except FileMissingError as exception:
                    display_warning_message_box(
                        self,
                        error_dialog_title,
                        unicode(exception))
            self.done(QDialog.Accepted)
            self.rectangle_map_tool.reset()

        except CanceledImportDialogError:
            # don't show anything because this exception raised
            # when user canceling the import process directly
            pass
        except Exception as exception:  # pylint: disable=broad-except
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            display_warning_message_box(
                self, error_dialog_title, unicode(exception))

            self.progress_dialog.cancel()

        finally:
            # Unlock the bounding_box_group
            self.bounding_box_group.setEnabled(True)

    def get_output_base_path(
            self,
            output_directory,
            output_prefix,
            feature_type,
            overwrite):
        """Get a full base name path to save the shapefile.

        :param output_directory: The directory where to put results.
        :type output_directory: str

        :param output_prefix: The prefix to add for the shapefile.
        :type output_prefix: str

        :param feature_type: What kind of features should be downloaded.
            Currently 'buildings', 'building-points' or 'roads' are supported.
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
            return OsmDownloaderDialog.get_unique_file_path_suffix(
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

        if path == '':
            # If let empty, we create an temporary directory
            return

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

        layer = self.iface.addVectorLayer(path, feature_type, 'ogr')

        # Check if it's a building layer about the 2.5D
        if feature_type == 'buildings':
            layer_scope = QgsExpressionContextUtils.layerScope(layer)
            if not layer_scope.variable('qgis_25d_height'):
                QgsExpressionContextUtils.setLayerVariable(
                    layer, 'qgis_25d_height', 0.0002)
            if not layer_scope.variable('qgis_25d_angle'):
                QgsExpressionContextUtils.setLayerVariable(
                    layer, 'qgis_25d_angle', 70)

        canvas_srid = self.canvas.mapSettings().destinationCrs().srsid()
        on_the_fly_projection = self.canvas.hasCrsTransformEnabled()
        if canvas_srid != 4326 and not on_the_fly_projection:
            self.canvas.setCrsTransformEnabled(True)

    def reject(self):
        """Redefinition of the method to remove the rectangle selection tool.

        It will call the super method.
        """
        self.canvas.unsetMapTool(self.rectangle_map_tool)
        self.rectangle_map_tool.reset()

        super(OsmDownloaderDialog, self).reject()
