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
from PyQt4.QtCore import QSettings, pyqtSlot, Qt

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

        self._iface = iface

        # Last analysis extent.
        self._last_analysis_rubberband = None  # Read only
        self._last_analysis_extent = None

        # Next analysis extent, AOI (Area Of Interest).
        self._next_analysis_rubberband = None  # Read only
        self._next_analysis_extent = None

        # Extent defining the user's preferred extent for the analysis.
        self._user_analysis_rubberband = None  # Read only
        self._user_extent = None
        self._user_extent_crs = None

        flag = bool(QSettings().value(
            'inasafe/showRubberBands', False, type=bool))
        self._show_rubber_bands = flag

    @property
    def crs(self):
        """Property to return the current CRS used in the map canvas.

        :return: The CRS used in the map canvas.
        :rtype: QgsCoordinateReferenceSystem
        """
        return self._iface.mapCanvas().mapSettings().destinationCrs()

    @pyqtSlot('bool')
    def toggle_rubber_bands(self, flag):
        """Disabled/enable the rendering of rubber bands.

        This slot is called from the button.

        :param flag: Flag to indicate if drawing of bands is active.
        :type flag: bool
        """
        self._show_rubber_bands = flag
        QSettings().setValue('inasafe/showRubberBands', flag)
        if flag:
            self.draw_rubber_bands()
        else:
            self.hide_last_analysis_extent()  # red
            self.hide_next_analysis_extent()  # green
            self.hide_user_analysis_extent()  # blue

    @property
    def user_extent(self):
        return self._user_extent

    @user_extent.setter
    def user_extent(self, extent):

        self._user_extent = extent

        self.hide_user_analysis_extent()

        if self._user_extent and self._user_extent_crs and self._show_rubber_bands:
            # These parameters might be empty from the user.

            user_extent = QgsGeometry(self.user_extent)

            # Make sure the extent is in the same crs as the canvas.
            destination_crs = self._iface.mapCanvas().mapSettings().\
                destinationCrs()
            if self._user_extent_crs() != destination_crs:
                transform = QgsCoordinateTransform(
                    self._user_extent_crs, destination_crs)
                user_extent.transform(transform)

            if not self._show_rubber_bands:
                # Dra in green.
                self._user_analysis_rubberband = self._draw_rubberband(
                    user_extent, user_analysis_color, user_analysis_width)

            settings = QSettings()
            settings.setValue(
                'inasafe/analysis_extent', self._user_extent.exportToWkt())
            settings.setValue(
                'inasafe/analysis_extent_crs', self._user_extent_crs.authid())

    @pyqtSlot('QgsRectangle', 'QgsCoordinateReferenceSystem')
    def define_user_analysis_extent(self, extent, crs):
        """Slot called when user has defined a custom analysis extent.

        .. versionadded: 4.0

        :param extent: Extent of the user's preferred analysis area.
        :type extent: QgsRectangle

        :param crs: Coordinate reference system for user defined analysis
            extent.
        :type crs: QgsCoordinateReferenceSystem
        """
        self.user_extent_crs = crs
        self.user_extent = extent

    @property
    def user_extent_crs(self):
        return self._user_extent_crs

    @user_extent_crs.setter
    def user_extent_crs(self, crs):
        self._user_extent_crs = crs

    @property
    def last_analysis_extent(self):
        return self._last_analysis_extent

    @last_analysis_extent.setter
    def last_analysis_extent(self, extent):
        self._last_analysis_extent = extent
        self.hide_last_analysis_extent()

        if self._show_rubber_bands:
            # Draw in red.
            self._last_analysis_rubberband = self._draw_rubberband(
                extent, last_analysis_color, last_analysis_width)

    @property
    def next_analysis_extent(self):
        return self._last_analysis_extent

    @next_analysis_extent.setter
    def next_analysis_extent(self, extent):
        self._next_analysis_extent = extent
        self.hide_next_analysis_extent()

        if self._show_rubber_bands:
            # Draw in green.
            self._next_analysis_rubberband = self._draw_rubberband(
                self._next_analysis_extent,
                next_analysis_color,
                next_analysis_width)

    def draw_rubber_bands(self):
        self.next_analysis_extent = self._next_analysis_extent
        self.last_analysis_extent = self._last_analysis_extent
        self.user_extent = self._user_extent

    def _draw_rubberband(self, geometry, colour, width):
        """
        Draw a rubber band on the canvas.

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
            self._iface.mapCanvas(), geometryType=QGis.Polygon)
        rubber_band.setBrushStyle(Qt.NoBrush)
        rubber_band.setColor(colour)
        rubber_band.setWidth(width)
        rubber_band.setToGeometry(geometry, None)

        return rubber_band

    def clear_user_analysis_extent(self):
        """Slot called when the users clears the analysis extents."""
        self.hide_user_analysis_extent()
        self.user_extent = None
        self.user_extent_crs = None

    def hide_user_analysis_extent(self):
        """Hide the rubber band showing extent of the user requested extent.

        .. versionadded: 2.2.0
        """
        if self._user_analysis_rubberband is not None:
            self._user_analysis_rubberband.reset(QGis.Polygon)
            self._user_analysis_rubberband = None

    def hide_next_analysis_extent(self):
        """Hide the rubber band showing extent of the next analysis.

        .. versionadded:: 2.1.0
        """
        if self._next_analysis_rubberband is not None:
            self._next_analysis_rubberband.reset(QGis.Polygon)
            self._next_analysis_rubberband = None

    def hide_last_analysis_extent(self):
        """Clear extent rubber band if any.

        .. versionadded:: 2.1.0
        """
        if self._last_analysis_rubberband is not None:
            self._last_analysis_rubberband.reset(QGis.Polygon)
            self._last_analysis_rubberband = None

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

        # store the extent to the instance property before reprojecting it
        self.last_analysis_extent = extent

        destination_crs = self._iface.mapCanvas().mapRenderer().destinationCrs()
        source_crs = QgsCoordinateReferenceSystem()
        source_crs.createFromSrid(4326)
        transform = QgsCoordinateTransform(source_crs, destination_crs)
        extent = transform.transformBoundingBox(extent)
        extent = geo_extent_to_crs(extent, destination_crs)

        if self._show_rubber_bands:
            # Draw in red
            self._last_analysis_rubberband = self._draw_rubberband(
                extent, last_analysis_color, last_analysis_width)
