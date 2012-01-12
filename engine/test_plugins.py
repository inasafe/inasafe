import unittest
from impact import plugins

import numpy
import sys
import os
import unittest
import warnings

from geonode.maps.utils import upload, file_upload, GeoNodeException

from impact.views import calculate
from impact.plugins.core import FunctionProvider
from impact.plugins.core import requirements_collect
from impact.plugins.core import requirement_check
from impact.plugins.core import get_plugins
from impact.plugins.core import compatible_layers

from impact.storage.io import get_layer_descriptors

from impact.models import Calculation, Workspace

from impact.storage.io import save_to_geonode, check_layer
from impact.storage.io import download
from impact.storage.io import read_layer
from impact.tests.utilities import TESTDATA
from django.test.client import Client
from django.conf import settings
from django.utils import simplejson as json
from geonode.maps.utils import get_valid_user

from impact.tests.utilities import TESTDATA, INTERNAL_SERVER_URL

DEFAULT_PLUGINS = ('Earthquake Fatality Function',)


# FIXME (Ole): Change H, E to layers.
class BasicFunction(FunctionProvider):
    """Risk plugin for testing

    :author Allen
    :rating 1
    :param requires category=="hazard"
    """

    @staticmethod
    def run(H, E,
            a=0.97429, b=11.037):

        return None


def padang_check_results(mmi, building_class):
    """Check calculated results through a lookup table
    returns False if the lookup fails and
    an exception if more than one lookup returned"""

    # Reference table established from plugin as of 28 July 2011
    # It was then manually verified against an Excel table by Abbie Baca
    # and Ted Dunstone. Format is
    # MMI, Building class, impact [%]
    padang_verified_results = [
        [7.50352, 1, 50.17018],
        [7.49936, 1, 49.96942],
        [7.63961, 2, 20.35277],
        [7.09855, 2, 5.895076],
        [7.49990, 3, 7.307292],
        [7.80284, 3, 13.71306],
        [7.66337, 4, 3.320895],
        [7.12665, 4, 0.050489],
        [7.12665, 5, 1.013092],
        [7.85400, 5, 7.521769],
        [7.54040, 6, 4.657564],
        [7.48122, 6, 4.167858],
        [7.31694, 6, 3.008460],
        [7.54057, 7, 1.349811],
        [7.12753, 7, 0.177422],
        [7.61912, 7, 1.866942],
        [7.64828, 8, 1.518264],
        [7.43644, 8, 0.513577],
        [7.12665, 8, 0.075070],
        [7.64828, 9, 1.731623],
        [7.48122, 9, 1.191497],
        [7.12665, 9, 0.488944]]

    impact_array = [verified_impact
        for verified_mmi, verified_building_class, verified_impact
               in padang_verified_results
                    if numpy.allclose(verified_mmi, mmi, rtol=1.0e-6) and
                    numpy.allclose(verified_building_class, building_class,
                                   rtol=1.0e-6)]

    if len(impact_array) == 0:
        return False
    elif len(impact_array) == 1:
        return impact_array[0]

    msg = 'More than one lookup result returned. May be precision error.'
    assert len(impact_array) < 2, msg

    # FIXME (Ole): Count how many buildings were damaged in each category?


class Test_plugins(unittest.TestCase):
    """Tests of Risiko calculations
    """

    def setUp(self):
        """Create valid superuser
        """
        self.user = get_valid_user()

    def test_get_plugins(self):
        """It is possible to retrieve the list of functions
        """
        plugin_list = plugins.get_plugins()
        msg = ('No plugins were found, not even the built-in ones')
        assert len(plugin_list) > 0, msg

    def test_single_get_plugins(self):
        """Named plugin can be retrieved
        """
        plugin_name = DEFAULT_PLUGINS[0]
        plugin_list = plugins.get_plugins(plugin_name)
        msg = ('No plugins were found matching %s' % plugin_name)
        assert len(plugin_list) > 0, msg

    def test_get_plugins(self):
        """Plugins can be collected
        """

        plugin_list = get_plugins()
        assert(len(plugin_list) > 0)

        # Check that every plugin has a requires line
        for plugin in plugin_list.values():
            requirements = requirements_collect(plugin)
            msg = 'There were no requirements in plugin %s' % plugin
            assert(len(requirements) > 0), msg

            for req_str in requirements:
                msg = 'All plugins should return True or False'
                assert(requirement_check({'category': 'hazard',
                                          'subcategory': 'earthquake',
                                          'layerType': 'raster'},
                                         req_str) in [True, False]), msg

    def test_requirements_check(self):
        """Plugins are correctly filtered based on requirements"""

        plugin_list = get_plugins('BasicFunction')
        assert(len(plugin_list) == 1)

        requirements = requirements_collect(plugin_list[0].values()[0])
        msg = 'Requirements are %s' % requirements
        assert(len(requirements) == 1), msg
        for req_str in requirements:
            msg = 'Should eval to True'
            assert(requirement_check({'category': 'hazard'},
                                     req_str) is True), msg
            msg = 'Should eval to False'
            assert(requirement_check({'broke': 'broke'},
                                     req_str) is False), msg

        try:
            plugin_list = get_plugins('NotRegistered')
        except AssertionError:
            pass
        else:
            msg = 'Search should fail'
            raise Exception(msg)

    def test_plugin_compatibility(self):
        """Default plugins perform as expected
        """

        # Upload a raster and a vector data set
        hazard_filename = os.path.join(TESTDATA,
                                       'shakemap_padang_20090930.asc')
        hazard_layer = save_to_geonode(hazard_filename)
        check_layer(hazard_layer, full=True)

        exposure_filename = os.path.join(TESTDATA,
                                         'lembang_schools.shp')
        exposure_layer = save_to_geonode(exposure_filename)
        check_layer(exposure_layer, full=True)

        # Test
        plugin_list = get_plugins()
        assert len(plugin_list) > 0

        geoserver = {'url': settings.GEOSERVER_BASE_URL + 'ows',
                     'name': 'Local Geoserver',
                     'version': '1.0.0',
                     'id': 0}
        metadata = get_layer_descriptors(geoserver['url'])

        msg = 'There were no layers in test geoserver'
        assert len(metadata) > 0, msg

        # Characterisation test to preserve the behaviour of
        # get_layer_descriptors. FIXME: I think we should change this to be
        # a dictionary of metadata entries (ticket #126).
        reference = [['geonode:lembang_schools',
                      {'layer_type': 'vector',
                       'category': 'exposure',
                       'subcategory': 'building',
                       'title': 'lembang_schools'}],
                     ['geonode:shakemap_padang_20090930',
                      {'layer_type': 'raster',
                       'category': 'hazard',
                       'subcategory': 'earthquake',
                       'title': 'shakemap_padang_20090930'}]]

        for entry in reference:
            name, mdblock = entry

            i = [x[0] for x in metadata].index(name)

            msg = 'Got name %s, expected %s' % (name, metadata[i][0])
            assert name == metadata[i][0], msg
            for key in entry[1]:
                refval = entry[1][key]
                val = metadata[i][1][key]
                msg = ('Got value "%s" for key "%s" '
                       'Expected "%s"' % (val, key, refval))
                assert refval == val, msg

        # Check plugins are returned
        annotated_plugins = [{'name': name,
                              'doc': f.__doc__,
                              'layers': compatible_layers(f, metadata)}
                             for name, f in plugin_list.items()]

        msg = 'No compatible layers returned'
        assert len(annotated_plugins) > 0, msg

    def test_django_plugins(self):
        """Django plugin functions can be retrieved correctly
        """

        c = Client()
        rv = c.post('/impact/api/functions/', data={})

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv['Content-Type'], 'application/json')
        data = json.loads(rv.content)

    def test_plugin_selection(self):
        """Verify the plugins can recognize compatible layers.
        """
        # Upload a raster and a vector data set
        hazard_filename = os.path.join(TESTDATA,
                                       'Earthquake_Ground_Shaking.asc')
        hazard_layer = save_to_geonode(hazard_filename,
                                       user=self.user,
                                       overwrite=True)
        check_layer(hazard_layer, full=True)

        msg = 'No keywords found in layer %s' % hazard_layer.name
        assert len(hazard_layer.keywords) > 0, msg

        exposure_filename = os.path.join(TESTDATA,
                                         'lembang_schools.shp')
        exposure_layer = save_to_geonode(exposure_filename)
        check_layer(exposure_layer, full=True)
        msg = 'No keywords found in layer %s' % exposure_layer.name
        assert len(exposure_layer.keywords) > 0, msg

        c = Client()
        rv = c.post('/impact/api/functions/', data={})

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv['Content-Type'], 'application/json')
        data = json.loads(rv.content)

        assert 'functions' in data

        functions = data['functions']

        # FIXME (Ariel): This test should implement an alternative function to
        # parse the requirements, but for now it will just take the buildings
        # damage one.
        for function in functions:
            if function['name'] == 'Earthquake Building Damage Function':
                layers = function['layers']

                msg_tmpl = 'Expected layer %s in list of compatible layers: %s'

                hazard_msg = msg_tmpl % (hazard_layer.typename, layers)
                assert hazard_layer.typename in layers, hazard_msg

                exposure_msg = msg_tmpl % (exposure_layer.typename, layers)
                assert exposure_layer.typename in layers, exposure_msg

    def test_padang_building_examples(self):
        """Padang building impact calculation works through the API
        """

        # Test for a range of hazard layers
        for mmi_filename in ['Shakemap_Padang_2009.asc']:
                               #'Lembang_Earthquake_Scenario.asc']:

            # Upload input data
            hazardfile = os.path.join(TESTDATA, mmi_filename)
            hazard_layer = save_to_geonode(hazardfile, user=self.user)
            hazard_name = '%s:%s' % (hazard_layer.workspace,
                                        hazard_layer.name)

            exposurefile = os.path.join(TESTDATA, 'Padang_WGS84.shp')
            exposure_layer = save_to_geonode(exposurefile, user=self.user)
            exposure_name = '%s:%s' % (exposure_layer.workspace,
                                          exposure_layer.name)

            # Call calculation routine

            # FIXME (Ole): The system freaks out if there are spaces in
            #              bbox string. Please let us catch that and deal
            #              nicely with it - also do this in download()
            bbox = '96.956, -5.51, 104.63933, 2.289497'

            with warnings.catch_warnings():
                warnings.simplefilter('ignore')

                c = Client()
                rv = c.post('/impact/api/calculate/', data=dict(
                            hazard_server=INTERNAL_SERVER_URL,
                            hazard=hazard_name,
                            exposure_server=INTERNAL_SERVER_URL,
                            exposure=exposure_name,
                            bbox=bbox,
                            impact_function='Padang Earthquake ' \
                                            'Building Damage Function',
                            keywords='test,buildings,padang',
                            ))

                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv['Content-Type'], 'application/json')
                data = json.loads(rv.content)
                assert 'hazard_layer' in data.keys()
                assert 'exposure_layer' in data.keys()
                assert 'run_duration' in data.keys()
                assert 'run_date' in data.keys()
                assert 'layer' in data.keys()

                # Download result and check
                layer_name = data['layer'].split('/')[-1]

                result_layer = download(INTERNAL_SERVER_URL,
                                       layer_name,
                                       bbox)
                assert os.path.exists(result_layer.filename)

                # Read hazard data for reference
                hazard_raster = read_layer(hazardfile)
                A = hazard_raster.get_data()
                mmi_min, mmi_max = hazard_raster.get_extrema()

                # Read calculated result
                impact_vector = read_layer(result_layer.filename)
                coordinates = impact_vector.get_geometry()
                attributes = impact_vector.get_data()

                # Verify calculated result
                count = 0
                verified_count = 0
                for i in range(len(attributes)):
                    lon, lat = coordinates[i][:]
                    calculated_mmi = attributes[i]['MMI']

                    if calculated_mmi == 0.0:
                        # FIXME (Ole): Some points have MMI==0 here.
                        # Weird but not a show stopper
                        continue

                    # Check that interpolated points are within range
                    msg = ('Interpolated mmi %f was outside extrema: '
                           '[%f, %f] at location '
                           '[%f, %f]. ' % (calculated_mmi,
                                           mmi_min, mmi_max,
                                           lon, lat))
                    assert mmi_min <= calculated_mmi <= mmi_max, msg

                    building_class = attributes[i]['TestBLDGCl']

                    # Check calculated damage
                    calculated_dam = attributes[i]['DAMAGE']
                    verified_dam = padang_check_results(calculated_mmi,
                                                        building_class)
                    #print calculated_mmi, building_class, calculated_dam
                    if verified_dam:
                        msg = ('Calculated damage was not as expected '
                                 'for hazard layer %s. I got %f '
                               'but expected %f' % (hazardfile,
                                                    calculated_dam,
                                                    verified_dam))
                        assert numpy.allclose(calculated_dam, verified_dam,
                                               rtol=1.0e-4), msg
                        verified_count += 1
                    count += 1

                msg = ('No points was verified in output. Please create '
                       'table withe reference data')
                assert verified_count > 0, msg
                msg = 'Number buildings was not 3896.'
                assert count == 3896, msg

if __name__ == '__main__':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'risiko.settings'
    suite = unittest.makeSuite(Test_plugins, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
