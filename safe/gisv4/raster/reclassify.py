# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

Issue https://github.com/inasafe/inasafe/issues/3182

"""

import numpy as np
from osgeo import gdal
from os.path import isfile
from qgis.core import QgsRasterLayer

from safe.common.exceptions import FileNotFoundError, KeywordNotFoundError
from safe.common.utilities import unique_filename, temp_dir
from safe.utilities.i18n import tr
from safe.definitionsv4.processing import reclassify_raster


def reclassify(layer, ranges, callback=None):
    """Reclassify a continuous raster layer.

    This function is a wrapper for the code from
    https://github.com/chiatt/gdal_reclassify

    For instance if you want to reclassify like this table :
            Original Value     |   Class
            - ∞ < val <= 0     |     1
            0   < val <= 0.5   |     2
            0.5 < val <= 5     |     3
            5   < val <= + ∞   |     6

    You need a dictionary :
        ranges = OrderedDict()
        ranges[1] = [None, 0]
        ranges[2] = [0.0, 0.5]
        ranges[3] = [0.5, 5]
        ranges[6] = [5, None]

    :param layer: The raster layer.
    :type layer: QgsRasterLayer

    :param ranges: Classes
    :type ranges: OrderedDict

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The classified raster layer.
    :rtype: QgsRasterLayer

    .. versionadded:: 4.0
    """
    output_layer_name = reclassify_raster['output_layer_name']
    processing_step = reclassify_raster['step_name']

    output_raster = unique_filename(suffix='.tiff', dir=temp_dir())

    driver = gdal.GetDriverByName('GTiff')

    raster_file = gdal.Open(layer.source())
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

    reclassified = QgsRasterLayer(output_raster, output_layer_name)

    # We transfer keywords to the output.
    # We don't need to update keywords as the CRS is dynamic.
    try:
        reclassified.keywords = layer.keywords
        reclassified.keywords['layer_mode'] = 'classified'
    except AttributeError:
        raise KeywordNotFoundError

    return reclassified
