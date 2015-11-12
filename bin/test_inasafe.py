# coding=utf-8
__author__ = 'Jannes123'
__project_name__ = 'inasafe'
__filename__ = 'test_inasafe.py'
__date__ = '01/06/15'
__copyright__ = 'jannes@kartoza.com'


import unittest
import os
import re
usage_dir = os.environ['InaSAFEQGIS'] + '/bin' + '/'
source_file = file(usage_dir + 'inasafe', 'r')
import imp
inasafe = imp.load_source('inasafe', usage_dir, source_file)
from inasafe import (
    get_exposure,
    get_hazard,
    get_impact_function_list,
    run_impact_function,
    build_report,
    analysis_setup,
    CommandLineArguments)


class TestInasafeCommandLine(unittest.TestCase):
    """Test Module for inasafe command line client.
            run from safe/ directory
    """
    def setUp(self):
        self.args = CommandLineArguments({
            '--download': False,
            '--exposure': 'safe/test/data/exposure/buildings.shp',
            '--extent': '106,8525945:-6,2085970:106,7999364:-6,1676174',
            '--hazard': 'safe/test/data/hazard/continuous_flood_20_20.asc',
            '--impact-function': 'FloodRasterBuildingFunction',
            '--layers': None,
            '--list-functions': False,
            '--output-file': '/tmp/inasafe/flood_on_buildings.shp',
            '--report-template': '../inasafe/resources/'
                                 'qgis-composer-templates/'
                                 'a4-portrait-blue.qpt',
            '--version': False,
            'LAYER_NAME': []})

    def test_get_exposure(self):
        """Test building an exposure layer from file."""
        exposure = get_exposure(self.args)
        self.assertEqual(
            exposure.isValid(), True, 'Exposure layer is not valid')

    def test_get_hazard(self):
        """Test building a hazard layer from file."""
        hazard = get_hazard(self.args)
        self.assertEqual(hazard.isValid(), True, 'Hazard layer is not valid')

    def test_get_impact_function_list(self):
        """Test getting a list of IF ids."""
        impact_function_list = get_impact_function_list()
        self.assertEqual(type(impact_function_list), list)

    def test_analysis_setup(self):
        exposure = get_exposure(self.args)
        hazard = get_hazard(self.args)
        analysis = analysis_setup(self.args, hazard, exposure)
        self.assertEqual(
            str(type(analysis)),
            "<class 'inasafe.safe.utilities.analysis.Analysis'>")

    def test_build_report(self):
        """Test whether a pdf can be created from
            run_impact_function's product.
        """
        run_impact_function(self.args)
        output_name = os.path.splitext(self.args.output_file)[0]
        build_report(self.args)
        self.assertEqual(os.path.isfile(output_name + '.pdf'), True)
        self.assertEqual(os.path.isfile(output_name + '_table.pdf'), True)

    def tearDown(self):
        # remove output files
        output_name = os.path.splitext(self.args.output_file)[0]
        dirname = os.path.dirname(output_name)
        names = os.listdir(dirname)

        for name in names:
            if os.path.exists(dirname + '/' + name) and \
                    re.search(os.path.basename(
                        os.path.splitext(output_name)[0]), name):
                os.remove(dirname + '/' + name)
                print dirname + '/' + name
        # close file used for import workaround
        source_file.close()
