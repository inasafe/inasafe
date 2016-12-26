# coding=utf-8

from qgis.core import (
    QgsCoordinateTransform,
    QgsRectangle,
    QgsPoint,
    QgsCoordinateReferenceSystem,
    QGis)
from qgis.gui import QgsRubberBand  # pylint: disable=no-name-in-module
# noinspection PyPackageRequirements
from PyQt4.QtCore import QSettings

from safe.common.exceptions import InvalidGeometryError
from safe.definitionsv4.colors import (
    user_analysis_color,
    next_analysis_color,
    last_analysis_color,
    user_analysis_width,
    next_analysis_width,
    last_analysis_width
)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class Extent(object):
    """Extent class to handle extent."""

    def __init__(self, iface):
        """Constructor."""

        self.iface = iface

        # Rubber bands and extents for showing analysis extent etc.
        # Note that rubber bands are transient but their associated
        # extents are persistent for the session.

        # Last analysis extents
        # Added by Tim in version 2.1.0
        self.last_analysis_rubberband = None
        # Added by Tim in version 2.2.0
        self.last_analysis_extent = None
        # This is a rubber band to show what the AOI of the
        # next analysis will be. Also added in 2.1.0
        self.next_analysis_rubberband = None
        # Added by Tim in version 2.2.0
        self.next_analysis_extent = None
        # Rubber band to show the user defined analysis using extent
        # Added in 2.2.0
        self.user_analysis_rubberband = None
        # Rectangle defining the user's preferred extent for the analysis
        # Added in 2.2.0
        self.user_extent = None
        # CRS for user defined preferred extent
        self.user_extent_crs = None

        # Whether to show rubber band of last and next scenario
        self.show_rubber_bands = False

    @property
    def destination_crs(self):
        """Return the destination CRS of the map canvas.

        :return: The map canvas CRS.
        :rtype: QgsCoordinateTransform
        """
        return self.iface.mapCanvas().mapRenderer().destinationCrs()

    def _draw_rubberband(self, extent, colour, width):
        """
        Draw a rubber band on the canvas.

        .. versionadded: 2.2.0

        :param extent: Extent that the rubber band should be drawn for.
        :type extent: QgsRectangle

        :param colour: Colour for the rubber band.
        :type colour: QColor

        :param width: The width for the rubber band pen stroke.
        :type width: int

        :returns: Rubber band that should be set to the extent.
        :rtype: QgsRubberBand
        """
        # noinspection PyArgumentList
        rubber_band = QgsRubberBand(
            self.iface.mapCanvas(), geometryType=QGis.Line)
        rubber_band.setColor(colour)
        rubber_band.setWidth(width)
        update_display_flag = False
        point = QgsPoint(extent.xMinimum(), extent.yMinimum())
        rubber_band.addPoint(point, update_display_flag)
        point = QgsPoint(extent.xMaximum(), extent.yMinimum())
        rubber_band.addPoint(point, update_display_flag)
        point = QgsPoint(extent.xMaximum(), extent.yMaximum())
        rubber_band.addPoint(point, update_display_flag)
        point = QgsPoint(extent.xMinimum(), extent.yMaximum())
        rubber_band.addPoint(point, update_display_flag)
        point = QgsPoint(extent.xMinimum(), extent.yMinimum())
        update_display_flag = True
        rubber_band.addPoint(point, update_display_flag)
        return rubber_band

    @staticmethod
    def validate_rectangle(extent):
        """

        .. versionadded: 2.2.0

        :param extent:
        :return:

        :raises: InvalidGeometryError
        """

        if not (isinstance(extent, list) or isinstance(extent, QgsRectangle)):
            raise InvalidGeometryError
        if isinstance(extent, list):
            try:
                extent = QgsRectangle(
                    extent[0],
                    extent[1],
                    extent[2],
                    extent[3])
            except:  # yes we want to catch all exception types here
                raise InvalidGeometryError
        return extent

    def _geo_extent_to_canvas_crs(self, extent):
        """Transform a bounding box into the CRS of the canvas.

        :param extent: An extent in geographic coordinates.
        :type extent: QgsRectangle

        :returns: The extent in CRS of the canvas.
        :rtype: QgsRectangle
        """

        # make sure the extent is in the same crs as the canvas
        source_crs = QgsCoordinateReferenceSystem()
        source_crs.createFromSrid(4326)
        transform = QgsCoordinateTransform(source_crs, self.destination_crs)
        extent = transform.transformBoundingBox(extent)
        return extent

    def hide_user_analysis_extent(self):
        """Hide the rubber band showing extent of the next analysis.

        .. versionadded: 2.2.0
        """
        if self.user_analysis_rubberband is not None:
            self.user_analysis_rubberband.reset(QGis.Polygon)
            self.user_analysis_rubberband = None

    def define_user_analysis_extent(self, extent, crs):
        """Slot called when user has defined a custom analysis extent.

        .. versionadded: 2.2.0

        :param extent: Extent of the user's preferred analysis area.
        :type extent: QgsRectangle

        :param crs: Coordinate reference system for user defined analysis
            extent.
        :type crs: QgsCoordinateReferenceSystem
        """
        self.hide_user_analysis_extent()

        try:
            extent = self.validate_rectangle(extent)
            self.user_extent = extent
            self.user_extent_crs = crs
        except InvalidGeometryError:
            # keep existing user extent without updating it
            raise InvalidGeometryError

        # Persist this extent for the next session
        settings = QSettings()
        user_extent = [
            self.user_extent.xMinimum(),
            self.user_extent.yMinimum(),
            self.user_extent.xMaximum(),
            self.user_extent.yMaximum()]
        extent_string = ', '.join(('%f' % x) for x in user_extent)
        settings.setValue('inasafe/analysis_extent', extent_string)
        settings.setValue('inasafe/analysis_extent_crs', crs.authid())

        self.show_user_analysis_extent()
        # Next extent might have changed as a result of the new user
        # analysis extent, so update it too.
        # TODO (ISMAIL): This should be handled in extent not in outer class.
        # self.show_next_analysis_extent()

    def clear_user_analysis_extent(self):
        """Slot called when the users clears the analysis extents."""
        self.hide_user_analysis_extent()
        self.user_extent = None
        self.user_extent_crs = None

    def show_user_analysis_extent(self):
        """Update the rubber band showing the user defined analysis extent.

        Primary purpose of this slot is to draw a rubber band of where the
        analysis will be carried out based on valid intersection between
        layers and the user's preferred analysis area.

        This slot is called on pan, zoom, layer visibility changes and
        when the user updates the defined extent.

        .. versionadded:: 2.2.0
        """
        self.hide_user_analysis_extent()

        extent = self.user_extent
        source_crs = self.user_extent_crs

        try:
            extent = self.validate_rectangle(extent)
        except InvalidGeometryError:
            # keep existing user extent without updating it
            return

        # make sure the extent is in the same crs as the canvas
        transform = QgsCoordinateTransform(source_crs, self.destination_crs)
        extent = transform.transformBoundingBox(extent)

        if self.show_rubber_bands:
            # Draw in blue
            self.user_analysis_rubberband = self._draw_rubberband(
                extent, user_analysis_color, user_analysis_width)

    def hide_next_analysis_extent(self):
        """Hide the rubber band showing extent of the next analysis.

        .. versionadded:: 2.1.0
        """
        if self.next_analysis_rubberband is not None:
            self.next_analysis_rubberband.reset(QGis.Polygon)
            self.next_analysis_rubberband = None

    def show_next_analysis_extent(self, next_analysis_extent):
        """Update the rubber band showing where the next analysis extent is.

        Primary purpose of this slot is to draw a rubber band of where the
        analysis will be carried out based on valid intersection between
        layers.

        :param next_analysis_extent: The next analysis extent.
        :type next_analysis_extent: list

        .. versionadded:: 2.1.0
        """
        try:
            next_analysis_extent = self.validate_rectangle(
                next_analysis_extent)
        except InvalidGeometryError:
            return

        # store the extent to the instance property before reprojecting it
        self.next_analysis_extent = next_analysis_extent

        next_analysis_extent = self._geo_extent_to_canvas_crs(
            next_analysis_extent)

        if self.show_rubber_bands:
            # draw in green
            self.next_analysis_rubberband = self._draw_rubberband(
                next_analysis_extent, next_analysis_color, next_analysis_width)

    def hide_last_analysis_extent(self):
        """Clear extent rubber band if any.

        This method can safely be called even if there is no rubber band set.

        .. versionadded:: 2.1.0
        """
        if self.last_analysis_rubberband is not None:
            self.last_analysis_rubberband.reset(QGis.Polygon)
            self.last_analysis_rubberband = None

    def show_last_analysis_extent(self, extent):
        """Show last analysis extent as a rubber band on the canvas.

        .. seealso:: hide_extent()

        .. versionadded:: 2.1.0

        :param extent: A rectangle to display on the canvas. If parameter is
            a list it should be in the form of [xmin, ymin, xmax, ymax]
            otherwise it will be silently ignored and this method will
            do nothing.
        :type extent: QgsRectangle, list
        """
        self.hide_last_analysis_extent()
        try:
            # Massage it into a QgsRectangle
            extent = self.validate_rectangle(extent)
        except InvalidGeometryError:
            return

        # store the extent to the instance property before reprojecting it
        self.last_analysis_extent = extent

        extent = self._geo_extent_to_canvas_crs(extent)

        if self.show_rubber_bands:
            # Draw in red
            self.last_analysis_rubberband = self._draw_rubberband(
                extent, last_analysis_color, last_analysis_width)
