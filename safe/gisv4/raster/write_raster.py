
import numpy
from osgeo import gdal


def array_to_raster_raw(array, dst_filename, top_left, pixel_size, wkt_projection):
    """Save a raster TIF file from a numpy array.

    :param array: array with data
    :param dst_filename: where to store the raster
    :param top_left: tuple (x,y) of top-left point in map units
    :param pixel_size: size of pixel in map units
    :param wkt_projection: WKT string of the raster's CRS
    """
    raster_size = array.shape[1], array.shape[0]

    driver = gdal.GetDriverByName('GTiff')

    dataset = driver.Create(
        dst_filename,
        raster_size[0],
        raster_size[1],
        1,
        gdal.GDT_Float32, )

    dataset.SetGeoTransform((top_left[0], pixel_size, 0,
                             top_left[1], 0, -pixel_size))
    dataset.SetProjection(wkt_projection)
    dataset.GetRasterBand(1).WriteArray(array)
    dataset.FlushCache()  # Write to disk.
    return dataset


def array_to_raster(array, dst_filename, other_layer):
    """Save a raster TIF file from a numpy array.
    The geo metadata will be the same as the other given QGIS raster layer."""

    provider = other_layer.dataProvider()
    assert provider.xSize() == array.shape[1] and provider.ySize() == array.shape[0]
    top_left = (other_layer.extent().xMinimum(),
                other_layer.extent().yMaximum())
    pixel_size = other_layer.extent().width() / provider.xSize()
    wkt_projection = str(other_layer.crs().toWkt())
    return array_to_raster_raw(array, dst_filename, top_left, pixel_size, wkt_projection)


def make_array(width, height):
    """Create a numpy array we can later use in array_to_raster() method."""
    # numpy indexing order is rows, cols
    return numpy.zeros((height, width))
