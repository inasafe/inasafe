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

from safe.common.utilities import unique_filename

LOGGER = logging.getLogger('InaSAFE')


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

    #all values that are in the threshold are set to 1, others are set to 0
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

    #polygonize
    spat_ref = osr.SpatialReference()
    proj = indataset.GetProjectionRef()
    spat_ref.ImportFromWkt(proj)
    drv = ogr.GetDriverByName("ESRI Shapefile")
    base_name = unique_filename()
    out_shape_file = base_name + ".shp"

    dst_ds = drv.CreateDataSource(out_shape_file)
    #ogr_layer_name = 'polygonized'
    ogr_layer_name = os.path.splitext(os.path.split(out_shape_file)[1])[0]
    dst_layer = dst_ds.CreateLayer(ogr_layer_name, spat_ref)
    #fd = ogr.FieldDefn("DN", ogr.OFTInteger )
    fd = ogr.FieldDefn("DN", ogr.OFTReal)
    dst_layer.CreateField(fd)
    dst_field = 0

    #gdal.Polygonize(outband, outband, dst_layer, dst_field, [], callback=None)
    gdal.Polygonize(outband, None, dst_layer, dst_field, [], callback=None)

    #produce in and out polygon layers
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
