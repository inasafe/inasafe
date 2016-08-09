# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank

Contact : etienne@kartoza.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from osgeo import gdal
import numpy as np
from os.path import isfile

from safe.gis.gdal_ogr_tools import polygonize
from safe.common.utilities import temp_dir, unique_filename
from safe.common.exceptions import FileNotFoundError

"""
Note from Etienne : 12/05/16
    * For the first first implementation, we were using this repository :
    https://github.com/chiatt/gdal_reclassify
    * I changed it, the algorithm is much smaller and seems to work, but less
     options (no gap, no no_data):
    http://gis.stackexchange.com/questions/163007/raster-reclassify-using \
    -python-gdal-and-numpy
"""


def reclassify(input_raster, ranges):
    """Reclassify a raster according to some ranges.

    This function is a wrapper for the code from
    https://github.com/chiatt/gdal_reclassify

    For instance if you want to classify like this table :
            Original Value     |   Class
            -∞  < val <= 0     |     1
            0   < val <= 0.5   |     2
            0.5 < val <= 5     |     3
            5   < val <= +∞    |     6

    You need a dictionary :
        ranges = OrderedDict()
        ranges[1] = [None, 0]
        ranges[2] = [0.0, 0.5]
        ranges[3] = [0.5, 5]
        ranges[6] = [5, None]

    .. versionadded:: 3.4

    :param input_raster: The file path to the raster to reclassify.
    :type input_raster: str

    :param ranges: The ranges as a OrderedDict.
    :type ranges: OrderedDict

    :return: The file path to the reclassified raster.
    :rtype: str
    """
    temporary_dir = temp_dir(sub_dir='pre-process')
    output_raster = unique_filename(
        suffix='-reclassified.tiff', dir=temporary_dir)

    driver = gdal.GetDriverByName('GTiff')

    raster_file = gdal.Open(input_raster)
    band = raster_file.GetRasterBand(1)
    source = band.ReadAsArray()
    destination = source.copy()

    for value, interval in ranges.iteritems():
        v_min = interval[0]
        v_max = interval[1]

        if v_min is None:
            destination[np.where(source <= v_max)] = value

        if v_max is None:
            destination[np.where(source > v_min)] = value

        if v_min < v_max:
            destination[np.where((v_min < source) & (source <= v_max))] = value

    # Create the new file.
    output_file = driver.Create(
        output_raster, raster_file.RasterXSize, raster_file.RasterYSize, 1)
    output_file.GetRasterBand(1).WriteArray(destination)

    # CRS
    output_file.SetProjection(raster_file.GetProjection())
    output_file.SetGeoTransform(raster_file.GetGeoTransform())
    output_file.FlushCache()

    del output_file
    if not isfile(output_raster):
        raise FileNotFoundError

    return output_raster


def reclassify_polygonize(input_raster, ranges, name_field='DN'):
    """Reclassify and polygonize a raster according to some ranges.

    .. note:: Delegates to reclassify() and
     safe.gis.gdal_ogr_tools.polygonize()

     .. versionadded:: 3.4

    :param input_raster: The file path to the raster to reclassify.
    :type input_raster: str

    :param ranges: The ranges as a OrderedDict.
    :type ranges: OrderedDict

    :param name_field: The name of the field with the cell value.
    :type name_field: str

    :return: The file path to shapefile.
    :rtype: str
    """
    return polygonize(reclassify(input_raster, ranges), name_field=name_field)
