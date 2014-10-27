# -*- coding: utf-8 -*-

"""
***************************************************************************
    extent_selector.py
    ---------------------
    Based on original code from:
        Date                 : December 2010
        Copyright            : (C) 2010 by Giuseppe Sucameli
        Email                : brush dot tyler at gmail dot com
    Refactored and improved in Oct 2014 by Tim Sutton for InaSAFE.
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
    Dialog for letting user determine analysis extents.
    """

    extent_defined = pyqtSignal()
    selection_stopped = pyqtSignal()
    selection_started = pyqtSignal()

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

        self.prepare_tool()
        # Use the current map canvas extents as a starting point
        self.set_extent(self.canvas.extent())
        self.populate_coordinates()

        self.x_minimum.valueChanged.connect(self.coordinates_changed)
        self.y_minimum.valueChanged.connect(self.coordinates_changed)
        self.x_maximum.valueChanged.connect(self.coordinates_changed)
        self.y_maximum.valueChanged.connect(self.coordinates_changed)
        self.start()

    def prepare_tool(self):
        """
        Set the canvas property.
        """
        self.tool = RectangleMapTool(self.canvas)
        self.previous_map_tool = self.canvas.mapTool()
        self.tool.rectangle_created.connect(self.populate_coordinates)

    def accept(self):
        """
        Stop capturing the rectangle.
        """
        if not self.is_started:
            return
        self.is_started = False
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
        self.coordinates_changed()
        self.selection_started.emit()

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
                self.x_minimum.value(),
                self.y_minimum.value())
            QgsPoint(
                self.x_maximum.value(),
                self.y_maximum.value())
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
                self.x_minimum.value(),
                self.y_minimum.value())
            point2 = QgsPoint(
                self.x_maximum.value(),
                self.y_maximum.value())
            rect = QgsRectangle(point1, point2)

        self.set_extent(rect)

    def populate_coordinates(self):
        """
        Update the UI with the current active coordinates.
        """
        rect = self.get_extent()
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
        self.extent_defined.emit()
