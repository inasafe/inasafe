"""Script to read NetCDF raster files, process and store as tif

This requires scientific python
"""

import os
import argparse


from safe.storage.vector import Vector

from realtime.netcdf_utilities import convert_netcdf2tif
from safe.storage.core import read_layer
from safe.engine.interpolation import tag_polygons_by_grid


def usage():
    s = 'python netcdf2tif.py <filename>.nc <number of hours>'
    return s

if __name__ == '__main__':

    doc = 'Convert FEWS flood forecast data to hazard layers for InaSAFE'
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('filename', type=str,
                        help='NetCDF filename from FEWS')
    parser.add_argument('--hours', metavar='h', type=int, default=24,
                        help='Number of hours to use from forecast')
    parser.add_argument('--regions', metavar='regions', type=str,
                        help=('Administrative areas to be flagged as '
                              'flooded or not'))

    args = parser.parse_args()
    print args
    print

    tif_filename = convert_netcdf2tif(args.filename, args.hours,
                                      verbose=True)

    # Tag each polygon with Y if it contains at least one pixel
    # exceeding a specific threshold (e.g. 0.3m).
    if args.regions is not None:
        print 'Tagging %s as "affected" or not' % args.regions
        polygons = read_layer(args.regions)
        grid = read_layer(tif_filename)
        res = tag_polygons_by_grid(polygons, grid,
                                   threshold=0.3,
                                   tag='affected')

        # Keep only those that are affected (speeds things up a lot,
        # but will reduce overall bounding box for buildings under
        # consideration)
        #geom = res.get_geometry()
        #data = res.get_data()
        #new_geom = []
        #new_data = []
        #
        #for i, d in enumerate(data):
        #    if d['affected']:
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
