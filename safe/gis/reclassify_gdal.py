# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank

Contact : etienne@kartoza.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import numpy
import operator
from os.path import isfile
from osgeo import gdal
from gdalconst import (
    GDT_Byte,
    GDT_Int16,
    GDT_UInt16,
    GDT_UInt32,
    GDT_Int32,
    GDT_Float32,
    GDT_Float64)

from safe.gis.gdal_ogr_tools import polygonize
from safe.common.utilities import temp_dir, unique_filename
from safe.common.exceptions import FileNotFoundError, ReadLayerError


def _integer_type(array_of_numbers):
    """Get the integer type.

    Note : Copy/paste from https://github.com/chiatt/gdal_reclassify
    """
    low, high = min(array_of_numbers), max(array_of_numbers)
    int_types = [
        (0, 255, numpy.uint8),
        (-128, 127, numpy.int16),
        (0, 65535, numpy.uint16),
        (-32768, 32767, numpy.int16),
        (0, 4294967295, numpy.uint32),
        (-2147483648, 2147483647, numpy.int32),
        (0, 18446744073709551615, numpy.uint64),
        (-9223372036854775808, 9223372036854775807, numpy.int64)
    ]

    int_np_type = None
    for i in int_types:
        if low >= i[0] and high <= i[1]:
            int_np_type = i[2]
            break
    return int_np_type


def _parse_in_classes(conds, pytype):
    """Parse input classes.

    Note : Copy/paste from https://github.com/chiatt/gdal_reclassify
    """
    parsed_conds = []
    for i in conds:
        oplist = ["!", "=", ">", "<"]
        op = ''
        num = ''
        for j in i:
            if j in oplist:
                op += j
            else:
                num += j
        parsed_conds.append((op, pytype(num)))
    return parsed_conds


def _parse_out_classes(number_string, default=None):
    """Parse classes.

    Note : Copy/paste from https://github.com/chiatt/gdal_reclassify
    """
    data_types = {
        numpy.dtype(numpy.uint8): GDT_Byte,
        numpy.dtype(numpy.int8): GDT_Int16,
        numpy.dtype(numpy.uint16): GDT_UInt16,
        numpy.dtype(numpy.int16): GDT_Int16,
        numpy.dtype(numpy.uint32): GDT_UInt32,
        numpy.dtype(numpy.int32): GDT_Int32,
        numpy.dtype(numpy.float32): GDT_Float32,
        numpy.dtype(numpy.int64): GDT_Int32,
        numpy.dtype(numpy.float64): GDT_Float64
    }

    out_classes = [str(i).strip() for i in number_string]
    python_type = int
    for i in out_classes:
        if '.' in i:
            python_type = float
    if default:
        python_type = type(default)
    out_classes_parsed = [python_type(g) for g in out_classes]
    if python_type == float:
        numpy_data_type = numpy.float_
    else:
        numpy_data_type = _integer_type(out_classes_parsed)
    gdal_data_type = data_types[numpy.dtype(numpy_data_type)]

    return numpy_data_type, gdal_data_type, out_classes_parsed


def _parse_default(default_in):
    """Parse default.

    Note : Copy/paste from https://github.com/chiatt/gdal_reclassify
    """
    if '.' in default_in:
        default_out = float(default_in)
    else:
        default_out = int(default_in)
    return default_out


def _reclass_array(np_array, in_classes, out_classes, np_dtype, default):
    """Reclass array.

    Note : Copy/paste from https://github.com/chiatt/gdal_reclassify
    """
    numpy_integer = (
        numpy.uint8,
        numpy.int8,
        numpy.uint16,
        numpy.int16,
        numpy.uint32,
        numpy.int32,
        numpy.uint64)
    if np_dtype not in numpy_integer:
        in_array = np_array.astype(float)
    else:
        in_array = np_array
    op_dict = {
        "<": operator.lt,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
        ">=": operator.ge,
        ">": operator.gt
    }
    try:
        select_result = numpy.select(
            [op_dict[i[0]](in_array, i[1]) for i in in_classes],
            out_classes, default)
        select_result_type_set = select_result.astype(np_dtype)
    finally:
        in_array = None
    return select_result_type_set


def _process_reclassify(
        input_file,
        output_file,
        classes,
        reclasses,
        default,
        nodata,
        output_format,
        compress_type):
    """
    Note : Copy/paste from https://github.com/chiatt/gdal_reclassify
    """
    if default:
        default = _parse_default(default)
    np_dtype, gdal_dtype, out_classes = _parse_out_classes(reclasses, default)
    src_ds = gdal.Open(input_file)
    if src_ds is None:
        raise ReadLayerError

    rows, cols = src_ds.RasterYSize, src_ds.RasterXSize
    transform = src_ds.GetGeoTransform()
    block_size = src_ds.GetRasterBand(1).GetBlockSize()
    proj = src_ds.GetProjection()
    driver = gdal.GetDriverByName(output_format)
    dst_ds = driver.Create(
        output_file, cols, rows, 1, gdal_dtype, options=compress_type)
    # dst_ds = driver.Create(
    # outfile, cols, rows, 1, 6, options = compress_type)
    out_band = dst_ds.GetRasterBand(1)
    x_block_size = block_size[0]
    y_block_size = block_size[1]
    sample = src_ds.ReadAsArray(0, 0, 1, 1)
    pytype = float
    numpy_integer = (
        numpy.uint8,
        numpy.int8,
        numpy.uint16,
        numpy.int16,
        numpy.uint32,
        numpy.int32,
        numpy.uint64)
    if sample.dtype in numpy_integer:
        pytype = int
    in_classes = _parse_in_classes(classes, pytype)
    for i in range(0, rows, y_block_size):
        if i + y_block_size < rows:
            num_rows = y_block_size
        else:
            num_rows = rows - i
        for j in range(0, cols, x_block_size):
            if j + x_block_size < cols:
                num_cols = x_block_size
            else:
                num_cols = cols - j
            block = src_ds.ReadAsArray(j, i, num_cols, num_rows)
            reclassed_block = _reclass_array(
                block, in_classes, out_classes, np_dtype, default)
            out_band.WriteArray(reclassed_block, j, i)
    out_band.FlushCache()
    dst_ds.SetGeoTransform(transform)
    if nodata in ["True", "true", "t", "T", "yes", "Yes", "Y", "y"]:
        out_band.SetNoDataValue(default)

    out_band.GetStatistics(0, 1)
    dst_ds.SetProjection(proj)


def _classes_to_string(ranges):
    """Function to transform the ranges dictionary as comma-delimited string.

    :param ranges: The ranges.
    :type ranges: OrderedDict

    :return: List(output classes, input classes).
    :rtype: list
    """
    output_ranges = []
    for interval in ranges.itervalues():
        if interval[0] is None:
            output_ranges.append('<%s' % interval[1])
        elif interval[0] == interval[1]:
            output_ranges.append('==%s' % interval[0])
        elif interval[0] < interval[1]:
            output_ranges.append('<=%s' % interval[1])
        elif interval[1] is None:
            output_ranges.append('>%s' % interval[0])

    return ranges.keys(), output_ranges


def reclassify(input_raster, ranges, no_data=0):
    """Reclassify a raster according to some ranges.

    This function is a wrapper for the code from
    https://github.com/chiatt/gdal_reclassify

    For instance if you want to classify like this table :
        Original Value    | Class
            0             |   1
            0.01 - 0.2    |   2
            0.2 - 2       |   3
            2.1 - 5       |   4
            5.1 - 10      |   5
            10 - 99       |   6

    You need a dictionary :
        ranges = OrderedDict()
        ranges[1] = [None, 0]
        ranges[2] = [0.01, 0.2]
        ranges[3] = [0.2, 2]
        ranges[4] = [2.1, 5]
        ranges[5] = [5.1, 10]
        ranges[6] = [10, None]

    You shouldn't use 0 for the class, as it's the no data value by default.

    .. versionadded:: 3.4

    :param input_raster: The file path to the raster to reclassify.
    :type input_raster: str

    :param ranges: The ranges as a OrderedDict.
    :type ranges: OrderedDict

    :param no_data: The no data value. Default to 0 for the output.
    :type no_data: int

    :return: The file path to the reclassified raster.
    :rtype: str
    """
    temporary_dir = temp_dir(sub_dir='pre-process')
    output_raster = unique_filename(
        suffix='-reclassified.tiff', dir=temporary_dir)

    output_classes, input_classes = _classes_to_string(ranges)
    value = 'True'
    output_format = 'GTiff'
    compression = ['COMPRESS=NONE']
    _process_reclassify(
        input_raster,
        output_raster,
        input_classes,
        output_classes,
        no_data,
        value,
        output_format,
        compression)

    if not isfile(output_raster):
        raise FileNotFoundError

    return output_raster


def reclassify_polygonize(input_raster, ranges):
    """Reclassify and polygonize a raster according to some ranges.

    .. note:: Delegates to reclassify() and
     safe.gis.gdal_ogr_tools.polygonize()

     .. versionadded:: 3.4

    :param input_raster: The file path to the raster to reclassify.
    :type input_raster: str

    :param ranges: The ranges as a OrderedDict.
    :type ranges: OrderedDict

    :return: The file path to shapefile.
    :rtype: str
    """
    return polygonize(reclassify(input_raster, ranges))
