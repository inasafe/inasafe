# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Converter Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'imajimatika@gmail.com'
__date__ = '27/03/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest
from converter import convert_mmi_data
from safe.common.utilities import unique_filename, temp_dir

from safe.common.testing import TESTDATA


class ConverterTest(unittest.TestCase):
    def test_convert_grid_to_raster(self):
        """Test converting grid.xml to raster (tif file)
        """
        my_grid_path = os.path.join(TESTDATA, 'grid.xml')
        my_output_raster = unique_filename(
            prefix='result_grid',
            suffix='.tif',
            dir=temp_dir('test'))
        my_result = convert_mmi_data(my_grid_path, my_output_raster)
        my_expected_result = my_output_raster.replace('.tif', '-nearest.tif')
        self.assertEqual(
            my_result, my_expected_result,
            'Result path not as expected')
        exists = os.path.exists(my_result)
        self.assertTrue(exists, 'File result : %s is not exist' % my_result)
        exists = os.path.exists(my_result[:-3] + 'keywords')
        self.assertTrue(
            exists,
            'File result : %s does not exist' % my_result[:-3] + 'keywords')
        exists = os.path.exists(my_result[:-3] + 'qml')
        self.assertTrue(
            exists,
            'File result : %s does not exist' % my_result[:-3] + 'qml')
    test_convert_grid_to_raster.slow = True


if __name__ == '__main__':
    suite = unittest.makeSuite(ConverterTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
