# coding=utf-8

"""Related to the extent (with or without an aggregation layer."""


from qgis.core import QgsCoordinateTransform, QgsGeometry, QgsWkbTypes
from qgis.gui import QgsRubberBand
from qgis.PyQt.QtCore import Qt

from safe.definitions.styles import (last_analysis_color, last_analysis_width,
                                     next_analysis_color, next_analysis_width,
                                     user_analysis_color, user_analysis_width)
from safe.utilities.settings import set_setting

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def singleton(class_):
    """Singleton definition.

    Method 1 from
    https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return get_instance


@singleton
class Extent():
    """Extent class to handle analysis extent.

    Rubber bands and extents for showing analysis extent etc.
    Note that rubber bands are transient but their associated extents are
    persistent for the session.

    Rubberbands are stored in the map canvas CRS.
    """

    def __init__(self, iface):
        """Constructor."""

        self._map_canvas = iface.mapCanvas()

        # Last analysis extents
        self._last_analysis_rubberband = None
        self._last_analysis_extent = None  # QgsGeometry

        # The AOI of the next analysis.
        self._next_analysis_rubberband = None
        self._next_analysis_extent = None  # QgsGeometry

        # Rectangle defining the user's preferred extent for the analysis
        self._user_analysis_rubberband = None
        self._user_extent = None  # QgsRectangle

        # Whether to show rubber band of last and next scenario
        self._show_rubber_bands = False

    @property
    def show_rubber_bands(self):
        """Return if we display rubberbands.

        :return: Boolean if we display rubberbands
        :rtype: bool
        """
        return self._show_rubber_bands

    @show_rubber_bands.setter
    def show_rubber_bands(self, display):
        """Setter if we need to display rubberbands.

        :param display: The boolean.
        :type display: bool
        """
        self._show_rubber_bands = display

        if self._show_rubber_bands:
            self.display_last_analysis()
            self.display_next_analysis()
            self.display_user_extent()
        else:
            self.hide_last_analysis_extent()
            self.hide_user_analysis_extent()
            self.hide_next_analysis_extent()

    @property
    def crs(self):
        """Return the CRS of the map canvas.

        :return: The map canvas CRS.
        :rtype: QgsCoordinateTransform
        """
        return self._map_canvas.mapSettings().destinationCrs()

    @property
    def user_extent(self):
        """The user extent in the canvas CRS.

        :return: The user extent.
        :rtype: QgsGeometry
        """
        return self._user_extent

    def set_user_extent(self, extent, crs):
        """Setter for the user requested extent.

        This function will redraw the rubberband if needed.

        :param extent: The user extent.
        :type extent: QgsGeometry

        :param crs: The CRS of the extent.
        :type crs: QgsCoordinateReferenceSystem
        """
        extent = QgsGeometry(extent)
        transform = QgsCoordinateTransform(crs, self.crs)
        extent.transform(transform)
        self._user_extent = extent
        set_setting('user_extent', extent.exportToWkt())
        set_setting('user_extent_crs', crs.authid())
        if self._show_rubber_bands:
            self.display_user_extent()

    @property
    def last_analysis_extent(self):
        """The last analysis extent in the canvas CRS.

        :return: The last analysis extent.
        :rtype: QgsGeometry
        """
        return self._last_analysis_extent

    def set_last_analysis_extent(self, extent, crs):
        """Setter for the last analysis extent.

        This function will redraw the rubberband if needed.

        :param extent: The last analysis extent.
        :type extent: QgsGeometry

        :param crs: The CRS of the extent.
        :type crs: QgsCoordinateReferenceSystem
        """
        extent = QgsGeometry(extent)
        transform = QgsCoordinateTransform(crs, self.crs)
        extent.transform(transform)
        self._last_analysis_extent = extent

        if self._show_rubber_bands:
            self.display_last_analysis()

    @property
    def next_analysis_extent(self):
        """The next analysis extent in the canvas CRS.

        :return: The next analysis extent.
        :rtype: QgsGeometry
        """
        return self._next_analysis_extent

    def set_next_analysis_extent(self, extent, crs):
        """Setter for the next analysis extent.

        This function will redraw the rubberband if needed.

        :param extent: The next analysis extent.
        :type extent: QgsGeometry

        :param crs: The CRS of the extent.
        :type crs: QgsCoordinateReferenceSystem
        """
        extent = QgsGeometry(extent)
        transform = QgsCoordinateTransform(crs, self.crs)
        extent.transform(transform)
        self._next_analysis_extent = extent

        if self._show_rubber_bands:
            self.display_next_analysis()

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
            self._map_canvas, geometryType=QgsWkbTypes.Polygon)
        rubber_band.setBrushStyle(Qt.NoBrush)
        rubber_band.setColor(colour)
        rubber_band.setWidth(width)
        rubber_band.setToGeometry(geometry, None)
        return rubber_band

    def display_user_extent(self):
        """Display the user extent."""
        self.hide_user_analysis_extent()
        if self._user_extent:
            self._user_analysis_rubberband = self._draw_rubberband(
                self._user_extent, user_analysis_color, user_analysis_width)

    def display_next_analysis(self):
        """Display the next analysis extent."""
        self.hide_next_analysis_extent()
        if self._next_analysis_extent:
            self._next_analysis_rubberband = self._draw_rubberband(
                self._next_analysis_extent,
                next_analysis_color,
                next_analysis_width)

    def display_last_analysis(self):
        """Display the next analysis extent."""
        self.hide_last_analysis_extent()
        if self._last_analysis_extent:
            self._last_analysis_rubberband = self._draw_rubberband(
                self._last_analysis_extent,
                last_analysis_color,
                last_analysis_width)

    def clear_user_analysis_extent(self):
        """Slot called when the users clears the analysis extents."""
        self.hide_user_analysis_extent()
        self._user_extent = None

    def clear_next_analysis_extent(self):
        """Slot called when the users clears the analysis extents."""
        self.hide_next_analysis_extent()
        self._next_analysis_extent = None

    def hide_user_analysis_extent(self):
        """Hide the rubber band showing extent of the next analysis.

        .. versionadded: 2.2.0
        """
        if self._user_analysis_rubberband is not None:
            self._user_analysis_rubberband.reset(QgsWkbTypes.Polygon)
            self._user_analysis_rubberband = None

    def hide_next_analysis_extent(self):
        """Hide the rubber band showing extent of the next analysis.

        .. versionadded:: 2.1.0
        """
        if self._next_analysis_rubberband is not None:
            self._next_analysis_rubberband.reset(QgsWkbTypes.Polygon)
            self._next_analysis_rubberband = None

    def hide_last_analysis_extent(self):
        """Clear extent rubber band if any.

        This method can safely be called even if there is no rubber band set.

        .. versionadded:: 2.1.0
        """
        if self._last_analysis_rubberband is not None:
            self._last_analysis_rubberband.reset(QgsWkbTypes.Polygon)
            self._last_analysis_rubberband = None
