# -*- coding: utf-8 -*-

"""
extent_selector_dialog.py
-------------------------
Based on original code from:
Date                 : December 2010
Copyright            : (C) 2010 by Giuseppe Sucameli
Email                : brush dot tyler at gmail dot com
Refactored and improved in Oct 2014 by Tim Sutton for InaSAFE.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. versionadded:: 2.2.0
"""

__author__ = 'Giuseppe Sucameli & Tim Sutton'
__date__ = 'December 2010'
__copyright__ = '(C) 2010, Giuseppe Sucameli'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import logging

# noinspection PyUnresolvedReferences
# pylint: disable=W0611
from qgis.core import QGis  # force sip2 api

# noinspection PyPackageRequirements
from PyQt4.QtCore import pyqtSignal
from PyQt4 import QtGui
# noinspection PyPackageRequirements
from PyQt4.QtGui import QDialog
from qgis.core import (
    QgsPoint,
    QgsRectangle,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform)

from safe_qgis.safe_interface import messaging as m
from safe_qgis.utilities.utilities import (html_footer, html_header)
from safe_qgis.utilities.help import show_context_help
from safe_qgis.ui.extent_selector_dialog_base import (
    Ui_ExtentSelectorDialogBase)
from safe_qgis.tools.rectangle_map_tool import RectangleMapTool
from safe_qgis.safe_interface import styles
INFO_STYLE = styles.INFO_STYLE
LOGGER = logging.getLogger('InaSAFE')


LOGGER = logging.getLogger('InaSAFE')


class ExtentSelectorDialog(QDialog, Ui_ExtentSelectorDialogBase):
    """Dialog for letting user determine analysis extents.
    """

    extent_defined = pyqtSignal(QgsRectangle, QgsCoordinateReferenceSystem)
    clear_extent = pyqtSignal()

    def __init__(self, iface, parent=None, extent=None, crs=None):
        """Constructor for the dialog.

        :param iface: A Quantum GIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param parent: Parent widget of this dialog
        :type parent: QWidget

        :param extent: Extent of the user's preferred analysis area.
        :type extent: QgsRectangle

        :param crs: Coordinate reference system for user defined analysis
            extent.
        :type crs: QgsCoordinateReferenceSystem
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.iface = iface
        self.parent = parent
        self.canvas = iface.mapCanvas()
        self.previous_map_tool = None
        self.show_info()
        # Prepare the map tool
        self.tool = RectangleMapTool(self.canvas)
        self.previous_map_tool = self.canvas.mapTool()

        if extent is None and crs is None:
            # Use the current map canvas extents as a starting point
            self.tool.set_rectangle(self.canvas.extent())
        else:
            # Ensure supplied extent is in current canvas crs
            transform = QgsCoordinateTransform(
                crs,
                self.canvas.mapRenderer().destinationCrs())
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
        cancel_button = self.button_box.button(QtGui.QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(self.reject)
        # Make sure to reshow this dialog when rectangle is captured
        self.tool.rectangle_created.connect(self.stop_capture)
        # Setup ok button
        ok_button = self.button_box.button(QtGui.QDialogButtonBox.Ok)
        ok_button.clicked.connect(self.accept)
        # Set up context help
        self.help_context = 'user_extents'
        help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        help_button.clicked.connect(self.show_help)
        # Reset / Clear button
        clear_button = self.button_box.button(QtGui.QDialogButtonBox.Reset)
        clear_button.setText(self.tr('Clear'))
        clear_button.clicked.connect(self.clear)

    def show_help(self):
        """Load the help text for the dialog."""
        show_context_help(self.help_context)

    def show_info(self):
        """Show usage info to the user."""
        # Read the header and footer html snippets
        header = html_header()
        footer = html_footer()

        string = header

        heading = m.Heading(self.tr('User Extents Tool'), **INFO_STYLE)
        body = self.tr(
            'This tool allows you to specify exactly which geographical '
            'region should be used for your analysis. You can either '
            'enter the coordinates directly into the input boxes below '
            '(using the same CRS as the canvas is currently set to), or '
            'you can interactively select the area by using the \'select '
            'on map\' button - which will temporarily hide this window and '
            'allow you to drag a rectangle on the map. After you have '
            'finished dragging the rectangle, this window will reappear. '
            'If you enable the \'Toggle scenario outlines\' tool on the '
            'InaSAFE toolbar, your user defined extent will be shown on '
            'the map as a blue rectangle. Please note that when running '
            'your analysis, the effective analysis extent will be the '
            'intersection of the hazard extent, exposure extent and user '
            'extent - thus the entire user extent area may not be used for '
            'analysis.'

        )

        message = m.Message()
        message.add(heading)
        message.add(body)
        string += message.to_html()
        string += footer

        self.web_view.setHtml(string)

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
        """Clear the currently set extent.
        """
        self.tool.reset()
        self._populate_coordinates()

    def reject(self):
        """User rejected the rectangle.
        """
        self.canvas.unsetMapTool(self.tool)
        if self.previous_map_tool != self.tool:
            self.canvas.setMapTool(self.previous_map_tool)
        self.tool.reset()
        super(ExtentSelectorDialog, self).reject()

    def accept(self):
        """User accepted the rectangle.
        """
        self.canvas.unsetMapTool(self.tool)
        if self.previous_map_tool != self.tool:
            self.canvas.setMapTool(self.previous_map_tool)

        if self.tool.rectangle() is not None:
            LOGGER.info(
                'Extent selector setting user extents to %s' %
                self.tool.rectangle().toString())
            self.extent_defined.emit(
                self.tool.rectangle(),
                self.canvas.mapRenderer().destinationCrs()
            )
        else:
            LOGGER.info(
                'Extent selector setting user extents to nothing')
            self.clear_extent.emit()

        self.tool.reset()
        super(ExtentSelectorDialog, self).accept()

    def _are_coordinates_valid(self):
        """
        Check if the coordinates are valid.

        :return: True if coordinates are valid otherwise False.
        :type: bool
        """
        try:
            QgsPoint(
                self.x_minimum.value(),
                self.y_maximum.value())
            QgsPoint(
                self.x_maximum.value(),
                self.y_minimum.value())
        except ValueError:
            return False

        return True

    def _coordinates_changed(self):
        """
        Handle a change in the coordinate input boxes.
        """
        if self._are_coordinates_valid():
            point1 = QgsPoint(
                self.x_minimum.value(),
                self.y_maximum.value())
            point2 = QgsPoint(
                self.x_maximum.value(),
                self.y_minimum.value())
            rect = QgsRectangle(point1, point2)

            self.tool.set_rectangle(rect)

    def _populate_coordinates(self):
        """
        Update the UI with the current active coordinates.
        """
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
