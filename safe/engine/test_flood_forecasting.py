__author__ = 'nielso'

import unittest
import numpy
import os

from safe.storage.netcdf_utilities import convert_netcdf2tif
from safe.storage.core import read_layer
#from safe.engine.interpolation import tag_polygons_by_grid
from safe.common.testing import TESTDATA


class Test_flood_forecasting_functionality(unittest.TestCase):
    """Specific tests of flood forecasting functionality
    """
    def setUp(self):
        self.nc_filename = os.path.join(TESTDATA,
            '201211120500_Jakarta_200m_Sobek_Forecast_CCAM.nc')

    def test_convert_netcdf2tif(self):
        """NetCDF flood forecasts can be converted to tif
        """

        # First check that input file is as expected
        from Scientific.IO.NetCDF import NetCDFFile
        fid = NetCDFFile(self.nc_filename)

        x = fid.variables['x'][:]  # Longitudes
        y = fid.variables['y'][:]  # Latitudes

        inundation_depth = fid.variables['Inundation_Depth'][:]

        T = inundation_depth.shape[0]  # Number of time steps
        M = inundation_depth.shape[1]  # Steps in the y direction
        N = inundation_depth.shape[2]  # Steps in the x direction

        assert T == 71
        assert M == 162  # Latitudes
        assert N == 160  # Longitudes

        assert len(x) == N
        assert len(y) == M

        # Pick a max value in an area known to have flooding
        # (approximately picked with ncview)
        max_136_51 = max(inundation_depth[:, 136, 51])
        assert numpy.allclose(max_136_51, 1.58)

        #print max_136_51
        #print 'y[136]', y[136]  # Lat
        #print 'x[51]', x[51]  # Lon

        assert numpy.allclose(x[51], 106.7777)
        assert numpy.allclose(y[136], -6.124634)

        # Run script over all hours
        all_hours_tif = convert_netcdf2tif(self.nc_filename, T, verbose=False)
        msg = 'Expected file %s did not exist' % all_hours_tif
        assert os.path.isfile(all_hours_tif), msg

        # Read resulting layer and check
        L = read_layer(all_hours_tif)
        D = L.get_data()
        print all_hours_tif
        os.remove(all_hours_tif)

        # Check point taking up-down flip into account
        assert numpy.allclose(D[-136 - 1, 51], max_136_51)

        # Run script for one hour and check first band
        one_hour_tif = convert_netcdf2tif(self.nc_filename, 1, verbose=False)
        D = read_layer(one_hour_tif).get_data()
        assert numpy.allclose(max(D.flat), 0.74)  # Checked band 1 with QGIS
        os.remove(one_hour_tif)

        return

    def Xtest_tag_regions_by_flood(self):
        """Regions can be tagged correctly with data from flood forecasts
        """
        pass
        #all_hours_tif = convert_netcdf2tif(self.nc_filename,
        # 24, verbose=False)
        #region_filename = os.path.join(TESTDATA, 'rw_jakarta_singlepart.shp')

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_flood_forecasting_functionality, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
