# coding=utf-8
"""InaSAFE Disaster risk assessment tool developed by AusAid -
  *SClipper implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '20/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import tempfile
import logging

from PyQt4.QtCore import QProcess
from qgis.core import (
    QGis,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsMapLayer,
    QgsFeatureRequest,
    QgsVectorFileWriter,
    QgsGeometry,
    QgsVectorLayer,
    QgsRasterLayer)

from safe_qgis.safe_interface import (
    verify,
    read_file_keywords,
    temp_dir,
    which)

from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.exceptions import (
    InvalidParameterError,
    NoFeaturesInExtentError,
    CallGDALError,
    InvalidProjectionError,
    InvalidClipGeometryError)
from safe_qgis.utilities.utilities import tr

LOGGER = logging.getLogger(name='InaSAFE')


def clip_layer(
        layer,
        extent,
        cell_size=None,
        extra_keywords=None,
        explode_flag=True,
        hard_clip_flag=False,
        explode_attribute=None):
    """Clip a Hazard or Exposure layer to the extents provided.

    .. note:: Will delegate to clipVectorLayer or clipRasterLayer as needed.

    :param layer: A valid QGIS vector or raster layer
    :type layer:

    :param extent: Either an array representing the exposure layer extents
        in the form [xmin, ymin, xmax, ymax]. It is assumed that the
        coordinates are in EPSG:4326 although currently no checks are made to
        enforce this.
        or:
        A QgsGeometry of type polygon.
        **Polygon clipping is currently only supported for vector datasets.**
    :type extent: list(float, float, float, float)

    :param cell_size: cell size which the layer should be resampled to.
        This argument will be ignored for vector layers and if not provided
        for a raster layer, the native raster cell size will be used.
    :type cell_size: float

    :param extra_keywords: Optional keywords dictionary to be added to
        output layer.
    :type extra_keywords: dict

    :param explode_flag: A bool specifying whether multipart features
        should be 'exploded' into singleparts.
        **This parameter is ignored for raster layer clipping.**
    :type explode_flag: bool

    :param hard_clip_flag: A bool specifying whether line and polygon
        features that extend beyond the extents should be clipped such that
        they are reduced in size to the part of the geometry that intersects
        the extent only. Default is False.
        **This parameter is ignored for raster layer clipping.**
    :type hard_clip_flag: bool

    :param explode_attribute: A str specifying to which attribute #1,
        #2 and so on will be added in case of explode_flag being true. The
        attribute is modified only if there are at least 2 parts.
        **This parameter is ignored for raster layer clipping.**
    :type explode_attribute: str

    :returns: Clipped layer (placed in the system temp dir). The output layer
        will be reprojected to EPSG:4326 if needed.
    :rtype: QgsMapLayer
    """

    if layer.type() == QgsMapLayer.VectorLayer:
        return _clip_vector_layer(
            layer,
            extent,
            extra_keywords=extra_keywords,
            explode_flag=explode_flag,
            hard_clip_flag=hard_clip_flag,
            explode_attribute=explode_attribute)
    else:
        try:
            return _clip_raster_layer(
                layer,
                extent,
                cell_size,
                extra_keywords=extra_keywords)
        except CallGDALError, e:
            raise e
        except IOError, e:
            raise e


#noinspection PyArgumentList
def _clip_vector_layer(
        layer,
        extent,
        extra_keywords=None,
        explode_flag=True,
        hard_clip_flag=False,
        explode_attribute=None):
    """Clip a Hazard or Exposure layer to the extents provided.

    The layer must be a vector layer or an exception will be thrown.

    The output layer will always be in WGS84/Geographic.

    :param layer: A valid QGIS vector or raster layer
    :type layer:

    :param extent: Either an array representing the exposure layer extents
        in the form [xmin, ymin, xmax, ymax]. It is assumed that the
        coordinates are in EPSG:4326 although currently no checks are made to
        enforce this.
        or:
        A QgsGeometry of type polygon.
        **Polygon clipping is currently only supported for vector datasets.**
    :type extent: list(float, float, float, float)

    :param extra_keywords: Optional keywords dictionary to be added to
        output layer.
    :type extra_keywords: dict

    :param explode_flag: A bool specifying whether multipart features
        should be 'exploded' into singleparts.
        **This parameter is ignored for raster layer clipping.**
    :type explode_flag: bool

    :param hard_clip_flag: A bool specifying whether line and polygon
        features that extend beyond the extents should be clipped such that
        they are reduced in size to the part of the geometry that intersects
        the extent only. Default is False.
        **This parameter is ignored for raster layer clipping.**
    :type hard_clip_flag: bool

    :param explode_attribute: A str specifying to which attribute #1,
        #2 and so on will be added in case of explode_flag being true. The
        attribute is modified only if there are at least 2 parts.
    :type explode_attribute: str

    :returns: Clipped layer (placed in the system temp dir). The output layer
        will be reprojected to EPSG:4326 if needed.
    :rtype: QgsVectorLayer

    """
    if not layer or not extent:
        message = tr('Layer or Extent passed to clip is None.')
        raise InvalidParameterError(message)

    if layer.type() != QgsMapLayer.VectorLayer:
        message = tr(
            'Expected a vector layer but received a %s.' %
            str(layer.type()))
        raise InvalidParameterError(message)

    #handle, file_name = tempfile.mkstemp('.sqlite', 'clip_',
    #    temp_dir())
    handle, file_name = tempfile.mkstemp(
        '.shp', 'clip_', temp_dir())

    # Ensure the file is deleted before we try to write to it
    # fixes windows specific issue where you get a message like this
    # ERROR 1: c:\temp\inasafe\clip_jpxjnt.shp is not a directory.
    # This is because mkstemp creates the file handle and leaves
    # the file open.
    os.close(handle)
    os.remove(file_name)

    # Get the clip extents in the layer's native CRS
    geo_crs = QgsCoordinateReferenceSystem()
    geo_crs.createFromSrid(4326)
    transform = QgsCoordinateTransform(geo_crs, layer.crs())
    allowed_clip_values = [QGis.WKBPolygon, QGis.WKBPolygon25D]
    if type(extent) is list:
        rectangle = QgsRectangle(
            extent[0], extent[1],
            extent[2], extent[3])
        # noinspection PyCallByClass
        #noinspection PyTypeChecker
        polygon = QgsGeometry.fromRect(rectangle)
    elif (type(extent) is QgsGeometry and
          extent.wkbType in allowed_clip_values):
        rectangle = extent.boundingBox().toRectF()
        polygon = extent
    else:
        raise InvalidClipGeometryError(
            tr(
                'Clip geometry must be an extent or a single part'
                'polygon based geometry.'))

    projected_extent = transform.transformBoundingBox(rectangle)

    # Get vector layer
    provider = layer.dataProvider()
    if provider is None:
        message = tr(
            'Could not obtain data provider from '
            'layer "%s"' % layer.source())
        raise Exception(message)

    # Get the layer field list, select by our extent then write to disk
    # .. todo:: FIXME - for different geometry types we should implement
    #    different clipping behaviour e.g. reject polygons that
    #    intersect the edge of the bbox. Tim
    request = QgsFeatureRequest()
    if not projected_extent.isEmpty():
        request.setFilterRect(projected_extent)
        request.setFlags(QgsFeatureRequest.ExactIntersect)

    field_list = provider.fields()

    writer = QgsVectorFileWriter(
        file_name,
        'UTF-8',
        field_list,
        layer.wkbType(),
        geo_crs,
        #'SQLite')  # FIXME (Ole): This works but is far too slow
        'ESRI Shapefile')
    if writer.hasError() != QgsVectorFileWriter.NoError:
        message = tr(
            'Error when creating shapefile: <br>Filename:'
            '%s<br>Error: %s' %
            (file_name, writer.hasError()))
        raise Exception(message)

    # Reverse the coordinate xform now so that we can convert
    # geometries from layer crs to geocrs.
    transform = QgsCoordinateTransform(layer.crs(), geo_crs)
    # Retrieve every feature with its geometry and attributes
    count = 0
    has_multipart = False

    for feature in provider.getFeatures(request):
        geometry = feature.geometry()

        # Loop through the parts adding them to the output file
        # we write out single part features unless explode_flag is False
        if explode_flag:
            geometry_list = explode_multipart_geometry(geometry)
        else:
            geometry_list = [geometry]

        for part_index, part in enumerate(geometry_list):
            part.transform(transform)
            if hard_clip_flag:
                # Remove any dangling bits so only intersecting area is
                # kept.
                part = clip_geometry(polygon, part)
            if part is None:
                continue

            feature.setGeometry(part)
            # There are multiple parts and we want to show it in the
            # explode_attribute
            if part_index > 0 and explode_attribute is not None:
                has_multipart = True

            writer.addFeature(feature)
        count += 1
    del writer  # Flush to disk

    if count < 1:
        message = tr(
            'No features fall within the clip extents. Try panning / zooming '
            'to an area containing data and then try to run your analysis '
            'again. If hazard and exposure data doesn\'t overlap at all, it '
            'is not possible to do an analysis. Another possibility is that '
            'the layers do overlap but because they may have different '
            'spatial references, they appear to be disjointed. If this is the '
            'case, try to turn on reproject on-the-fly in QGIS.')
        raise NoFeaturesInExtentError(message)

    keyword_io = KeywordIO()
    if extra_keywords is None:
        extra_keywords = {}
    extra_keywords['had multipart polygon'] = has_multipart
    keyword_io.copy_keywords(
        layer, file_name, extra_keywords=extra_keywords)
    base_name = '%s clipped' % layer.name()
    layer = QgsVectorLayer(file_name, base_name, 'ogr')

    return layer


def clip_geometry(clip_polygon, geometry):
    """Clip a geometry (linestring or polygon) using a clip polygon.

    To do this we combine the clip polygon with the input geometry which
    will add nodes to the input geometry where it intersects the clip polygon.
    Next we get the symmetrical difference between the input geometry and the
    combined geometry.

    :param clip_polygon: A Polygon or Polygon25D geometry to clip with.
        Multipart polygons are not supported so the client needs to take care
        of that.
    :type clip_polygon: QgsGeometry

    :param geometry: Linestring or polygon that should be clipped.
    :type geometry: QgsGeometry

    :returns: A new geometry clipped to the region of the clip polygon.
    :rtype: QgsGeometry
    """
    # Add nodes to input geometry where it intersects with clip
    line_types = [QGis.WKBLineString, QGis.WKBLineString25D]
    point_types = [QGis.WKBPoint, QGis.WKBPoint25D]
    polygons_types = [QGis.WKBPolygon, QGis.WKBPolygon25D]
    geometry_type = geometry.wkbType()
    if geometry_type in line_types:
        combined_geometry = geometry.combine(clip_polygon)
        # Gives you the lines inside the clip
        symmetrical_geometry = geometry.symDifference(combined_geometry)
        return symmetrical_geometry
    elif geometry_type in polygons_types:
        intersection_geometry = geometry.intersection(clip_polygon)
        return intersection_geometry
    elif geometry_type in point_types:
        if clip_polygon.contains(geometry):
            return geometry
        else:
            return None
    else:
        return None


def explode_multipart_geometry(geometry):
    """Convert a multipart geometry to a list of single parts.

    This method was adapted from Carson Farmer's fTools doGeometry
    implementation in QGIS.

    :param geometry: A geometry to be exploded it it is multipart.
    :type geometry: QgsGeometry

    :returns: A list of single part geometries.
    :rtype: list

    """
    parts = []
    if geometry.type() == QGis.Point:
        if geometry.isMultipart():
            multi_geometry = geometry.asMultiPoint()
            for i in multi_geometry:
                parts.append(QgsGeometry().fromPoint(i))
        else:
            parts.append(geometry)
    elif geometry.type() == QGis.Line:
        if geometry.isMultipart():
            multi_geometry = geometry.asMultiPolyline()
            for i in multi_geometry:
                parts.append(QgsGeometry().fromPolyline(i))
        else:
            parts.append(geometry)
    elif geometry.type() == QGis.Polygon:
        if geometry.isMultipart():
            multi_geometry = geometry.asMultiPolygon()
            for i in multi_geometry:
                parts.append(QgsGeometry().fromPolygon(i))
        else:
            parts.append(geometry)
    return parts


def _clip_raster_layer(
        layer, extent, cell_size=None, extra_keywords=None):
    """Clip a Hazard or Exposure raster layer to the extents provided.

    The layer must be a raster layer or an exception will be thrown.

    .. note:: The extent *must* be in EPSG:4326.

    The output layer will always be in WGS84/Geographic.

    :param layer: A valid QGIS raster layer in EPSG:4326
    :type layer: QgsRasterLayer

    :param extent:  An array representing the exposure layer
           extents in the form [xmin, ymin, xmax, ymax]. It is assumed
           that the coordinates are in EPSG:4326 although currently
           no checks are made to enforce this.
           or:
           A QgsGeometry of type polygon.
           **Polygon clipping currently only supported for vector datasets.**
    :type extent: list(float), QgsGeometry

    :param cell_size: Cell size (in GeoCRS) which the layer should
            be resampled to. If not provided for a raster layer (i.e.
            theCellSize=None), the native raster cell size will be used.
    :type cell_size: float

    :returns: Output clipped layer (placed in the system temp dir).
    :rtype: QgsRasterLayer

    :raises: InvalidProjectionError - if input layer is a density
        layer in projected coordinates. See issue #123.

    """
    if not layer or not extent:
        message = tr('Layer or Extent passed to clip is None.')
        raise InvalidParameterError(message)

    if layer.type() != QgsMapLayer.RasterLayer:
        message = tr(
            'Expected a raster layer but received a %s.' %
            str(layer.type()))
        raise InvalidParameterError(message)

    working_layer = str(layer.source())

    # Check for existence of keywords file
    base, _ = os.path.splitext(working_layer)
    keywords_path = base + '.keywords'
    message = tr(
        'Input file to be clipped "%s" does not have the '
        'expected keywords file %s' % (
            working_layer,
            keywords_path
        ))
    verify(os.path.isfile(keywords_path), message)

    # Raise exception if layer is projected and refers to density (issue #123)
    # FIXME (Ole): Need to deal with it - e.g. by automatically reprojecting
    # the layer at this point and setting the native resolution accordingly
    # in its keywords.
    keywords = read_file_keywords(keywords_path)
    if 'datatype' in keywords and keywords['datatype'] == 'density':
        if str(layer.crs().authid()) != 'EPSG:4326':

            # This layer is not WGS84 geographic
            message = (
                'Layer %s represents density but has spatial reference "%s". '
                'Density layers must be given in WGS84 geographic '
                'coordinates, so please reproject and try again. For more '
                'information, see issue '
                'https://github.com/AIFDR/inasafe/issues/123' % (
                    working_layer,
                    layer.crs().toProj4()
                ))
            raise InvalidProjectionError(message)

    # We need to provide gdalwarp with a dataset for the clip
    # because unline gdal_translate, it does not take projwin.
    clip_kml = extent_to_kml(extent)

    # Create a filename for the clipped, resampled and reprojected layer
    handle, filename = tempfile.mkstemp('.tif', 'clip_', temp_dir())
    os.close(handle)
    os.remove(filename)

    # If no cell size is specified, we need to run gdalwarp without
    # specifying the output pixel size to ensure the raster dims
    # remain consistent.
    binary_list = which('gdalwarp')
    LOGGER.debug('Path for gdalwarp: %s' % binary_list)
    if len(binary_list) < 1:
        raise CallGDALError(
            tr('gdalwarp could not be found on your computer'))
    # Use the first matching gdalwarp found
    binary = binary_list[0]
    if cell_size is None:
        command = (
            '"%s" -q -t_srs EPSG:4326 -r near -cutline %s -crop_to_cutline '
            '-ot Float64 -of GTiff "%s" "%s"' % (
                binary,
                clip_kml,
                working_layer,
                filename))
    else:
        command = (
            '"%s" -q -t_srs EPSG:4326 -r near -tr %.14f %.14f -cutline %s '
            '-crop_to_cutline -ot Float64 -of GTiff "%s" "%s"' % (
                binary,
                cell_size,
                cell_size,
                clip_kml,
                working_layer,
                filename))

    LOGGER.debug(command)
    result = QProcess().execute(command)

    # For QProcess exit codes see
    # http://qt-project.org/doc/qt-4.8/qprocess.html#execute
    if result == -2:  # cannot be started
        message_detail = tr('Process could not be started.')
        message = tr(
            '<p>Error while executing the following shell command:'
            '</p><pre>%s</pre><p>Error message: %s'
            % (command, message_detail))
        raise CallGDALError(message)
    elif result == -1:  # process crashed
        message_detail = tr('Process crashed.')
        message = tr(
            '<p>Error while executing the following shell command:</p>'
            '<pre>%s</pre><p>Error message: %s' % (command, message_detail))
        raise CallGDALError(message)

    # .. todo:: Check the result of the shell call is ok
    keyword_io = KeywordIO()
    keyword_io.copy_keywords(layer, filename, extra_keywords=extra_keywords)
    base_name = '%s clipped' % layer.name()
    layer = QgsRasterLayer(filename, base_name)

    return layer


def extent_to_kml(extent):
    """A helper to get a little kml doc for an extent.

    We can use the resulting kml with gdal warp for clipping.

    :param extent: Extent in the form [xmin, ymin, xmax, ymax].
    :type extent: list(float)
    """

    bottom_left_corner = '%f,%f' % (extent[0], extent[1])
    top_left_corner = '%f,%f' % (extent[0], extent[3])
    top_right_corner = '%f,%f' % (extent[2], extent[3])
    bottom_right_corner = '%f,%f' % (extent[2], extent[1])
    kml = ("""<?xml version="1.0" encoding="utf-8" ?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Folder>
      <Placemark>
        <Polygon>
          <outerBoundaryIs>
            <LinearRing>
              <coordinates>
                %s %s %s %s %s
              </coordinates>
            </LinearRing>
          </outerBoundaryIs>
        </Polygon>
      </Placemark>
    </Folder>
  </Document>
</kml>""" % (
        bottom_left_corner,
        top_left_corner,
        top_right_corner,
        bottom_right_corner,
        bottom_left_corner))

    file_name = tempfile.mkstemp('.kml', 'extent_', temp_dir())[1]
    file_handle = file(file_name, 'w')
    file_handle.write(kml)
    file_handle.close()
    return file_name


def extent_to_geoarray(extent, source_crs):
    """Convert the supplied extent to geographic and return as as array.

    :param extent: QgsRectangle to be transformed to geocrs.
    :type extent:

    :param source_crs: QgsCoordinateReferenceSystem representing the
        original extent's CRS.
    :type source_crs:

    :returns: Transformed extents in EPSG:4326 in the form
        [xmin, ymin, xmax, ymax]
    """

    geo_crs = QgsCoordinateReferenceSystem()
    geo_crs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
    transform = QgsCoordinateTransform(
        source_crs,
        geo_crs)

    # Get the clip area in the layer's crs
    transformed_extent = transform.transformBoundingBox(extent)

    geo_extent = [
        transformed_extent.xMinimum(),
        transformed_extent.yMinimum(),
        transformed_extent.xMaximum(),
        transformed_extent.yMaximum()]
    return geo_extent
