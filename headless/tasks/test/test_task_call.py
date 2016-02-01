# coding=utf-8
import logging
import os
import shutil
import tempfile
import unittest

from headless.celeryconfig import deploy_output_dir, deploy_output_url
from headless.tasks.inasafe_wrapper import filter_impact_function, \
    run_analysis
from headless.tasks.utilities import archive_layer

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/29/16'


LOGGER = logging.getLogger('InaSAFE')
LOGGER.setLevel(logging.DEBUG)


class TestTaskCall(unittest.TestCase):

    def setUp(self):
        self.inasafe_work_dir = os.environ['InaSAFEQGIS']
        # generate tempfile
        hazard = os.path.join(
            self.inasafe_work_dir,
            'safe/test/data/hazard/continuous_flood_20_20.asc')
        exposure = os.path.join(
            self.inasafe_work_dir,
            'safe/test/data/exposure/pop_binary_raster_20_20.asc')
        aggregation = os.path.join(
            self.inasafe_work_dir,
            'safe/test/data/boundaries/district_osm_jakarta.shp')
        hazard = archive_layer(hazard)
        exposure = archive_layer(exposure)
        aggregation = archive_layer(aggregation)
        hazard_temp = tempfile.mktemp(suffix='.zip')
        exposure_temp = tempfile.mktemp(suffix='.zip')
        aggregation_temp = tempfile.mktemp(suffix='.zip')
        shutil.move(hazard, hazard_temp)
        shutil.move(exposure, exposure_temp)
        shutil.move(aggregation, aggregation_temp)
        self.hazard_temp = hazard_temp
        self.exposure_temp = exposure_temp
        self.aggregation_temp = aggregation_temp

    def test_filter_impact_function(self):

        celery_result = filter_impact_function.apply(
            args=[self.hazard_temp, self.exposure_temp])

        ifs = celery_result.get()

        self.assertEqual(len(ifs), 1)

        actual_id = ifs[0]['id']
        expected_id = 'FloodEvacuationRasterHazardFunction'

        self.assertEqual(actual_id, expected_id)

    def test_run_analysis(self):
        celery_result = run_analysis.apply(
            args=[
                self.hazard_temp,
                self.exposure_temp,
                'FloodEvacuationRasterHazardFunction'],
            kwargs={
                'generate_report': True,
                'aggregation': self.aggregation_temp
            })

        url_name = celery_result.get()

        self.assertTrue(url_name)

        # check the file is generated in /home/web directory
        relative_name = url_name.replace(deploy_output_url, '')
        absolute_name = os.path.join(deploy_output_dir, relative_name)
        self.assertTrue(os.path.exists(absolute_name))
        # check  pdf report is generated
        basename, _ = os.path.splitext(absolute_name)
        self.assertTrue(os.path.exists(basename + '.pdf'),
                        'Report file not exist')
        self.assertTrue(os.path.exists(basename + '_table.pdf'),
                        'Table report file not exist')
        self.assertTrue(os.path.exists(basename + '.qml'),
                        'QML style file not exist')
        self.assertTrue(os.path.exists(basename + '.xml'),
                        'XML Metadata file not exist')

        folder_name, _ = os.path.split(absolute_name)
        shutil.rmtree(folder_name)


if __name__ == '__main__':
    unittest.main()
