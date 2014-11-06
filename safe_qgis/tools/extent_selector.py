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

.. versionadded:: 2.2.0
"""

__author__ = 'Giuseppe Sucameli & Tim Sutton'
__date__ = 'December 2010'
__copyright__ = '(C) 2010, Giuseppe Sucameli'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import logging
# noinspection PyPackageRequirements
from PyQt4.QtCore import pyqtSignal
# noinspection PyPackageRequirements
from PyQt4.QtGui import QDialog
from qgis.core import QgsPoint, QgsRectangle, QgsCoordinateReferenceSystem

from safe_qgis.ui.extent_selector_base import Ui_ExtentSelectorBase
from safe_qgis.tools.rectangle_map_tool import RectangleMapTool

LOGGER = logging.getLogger('InaSAFE')


class ExtentSelector(QDialog, Ui_ExtentSelectorBase):
    """
    Dialog for letting user determine analysis extents.
    """

    extent_defined = pyqtSignal(QgsRectangle, QgsCoordinateReferenceSystem)
    clear_extent = pyqtSignal()

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

        self.previous_map_tool = None
        # Prepare the map tool
        self.tool = RectangleMapTool(self.canvas)
        self.previous_map_tool = self.canvas.mapTool()
        self.tool.rectangle_created.connect(self._populate_coordinates)

        # Use the current map canvas extents as a starting point
        self.tool.set_rectangle(self.canvas.extent())
        self._populate_coordinates()

        # Observe inputs for changes
        self.x_minimum.valueChanged.connect(self._coordinates_changed)
        self.y_minimum.valueChanged.connect(self._coordinates_changed)
        self.x_maximum.valueChanged.connect(self._coordinates_changed)
        self.y_maximum.valueChanged.connect(self._coordinates_changed)

        # Start capturing the rectangle.
        previous_map_tool = self.canvas.mapTool()
        if previous_map_tool != self.tool:
            self.previous_map_tool = previous_map_tool
        self.canvas.setMapTool(self.tool)
        self._coordinates_changed()

        self.clear_button.clicked.connect(self.clear)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def clear(self):
        """Clear the currently set extent."""
        self.tool.reset()
        self._populate_coordinates()

    def reject(self):
        """User rejected the rectangle."""
        self.canvas.unsetMapTool(self.tool)
        if self.previous_map_tool != self.tool:
            self.canvas.setMapTool(self.previous_map_tool)
        self.tool.reset()
        super(ExtentSelector, self).reject()

    def accept(self):
        """
        User accepted the rectangle.
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
                self.iface.mapCanvas().mapRenderer().destinationCrs()
            )
        else:
            LOGGER.info(
                'Extent selector setting user extents to nothing')
            self.clear_extent.emit()

        self.tool.reset()
        super(ExtentSelector, self).accept()

    def _are_coordinates_valid(self):
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

    def _coordinates_changed(self):
        """
        Handle a change in the coordinates.
        """
        if self._are_coordinates_valid():
            point1 = QgsPoint(
                self.x_minimum.value(),
                self.y_minimum.value())
            point2 = QgsPoint(
                self.x_maximum.value(),
                self.y_maximum.value())
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
