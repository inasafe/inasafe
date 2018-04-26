# coding=utf-8

"""Reclassify a raster layer."""

from os.path import isfile

import numpy as np
from osgeo import gdal
from qgis.core import QgsRasterLayer

from safe.common.exceptions import (
    FileNotFoundError, InvalidKeywordsForProcessingAlgorithm)
from safe.common.utilities import unique_filename, temp_dir
from safe.definitions.constants import no_data_value
from safe.definitions.processing_steps import reclassify_raster_steps
from safe.definitions.utilities import definition
from safe.gis.sanity_check import check_layer
from safe.utilities.metadata import (
    active_thresholds_value_maps, active_classification)
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def reclassify(layer, exposure_key=None, overwrite_input=False):
    """Reclassify a continuous raster layer.

    Issue https://github.com/inasafe/inasafe/issues/3182


    This function is a wrapper for the code from
    https://github.com/chiatt/gdal_reclassify

    For instance if you want to reclassify like this table :
            Original Value     |   Class
            - ∞ < val <= 0     |     1
            0   < val <= 0.5   |     2
            0.5 < val <= 5     |     3
            5   < val <  + ∞   |     6

    You need a dictionary :
        ranges = OrderedDict()
        ranges[1] = [None, 0]
        ranges[2] = [0.0, 0.5]
        ranges[3] = [0.5, 5]
        ranges[6] = [5, None]

    :param layer: The raster layer.
    :type layer: QgsRasterLayer

    :param overwrite_input: Option for the output layer. True will overwrite
        the input layer. False will create a temporary layer.
    :type overwrite_input: bool

    :param exposure_key: The exposure key.
    :type exposure_key: str

    :return: The classified raster layer.
    :rtype: QgsRasterLayer

    .. versionadded:: 4.0
    """
    output_layer_name = reclassify_raster_steps['output_layer_name']
    output_layer_name = output_layer_name % layer.keywords['layer_purpose']

    if exposure_key:
        classification_key = active_classification(
            layer.keywords, exposure_key)
        thresholds = active_thresholds_value_maps(layer.keywords, exposure_key)
        layer.keywords['thresholds'] = thresholds
        layer.keywords['classification'] = classification_key
    else:
        classification_key = layer.keywords.get('classification')
        thresholds = layer.keywords.get('thresholds')
    if not thresholds:
        raise InvalidKeywordsForProcessingAlgorithm(
            'thresholds are missing from the layer %s'
            % layer.keywords['layer_purpose'])

    if not classification_key:
        raise InvalidKeywordsForProcessingAlgorithm(
            'classification is missing from the layer %s'
            % layer.keywords['layer_purpose'])

    ranges = {}
    value_map = {}
    hazard_classes = definition(classification_key)['classes']
    for hazard_class in hazard_classes:
        ranges[hazard_class['value']] = thresholds[hazard_class['key']]
        value_map[hazard_class['key']] = [hazard_class['value']]

    if overwrite_input:
        output_raster = layer.source()
    else:
        output_raster = unique_filename(suffix='.tiff', dir=temp_dir())

    driver = gdal.GetDriverByName('GTiff')

    raster_file = gdal.Open(layer.source())
    band = raster_file.GetRasterBand(1)
    no_data = band.GetNoDataValue()
    source = band.ReadAsArray()
    destination = source.copy()

    for value, interval in list(ranges.items()):
        v_min = interval[0]
        v_max = interval[1]

        if v_min is None:
            destination[np.where(source <= v_max)] = value
        elif v_max is None:
            destination[np.where(source > v_min)] = value
        elif v_min < v_max:
            destination[np.where((v_min < source) & (source <= v_max))] = value

    # Tag no data cells
    destination[np.where(source == no_data)] = no_data_value

    # Create the new file.
    output_file = driver.Create(
        output_raster, raster_file.RasterXSize, raster_file.RasterYSize, 1)
    output_file.GetRasterBand(1).WriteArray(destination)
    output_file.GetRasterBand(1).SetNoDataValue(no_data_value)

    # CRS
    output_file.SetProjection(raster_file.GetProjection())
    output_file.SetGeoTransform(raster_file.GetGeoTransform())
    output_file.FlushCache()

    del output_file

    if not isfile(output_raster):
        raise FileNotFoundError

    reclassified = QgsRasterLayer(output_raster, output_layer_name)

    # We transfer keywords to the output.
    reclassified.keywords = layer.keywords.copy()
    reclassified.keywords['layer_mode'] = 'classified'

    value_map = {}

    hazard_classes = definition(classification_key)['classes']
    for hazard_class in reversed(hazard_classes):
        value_map[hazard_class['key']] = [hazard_class['value']]

    reclassified.keywords['value_map'] = value_map
    reclassified.keywords['title'] = output_layer_name

    check_layer(reclassified)
    return reclassified
