
__author__ = 'Jannes123'
__project_name__ = 'inasafe'
__filename__ = 'test_inasafe.py'
__date__ = '01/06/15'
__copyright__ = 'jannes@kartoza.com'


import unittest
import os
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
            '--report-template': '../inasafe/resources/qgis-composer-templates/'
                                 'inasafe-portrait-a4.qpt',
            '--version': False,
            'LAYER_NAME': []})

    def test_get_exposure(self):
        """Test building an exposure layer from file."""
        ex = get_exposure(self.args)
        self.assertEqual(ex.isValid(), True, 'Exposure layer is not valid')

    def test_hazard(self):
        """Test building a hazard layer from file."""
        haz = get_hazard(self.args)
        self.assertEqual(haz.isValid(), True, 'Hazard layer is not valid')

    def test_get_impact_function_list(self):
        """Test getting a list of IF ids."""
        impact_function_list = get_impact_function_list()
        self.assertEqual(type(impact_function_list), list)

    def test_run_if(self):
        """Run an IF and check if vector file was created."""
        run_impact_function(self.args)
        # check if impact file exists
        self.assertEqual(os.path.isfile(self.args.output_file), True)

    def test_build_report(self):
        """Test whether a pdf can be created from run_if's product."""
        # delete pdfs in inasafe
        output_name = os.path.splitext(self.args.output_file)[0]
        os.remove(output_name + '.pdf')
        os.remove(output_name + '_table.pdf')
        build_report(self.args)
        self.assertEqual(os.path.isfile(output_name + '.pdf'), True)
        self.assertEqual(os.path.isfile(output_name + '_table.pdf'), True)



