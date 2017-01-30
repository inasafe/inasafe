# coding=utf-8

import numpy
from osgeo import gdal
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def array_to_raster_raw(
        array, destination_filename, top_left, pixel_size, wkt_projection):
    """Save a raster TIF file from a numpy array using GDAL.

    :param array: Array with data.
    :type array: numpy.array

    :param destination_filename: where to store the raster.
    :type destination_filename: basestring

    :param top_left: tuple (x,y) of top-left point in map units.
    :type top_left: tuple

    :param pixel_size: size of pixel in map units.
    :type pixel_size: int

    :param wkt_projection: WKT string of the raster's CRS.
    :type wkt_projection: basestring

    :return: The new GDAL dataset.
    :rtype: GDALDataset
    """
    raster_size = array.shape[1], array.shape[0]

    driver = gdal.GetDriverByName('GTiff')

    dataset = driver.Create(
        destination_filename,
        raster_size[0],
        raster_size[1],
        1,
        gdal.GDT_Float32, )

    dataset.SetGeoTransform(
        (top_left[0], pixel_size, 0, top_left[1], 0, -pixel_size))
    dataset.SetProjection(wkt_projection)
    dataset.GetRasterBand(1).WriteArray(array)
    dataset.FlushCache()  # Write to disk.
    return dataset


@profile
def array_to_raster(array, destination_filename, other_layer):
    """Save a raster TIF file from a numpy array.

    The geo metadata will be the same as the other given QGIS raster layer.

    :param array: The array to write.
    :type array: numpy.array

    :param destination_filename: The destination file name.
    :type destination_filename: basestring

    :param other_layer: The other layer.
    :type other_layer: QgsRasterLayer
    """
    provider = other_layer.dataProvider()
    assert provider.xSize() == array.shape[1]
    assert provider.ySize() == array.shape[0]
    top_left = (
        other_layer.extent().xMinimum(), other_layer.extent().yMaximum())
    pixel_size = other_layer.extent().width() / provider.xSize()
    wkt_projection = str(other_layer.crs().toWkt())
    raster = array_to_raster_raw(
        array, destination_filename, top_left, pixel_size, wkt_projection)
    return raster


def make_array(width, height):
    """Create a numpy array we can later use in array_to_raster() method.

    :param width: The width.
    :type width: int

    :param height: The height.
    :type height: int

    :return: The empty numpy array with zeros.
    :rtype: numpy.array
    """
    # numpy indexing order is rows, cols
    return numpy.zeros((height, width))
