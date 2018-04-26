# coding=utf-8
"""Create contour from shakemap raster layer."""

import logging
import os
import shutil
from datetime import datetime

import numpy as np
from osgeo import gdal, ogr
from osgeo.gdalconst import GA_ReadOnly
from qgis.core import QgsVectorLayer, QgsFeatureRequest

from safe.common.exceptions import (
    ContourCreationError,
    InvalidLayerError,
    FileNotFoundError,
)
from safe.common.utilities import romanise, unique_filename, temp_dir
from safe.definitions.constants import NUMPY_SMOOTHING
from safe.definitions.fields import (
    contour_fields,
    contour_x_field,
    contour_y_field,
    contour_colour_field,
    contour_roman_field,
    contour_halign_field,
    contour_valign_field,
    contour_length_field,
    contour_mmi_field,

)
from safe.definitions.layer_geometry import layer_geometry_line
from safe.definitions.layer_modes import layer_mode_classified
from safe.definitions.layer_purposes import layer_purpose_earthquake_contour
from safe.gis.vector.tools import (
    create_ogr_field_from_definition, field_index_from_definition)
from safe.utilities.i18n import tr
from safe.utilities.metadata import write_iso19115_metadata
from safe.utilities.resources import resources_path
from safe.utilities.styling import mmi_colour

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


def gaussian_kernel(sigma, truncate=4.0):
    """Return Gaussian that truncates at the given number of std deviations.

    Adapted from https://github.com/nicjhan/gaussian-filter
    """

    sigma = float(sigma)
    radius = int(truncate * sigma + 0.5)

    x, y = np.mgrid[-radius:radius + 1, -radius:radius + 1]
    sigma = sigma ** 2

    k = 2 * np.exp(-0.5 * (x ** 2 + y ** 2) / sigma)
    k = k / np.sum(k)

    return k


def tile_and_reflect(input):
    """Make 3x3 tiled array.

    Central area is 'input', surrounding areas are reflected.

    Adapted from https://github.com/nicjhan/gaussian-filter
    """

    tiled_input = np.tile(input, (3, 3))

    rows = input.shape[0]
    cols = input.shape[1]

    # Now we have a 3x3 tiles - do the reflections.
    # All those on the sides need to be flipped left-to-right.
    for i in range(3):
        # Left hand side tiles
        tiled_input[i * rows:(i + 1) * rows, 0:cols] = \
            np.fliplr(tiled_input[i * rows:(i + 1) * rows, 0:cols])
        # Right hand side tiles
        tiled_input[i * rows:(i + 1) * rows, -cols:] = \
            np.fliplr(tiled_input[i * rows:(i + 1) * rows, -cols:])

    # All those on the top and bottom need to be flipped up-to-down
    for i in range(3):
        # Top row
        tiled_input[0:rows, i * cols:(i + 1) * cols] = \
            np.flipud(tiled_input[0:rows, i * cols:(i + 1) * cols])
        # Bottom row
        tiled_input[-rows:, i * cols:(i + 1) * cols] = \
            np.flipud(tiled_input[-rows:, i * cols:(i + 1) * cols])

    # The central array should be unchanged.
    assert (np.array_equal(input, tiled_input[rows:2 * rows, cols:2 * cols]))

    # All sides of the middle array should be the same as those bordering them.
    # Check this starting at the top and going around clockwise. This can be
    # visually checked by plotting the 'tiled_input' array.
    assert (np.array_equal(input[0, :], tiled_input[rows - 1, cols:2 * cols]))
    assert (np.array_equal(input[:, -1], tiled_input[rows:2 * rows, 2 * cols]))
    assert (np.array_equal(input[-1, :], tiled_input[2 * rows, cols:2 * cols]))
    assert (np.array_equal(input[:, 0], tiled_input[rows:2 * rows, cols - 1]))

    return tiled_input


def convolve(input, weights, mask=None, slow=False):
    """2 dimensional convolution.

    This is a Python implementation of what will be written in Fortran.

    Borders are handled with reflection.

    Masking is supported in the following way:
        * Masked points are skipped.
        * Parts of the input which are masked have weight 0 in the kernel.
        * Since the kernel as a whole needs to have value 1, the weights of the
          masked parts of the kernel are evenly distributed over the non-masked
          parts.

    Adapted from https://github.com/nicjhan/gaussian-filter
    """

    assert (len(input.shape) == 2)
    assert (len(weights.shape) == 2)

    # Only one reflection is done on each side so the weights array cannot be
    # bigger than width/height of input +1.
    assert (weights.shape[0] < input.shape[0] + 1)
    assert (weights.shape[1] < input.shape[1] + 1)

    if mask is not None:
        # The slow convolve does not support masking.
        assert (not slow)
        assert (input.shape == mask.shape)
        tiled_mask = tile_and_reflect(mask)

    output = np.copy(input)
    tiled_input = tile_and_reflect(input)

    rows = input.shape[0]
    cols = input.shape[1]
    # Stands for half weights row.
    hw_row = weights.shape[0] / 2
    hw_col = weights.shape[1] / 2

    # Now do convolution on central array.
    # Iterate over tiled_input.
    for i, io in zip(list(range(rows, rows * 2)), list(range(rows))):
        for j, jo in zip(list(range(cols, cols * 2)), list(range(cols))):
            # The current central pixel is at (i, j)

            # Skip masked points.
            if mask is not None and tiled_mask[i, j]:
                continue

            average = 0.0
            if slow:
                # Iterate over weights/kernel.
                for k in range(weights.shape[0]):
                    for l in range(weights.shape[1]):
                        # Get coordinates of tiled_input array that match given
                        # weights
                        m = i + k - hw_row
                        n = j + l - hw_col

                        average += tiled_input[m, n] * weights[k, l]
            else:
                # Find the part of the tiled_input array that overlaps with the
                # weights array.
                overlapping = tiled_input[
                    i - hw_row:i + hw_row,
                    j - hw_col:j + hw_col]
                assert (overlapping.shape == weights.shape)

                # If any of 'overlapping' is masked then set the corresponding
                # points in the weights matrix to 0 and redistribute these to
                # non-masked points.
                if mask is not None:
                    overlapping_mask = tiled_mask[
                        i - hw_row:i + hw_row,
                        j - hw_col:j + hw_col]
                    assert (overlapping_mask.shape == weights.shape)

                    # Total value and number of weights clobbered by the mask.
                    clobber_total = np.sum(weights[overlapping_mask])
                    remaining_num = np.sum(np.logical_not(overlapping_mask))
                    # This is impossible since at least i, j is not masked.
                    assert (remaining_num > 0)
                    correction = clobber_total / remaining_num

                    # It is OK if nothing is masked - the weights will not be
                    #  changed.
                    if correction == 0:
                        assert (not overlapping_mask.any())

                    # Redistribute to non-masked points.
                    tmp_weights = np.copy(weights)
                    tmp_weights[overlapping_mask] = 0.0
                    tmp_weights[np.where(tmp_weights != 0)] += correction

                    # Should be very close to 1. May not be exact due to
                    # rounding.
                    assert (abs(np.sum(tmp_weights) - 1) < 1e-15)

                else:
                    tmp_weights = weights

                merged = tmp_weights[:] * overlapping
                average = np.sum(merged)

            # Set new output value.
            output[io, jo] = average

    return output


def create_smooth_contour(
        shakemap_layer,
        output_file_path='',
        active_band=1,
        smoothing_method=NUMPY_SMOOTHING,
        smoothing_sigma=0.9):
    """Create contour from a shake map layer by using smoothing method.

    :param shakemap_layer: The shake map raster layer.
    :type shakemap_layer: QgsRasterLayer

    :param active_band: The band which the data located, default to 1.
    :type active_band: int

    :param smoothing_method: The smoothing method that wanted to be used.
    :type smoothing_method: NONE_SMOOTHING, NUMPY_SMOOTHING, SCIPY_SMOOTHING

    :param smooth_sigma: parameter for gaussian filter used in smoothing
        function.
    :type smooth_sigma: float

    :returns: The contour of the shake map layer path.
    :rtype: basestring
    """
    timestamp = datetime.now()
    temp_smoothed_shakemap_path = unique_filename(
        prefix='temp-shake-map' + timestamp.strftime('%Y%m%d-%H%M%S'),
        suffix='.tif',
        dir=temp_dir('temp'))

    temp_smoothed_shakemap_path = smooth_shakemap(
        shakemap_layer.source(),
        output_file_path=temp_smoothed_shakemap_path,
        active_band=active_band,
        smoothing_method=smoothing_method,
        smoothing_sigma=smoothing_sigma
    )

    return shakemap_contour(
        temp_smoothed_shakemap_path,
        output_file_path=output_file_path,
        active_band=active_band
    )


def smooth_shakemap(
        shakemap_layer_path,
        output_file_path='',
        active_band=1,
        smoothing_method=NUMPY_SMOOTHING,
        smoothing_sigma=0.9):
    """Make a smoother shakemap layer from a shake map.

    :param shakemap_layer_path: The shake map raster layer path.
    :type shakemap_layer_path: basestring

    :param active_band: The band which the data located, default to 1.
    :type active_band: int

    :param smoothing_method: The smoothing method that wanted to be used.
    :type smoothing_method: NONE_SMOOTHING, NUMPY_SMOOTHING, SCIPY_SMOOTHING

    :param smooth_sigma: parameter for gaussian filter used in smoothing
        function.
    :type smooth_sigma: float

    :returns: The contour of the shake map layer.
    :rtype: QgsRasterLayer
    """
    # Set output path
    if not output_file_path:
        output_file_path = unique_filename(suffix='.tiff', dir=temp_dir())

    # convert to numpy
    shakemap_file = gdal.Open(shakemap_layer_path)
    shakemap_array = np.array(
        shakemap_file.GetRasterBand(active_band).ReadAsArray())

    # do smoothing
    if smoothing_method == NUMPY_SMOOTHING:
        smoothed_array = convolve(shakemap_array, gaussian_kernel(
            smoothing_sigma))
    else:
        smoothed_array = shakemap_array

    # Create smoothed shakemap raster layer
    driver = gdal.GetDriverByName('GTiff')
    smoothed_shakemap_file = driver.Create(
        output_file_path,
        shakemap_file.RasterXSize,
        shakemap_file.RasterYSize,
        1,
        gdal.GDT_Float32  # Important, since the default is integer
    )
    smoothed_shakemap_file.GetRasterBand(1).WriteArray(smoothed_array)

    # CRS
    smoothed_shakemap_file.SetProjection(shakemap_file.GetProjection())
    smoothed_shakemap_file.SetGeoTransform(shakemap_file.GetGeoTransform())
    smoothed_shakemap_file.FlushCache()

    del smoothed_shakemap_file

    if not os.path.isfile(output_file_path):
        raise FileNotFoundError(tr(
            'The smoothed shakemap is not created. It should be at '
            '{output_file_path}'.format(output_file_path=output_file_path)))

    return output_file_path


def shakemap_contour(shakemap_layer_path, output_file_path='', active_band=1):
    """Creating contour from a shakemap layer.

    :param shakemap_layer_path: The shake map raster layer path.
    :type shakemap_layer_path: basestring

    :param output_file_path: The path where the contour will be saved.
    :type output_file_path: basestring

    :param active_band: The band which the data located, default to 1.
    :type active_band: int

    :returns: The contour of the shake map layer path.
    :rtype: basestring
    """
    # Set output path
    if not output_file_path:
        output_file_path = unique_filename(suffix='.shp', dir=temp_dir())

    output_directory = os.path.dirname(output_file_path)
    output_file_name = os.path.basename(output_file_path)
    output_base_name = os.path.splitext(output_file_name)[0]

    # Based largely on
    # http://svn.osgeo.org/gdal/trunk/autotest/alg/contour.py
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ogr_dataset = driver.CreateDataSource(output_file_path)
    if ogr_dataset is None:
        # Probably the file existed and could not be overriden
        raise ContourCreationError(
            'Could not create datasource for:\n%s. Check that the file '
            'does not already exist and that you do not have file system '
            'permissions issues' % output_file_path)
    layer = ogr_dataset.CreateLayer('contour')

    for contour_field in contour_fields:
        field_definition = create_ogr_field_from_definition(contour_field)
        layer.CreateField(field_definition)

    shakemap_data = gdal.Open(shakemap_layer_path, GA_ReadOnly)
    # see http://gdal.org/java/org/gdal/gdal/gdal.html for these options
    contour_interval = 0.5
    contour_base = 0
    fixed_level_list = []
    use_no_data_flag = 0
    no_data_value = -9999
    id_field = 0  # first field defined above
    elevation_field = 1  # second (MMI) field defined above
    try:
        gdal.ContourGenerate(
            shakemap_data.GetRasterBand(active_band),
            contour_interval,
            contour_base,
            fixed_level_list,
            use_no_data_flag,
            no_data_value,
            layer,
            id_field,
            elevation_field)
    except Exception as e:
        LOGGER.exception('Contour creation failed')
        raise ContourCreationError(str(e))
    finally:
        ogr_dataset.Release()

    # Copy over the standard .prj file since ContourGenerate does not
    # create a projection definition
    projection_path = os.path.join(
        output_directory, output_base_name + '.prj')
    source_projection_path = resources_path(
        'converter_data', 'mmi-contours.prj')
    shutil.copyfile(source_projection_path, projection_path)

    # Lastly copy over the standard qml (QGIS Style file)
    qml_path = os.path.join(
        output_directory, output_base_name + '.qml')
    source_qml_path = resources_path('converter_data', 'mmi-contours.qml')
    shutil.copyfile(source_qml_path, qml_path)

    # Create metadata file
    create_contour_metadata(output_file_path)

    # Now update the additional columns - X,Y, ROMAN and RGB
    try:
        set_contour_properties(output_file_path)
    except InvalidLayerError:
        raise

    del shakemap_data

    return output_file_path


def set_contour_properties(contour_file_path):
    """Set the X, Y, RGB, ROMAN attributes of the contour layer.

    :param contour_file_path: Path of the contour layer.
    :type contour_file_path: str

    :raise: InvalidLayerError if anything is amiss with the layer.
    """
    LOGGER.debug(
        'Set_contour_properties requested for %s.' % contour_file_path)
    layer = QgsVectorLayer(contour_file_path, 'mmi-contours', "ogr")
    if not layer.isValid():
        raise InvalidLayerError(contour_file_path)

    layer.startEditing()
    # Now loop through the db adding selected features to mem layer
    request = QgsFeatureRequest()

    for feature in layer.getFeatures(request):
        if not feature.isValid():
            LOGGER.debug('Skipping feature')
            continue
        # Work out x and y
        line = feature.geometry().asPolyline()
        y = line[0].y()

        x_max = line[0].x()
        x_min = x_max
        for point in line:
            if point.y() < y:
                y = point.y()
            x = point.x()
            if x < x_min:
                x_min = x
            if x > x_max:
                x_max = x
        x = x_min + ((x_max - x_min) / 2)

        # Get length
        length = feature.geometry().length()

        mmi_value = float(feature[contour_mmi_field['field_name']])
        # We only want labels on the whole number contours
        if mmi_value != round(mmi_value):
            roman = ''
        else:
            roman = romanise(mmi_value)

        # RGB from http://en.wikipedia.org/wiki/Mercalli_intensity_scale
        rgb = mmi_colour(mmi_value)

        # Now update the feature
        feature_id = feature.id()
        layer.changeAttributeValue(
            feature_id, field_index_from_definition(layer, contour_x_field), x)
        layer.changeAttributeValue(
            feature_id, field_index_from_definition(layer, contour_y_field), y)
        layer.changeAttributeValue(
            feature_id,
            field_index_from_definition(layer, contour_colour_field), rgb)
        layer.changeAttributeValue(
            feature_id,
            field_index_from_definition(layer, contour_roman_field), roman)
        layer.changeAttributeValue(
            feature_id,
            field_index_from_definition(layer, contour_halign_field), 'Center')
        layer.changeAttributeValue(
            feature_id,
            field_index_from_definition(layer, contour_valign_field), 'HALF')
        layer.changeAttributeValue(
            feature_id,
            field_index_from_definition(layer, contour_length_field), length)

    layer.commitChanges()


def create_contour_metadata(contour_path):
    """Create metadata file for contour layer.

    :param contour_path: Path where the contour is located.
    :type contour_path: basestring
    """
    metadata = {
        'title': tr('Earthquake Contour'),
        'layer_purpose': layer_purpose_earthquake_contour['key'],
        'layer_geometry': layer_geometry_line['key'],
        'layer_mode': layer_mode_classified['key'],
        'inasafe_fields': {}
    }

    for contour_field in contour_fields:
        metadata['inasafe_fields'][contour_field['key']] = contour_field[
            'field_name']

    write_iso19115_metadata(contour_path, metadata)
