# coding=utf-8
"""
GDAL/OGR utility tools
"""
__author__ = 'Yewondwossen Assefa <assefay@gmail.com>'
__revision__ = '$Format:%H$'
__date__ = '14/03/2014'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


import logging
import os

import numpy
from osgeo import gdal, ogr, osr

from safe.common.utilities import unique_filename, temp_dir

LOGGER = logging.getLogger('InaSAFE')


# From https://qgis.org/api/classQGis.html#a8da456870e1caec209d8ba7502cceff7
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


def polygonize_thresholds(
        raster_file_name,
        threshold_min=0.0,
        threshold_max=float('inf')):
    """
    Function to polygonize raster. Areas (pixels) with threshold_min <
    pixel_values < threshold_max will be converted to polygons.

    :param raster_file_name:  Raster file name
    :type raster_file_name: string

    :param threshold_min: Value that splits raster to
                    flooded or not flooded.
    :type threshold_min: float

    :param threshold_max: Value that splits raster to
                    flooded or not flooded.
    :type threshold_max: float

    :returns:   Polygon shape file name
    :rtype:     string

    """

    # all values that are in the threshold are set to 1, others are set to 0
    base_name = unique_filename()
    outfile = base_name + '.tif'

    indataset = gdal.Open(raster_file_name, gdal.GA_ReadOnly)
    out_driver = gdal.GetDriverByName('GTiff')
    outdataset = out_driver.Create(
        outfile,
        indataset.RasterXSize,
        indataset.RasterYSize,
        indataset.RasterCount,
        gdal.GDT_Byte)

    gt = indataset.GetGeoTransform()
    if gt is not None and gt != (0.0, 1.0, 0.0, 0.0, 0.0, 1.0):
        outdataset.SetGeoTransform(gt)
    prj = indataset.GetProjectionRef()
    if prj is not None and len(prj) > 0:
        outdataset.SetProjection(prj)

    outNoData = 1
    for iBand in range(1, indataset.RasterCount + 1):
        inband = indataset.GetRasterBand(iBand)
        outband = outdataset.GetRasterBand(iBand)

        for i in range(inband.YSize - 1, -1, -1):
            scanline = inband.ReadAsArray(
                0, i, inband.XSize, 1, inband.XSize, 1)

            if threshold_min >= 0:
                scanline = \
                    numpy.choose(numpy.less(scanline, float(threshold_min)),
                                 (scanline, 0))

            if threshold_max > 0 and threshold_max > threshold_min:
                scanline = \
                    numpy.choose(numpy.greater(scanline, float(threshold_max)),
                                 (scanline, 0))

            scanline = numpy.choose(numpy.not_equal(scanline, 0),
                                    (scanline, outNoData))
            outband.WriteArray(scanline, 0, i)

    # polygonize
    spat_ref = osr.SpatialReference()
    proj = indataset.GetProjectionRef()
    spat_ref.ImportFromWkt(proj)
    drv = ogr.GetDriverByName("ESRI Shapefile")
    base_name = unique_filename()
    out_shape_file = base_name + ".shp"

    dst_ds = drv.CreateDataSource(out_shape_file)
    # ogr_layer_name = 'polygonized'
    ogr_layer_name = os.path.splitext(os.path.split(out_shape_file)[1])[0]
    dst_layer = dst_ds.CreateLayer(ogr_layer_name, spat_ref)
    # fd = ogr.FieldDefn("DN", ogr.OFTInteger )
    fd = ogr.FieldDefn("DN", ogr.OFTReal)
    dst_layer.CreateField(fd)
    dst_field = 0

    # gdal.Polygonize(
    #     outband, outband, dst_layer, dst_field, [], callback=None)
    gdal.Polygonize(outband, None, dst_layer, dst_field, [], callback=None)

    # produce in and out polygon layers
    base_name = unique_filename()
    inside_shape_file = base_name + "_inside.shp"
    inside_layer_name = \
        os.path.splitext(os.path.split(inside_shape_file)[1])[0]

    outside_shape_file = base_name + "_outside.shp"
    outside_layer_name = \
        os.path.splitext(os.path.split(outside_shape_file)[1])[0]

    inside_ds = drv.CreateDataSource(inside_shape_file)
    inside_layer = inside_ds.CreateLayer(inside_layer_name, spat_ref)

    outside_ds = drv.CreateDataSource(outside_shape_file)
    outside_layer = inside_ds.CreateLayer(outside_layer_name, spat_ref)

    for feature in dst_layer:
        value = feature.GetField("DN")
        geom = feature.GetGeometryRef()
        if value == 1:
            new_feature = ogr.Feature(inside_layer.GetLayerDefn())
            new_feature.SetGeometry(geom)
            inside_layer.CreateFeature(new_feature)
        else:
            new_feature = ogr.Feature(outside_layer.GetLayerDefn())
            new_feature.SetGeometry(geom)
            outside_layer.CreateFeature(new_feature)

    inside_ds.Destroy()
    outside_ds.Destroy()
    dst_ds.Destroy()
    return (
        inside_shape_file,
        inside_layer_name,
        outside_shape_file,
        outside_layer_name)


def polygonize(raster_file_name, band=1, name_field='DN'):
    """Polygonize one band from a raster file.

    Note that currently the source pixel band values are read into a signed
    32bit integer buffer, so floating point or complex bands will be implicitly
    truncated before processing.

    .. versionadded:: 3.4

    :param raster_file_name: The raster file path to polygonize.
    :type raster_file_name: str

    :param band: The band to polygonize. Default to 1.
    :type band: int

    :param name_field: The name field to add in the attribute value.
     Default to 'DN'.
    :type name_field: str

    :return: The file path to the shapefile.
    :rtype: str
    """
    input_dataset = gdal.Open(raster_file_name, gdal.GA_ReadOnly)

    srs = osr.SpatialReference()
    srs.ImportFromWkt(input_dataset.GetProjectionRef())

    temporary_dir = temp_dir(sub_dir='pre-process')
    out_shapefile = unique_filename(
        suffix='-polygonized.shp', dir=temporary_dir
    )

    driver = ogr.GetDriverByName("ESRI Shapefile")
    destination = driver.CreateDataSource(out_shapefile)

    layer_name = os.path.splitext(os.path.split(out_shapefile)[1])[0]

    layer = destination.CreateLayer(layer_name, srs)

    fd = ogr.FieldDefn(name_field, ogr.OFTReal)
    layer.CreateField(fd)
    dst_field = 0

    input_band = input_dataset.GetRasterBand(band)
    gdal.Polygonize(input_band, None, layer, dst_field, [], callback=None)
    destination.Destroy()
    return out_shapefile
