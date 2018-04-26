# coding=utf-8
"""Extent selector dialog."""

import logging
import sqlite3

# noinspection PyPackageRequirements
from qgis.PyQt import QtGui, QtWidgets
# noinspection PyPackageRequirements
from qgis.PyQt.QtCore import pyqtSignal, pyqtSlot
# noinspection PyPackageRequirements
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtGui import QIcon
# noinspection PyUnresolvedReferences
# pylint: disable=unused-import
# force sip2 api
from qgis.core import Qgis  # NOQA
from qgis.core import (
    QgsPointXY,
    QgsRectangle,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsApplication,
    QgsCoordinateTransform,
    QgsProject,
    QgsCsException)

from safe.definitions.constants import (
    EXPOSURE,
    HAZARD_EXPOSURE,
    HAZARD_EXPOSURE_VIEW,
    HAZARD_EXPOSURE_BOOKMARK,
    HAZARD_EXPOSURE_BOUNDINGBOX)
from safe.gui.tools.help.extent_selector_help import extent_selector_help
from safe.gui.tools.rectangle_map_tool import RectangleMapTool
from safe.messaging import styles
from safe.utilities.gis import wkt_to_rectangle
from safe.utilities.resources import (
    html_header, html_footer, get_ui_class, resources_path)
from safe.utilities.settings import setting, set_setting

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
LOGGER = logging.getLogger('InaSAFE')
FORM_CLASS = get_ui_class('extent_selector_dialog_base.ui')


class ExtentSelectorDialog(QDialog, FORM_CLASS):

    """Dialog for letting user determine analysis extents."""

    extent_defined = pyqtSignal(QgsRectangle, QgsCoordinateReferenceSystem)
    clear_extent = pyqtSignal()
    extent_selector_closed = pyqtSignal()

    def __init__(self, iface, parent=None, extent=None, crs=None):
        """Constructor for the dialog.

        :param iface: A Quantum GIS QgisAppInterface instance.
        :type iface: QgisAppInterface

        :param parent: Parent widget of this dialog.
        :type parent: QWidget

        :param extent: Extent of the user's preferred analysis area.
        :type extent: QgsRectangle

        :param crs: CRS for user defined analysis extent.
        :type crs: QgsCoordinateReferenceSystem
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        icon = resources_path('img', 'icons', 'set-extents-tool.svg')
        self.setWindowIcon(QIcon(icon))

        self.iface = iface
        self.parent = parent
        self.canvas = iface.mapCanvas()
        self.previous_map_tool = None
        # Prepare the map tool
        self.tool = RectangleMapTool(self.canvas)
        self.previous_map_tool = self.canvas.mapTool()

        if extent is None:
            # Use the current map canvas extents as a starting point
            self.tool.set_rectangle(self.canvas.extent())
        else:

            if isinstance(extent, QgsGeometry):
                # In InaSAFE V4, the extent is a QgsGeometry.
                # This like a hack to transform a geometry to a rectangle.
                extent = wkt_to_rectangle(extent.asWkt())

            # Ensure supplied extent is in current canvas crs
            transform = QgsCoordinateTransform(
                crs, self.canvas.mapSettings().destinationCrs(), QgsProject.instance())
            transformed_extent = transform.transformBoundingBox(extent)
            self.tool.set_rectangle(transformed_extent)

        self._populate_coordinates()

        # Observe inputs for changes
        self.x_minimum.valueChanged.connect(self._coordinates_changed)
        self.y_minimum.valueChanged.connect(self._coordinates_changed)
        self.x_maximum.valueChanged.connect(self._coordinates_changed)
        self.y_maximum.valueChanged.connect(self._coordinates_changed)

        # Draw the rubberband
        self._coordinates_changed()

        # Wire up button events
        self.capture_button.clicked.connect(self.start_capture)
        # Handle cancel
        cancel_button = self.button_box.button(QtWidgets.QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(self.reject)
        # Make sure to reshow this dialog when rectangle is captured
        self.tool.rectangle_created.connect(self.stop_capture)
        # Setup ok button
        self.ok_button = self.button_box.button(QtWidgets.QDialogButtonBox.Ok)
        self.ok_button.clicked.connect(self.accept)
        # Set up context help
        self.help_button = self.button_box.button(QtWidgets.QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)
        # Reset / Clear button
        clear_button = self.button_box.button(QtWidgets.QDialogButtonBox.Reset)
        clear_button.setText(self.tr('Clear'))
        clear_button.clicked.connect(self.clear)

        # Populate the bookmarks list and connect the combobox
        self._populate_bookmarks_list()
        self.bookmarks_list.currentIndexChanged.connect(
            self.bookmarks_index_changed)

        # Reinstate the last used radio button
        mode = setting('analysis_extents_mode', HAZARD_EXPOSURE_VIEW)

        if mode == HAZARD_EXPOSURE_VIEW:
            self.hazard_exposure_view_extent.setChecked(True)
        elif mode == EXPOSURE:
            self.exposure_only.setChecked(True)
        elif mode == HAZARD_EXPOSURE:
            self.hazard_exposure_only.setChecked(True)
        elif mode == HAZARD_EXPOSURE_BOOKMARK:
            self.hazard_exposure_bookmark.setChecked(True)
        elif mode == HAZARD_EXPOSURE_BOUNDINGBOX:
            self.hazard_exposure_user_extent.setChecked(True)

        self.show_warnings.setChecked(
            setting('show_extent_warnings', True, bool))
        self.show_confirmations.setChecked(
            setting('show_extent_confirmations', True, bool))

    @pyqtSlot(bool)  # prevents actions being handled twice
    def help_toggled(self, flag):
        """Show or hide the help tab in the main stacked widget.

        .. versionadded: 3.2.1

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

        .. versionadded:: 3.2.1
        """
        self.main_stacked_widget.setCurrentIndex(1)

    def show_help(self):
        """Show usage info to the user."""
        # Read the header and footer html snippets
        self.main_stacked_widget.setCurrentIndex(0)
        header = html_header()
        footer = html_footer()

        string = header

        message = extent_selector_help()

        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)

    def start_capture(self):
        """Start capturing the rectangle."""
        previous_map_tool = self.canvas.mapTool()
        if previous_map_tool != self.tool:
            self.previous_map_tool = previous_map_tool
        self.canvas.setMapTool(self.tool)
        self.hide()

    def stop_capture(self):
        """Stop capturing the rectangle and reshow the dialog."""
        self._populate_coordinates()
        self.canvas.setMapTool(self.previous_map_tool)
        self.show()

    def clear(self):
        """Clear the currently set extent."""
        self.tool.reset()
        self._populate_coordinates()
        # Revert to using hazard, exposure and view as basis for analysis
        self.hazard_exposure_view_extent.setChecked(True)

    def reject(self):
        """User rejected the rectangle."""
        self.canvas.unsetMapTool(self.tool)
        if self.previous_map_tool != self.tool:
            self.canvas.setMapTool(self.previous_map_tool)
        self.tool.reset()
        self.extent_selector_closed.emit()
        super(ExtentSelectorDialog, self).reject()

    def accept(self):
        """User accepted the rectangle."""
        mode = None
        if self.hazard_exposure_view_extent.isChecked():
            mode = HAZARD_EXPOSURE_VIEW
        elif self.exposure_only.isChecked():
            mode = EXPOSURE
        elif self.hazard_exposure_only.isChecked():
            mode = HAZARD_EXPOSURE
        elif self.hazard_exposure_bookmark.isChecked():
            mode = HAZARD_EXPOSURE_BOOKMARK
        elif self.hazard_exposure_user_extent.isChecked():
            mode = HAZARD_EXPOSURE_BOUNDINGBOX

        set_setting('analysis_extents_mode', mode)

        self.canvas.unsetMapTool(self.tool)
        if self.previous_map_tool != self.tool:
            self.canvas.setMapTool(self.previous_map_tool)

        if self.tool.rectangle() is not None:
            self.extent_defined.emit(
                self.tool.rectangle(),
                self.canvas.mapSettings().destinationCrs())
            extent = QgsGeometry.fromRect(self.tool.rectangle())
            LOGGER.info(
                'Requested extent : {wkt}'.format(wkt=extent.asWkt()))
        else:
            self.clear_extent.emit()

        # State handlers for showing warning message bars
        set_setting('show_extent_warnings', self.show_warnings.isChecked())
        set_setting(
            'show_extent_confirmations', self.show_confirmations.isChecked())

        self.tool.reset()
        self.extent_selector_closed.emit()
        super(ExtentSelectorDialog, self).accept()

    def _are_coordinates_valid(self):
        """Check if the coordinates are valid.

        :return: True if coordinates are valid otherwise False.
        :type: bool
        """
        try:
            QgsPointXY(
                self.x_minimum.value(),
                self.y_maximum.value())
            QgsPointXY(
                self.x_maximum.value(),
                self.y_minimum.value())
        except ValueError:
            return False

        return True

    def _coordinates_changed(self):
        """Handle a change in the coordinate input boxes."""
        if self._are_coordinates_valid():
            point1 = QgsPointXY(
                self.x_minimum.value(),
                self.y_maximum.value())
            point2 = QgsPointXY(
                self.x_maximum.value(),
                self.y_minimum.value())
            rect = QgsRectangle(point1, point2)

            self.tool.set_rectangle(rect)

    def _populate_coordinates(self):
        """Update the UI with the current active coordinates."""
        rect = self.tool.rectangle()
        self.blockSignals(True)
        if rect is not None:
            self.x_minimum.setValue(rect.xMinimum())
            self.y_minimum.setValue(rect.yMinimum())
            self.x_maximum.setValue(rect.xMaximum())
            self.y_maximum.setValue(rect.yMaximum())
        else:
            self.x_minimum.clear()
            self.y_minimum.clear()
            self.x_maximum.clear()
            self.y_maximum.clear()
        self.blockSignals(False)

    def bookmarks_index_changed(self):
        """Update the UI when the bookmarks combobox has changed."""
        index = self.bookmarks_list.currentIndex()
        if index >= 0:
            self.tool.reset()
            rectangle = self.bookmarks_list.itemData(index)
            self.tool.set_rectangle(rectangle)
            self.canvas.setExtent(rectangle)
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setDisabled(True)

    def on_hazard_exposure_view_extent_toggled(self, enabled):
        """Handler for hazard/exposure/view radiobutton toggle.

        :param enabled: The status of the radiobutton.
        :type enabled: bool
        """
        if enabled:
            self.tool.reset()
            self._populate_coordinates()

    def on_hazard_exposure_only_toggled(self, enabled):
        """Handler for hazard/exposure radiobutton toggle.

        :param enabled: The status of the radiobutton.
        :type enabled: bool
        """
        if enabled:
            self.tool.reset()
            self._populate_coordinates()

    def on_hazard_exposure_bookmark_toggled(self, enabled):
        """Update the UI when the user toggles the bookmarks radiobutton.

        :param enabled: The status of the radiobutton.
        :type enabled: bool
        """
        if enabled:
            self.bookmarks_index_changed()
        else:
            self.ok_button.setEnabled(True)
        self._populate_coordinates()

    def _populate_bookmarks_list(self):
        """Read the sqlite database and populate the bookmarks list.

        If no bookmarks are found, the bookmarks radio button will be disabled
        and the label will be shown indicating that the user should add
        bookmarks in QGIS first.

        Every bookmark are reprojected to mapcanvas crs.
        """
        # Connect to the QGIS sqlite database and check if the table exists.
        # noinspection PyArgumentList
        db_file_path = QgsApplication.qgisUserDatabaseFilePath()
        db = sqlite3.connect(db_file_path)
        cursor = db.cursor()
        cursor.execute(
            'SELECT COUNT(*) '
            'FROM sqlite_master '
            'WHERE type=\'table\' '
            'AND name=\'tbl_bookmarks\';')

        number_of_rows = cursor.fetchone()[0]
        if number_of_rows > 0:
            cursor.execute(
                'SELECT * '
                'FROM tbl_bookmarks;')
            bookmarks = cursor.fetchall()

            canvas_srid = self.canvas.mapSettings().destinationCrs().srsid()

            for bookmark in bookmarks:
                name = bookmark[1]
                srid = bookmark[7]
                rectangle = QgsRectangle(
                    bookmark[3], bookmark[4], bookmark[5], bookmark[6])

                if srid != canvas_srid:
                    transform = QgsCoordinateTransform(
                        srid, canvas_srid, QgsProject.instance())
                    try:
                        rectangle = transform.transform(rectangle)
                    except QgsCsException:
                        rectangle = None

                if rectangle is None or rectangle.isEmpty():
                    pass

                self.bookmarks_list.addItem(name, rectangle)
        if self.bookmarks_list.currentIndex() >= 0:
            self.create_bookmarks_label.hide()
        else:
            self.create_bookmarks_label.show()
            self.hazard_exposure_bookmark.setDisabled(True)
            self.bookmarks_list.hide()
