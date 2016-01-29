# coding=utf-8
import unittest

import os
from zipfile import ZipFile

from headless.tasks.inasafe_wrapper import filter_impact_function
from safe.common.utilities import temp_dir

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/29/16'


class TestTaskCall(unittest.TestCase):

    def setUp(self):
        self.inasafe_work_dir = os.environ['INASAFE_SOURCE_DIR']

    def zip_layer(self, layer_path, zip_folder):
        base_name = os.path.basename(layer_path)
        base_name, _ = os.path.splitext(base_name)
        dir_name = os.path.dirname(layer_path)
        zip_path = os.path.join(
            zip_folder,
            '%s.zip' % base_name
        )
        with ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(dir_name):
                for f in files:
                    f_name, ext = os.path.splitext(f)
                    if f_name.startswith(base_name):
                        filename = os.path.join(root, f)
                        zipf.write(filename, arcname=f)

        return zip_path

    def test_filter_impact_function(self):
        zip_folder = temp_dir()
        hazard_path = os.path.join(
            self.inasafe_work_dir,
            'safe/test/data/hazard/continuous_flood_20_20.asc'
        )
        hazard_path = self.zip_layer(hazard_path, zip_folder)
        exposure_path = os.path.join(
            self.inasafe_work_dir,
            'safe/test/data/exposure/pop_binary_raster_20_20.asc'
        )
        exposure_path = self.zip_layer(exposure_path, zip_folder)
        result = filter_impact_function.delay(hazard_path, exposure_path)
        ifs = result.get()
        self.assertTrue(len(ifs) > 0)


if __name__ == '__main__':
    unittest.main()
