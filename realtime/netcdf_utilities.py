__author__ = 'nielso'

import os
import numpy

# This module requires the package: python-scientific
# To query netcdf files with ncdump also install netcdf-bin
# The package libnetcdf-dev is also required but is automatically
# installed as a dependency on python-scientific
from Scientific.IO.NetCDF import NetCDFFile

from safe.storage.raster import Raster
from safe.storage.utilities import raster_geometry2geotransform


# FIXME (Ole): Write test using
# inasafe_data/test/201211120500_Jakarta_200m_Sobek_Forecast_CCAM.nc
def convert_netcdf2tif(filename, n, verbose=False, output_dir=None):

    """Convert netcdf to tif aggregating first n bands

    Args
        * filename: NetCDF multiband raster with extension .nc
        * n: Positive integer determining how many bands to use
        * verbose: Boolean flag controlling whether diagnostics
          will be printed to screen. This is useful when run from
          a command line script.

    Returns
        * Raster file in tif format. Each pixel will be the maximum
          of that pixel in the first n bands in the input file.

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

    if verbose:
        print filename, n, 'hours'

    # Read NetCDF file
    fid = NetCDFFile(filename)
    dimensions = fid.dimensions.keys()
    variables = fid.variables.keys()

    title = getattr(fid, 'title')
    institution = getattr(fid, 'institution')
    source = getattr(fid, 'source')
    history = getattr(fid, 'history')
    references = getattr(fid, 'references')
    conventions = getattr(fid, 'Conventions')
    coordinate_system = getattr(fid, 'coordinate_system')

    if verbose:
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
    # t = fid.variables['time'][:]
    inundation_depth = fid.variables['Inundation_Depth'][:]

    T = inundation_depth.shape[0]  # Number of time steps
    M = inundation_depth.shape[1]  # Steps in the y direction
    N = inundation_depth.shape[2]  # Steps in the x direction

    if n > T:
        msg = ('You requested %i hours prediction, but the '
               'forecast only contains %i hours' % (n, T))
        raise RuntimeError(msg)

    # Compute the max of the first n timesteps
    A = numpy.zeros((M, N), dtype='float')
    for i in range(n):
        B = inundation_depth[i, :, :]
        A = numpy.maximum(A, B)

        # Calculate overall maximal value
        total_max = numpy.max(A[:])
        #print i, numpy.max(B[:]), total_max

    geotransform = raster_geometry2geotransform(x, y)

    # Write result to tif file
    # NOTE: This assumes a default projection (WGS 84, geographic)
    date = os.path.split(basename)[-1].split('_')[0]

    if verbose:
        print 'Overall max depth over %i hours: %.2f m' % (n, total_max)
        print 'Geotransform', geotransform
        print 'date', date

    # Flip array upside down as it comes with rows ordered from south to north
    A = numpy.flipud(A)

    R = Raster(data=A,
               geotransform=geotransform,
               keywords={'category': 'hazard',
                         'subcategory': 'flood',
                         'unit': 'm',
                         'title': ('%d hour flood forecast grid '
                                   'in Jakarta at %s' % (n, date))})

    tif_filename = '%s_%d_hours_max_%.2f.tif' % (basename, n, total_max)
    if output_dir is not None:
        subdir_name = os.path.splitext(os.path.basename(tif_filename))[0]
        shapefile_dir = os.path.join(output_dir, subdir_name)
        if not os.path.isdir(shapefile_dir):
            os.mkdir(shapefile_dir)
        tif_filename = os.path.join(shapefile_dir, subdir_name + '.tif')

    R.write_to_file(tif_filename)

    if verbose:
        print 'Success: %d hour forecast written to %s' % (n, R.filename)

    return tif_filename
