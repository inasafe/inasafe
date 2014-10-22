# -*- coding: utf-8 -*-

"""
***************************************************************************
    extentSelector.py
    ---------------------
    Date                 : December 2010
    Copyright            : (C) 2010 by Giuseppe Sucameli
    Email                : brush dot tyler at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Giuseppe Sucameli'
__date__ = 'December 2010'
__copyright__ = '(C) 2010, Giuseppe Sucameli'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QWidget
from qgis.core import QgsPoint, QgsRectangle

from ui_extent_selector import Ui_ExtentSelector


class ExtentSelector(QWidget, Ui_ExtentSelector):
    """

    :param parent:
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.canvas = None
        self.tool = None
        self.previous_map_tool = None
        self.is_started = False
        self.start_point
        self.setupUi(self)

        self.x1CoordEdit.textChanged.connect(self.coordinates_changed)
        self.x2CoordEdit.textChanged.connect(self.coordinates_changed)
        self.y1CoordEdit.textChanged.connect(self.coordinates_changed)
        self.y2CoordEdit.textChanged.connect(self.coordinates_changed)
        self.btnEnable.clicked.connect(self.start)

    def set_canvas(self, canvas):
        """

        :param canvas:
        """
        self.canvas = canvas
        self.tool = RectangleMapTool(self.canvas)
        self.previous_map_tool = self.canvas.mapTool()
        self.tool.rectangleCreated.connect(self.populate_coordinates)
        self.tool.deactivated.connect(self.pause)

    def stop(self):
        """
        Stop capturing the rectangle.
        """
        if not self.is_started:
            return
        self.is_started = False
        self.btnEnable.setVisible(False)
        self.tool.reset()
        self.canvas.unsetMapTool(self.tool)
        if self.previous_map_tool != self.tool:
            self.canvas.setMapTool(self.previous_map_tool)
        # self.coordsChanged()
        self.emit(SIGNAL("selectionStopped()"))

    def start(self):
        """
        Start capturing the rectangle.
        """
        previous_map_tool = self.canvas.mapTool()
        if previous_map_tool != self.tool:
            self.previous_map_tool = previous_map_tool
        self.canvas.setMapTool(self.tool)
        self.is_started = True
        self.btnEnable.setVisible(False)
        self.coordinates_changed()
        self.emit(SIGNAL("selectionStarted()"))

    def pause(self):
        """


        :return:
        """
        if not self.is_started:
            return

        self.btnEnable.setVisible(True)
        self.emit(SIGNAL("selectionPaused()"))

    def set_extent(self, rect):
        """

        :param rect:
        """
        if self.tool.set_rectangle(rect):
            self.emit(SIGNAL("newExtentDefined()"))

    def get_extent(self):
        """


        :return:
        """
        return self.tool.rectangle()

    def are_coordinates_valid(self):
        """
        Check if the coordinates are valid.
        :return:
        """
        try:
            QgsPoint(
                float(self.x1CoordEdit.text()),
                float(self.y1CoordEdit.text()))
            QgsPoint(
                float(self.x2CoordEdit.text()),
                float(self.y2CoordEdit.text()))
        except ValueError:
            return False

        return True

    def coordinates_changed(self):
        """
        Handle a change in the coordinates.
        """
        rect = None
        if self.are_coordinates_valid():
            point1 = QgsPoint(float(self.x1CoordEdit.text()),
                              float(self.y1CoordEdit.text()))
            point2 = QgsPoint(float(self.x2CoordEdit.text()),
                              float(self.y2CoordEdit.text()))
            rect = QgsRectangle(point1, point2)

        self.set_extent(rect)

    def populate_coordinates(self):
        """


        """
        rect = self.get_extent()
        self.blockSignals(True)
        if rect is not None:
            self.x1CoordEdit.setText(str(rect.xMinimum()))
            self.x2CoordEdit.setText(str(rect.xMaximum()))
            self.y1CoordEdit.setText(str(rect.yMaximum()))
            self.y2CoordEdit.setText(str(rect.yMinimum()))
        else:
            self.x1CoordEdit.clear()
            self.x2CoordEdit.clear()
            self.y1CoordEdit.clear()
            self.y2CoordEdit.clear()
        self.blockSignals(False)
        self.emit(SIGNAL("newExtentDefined()"))

