
from PyQt4.QtGui import QColor
from qgis.core import QgsPoint, QgsRectangle, QGis
from qgis.gui import QgsRubberBand, QgsMapTool

class RectangleMapTool(QgsMapToolEmitPoint):
    """
    Map tool that lets the user define the analysis extents.
    """

    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.rubberBand = QgsRubberBand(self.canvas, QGis.Polygon)
        self.rubberBand.setColor(QColor(255, 0, 0, 100))
        self.rubberBand.setWidth(2)

        self.reset()

    def reset(self):
        """
        Clear the rubber band for the analysis extents.
        """
        self.start_point = self.end_point = None
        self.is_emitting_point = False
        self.rubberBand.reset(QGis.Polygon)

    def canvasPressEvent(self, e):
        """
        Handle canvas press events so we know when user is capturing the rect.
        :param e:
        """
        self.start_point = self.toMapCoordinates(e.pos())
        self.end_point = self.start_point
        self.is_emitting_point = True

        self.show_rectangle(self.start_point, self.end_point)

    def canvasReleaseEvent(self, e):
        """

        :param e:
        """
        self.is_emitting_point = False
        # if self.rectangle() != None:
        #  self.emit( SIGNAL("rectangleCreated()") )
        self.emit(SIGNAL("rectangleCreated()"))

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

        :param start_point: Tuple containing X, Y of the start point.
        :type start_point: tuple

        :param end_point: Tuple containing X, Y of the end point.
        :type end_point: tuple

        :return:
        """
        self.rubberBand.reset(QGis.Polygon)
        if start_point.x() == end_point.x() or start_point.y() == end_point.y():
            return

        point1 = QgsPoint(start_point.x(), start_point.y())
        point2 = QgsPoint(start_point.x(), end_point.y())
        point3 = QgsPoint(end_point.x(), end_point.y())
        point4 = QgsPoint(end_point.x(), start_point.y())

        self.rubberBand.addPoint(point1, False)
        self.rubberBand.addPoint(point2, False)
        self.rubberBand.addPoint(point3, False)
        # noinspection PyArgumentEqualDefault
        self.rubberBand.addPoint(point4, True)  # true to update canvas
        self.rubberBand.show()

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

        if rectangle == None:
            self.reset()
        else:
            self.start_point = QgsPoint(rectangle.xMaximum(), rectangle.yMaximum())
            self.end_point = QgsPoint(rectangle.xMinimum(), rectangle.yMinimum())
            self.show_rectangle(self.start_point, self.end_point)
        return True

    def deactivate(self):
        """
        Disable the tool.
        """
        QgsMapTool.deactivate(self)
        self.emit(SIGNAL("deactivated()"))

