# -*- coding: utf-8 -*-

"""
***************************************************************************
    extent_selector.py
    ---------------------
    Based on original code from:
        Date                 : December 2010
        Copyright            : (C) 2010 by Giuseppe Sucameli
        Email                : brush dot tyler at gmail dot com
    Refactored in Oct 2014 by Tim Sutton for InaSAFE.
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Giuseppe Sucameli & Tim Sutton'
__date__ = 'December 2010'
__copyright__ = '(C) 2010, Giuseppe Sucameli'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

# noinspection PyPackageRequirements
from PyQt4.QtCore import SIGNAL, pyqtSignal
# noinspection PyPackageRequirements
from PyQt4.QtGui import QDialog
from qgis.core import QgsPoint, QgsRectangle

from safe_qgis.ui.extent_selector_base import Ui_ExtentSelectorBase
from safe_qgis.tools.rectangle_map_tool import RectangleMapTool


class ExtentSelector(QDialog, Ui_ExtentSelectorBase):
    """

    :param parent: Parent widget claiming ownsership of this.
    """

    extent_defined = pyqtSignal()
    selection_stopped = pyqtSignal()
    selection_started = pyqtSignal()
    selection_paused = pyqtSignal()

    def __init__(self, iface, parent=None):
        """
        Constructor for the dialog.

        :param iface: A Quantum GIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param parent: Parent widget of this dialog
        :type parent: QWidget
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.iface = iface
        self.parent = parent
        self.canvas = iface.mapCanvas()

        self.tool = None
        self.previous_map_tool = None
        self.is_started = False

        self.set_canvas(self.canvas)
        self.set_extent(self.canvas.extent())
        self.populate_coordinates()

        self.x_minimum.textChanged.connect(self.coordinates_changed)
        self.y_minimum.textChanged.connect(self.coordinates_changed)
        self.x_maximum.textChanged.connect(self.coordinates_changed)
        self.y_maximum.textChanged.connect(self.coordinates_changed)
        self.activate_button.clicked.connect(self.start)

    def set_canvas(self, canvas):
        """
        Set the canvas property.

        :param canvas: Canvas that should be associated with this tool.
        :type canvas: QgsMapCanvas

        """
        self.canvas = canvas
        self.tool = RectangleMapTool(self.canvas)
        self.previous_map_tool = self.canvas.mapTool()
        self.tool.rectangle_created.connect(self.populate_coordinates)
        self.tool.deactivated.connect(self.pause)
        self.start()

    def stop(self):
        """
        Stop capturing the rectangle.
        """
        if not self.is_started:
            return
        self.is_started = False
        self.activate_button.setVisible(False)
        self.tool.reset()
        self.canvas.unsetMapTool(self.tool)
        if self.previous_map_tool != self.tool:
            self.canvas.setMapTool(self.previous_map_tool)
        self.selection_stopped.emit()

    def start(self):
        """
        Start capturing the rectangle.
        """
        previous_map_tool = self.canvas.mapTool()
        if previous_map_tool != self.tool:
            self.previous_map_tool = previous_map_tool
        self.canvas.setMapTool(self.tool)
        self.is_started = True
        self.activate_button.setVisible(False)
        self.coordinates_changed()
        self.selection_started.emit()

    def pause(self):
        """
        Pause capture.
        """
        if not self.is_started:
            return

        self.activate_button.setVisible(True)
        self.selection_paused.emit()

    def set_extent(self, rect):
        """
        Set the extents.

        :param rect: Rectangle that the extents should be set to.
        :type rect: QgsRectangle
        """
        if self.tool.set_rectangle(rect):
            self.extent_defined.emit()

    def get_extent(self):
        """
        Get the current extents.

        :return: Extents of the marquee.
        :rtype: QgsRectangle
        """
        return self.tool.rectangle()

    def are_coordinates_valid(self):
        """
        Check if the coordinates are valid.

        :return: True if coordinates are valid otherwise False.
        :type: bool
        """
        try:
            QgsPoint(
                float(self.x_minimum.text()),
                float(self.y_minimum.text()))
            QgsPoint(
                float(self.x_maximum.text()),
                float(self.y_maximum.text()))
        except ValueError:
            return False

        return True

    def coordinates_changed(self):
        """
        Handle a change in the coordinates.
        """
        rect = None
        if self.are_coordinates_valid():
            point1 = QgsPoint(
                float(self.x_minimum.text()),
                float(self.y_minimum.text()))
            point2 = QgsPoint(
                float(self.x_maximum.text()),
                float(self.y_maximum.text()))
            rect = QgsRectangle(point1, point2)

        self.set_extent(rect)

    def populate_coordinates(self):
        """
        Update the UI with the current active coordinates.
        """
        rect = self.get_extent()
        self.blockSignals(True)
        if rect is not None:
            self.x_minimum.setText(str(rect.xMinimum()))
            self.y_minimum.setText(str(rect.xMaximum()))
            self.x_maximum.setText(str(rect.yMaximum()))
            self.y_maximum.setText(str(rect.yMinimum()))
        else:
            self.x_minimum.clear()
            self.y_minimum.clear()
            self.x_maximum.clear()
            self.y_maximum.clear()
        self.blockSignals(False)
        self.extent_defined.emit()
