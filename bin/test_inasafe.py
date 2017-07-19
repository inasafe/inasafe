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
    download_exposure,
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
            '--extent': '106,7999364:-6,2085970:106,8525945:-6,1676174',
            '--aggregation': None,
            '--layers': None,
            '--list-functions': False,
            '--output-dir': 'test_cli',
            '--version': False,
            'LAYER_NAME': []})
        # Let's assume that for this test, the output dir is:
        self.args.output_dir = os.path.join(
            QDir(mkdtemp()).absolutePath(), self.args.output_dir)
        os.makedirs(self.args.output_dir)

    def test_download(self):
        """Test download using CLI"""
        args = CommandLineArguments({
            '--aggregation': None,
            '--download': True,
            '--exposure': None,
            '--extent': '106,85:-6,2085970:106,8525945:-6,20',
            '--hazard': None,
            '--help': False,
            '--feature-type': 'buildings',
            '--output-dir': 'test_cli',
            '--version': False,
            'LAYER_NAME': []})
        args.output_dir = os.path.join(
            QDir(mkdtemp()).absolutePath(), args.output_dir)
        download_exposure(args)
        self.assertTrue(os.path.exists(args.exposure))

        # Remove
        if os.path.exists(args.output_dir):
            shutil.rmtree(
                os.path.join(self.args.output_dir, os.pardir),
                ignore_errors=True)

    def test_run_impact_function(self):
        """Test whether we can run impact function."""
        status, message, impact_function = run_impact_function(self.args)
        self.assertEqual(status, ANALYSIS_SUCCESS)
        self.assertEqual(
            2 * len(impact_function.datastore.layers()),
            len(os.listdir(self.args.output_dir)))

    def test_build_report(self):
        """Test whether a pdf can be created from
            run_impact_function's product.
        """
        status, message, impact_function = run_impact_function(self.args)
        self.assertEqual(status, ANALYSIS_SUCCESS)

        status, message = build_report(self.args, impact_function)
        self.assertEqual(status, ImpactReport.REPORT_GENERATION_SUCCESS)

    def tearDown(self):
        # remove output dir
        if os.path.exists(self.args.output_dir):
            shutil.rmtree(
                os.path.join(self.args.output_dir, os.pardir),
                ignore_errors=True)
