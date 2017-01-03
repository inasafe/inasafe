# coding=utf-8

from qgis.core import (
    QgsCoordinateTransform,
    QgsRectangle,
    QgsGeometry,
    QgsPoint,
    QgsCoordinateReferenceSystem,
    QGis)
from qgis.gui import QgsRubberBand  # pylint: disable=no-name-in-module
# noinspection PyPackageRequirements
from PyQt4.QtCore import QSettings, Qt

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
    """Extent class to handle analysis extent.

    Rubber bands and extents for showing analysis extent etc.
    Note that rubber bands are transient but their associated extents are
    persistent for the session.

    Rubberbands are stored in the map canvas CRS.
    """

    def __init__(self, iface):
        """Constructor."""

        self.iface = iface

        # Rubber bands and extents for showing analysis extent etc.
        # Note that rubber bands are transient but their associated
        # extents are persistent for the session.

        # Last analysis extents
        self.last_analysis_rubberband = None
        self.last_analysis_extent = None  # QgsGeometry

        # The AOI of the next analysis.
        self.next_analysis_rubberband = None
        self.next_analysis_extent = None  # QgsGeometry

        # Rectangle defining the user's preferred extent for the analysis
        self.user_analysis_rubberband = None
        self.user_extent = None  # QgsRectangle
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

    def _draw_rubberband(self, geometry, colour, width):
        """Draw a rubber band on the canvas.

        .. versionadded: 2.2.0

        :param geometry: Extent that the rubber band should be drawn for.
        :type geometry: QgsGeometry

        :param colour: Colour for the rubber band.
        :type colour: QColor

        :param width: The width for the rubber band pen stroke.
        :type width: int

        :returns: Rubber band that should be set to the extent.
        :rtype: QgsRubberBand
        """
        # noinspection PyArgumentList
        rubber_band = QgsRubberBand(
            self.iface.mapCanvas(), geometryType=QGis.Polygon)
        rubber_band.setBrushStyle(Qt.NoBrush)
        rubber_band.setColor(colour)
        rubber_band.setWidth(width)
        rubber_band.setToGeometry(geometry, None)

        return rubber_band

    def _geo_extent_to_canvas_crs(self, extent):
        """Transform a bounding box into the CRS of the canvas.

        :param extent: An extent in geographic coordinates.
        :type extent: QgsGeometry

        :returns: The extent in CRS of the canvas.
        :rtype: QgsGeometry
        """

        # Temporary hack. ET.
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

        self.user_extent = extent
        self.user_extent_crs = crs

        # Persist this extent for the next session
        settings = QSettings()
        settings.setValue('inasafe/user_extent', extent.asWktPolygon())
        settings.setValue('inasafe/user_extent_crs', crs.authid())

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

        if not extent or not source_crs:
            return

        extent = QgsGeometry.fromRect(extent)

        # make sure the extent is in the same crs as the canvas
        transform = QgsCoordinateTransform(source_crs, self.destination_crs)
        extent.transform(transform)

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
        :type next_analysis_extent: QgsGeometry

        .. versionadded:: 2.1.0
        """

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

        :param extent: The last analysis extent.
        :type extent: QgsGeometry
        """
        self.hide_last_analysis_extent()

        # store the extent to the instance property before reprojecting it
        self.last_analysis_extent = extent

        extent = self._geo_extent_to_canvas_crs(extent)

        if self.show_rubber_bands:
            # Draw in red
            self.last_analysis_rubberband = self._draw_rubberband(
                extent, last_analysis_color, last_analysis_width)
