# coding=utf-8
import logging
import os
import shutil
import tempfile
import unittest
import urlparse

import headless
from headless.celery_app import app
from headless.celeryconfig import DEPLOY_OUTPUT_DIR, DEPLOY_OUTPUT_URL
from headless.tasks.celery_test_setup import \
    update_celery_configuration
from headless.tasks.inasafe_wrapper import (
    filter_impact_function,
    run_analysis,
    read_keywords_iso_metadata)
from headless.tasks.utilities import archive_layer

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/29/16'


LOGGER = logging.getLogger('InaSAFE')
LOGGER.setLevel(logging.DEBUG)


class TestTaskCallFilesystem(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTaskCallFilesystem, self).__init__(*args, **kwargs)

        default_work_dir = os.path.dirname(headless.__file__)
        default_work_dir = os.path.abspath(
            os.path.join(default_work_dir, '../'))
        self.inasafe_work_dir = os.environ.get(
            'InaSAFEQGIS', default_work_dir)

    def convert_path(self, path):
        return path

    def setUp(self):
        # Modify test behavior of celery based on environment settings
        update_celery_configuration(app)

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

        test_deploy_dir = os.path.join(DEPLOY_OUTPUT_DIR, 'test_deploy')
        self.test_deploy_dir = test_deploy_dir

        if not os.path.exists(test_deploy_dir):
            os.makedirs(test_deploy_dir)

        hazard_temp = tempfile.mktemp(suffix='.zip', dir=test_deploy_dir)
        exposure_temp = tempfile.mktemp(suffix='.zip', dir=test_deploy_dir)
        aggregation_temp = tempfile.mktemp(suffix='.zip', dir=test_deploy_dir)
        shutil.move(hazard, hazard_temp)
        shutil.move(exposure, exposure_temp)
        shutil.move(aggregation, aggregation_temp)
        self.hazard_temp = self.convert_path(hazard_temp)
        self.exposure_temp = self.convert_path(exposure_temp)
        self.aggregation_temp = self.convert_path(aggregation_temp)

        self.keywords_file = os.path.join(
            self.inasafe_work_dir,
            'safe/test/data/hazard/continuous_flood_20_20.xml')

    def tearDown(self):
        shutil.rmtree(self.test_deploy_dir)

    def test_filter_impact_function(self):

        celery_result = filter_impact_function.delay(
            self.hazard_temp, self.exposure_temp)

        ifs = celery_result.get()

        self.assertEqual(len(ifs), 1)

        actual_id = ifs[0]
        expected_id = {
            'id': 'FloodEvacuationRasterHazardFunction',
            'name': u'Raster flood on population'
        }

        self.assertEqual(actual_id, expected_id)

    def test_run_analysis(self):
        celery_result = run_analysis.delay(
                self.hazard_temp,
                self.exposure_temp,
                'FloodEvacuationRasterHazardFunction',
                aggregation=self.aggregation_temp,
                generate_report=True)

        url_name = celery_result.get()

        self.assertTrue(url_name)

        # check the file is generated in /home/web directory
        relative_name = url_name.replace(DEPLOY_OUTPUT_URL, '')
        absolute_name = os.path.join(DEPLOY_OUTPUT_DIR, relative_name)
        self.assertTrue(os.path.exists(absolute_name), absolute_name)
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

    def test_read_keywords(self):
        result = read_keywords_iso_metadata.delay(self.keywords_file)
        expected = {
            'hazard_category': u'single_event',
            'keyword_version': u'3.5',
            'title': u'Continuous Flood',
            'hazard': u'flood',
            'continuous_hazard_unit': u'metres',
            'source': u'Akbar Gumbira',
            'layer_geometry': u'raster',
            'layer_purpose': u'hazard',
            'layer_mode': u'continuous'
        }
        actual = result.get()
        self.assertDictEqual(actual, expected)


class TestTaskCallUrl(TestTaskCallFilesystem):

    def __init__(self, *args, **kwargs):
        super(TestTaskCallUrl, self).__init__(*args, **kwargs)

    def convert_path(self, path):
        tail_name = path.replace(DEPLOY_OUTPUT_DIR, '')
        return urlparse.urljoin(DEPLOY_OUTPUT_URL, tail_name)


if __name__ == '__main__':
    unittest.main()
