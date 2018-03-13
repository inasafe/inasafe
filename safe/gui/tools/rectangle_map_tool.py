# coding=utf-8
"""Map tool implementation for selecting rectangles.

Based on work by Guisepe Sucameli, 2010. Updated for coding compliance etc.
by Tim Sutton, Oct 2014.

.. versionadded:: 2.2.0

"""

# pylint: enable=no-name-in-module
# noinspection PyPackageRequirements
from PyQt4.QtCore import pyqtSignal
# noinspection PyPackageRequirements
from PyQt4.QtGui import QColor
from qgis.core import QgsPoint, QgsRectangle, QGis
# pylint: disable=no-name-in-module
from qgis.gui import QgsRubberBand, QgsMapTool, QgsMapToolEmitPoint


class RectangleMapTool(QgsMapToolEmitPoint):

    """Map tool that lets the user define the analysis extents."""

    rectangle_created = pyqtSignal()
    deactivated = pyqtSignal()

    def __init__(self, canvas):
        """Constructor for the map tool.

        :param canvas: Canvas that tool will interact with.
        :type canvas: QgsMapCanvas
        """
        self.canvas = canvas
        self.start_point = None
        self.end_point = None
        self.is_emitting_point = False

        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.rubber_band = QgsRubberBand(self.canvas, geometryType=QGis.Line)
        self.rubber_band.setColor(QColor(0, 0, 240, 100))
        # Needs QGIS 2.6
        # self.rubber_band.setFillColor(QColor(0, 0, 240, 0))
        self.rubber_band.setWidth(1)

        self.reset()

    def reset(self):
        """
        Clear the rubber band for the analysis extents.
        """
        self.start_point = self.end_point = None
        self.is_emitting_point = False
        self.rubber_band.reset(QGis.Polygon)

    def canvasPressEvent(self, e):
        """
        Handle canvas press events so we know when user is capturing the rect.

        :param e: A Qt event object.
        :type: QEvent
        """
        self.start_point = self.toMapCoordinates(e.pos())
        self.end_point = self.start_point
        self.is_emitting_point = True

        self.show_rectangle(self.start_point, self.end_point)

    def canvasReleaseEvent(self, e):
        """Handle canvas release events has finished capturing e.

        :param e: A Qt event object.
        :type: QEvent
        """
        _ = e  # NOQA
        self.is_emitting_point = False
        self.rectangle_created.emit()

    def canvasMoveEvent(self, e):
        """

        :param e:
        :return:
        """
        if not self.is_emitting_point:
            return

        self.end_point = self.toMapCoordinates(e.pos())
        self.show_rectangle(self.start_point, self.end_point)

    def show_rectangle(self, start_point, end_point):
        """Show the rectangle on the canvas.

        :param start_point: QGIS Point object representing the origin (
            top left).
        :type start_point: QgsPoint

        :param end_point: QGIS Point object representing the contra-origin (
            bottom right).
        :type end_point: QgsPoint

        :return:
        """
        self.rubber_band.reset(QGis.Polygon)
        if (start_point.x() == end_point.x() or
                start_point.y() == end_point.y()):
            return

        point1 = start_point
        point2 = QgsPoint(end_point.x(), start_point.y())
        point3 = end_point
        point4 = QgsPoint(start_point.x(), end_point.y())

        update_canvas = False
        self.rubber_band.addPoint(point1, update_canvas)
        self.rubber_band.addPoint(point2, update_canvas)
        self.rubber_band.addPoint(point3, update_canvas)
        self.rubber_band.addPoint(point4, update_canvas)
        # noinspection PyArgumentEqualDefault
        # no False so canvas will update
        # close the polygon otherwise it shows as a filled rect
        self.rubber_band.addPoint(point1)
        self.rubber_band.show()

    def rectangle(self):
        """Accessor for the rectangle.

        :return: A rectangle showing the designed extent.
        :rtype: QgsRectangle
        """
        if self.start_point is None or self.end_point is None:
            return None
        elif self.start_point.x() == self.end_point.x() or \
                self.start_point.y() == self.end_point.y():
            return None

        return QgsRectangle(self.start_point, self.end_point)

    def set_rectangle(self, rectangle):
        """
        Set the rectangle for the selection.
        :param rectangle:
        :return:
        """
        if rectangle == self.rectangle():
            return False

        if rectangle is None:
            self.reset()
        else:
            self.start_point = QgsPoint(
                rectangle.xMinimum(), rectangle.yMinimum())
            self.end_point = QgsPoint(
                rectangle.xMaximum(), rectangle.yMaximum())
            self.show_rectangle(self.start_point, self.end_point)
        return True

    def deactivate(self):
        """
        Disable the tool.
        """
        self.rubber_band.reset(QGis.Polygon)
        QgsMapTool.deactivate(self)
        self.deactivated.emit()
