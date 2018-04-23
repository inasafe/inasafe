# coding=utf-8

"""Utilities for GIS package."""

from osgeo import ogr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# From https://qgis.org/api/classQgis.html#a8da456870e1caec209d8ba7502cceff7
QGIS_OGR_GEOMETRY_MAP = {
    0: ogr.wkbUnknown,
    1: ogr.wkbPoint,
    2: ogr.wkbLineString,
    3: ogr.wkbPolygon,
    4: ogr.wkbMultiPoint,
    5: ogr.wkbMultiLineString,
    6: ogr.wkbMultiPolygon,
    100: ogr.wkbNone
}
