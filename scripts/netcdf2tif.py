"""Script to read NetCDF raster files, process and store as tif

This requires scientific python
"""

import os
import sys
import numpy
from Scientific.IO.NetCDF import NetCDFFile
from safe.storage.raster import Raster
from safe.storage.utilities import raster_geometry2geotransform


def convert_netcdf2tif(filename, n):
    """Convert netcdf to tif aggregating firsts n bands
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

    print filename, n

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
    t = fid.variables['time'][:]
    inundation_depth = fid.variables['Inundation_Depth'][:]

    T = inundation_depth.shape[0]  # Number of time steps
    M = inundation_depth.shape[1]  # Steps in the y direction
    N = inundation_depth.shape[2]  # Steps in the x direction

    # Compute the max of the first n timesteps
    A = numpy.zeros((M, N), dtype='float')
    for i in range(n):
        B = inundation_depth[i, :, :]
        A = numpy.maximum(A, B)

    geotransform = raster_geometry2geotransform(x, y)
    print 'Geotransform', geotransform

    # Write result to tif file
    R = Raster(data=A,
               projection="""PROJCS["DGN95 / Indonesia TM-3 zone 48.2",
                             GEOGCS["DGN95",
                                 DATUM["Datum_Geodesi_Nasional_1995",
                                     SPHEROID["WGS 84",6378137,298.257223563,
                                         AUTHORITY["EPSG","7030"]],
                                     TOWGS84[0,0,0,0,0,0,0],
                                     AUTHORITY["EPSG","6755"]],
                                 PRIMEM["Greenwich",0,
                                     AUTHORITY["EPSG","8901"]],
                                 UNIT["degree",0.01745329251994328,
                                     AUTHORITY["EPSG","9122"]],
                                 AUTHORITY["EPSG","4755"]],
                             UNIT["metre",1,
                                 AUTHORITY["EPSG","9001"]],
                             PROJECTION["Transverse_Mercator"],
                             PARAMETER["latitude_of_origin",0],
                             PARAMETER["central_meridian",106.5],
                             PARAMETER["scale_factor",0.9999],
                             PARAMETER["false_easting",200000],
                             PARAMETER["false_northing",1500000],
                             AUTHORITY["EPSG","23834"],
                             AXIS["X",EAST],
                             AXIS["Y",NORTH]]""",
               geotransform=geotransform,
               keywords={'category': 'hazard',
                         'subcategory': 'flood',
                         'unit': 'm',
                         'title': ('Hypothetical %d hour flood forecast '
                                   'in Jakarta' % n)})
    R.write_to_file('%s_%d_hours.tif' % (basename, n))
    print 'Success: %d hour forecast written to %s' % (n, R.filename)


def usage():
    s = 'python netcdf2tif.py <filename>.nc <number of hours>'
    return s

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print usage()
    else:
        filename = sys.argv[1]
        N = sys.argv[2]

        convert_netcdf2tif(filename, N)
