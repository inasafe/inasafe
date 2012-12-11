"""**Tests for safe common utilities**
"""

__author__ = 'Ismail Sunni <ismailsunni@yahoo.co.id>'
__revision__ = '$Format:%H$'
__date__ = '10/12/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


import unittest
import os


from safe.common.testing import (TESTDATA)
from converter import convert_netcdf2tif
from core import read_layer


class ConverterTest(unittest.TestCase):
    def test_convert_netcdf2tif(self):
        """Test convert netfdf file to tif."""
        netcdf_file_name = "201212080500_Jakarta_200m_Sobek_Forecast_CCAM.nc"
        netcdf_file_path = os.path.abspath(
            os.path.join(TESTDATA, netcdf_file_name))
        num_bands = 12
        tif_file = convert_netcdf2tif(netcdf_file_path, num_bands, False)
        print tif_file
        assert (os.path.isfile(tif_file)), 'File not found'
        tif_file = read_layer(tif_file)
        assert tif_file.number_of_bands == 1, 'Number of band is not same'
        assert tif_file.columns == 160, 'Number of columns is not same'
        assert tif_file.rows == 162, 'Number of rows is not same'

if __name__ == '__main__':
    unittest.main()
