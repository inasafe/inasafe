"""Script to read NetCDF raster files, process and store as tif

This requires scientific python
"""

import os
import sys
import numpy
import argparse

# This module requires the package: python-scientific
# To query netcdf files with ncdump also install netcdf-bin
# The package libnetcdf-dev is also required but is automatically
# installed as a dependency on python-scientific
from Scientific.IO.NetCDF import NetCDFFile

from safe.storage.raster import Raster
from safe.storage.vector import Vector
from safe.storage.utilities import raster_geometry2geotransform
from safe.storage.core import read_layer
from safe.engine.interpolation import tag_polygons_by_grid


# FIXME (Ole): Move this function to e.g. safe.storage.utilities and write
# unit test using test data
# inasafe_data/test/201211071300_Jakarta_200m_Sobek_Forecast_CCAM.nc
def convert_netcdf2tif(filename, n):
    """Convert netcdf to tif aggregating first n bands

    Args
        * filename: NetCDF multiband raster with extension .nc
        * n: Positive integer determining how many bands to use

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
    # NOTE: This assumes a default projection (WGS 84, geographic)
    date = os.path.split(basename)[-1].split('_')[0]
    print 'date', date
    R = Raster(data=A,
               geotransform=geotransform,
               keywords={'category': 'hazard',
                         'subcategory': 'flood',
                         'unit': 'm',
                         'title': ('%d hour flood forecast grid '
                                   'in Jakarta at %s' % (n, date))})

    tif_filename = '%s_%d_hours.tif' % (basename, n)
    R.write_to_file(tif_filename)

    print 'Success: %d hour forecast written to %s' % (n, R.filename)
    return tif_filename


def usage():
    s = 'python netcdf2tif.py <filename>.nc <number of hours>'
    return s

if __name__ == '__main__':

    doc = 'Convert FEWS flood forecast data to hazard layers for InaSAFE'
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('filename', type=str,
                        help='NetCDF filename from FEWS')
    parser.add_argument('--hours', metavar='h', type=int, default=6,
                        help='Number of hours to use from forecast')
    parser.add_argument('--regions', metavar='regions', type=str,
                        help=('Administrative areas to be flagged as '
                              'flooded or not'))

    args = parser.parse_args()
    print args
    print

    tif_filename = convert_netcdf2tif(args.filename, args.hours)

    # Tag each polygon with Y if it contains at least one pixel
    # exceeding a specific threshold (e.g. 0.3m).
    if args.regions is not None:
        print 'Tagging %s as "Flooded" or not' % args.regions
        polygons = read_layer(args.regions)
        grid = read_layer(tif_filename)
        res = tag_polygons_by_grid(polygons, grid,
                                   threshold=0.3,
                                   tag='Flooded')

        # Keep only those that are affected (speeds things up a lot,
        # but will reduce overall bounding box for buildings under
        # consideration)
        #geom = res.get_geometry()
        #data = res.get_data()
        #new_geom = []
        #new_data = []
        #
        #for i, d in enumerate(data):
        #    if d['Flooded']:
        #        g = geom[i]
        #        new_geom.append(g)
        #        new_data.append(d)

        # Keep all polygons
        new_geom = res.get_geometry()
        new_data = res.get_data()

        date = os.path.split(args.filename)[-1].split('_')[0]
        v = Vector(geometry=new_geom, data=new_data,
                   projection=res.projection,
                   keywords={'category': 'hazard',
                             'subcategory': 'flood',
                             'title': ('%d hour flood forecast regions '
                                       'in Jakarta at %s' % (args.hours,
                                                             date))})

        polyforecast_filename = (os.path.splitext(tif_filename)[0] +
                                 '_regions.shp')
        v.write_to_file(polyforecast_filename)
        print 'Wrote tagged polygons to %s' % polyforecast_filename
