"""**Class Converter**

Provide function for convert a file type to another Raster or Vector.
"""

import numpy
import os
from Scientific.IO.NetCDF import NetCDFFile

from safe.common.utilities import unique_filename

from raster import Raster
from utilities import raster_geometry2geotransform


def convert_netcdf2tif(filename, n, verbose=True):
    """Convert netcdf to tif aggregating first n bands

    Args
        * filename: NetCDF multiband raster with extension .nc
        * n: Positive integer determining how many bands to use
        * verbose : if true, print all information

    Returns
        * Raster file in tif format. Each pixel will be the maximum
          of that pixel in the first n bands in the input file.

    Note : Adapted from scripts/netcdf2tif.py

    """

    if not isinstance(filename, basestring):
        msg = 'Argument filename should be a string. I got %s' % filename
        raise RuntimeError(msg)

    basename, ext = os.path.splitext(filename)
    msg = ('Expected NetCDF file with extension .nc - '
           'Instead I got %s' % filename)
    if ext != '.nc':
        raise RuntimeError(msg)

    try:
        n = int(n)
    except:
        msg = 'Argument N should be an integer. I got %s' % n
        raise RuntimeError(msg)

    # print filename, n

    # Read NetCDF file
    fid = NetCDFFile(filename)
    if verbose:
        dimensions = fid.dimensions.keys()
        variables = fid.variables.keys()

        title = getattr(fid, 'title')
        institution = getattr(fid, 'institution')
        source = getattr(fid, 'source')
        history = getattr(fid, 'history')
        references = getattr(fid, 'references')
        conventions = getattr(fid, 'Conventions')
        coordinate_system = getattr(fid, 'coordinate_system')

        print 'Read from %s' % filename
        print 'Title: %s' % title
        print 'Institution: %s' % institution
        print 'Source: %s' % source
        print 'History: %s' % history
        print 'References: %s' % references
        print 'Conventions: %s' % conventions
        print 'Coordinate system: %s' % coordinate_system

        print 'Dimensions: %s' % dimensions
        print 'Variables:  %s' % variables

    # Get data
    x = fid.variables['x'][:]
    y = fid.variables['y'][:]
    _ = fid.variables['time'][:]
    inundation_depth = fid.variables['Inundation_Depth'][:]

    _ = inundation_depth.shape[0]  # Number of time steps
    M = inundation_depth.shape[1]  # Steps in the y direction
    N = inundation_depth.shape[2]  # Steps in the x direction

    # Compute the max of the first n timesteps
    A = numpy.zeros((M, N), dtype='float')
    for i in range(n):
        B = inundation_depth[i, :, :]
        A = numpy.maximum(A, B)

    geotransform = raster_geometry2geotransform(x, y)
    if verbose:
        print 'Geotransform', geotransform

    # Write result to tif file
    # NOTE: This assumes a default projection (WGS 84, geographic)
    date = os.path.split(basename)[-1].split('_')[0]
    if verbose:
        print 'date', date
    R = Raster(data=A,
        geotransform=geotransform,
        keywords={'category': 'hazard',
                  'subcategory': 'flood',
                  'unit': 'm',
                  'title': ('%d hour flood forecast grid '
                            'in Jakarta at %s' % (n, date))})

    tif_filename = unique_filename(suffix='.tif')
    R.write_to_file(tif_filename)

    if verbose:
        print 'Success: %d hour forecast written to %s' % (n, R.filename)
    return tif_filename
