import logging
import os

from osgeo import gdal, ogr, osr

from safe.common.utilities import unique_filename, temp_dir

LOGGER = logging.getLogger('InaSAFE')

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
    package = unique_filename(
        suffix='-inasafe-package', dir=temporary_dir
    )
    print package
    driver = ogr.GetDriverByName('GPKG')
    destination = driver.CreateDataSource(package )
    layer_name = 'hazard'
    layer = destination.CreateLayer(
        layer_name,
        geom_type=ogr.wkbPolygon,
        srs=srs)
    fd = ogr.FieldDefn(name_field, ogr.OFTReal)
    layer.CreateField(fd)
    dst_field = 0

    input_band = input_dataset.GetRasterBand(band)
    gdal.Polygonize(input_band, None, layer, dst_field, [], callback=None)
    destination.Destroy()
    return package
