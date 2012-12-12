"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Functionality related to shake data files.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'imajimatika@gmail.com'
__version__ = '0.5.0'
__date__ = '12/12/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import os
from safe.storage.converter import convert_netcdf2tif
from safe.storage.vector import Vector
from safe.engine.interpolation import tag_polygons_by_grid
from safe.storage.core import read_layer
from download_netcdf import download_file_url, download_directory, netcdf_url

flood_directory = '/home/sunnii/Documents/inasafe/inasafe_real_flood'\
                  '/flood/'

if __name__ == '__main__':
    print 'start flood forecasting'

    # retrieve data from the web
    netcdf_file = download_file_url(netcdf_url, download_directory)
    print netcdf_file
#    netcdf_file = '../inasafe_data/test/201212080500_Jakarta_200m_Sobek_Forecast_CCAM.nc'
    hours = 12

    # check environment variables
    if 'INASAFE_WORK_DIR' in os.environ:
        INASAFE_WORK_DIR = os.environ

    # convert to tif
    tif_file = convert_netcdf2tif(netcdf_file, hours, verbose=False)
    tif_file = read_layer(tif_file)
    if 'INASAFE_RW_JKT_PATH' in os.environ:
        my_polygons = os.environ['INASAFE_RW_JKT_PATH']
#        my_polygons = read_layer(my_polygons)
        my_polygons = read_layer('../inasafe_data/boundaries/rw_jakarta.shp')
    else:
        print 'polygon file not found'
        exit()
    my_result = tag_polygons_by_grid(my_polygons, tif_file, threshold=0.3, tag='affected')

    new_geom = my_result.get_geometry()
    new_data = my_result.get_data()

    date = os.path.split(netcdf_file)[-1].split('_')[0]
    v = Vector(geometry=new_geom, data=new_data,
        projection=my_result.projection,
        keywords={'category': 'hazard',
                  'subcategory': 'flood',
                  'title': ('%d hour flood forecast regions '
                            'in Jakarta at %s' % (hours,
                                                  date))})
    print netcdf_file.__class__
    polyforecast_filename = os.path.split(netcdf_file)[1].replace('.nc', '_regions.shp')
    #    polyforecast_filename = (os.path.splitext(netcdf_file)[0] +
#                             '_regions.shp')
    polyforecast_filepath = os.path.join(flood_directory, polyforecast_filename)
    v.write_to_file(polyforecast_filepath)
    print 'Wrote tagged polygons to %s' % polyforecast_filepath