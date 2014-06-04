# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Shake Event Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '2/08/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# this import required to enable PyQt API v2 - DO NOT REMOVE!
#noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

import os
import shutil
import unittest
import logging
import difflib

import ogr

# pylint: disable=E0611
# pylint: disable=W0611
from qgis.core import QgsFeatureRequest
# pylint: enable=E0611
# pylint: enable=W0611
from safe.api import unique_filename, temp_dir
from safe.common.testing import get_qgis_app
from realtime.utilities import (
    shakemap_extract_dir,
    data_dir)
from realtime.shake_event import ShakeEvent
from realtime.utilities import base_data_dir

# The logger is initialised in realtime/__init__
LOGGER = logging.getLogger('InaSAFE')
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

# Shake ID for this test
SHAKE_ID = '20131105060809'


class TestShakeEvent(unittest.TestCase):
    """Tests relating to shake events"""
    #noinspection PyPep8Naming
    def setUp(self):
        """Copy our cached dataset from the fixture dir to the cache dir."""
        # Since ShakeEvent will be using sftp_shake_data, we'll copy the grid
        # file inside 20131105060809 folder to
        # shakemap_cache_dir/20131105060809/grid.xml
        input_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../fixtures/shake_data',
                SHAKE_ID,
                'output/grid.xml'))
        target_folder = os.path.join(
            shakemap_extract_dir(), SHAKE_ID)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        target_path = os.path.abspath(os.path.join(target_folder, 'grid.xml'))
        shutil.copyfile(input_path, target_path)

    #noinspection PyPep8Naming
    def tearDown(self):
        """Delete the cached data."""
        target_path = os.path.join(shakemap_extract_dir(), SHAKE_ID)
        shutil.rmtree(target_path)

    def test_grid_file_path(self):
        """Test grid_file_path works using cached data."""
        expected_path = os.path.join(
            shakemap_extract_dir(), SHAKE_ID, 'grid.xml')
        shake_event = ShakeEvent(SHAKE_ID, data_is_local_flag=True)
        grid_path = shake_event.grid_file_path()
        self.assertEquals(expected_path, grid_path)

    def test_to_string(self):
        """Test __str__ works properly."""
        shake_event = ShakeEvent(SHAKE_ID, data_is_local_flag=True)
        expected_state = (
            'latitude: -2.43\n'
            'longitude: 140.62\n'
            'event_id: 20131105060809\n'
            'magnitude: 3.6\n'
            'depth: 10.0\n'
            'description: None\n'
            'location: Papua\n'
            'day: 5\n'
            'month: 11\n'
            'year: 2013\n'
            'time: None\n'
            'time_zone: WIB\n'
            'x_minimum: 139.37\n'
            'x_maximum: 141.87\n'
            'y_minimum: -3.67875\n'
            'y_maximum: -1.18125\n'
            'rows: 101.0\n'
            'columns: 101.0\n'
            'mmi_data: Populated\n'
            'population_raster_path: None\n'
            'impact_file: None\n'
            'impact_keywords_file: None\n'
            'fatality_counts: None\n'
            'displaced_counts: None\n'
            'affected_counts: None\n'
            'extent_with_cities: Not set\n'
            'zoom_factor: 1.25\n'
            'search_boxes: None\n')

        state = str(shake_event)
        message = (('Expected:\n----------------\n%s'
                    '\n\nGot\n------------------\n%s\n') %
                   (expected_state, state))
        self.assertEqual(state, expected_state, message)

    def check_feature_count(self, path, count):
        data_source = ogr.Open(path)
        base_name = os.path.splitext(os.path.basename(path))[0]
        # do a little query to make sure we got some results...
        sql_statement = 'select * from \'%s\' order by MMI asc' % base_name
        #print sql_statement
        layer = data_source.ExecuteSQL(sql_statement)
        feature_count = layer.GetFeatureCount()
        flag = feature_count == count
        message = ''
        if not flag:
            message = 'Expected %s features, got %s' % (count, feature_count)
        data_source.ReleaseResultSet(layer)
        data_source.Destroy()
        return flag, message

    def test_event_to_contours(self):
        """Check we can extract contours from the event"""
        shake_event = ShakeEvent(SHAKE_ID, data_is_local_flag=True)
        file_path = shake_event.mmi_data_to_contours(force_flag=True,
                                                     algorithm='invdist')
        self.assertTrue(self.check_feature_count(file_path, 16))
        self.assertTrue(os.path.exists(file_path))
        expected_qml = file_path.replace('shp', 'qml')
        message = '%s not found' % expected_qml
        self.assertTrue(os.path.exists(expected_qml), message)

        file_path = shake_event.mmi_data_to_contours(force_flag=True,
                                                     algorithm='nearest')
        self.assertTrue(self.check_feature_count(file_path, 132))
        file_path = shake_event.mmi_data_to_contours(force_flag=True,
                                                     algorithm='average')
        self.assertTrue(self.check_feature_count(file_path, 132))

    def test_local_cities(self):
        """Test that we can retrieve the cities local to the event"""
        shake_event = ShakeEvent(SHAKE_ID, data_is_local_flag=True)
        # Get teh mem layer
        cities_layer = shake_event.local_cities_memory_layer()
        provider = cities_layer.dataProvider()

        expected_feature_count = 2
        self.assertEquals(provider.featureCount(), expected_feature_count)
        strings = []
        request = QgsFeatureRequest()
        for feature in cities_layer.getFeatures(request):
            # fetch map of attributes
            attributes = cities_layer.dataProvider().attributeIndexes()
            for attribute_key in attributes:
                strings.append("%d: %s\n" % (
                    attribute_key, feature[attribute_key]))
            strings.append('------------------\n')
        LOGGER.debug('Mem table:\n %s' % strings)
        file_path = unique_filename(prefix='test_local_cities',
                                    suffix='.txt',
                                    dir=temp_dir('test'))
        cities_file = file(file_path, 'w')
        cities_file.writelines(strings)
        cities_file.close()

        fixture_path = os.path.join(data_dir(),
                                    'tests',
                                    'test_local_cities.txt')
        cities_file = file(fixture_path)
        expected_string = cities_file.readlines()
        cities_file.close()

        diff = difflib.unified_diff(expected_string, strings)
        diff_list = list(diff)
        diff_string = ''
        for _, myLine in enumerate(diff_list):
            diff_string += myLine

        message = ('Diff is not zero length:\n'
                   'Control file: %s\n'
                   'Test file: %s\n'
                   'Diff:\n%s' %
                   (fixture_path,
                    file_path,
                    diff_string))
        self.assertEqual(diff_string, '', message)

    def test_cities_to_shape(self):
        """Test that we can retrieve the cities local to the event."""
        shake_event = ShakeEvent(SHAKE_ID, data_is_local_flag=True)
        file_path = shake_event.cities_to_shapefile()
        self.assertTrue(os.path.exists(file_path))

    def test_cities_search_boxes_to_shape(self):
        """Test that we can retrieve the search boxes used to find cities."""
        shake_event = ShakeEvent(SHAKE_ID, data_is_local_flag=True)
        file_path = shake_event.city_search_boxes_to_shapefile()
        self.assertTrue(os.path.exists(file_path))

    def test_calculate_fatalities(self):
        """Test that we can calculate fatalities."""
        LOGGER.debug(QGIS_APP.showSettings())
        shake_event = ShakeEvent(SHAKE_ID, data_is_local_flag=True)
        result, fatalities_html = shake_event.calculate_impacts()

        # Get the os environment INASAFE_WORK_DIR if it exists
        inasafe_work_dir = base_data_dir()

        expected_result = ('%s/shakemaps-extracted/20131105060809/impact'
                           '-nearest.tif') % inasafe_work_dir
        message = 'Got: %s, Expected: %s' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

        expected_result = ('%s/shakemaps-extracted/20131105060809/impacts'
                           '.html') % inasafe_work_dir

        message = 'Got: %s, Expected: %s' % (fatalities_html, expected_result)
        self.assertEqual(fatalities_html, expected_result, message)

        expected_fatalities = {2: 0.0,
                               3: 0.0,
                               4: 0.000036387775168853676,
                               5: 0.0,
                               6: 0.0,
                               7: 0.0,
                               8: 0.0,
                               9: 0.0}
        message = 'Got: %s, Expected: %s' % (
            shake_event.fatality_counts, expected_fatalities)
        self.assertEqual(
            shake_event.fatality_counts, expected_fatalities, message)

    def test_bounds_to_rect(self):
        """Test that we can calculate the event bounds properly"""
        shake_event = ShakeEvent(SHAKE_ID, data_is_local_flag=True)
        bounds = shake_event.bounds_to_rectangle().toString()
        expected_result = (
            '139.3700000000000045,-3.6787500000000000 : '
            '141.8700000000000045,-1.1812499999999999')
        message = 'Got:\n%s\nExpected:\n%s\n' % (bounds, expected_result)
        self.assertEqual(bounds, expected_result, message)

    def test_sorted_impacted_cities(self):
        """Test getting impacted cities sorted by mmi then population."""
        shake_event = ShakeEvent(SHAKE_ID, data_is_local_flag=True)
        table = shake_event.sorted_impacted_cities()

        file_path = unique_filename(
            prefix='test_sorted_impacted_cities',
            suffix='.txt',
            dir=temp_dir('test'))
        cities_file = file(file_path, 'w')
        cities_file.writelines(str(table))
        cities_file.close()
        table = str(table).replace(', \'', ',\n\'')
        table += '\n'

        fixture_path = os.path.join(
            data_dir(), 'tests', 'test_sorted_impacted_cities.txt')
        cities_file = file(fixture_path)
        expected_string = cities_file.read()
        cities_file.close()
        expected_string = expected_string.replace(', \'', ',\n\'')

        self.max_diff = None
        message = 'Expectation:\n%s, Got\n%s' % (expected_string, table)
        self.assertEqual(expected_string, table, message)

    def test_impacted_cities_table(self):
        """Test getting impacted cities table."""
        shake_event = ShakeEvent(SHAKE_ID, data_is_local_flag=True)
        table, path = shake_event.impacted_cities_table()
        expected_string = [
            '<td>Jayapura</td><td>134</td><td>I</td>',
            '<td>Abepura</td><td>62</td><td>I</td>']
        table = table.toNewlineFreeString().replace('   ', '')
        for string in expected_string:
            self.assertIn(string, table)

        self.max_diff = None

        # Get the os environment INASAFE_WORK_DIR if it exists
        inasafe_work_dir = base_data_dir()
        expected_path = (
            '%s/shakemaps-extracted/20131105060809/affected-cities.html' %
            inasafe_work_dir)
        message = 'Got:\n%s\nExpected:\n%s\n' % (path, expected_path)
        self.assertEqual(path, expected_path, message)

    def test_fatalities_table(self):
        """Test rendering a fatalities table."""
        shake_event = ShakeEvent(SHAKE_ID, data_is_local_flag=True)
        shake_event.calculate_impacts()
        result = shake_event.impact_table()

        # TODO compare actual content of impact table...

        # Get the os environment INASAFE_WORK_DIR if it exists
        inasafe_work_dir = base_data_dir()
        expected_result = (
            '%s/shakemaps-extracted/20131105060809/impacts.html' %
            inasafe_work_dir)
        message = 'Got:\n%s\nExpected:\n%s' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

    def test_event_info_dict(self):
        """Test we can get a dictionary of location info nicely."""
        shake_event = ShakeEvent(SHAKE_ID, data_is_local_flag=True)
        result = shake_event.event_dict()
        #noinspection PyUnresolvedReferences
        expected_dict = {
            'place-name': u'n/a',
            'depth-name': u'Depth',
            'fatalities-name': u'Estimated fatalities',
            'fatalities-count': u'0',  # 44 only after render
            'elapsed-time': u'',  # empty as it will change
            'legend-name': u'Population density',
            'fatalities-range': '0 - 100',
            'longitude-name': u'Longitude',
            'located-label': u'Located',
            'distance-unit': u'km',
            'bearing-compass': u'n/a',
            'elapsed-time-name': u'Elapsed time since event',
            'exposure-table-name': u'Estimated number of people '
                                   u'affected by each MMI level',
            'longitude-value': u'140\xb037\'12.00"E',
            'city-table-name': u'Places Affected',
            'bearing-text': u'bearing',
            'limitations': (
                u'This impact estimation is automatically generated and only '
                u'takes into account the population and cities affected by '
                u'different levels of ground shaking. The estimate is based '
                u'on ground shaking data from BMKG, population density data '
                u'from asiapop.org, place information from geonames.org and '
                u'software developed by BNPB. Limitations in the estimates of '
                u'ground shaking, population  data and place names datasets '
                u'may result in significant misrepresentation of the '
                u'on-the-ground situation in the figures shown here. '
                u'Consequently decisions should not be made solely on the '
                u'information presented here and should always be verified by '
                u'ground truthing and other reliable information sources. The '
                u'fatality calculation assumes that no fatalities occur for '
                u'shake levels below MMI 4. Fatality counts of less than 50 '
                u'are disregarded.'),
            'depth-unit': u'km',
            'latitude-name': u'Latitude',
            'mmi': '3.6',
            'map-name': u'Estimated Earthquake Impact',
            'date': '5-11-2013',
            'bearing-degrees': '0.00\xb0',
            'formatted-date-time': '05-Nov-13 06:08:09 ',
            'distance': '0.00',
            'direction-relation': u'of',
            'credits': (
                u'Supported by the Australia-Indonesia Facility for Disaster '
                u'Reduction, Geoscience Australia and the World Bank-GFDRR.'),
            'latitude-value': u'2\xb025\'48.00"S',
            'time': '6:8:9',
            'depth-value': '10.0'}
        result['elapsed-time'] = u''
        message = 'Got:\n%s\nExpected:\n%s\n' % (result, expected_dict)
        self.max_diff = None
        difference = DictDiffer(result, expected_dict)
        print difference.all()
        self.assertDictEqual(expected_dict, result, message)

    def test_event_info_string(self):
        """Test we can get a location info string nicely."""
        shake_event = ShakeEvent(SHAKE_ID, data_is_local_flag=True)
        degree_symbol = unichr(176)
        expected_result = (
            'M 3.6 5-11-2013 6:8:9 Latitude: 2%s25\'48.00"S Longitude: '
            '140%s37\'12.00"E Depth: 10.0km Located 0.00km n/a of n/a'
            % (degree_symbol, degree_symbol))
        result = shake_event.event_info()
        message = ('Got:\n%s\nExpected:\n%s\n' %
                   (result, expected_result))
        self.assertEqual(result, expected_result, message)

    def test_bearing_to_cardinal(self):
        """Test we can convert a bearing to a cardinal direction."""
        shake_event = ShakeEvent(SHAKE_ID, data_is_local_flag=True)

        # Ints should work
        expected_result = 'SSE'
        result = shake_event.bearing_to_cardinal(160)
        message = ('Got:\n%s\nExpected:\n%s\n' %
                   (result, expected_result))
        self.assertEqual(result, expected_result, message)

        # Floats should work
        expected_result = 'SW'
        result = shake_event.bearing_to_cardinal(225.4)
        message = ('Got:\n%s\nExpected:\n%s\n' %
                   (result, expected_result))
        self.assertEqual(result, expected_result, message)

        # non numeric data as input should return None
        expected_result = None
        result = shake_event.bearing_to_cardinal('foo')
        message = ('Got:\n%s\nExpected:\n%s\n' %
                   (result, expected_result))
        self.assertEqual(result, expected_result, message)

    def test_i18n(self):
        """See if internationalisation is working."""
        shake_event = ShakeEvent(
            SHAKE_ID, locale='id', data_is_local_flag=True)
        shaking = shake_event.mmi_shaking(5)
        expected_shaking = 'Sedang'
        self.assertEqual(expected_shaking, shaking)


class DictDiffer(object):
    """
    Taken from
    http://stackoverflow.com/questions/1165352/
                  fast-comparison-between-two-python-dictionary
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """

    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(
            past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        """Differences between two dictionaries as items added."""
        return self.set_current - self.intersect

    def removed(self):
        """Differences between two dictionaries as items removed."""
        return self.set_past - self.intersect

    def changed(self):
        """Differences between two dictionaries as values changed."""
        return set(o for o in self.intersect if
                   self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        """Differences between 2 dictionaries as values not changed."""
        return set(o for o in self.intersect if
                   self.past_dict[o] == self.current_dict[o])

    def all(self):
        """Test all."""
        string = 'Added: %s\n' % self.added()
        string += 'Removed: %s\n' % self.removed()
        string += 'changed: %s\n' % self.changed()
        return string

if __name__ == '__main__':
    suite = unittest.makeSuite(TestShakeEvent, 'test_local_cities')
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main()
