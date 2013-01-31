__author__ = 'nielso'

import unittest
import numpy
import os

from netcdf_utilities import convert_netcdf2tif
from safe.storage.core import read_layer
from safe.storage.vector import Vector
from safe.engine.interpolation import tag_polygons_by_grid
from safe.common.testing import TESTDATA
from safe.common.utilities import unique_filename
from safe.common.polygon import is_inside_polygon
from safe.common.utilities import verify


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
        os.remove(all_hours_tif)

        # Check point taking up-down flip into account
        assert numpy.allclose(D[-136 - 1, 51], max_136_51)

        # Run script for one hour and check first band
        one_hour_tif = convert_netcdf2tif(self.nc_filename, 1, verbose=False)
        D = read_layer(one_hour_tif).get_data()
        assert numpy.allclose(max(D.flat), 0.74)  # Checked band 1 with QGIS

        # Characterisation test of location of max inundation
        assert D[28, 53] == max(D.flat)
        assert numpy.allclose(y[28], -6.3199)
        assert numpy.allclose(x[53], 106.781)

        os.remove(one_hour_tif)

        return

    def test_tag_regions_by_flood(self):
        """Regions can be tagged correctly with data from flood forecasts
        """

        threshold = 0.3
        label = 'affected'

        tif_filename = convert_netcdf2tif(self.nc_filename, 24, verbose=False)
        region_filename = os.path.join(TESTDATA, 'rw_jakarta_singlepart.shp')

        grid = read_layer(tif_filename)
        polygons = read_layer(region_filename)

        res = tag_polygons_by_grid(polygons, grid,
                                   threshold=threshold,
                                   tag=label)
        os.remove(tif_filename)
        geom = res.get_geometry()
        data = res.get_data()

        # Check correctness of affected regions
        affected_geom = []
        affected_data = []
        for i, d in enumerate(data):
            if d[label]:
                g = geom[i]
                affected_geom.append(g)
                affected_data.append(d)

        assert len(affected_geom) == 37
        assert len(affected_data) == 37

        # Check that every grid point exceeding threshold lies inside
        # one of the polygons marked as affected
        P, V = grid.to_vector_points()

        flooded_points_geom = []
        flooded_points_data = []
        for i, point in enumerate(P):
            val = V[i]
            if val > threshold:
                # Point that is flooded must be in one of the tagged polygons
                found = False
                for polygon in affected_geom:
                    if is_inside_polygon(point, polygon):
                        found = True
                msg = ('No affected polygon was found for point [%f, %f] '
                       'with value %f' % (point[0], point[1], val))
                verify(found, msg)

                # Collected flooded points for visualisation
                flooded_points_geom.append(point)
                flooded_points_data.append({'depth': val})

        # To generate files for visual inspection.
        # See
# https://raw.github.com/AIFDR/inasafe/master/files/flood_tagging_test.png
# https://github.com/AIFDR/inasafe/blob/master/files/flood_tagging_test.tgz

        tmp_filename = unique_filename(prefix='grid', suffix='.tif')
        grid.write_to_file(tmp_filename)
        #print 'Grid written to ', tmp_filename

        tmp_filename = unique_filename(prefix='regions', suffix='.shp')
        res.write_to_file(tmp_filename)
        #print 'Regions written to ', tmp_filename

        tmp_filename = unique_filename(prefix='flooded_points', suffix='.shp')
        v = Vector(geometry=flooded_points_geom, data=flooded_points_data)
        v.write_to_file(tmp_filename)
        #print 'Flooded points written to ', tmp_filename

    test_tag_regions_by_flood.slow = True

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_flood_forecasting_functionality, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
