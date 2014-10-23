# coding=utf-8
"""Map tool implementation for selecting rectangles.

Based on work by Guisepe Sucameli, 2010. Updated for coding compliance etc.
by Tim Sutton, Oct 2014.

"""


# noinspection PyPackageRequirements
from PyQt4.QtCore import SIGNAL, pyqtSignal
# noinspection PyPackageRequirements
from PyQt4.QtGui import QColor
from qgis.core import QgsPoint, QgsRectangle, QGis
from qgis.gui import QgsRubberBand, QgsMapTool, QgsMapToolEmitPoint


class RectangleMapTool(QgsMapToolEmitPoint):
    """
    Map tool that lets the user define the analysis extents.
    """
    rectangle_created = pyqtSignal()

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

        self.rubber_band = QgsRubberBand(self.canvas, QGis.Polygon)
        self.rubber_band.setColor(QColor(255, 0, 0, 100))
        self.rubber_band.setWidth(2)

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
        """
        Handle canvas release events  has finished capturing e

        :param e: A Qt event object.
        :type: QEvent
        """
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
        """
        Show the rectangle on the canvas.

        :param start_point: QGIS Point object representing the origin (
            top left).
        :type start_point: QgsPoint

        :param end_point: QGIS Point object representing the contra-origin (
            bottom right).
        :type end_point: QgsPoint

        :return:
        """
        self.rubber_band.reset(QGis.Polygon)
        if start_point.x() == end_point.x() or start_point.y() == end_point.y():
            return

        point1 = start_point
        point2 = QgsPoint(start_point.x(), end_point.y())
        point3 = end_point
        point4 = QgsPoint(end_point.x(), start_point.y())

        self.rubber_band.addPoint(point1, False)
        self.rubber_band.addPoint(point2, False)
        self.rubber_band.addPoint(point3, False)
        # noinspection PyArgumentEqualDefault
        self.rubber_band.addPoint(point4, True)  # true to update canvas
        self.rubber_band.show()

    def rectangle(self):
        """
        Accessor for the rectangle.

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
                rectangle.xMaximum(), rectangle.yMaximum())
            self.end_point = QgsPoint(
                rectangle.xMinimum(), rectangle.yMinimum())
            self.show_rectangle(self.start_point, self.end_point)
        return True

    def deactivate(self):
        """
        Disable the tool.
        """
        QgsMapTool.deactivate(self)
        self.emit(SIGNAL("deactivated()"))
