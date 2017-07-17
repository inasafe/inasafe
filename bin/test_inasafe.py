# coding=utf-8
__author__ = 'Jannes123'
__project_name__ = 'inasafe'
__filename__ = 'test_inasafe.py'
__date__ = '01/06/15'
__copyright__ = 'jannes@kartoza.com'


import unittest
import shutil
import os
from tempfile import mkdtemp

from inasafe import (
    run_impact_function,
    build_report,
    CommandLineArguments,
    ImpactReport,
    ANALYSIS_SUCCESS)

from PyQt4.QtCore import QDir


class TestInasafeCommandLine(unittest.TestCase):
    """Test Module for inasafe command line client.
            run from safe/ directory
    """
    def setUp(self):
        self.args = CommandLineArguments({
            '--download': False,
            '--hazard':
                '../safe/test/data/gisv4/hazard/tsunami_vector.geojson',
            '--exposure':
                '../safe/test/data/gisv4/exposure/raster/population.asc',
            '--extent': '106,8525945:-6,2085970:106,7999364:-6,1676174',
            '--aggregation': None,
            '--layers': None,
            '--list-functions': False,
            '--output-dir': 'test_cli',
            '--report-template': '../resources/'
                                 'qgis-composer-templates/'
                                 'a4-portrait-blue.qpt',
            '--version': False,
            'LAYER_NAME': []})
        # Let's assume that for this test, the output dir is:
        self.args.output_dir = os.path.join(
            QDir(mkdtemp()).absolutePath(), self.args.output_dir)
        # self.args.output_dir = os.path.join(
        #     '/home/akbar/dev/data/test', self.args.output_dir)
        os.makedirs(self.args.output_dir, 0777)

    def test_run_impact_function(self):
        """Test whether we can run impact function."""
        status, message, impact_function = run_impact_function(self.args)
        self.assertEqual(status, ANALYSIS_SUCCESS)
        self.assertEqual(
            2*len(impact_function.datastore.layers()),
            len(os.listdir(self.args.output_dir)))

    def test_build_report(self):
        """Test whether a pdf can be created from
            run_impact_function's product.
        """
        status, message, impact_function = run_impact_function(self.args)
        self.assertEqual(status, ANALYSIS_SUCCESS)

        status, message = build_report(self.args, impact_function)
        self.assertEqual(status, ImpactReport.REPORT_GENERATION_SUCCESS)

        # output_name = os.path.splitext(self.args.output_file)[0]
        # build_report(self.args)
        # self.assertEqual(os.path.isfile(output_name + '.pdf'), True)
        # self.assertEqual(os.path.isfile(output_name + '_table.pdf'), True)

    def tearDown(self):
        # remove output dir
        if os.path.exists(self.args.output_dir):
            shutil.rmtree(
                os.path.join(self.args.output_dir, os.pardir),
                ignore_errors=True)
