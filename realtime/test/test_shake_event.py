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
from safe.common.testing import get_qgis_app

__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '2/08/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import shutil
import unittest
import logging
import difflib

import ogr
import PyQt4

# pylint: disable=E0611
# pylint: disable=W0611
from qgis.core import QgsFeatureRequest
# pylint: enable=E0611
# pylint: enable=W0611
from safe.api import unique_filename, temp_dir
from realtime.utils import shakemap_extract_dir, shakemap_zip_dir, data_dir
from realtime.shake_event import ShakeEvent
# The logger is intialised in utils.py by init
LOGGER = logging.getLogger('InaSAFE')
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestShakeEvent(unittest.TestCase):
    """Tests relating to shake events"""

    def setUp(self):
        """Copy our cached dataset from the fixture dir to the cache dir"""
        output_file = '20120726022003.out.zip'
        input_file = '20120726022003.inp.zip'
        output_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../fixtures',
            output_file))
        input_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../fixtures',
            input_file))
        shutil.copyfile(output_path,
                        os.path.join(shakemap_zip_dir(), output_file))
        shutil.copyfile(input_path,
                        os.path.join(shakemap_zip_dir(), input_file))

        #TODO Downloaded data should be removed before each test

    def test_grid_xml_file_path(self):
        """Test eventFilePath works(using cached data)"""
        shake_id = '20120726022003'
        expected_path = os.path.join(shakemap_extract_dir(),
                                     shake_id,
                                     'grid.xml')
        shake_event = ShakeEvent(shake_id)
        grid_path = shake_event.grid_file_path()
        self.assertEquals(expected_path, grid_path)

    def test_event_parser(self):
        """Test eventFilePath works (using cached data)"""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        self.assertEquals(26, shake_event.day)
        self.assertEquals(7, shake_event.month)
        self.assertEquals(2012, shake_event.year)
        self.assertEquals(2, shake_event.hour)
        self.assertEquals(15, shake_event.minute)
        self.assertEquals(35, shake_event.second)
        self.assertEquals('WIB', shake_event.timezone)
        self.assertEquals(124.45, shake_event.longitude)
        self.assertEquals(-0.21, shake_event.latitude)
        self.assertEquals(11.0, shake_event.depth)
        self.assertEquals('Southern Molucca Sea', shake_event.location)
        self.assertEquals(122.45, shake_event.x_minimum)
        self.assertEquals(126.45, shake_event.x_maximum)
        self.assertEquals(-2.21, shake_event.y_minimum)
        self.assertEquals(1.79, shake_event.y_maximum)

        grid_xml_data = shake_event.mmi_data
        self.assertEquals(25921, len(grid_xml_data))

        delimited_string = shake_event.mmi_data_to_delimited_text()
        self.assertEqual(578234, len(delimited_string))

    def test_event_grid_to_csv(self):
        """Test grid data can be written to csv"""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        file_path = shake_event.mmi_data_to_delimited_file(force_flag=True)
        delimited_file = file(file_path, 'rt')
        delimited_string = delimited_file.readlines()
        delimited_file.close()
        self.assertEqual(25922, len(delimited_string))

    def test_event_to_raster(self):
        """Check we can convert the shake event to a raster"""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        expected_state = """latitude: -0.21
longitude: 124.45
event_id: 20120726022003
magnitude: 5.0
depth: 11.0
description: None
location: Southern Molucca Sea
day: 26
month: 7
year: 2012
time: None
time_zone: WIB
x_minimum: 122.45
x_maximum: 126.45
y_minimum: -2.21
y_maximum: 1.79
rows: 161.0
columns: 161.0
mmi_data: Populated
population_raster_path: None
impact_file: None
impact_keywords_file: None
fatality_counts: None
displaced_counts: None
affected_counts: None
extent_with_cities: Not set
zoom_factor: 1.25
search_boxes: None
"""
        state = str(shake_event)
        message = (('Expected:\n----------------\n%s'
                    '\n\nGot\n------------------\n%s\n') %
                   (expected_state, state))
        assert state == expected_state, message
        raster_path = shake_event.mmi_data_to_raster(force_flag=True)
        assert os.path.exists(raster_path)
        expected_qml = raster_path.replace('tif', 'qml')
        assert os.path.exists(expected_qml)
        expected_keywords = raster_path.replace('tif', 'keywords')
        assert os.path.exists(expected_keywords)

    def test_event_to_shapefile(self):
        """Check we can convert the shake event to a raster"""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        file_path = shake_event.mmi_data_to_shapefile(force_flag=True)
        assert os.path.exists(file_path)
        expected_qml = file_path.replace('shp', 'qml')
        message = '%s not found' % expected_qml
        assert os.path.exists(expected_qml), message

    def check_feature_count(self, thePath, theCount):
        data_source = ogr.Open(thePath)
        base_name = os.path.splitext(os.path.basename(thePath))[0]
        # do a little query to make sure we got some results...
        sql_statement = 'select * from \'%s\' order by MMI asc' % base_name
        #print sql_statement
        layer = data_source.ExecuteSQL(sql_statement)
        count = layer.GetFeatureCount()
        flag = count == theCount
        message = ''
        if not flag:
            message = 'Expected %s features, got %s' % (theCount, count)
        data_source.ReleaseResultSet(layer)
        data_source.Destroy()
        return flag, message

    def test_event_to_contours(self):
        """Check we can extract contours from the event"""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        file_path = shake_event.mmi_data_to_contours(force_flag=True,
                                                     algorithm='invdist')
        assert self.check_feature_count(file_path, 16)
        assert os.path.exists(file_path)
        expected_qml = file_path.replace('shp', 'qml')
        message = '%s not found' % expected_qml
        assert os.path.exists(expected_qml), message

        file_path = shake_event.mmi_data_to_contours(force_flag=True,
                                                     algorithm='nearest')
        assert self.check_feature_count(file_path, 132)
        file_path = shake_event.mmi_data_to_contours(force_flag=True,
                                                     algorithm='average')
        assert self.check_feature_count(file_path, 132)

    def test_local_cities(self):
        """Test that we can retrieve the cities local to the event"""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        # Get teh mem layer
        cities_layer = shake_event.local_cities_memory_layer()
        provider = cities_layer.dataProvider()

        expected_feature_count = 6
        self.assertEquals(provider.featureCount(), expected_feature_count)
        strings = []
        request = QgsFeatureRequest()
        for feature in cities_layer.getFeatures(request):
            # fetch map of attributes
            attributes = cities_layer.dataProvider().attributeIndexes()
            for attribute_key in attributes:
                strings.append("%d: %s\n" % (
                    attribute_key, feature[attribute_key].toString()))
            strings.append('------------------\n')
        LOGGER.debug('Mem table:\n %s' % strings)
        file_path = unique_filename(prefix='test_local_cities',
                                    suffix='.txt',
                                    dir=temp_dir('test'))
        cities_file = file(file_path, 'wt')
        cities_file.writelines(strings)
        cities_file.close()

        fixture_path = os.path.join(data_dir(),
                                    'tests',
                                    'test_local_cities.txt')
        cities_file = file(fixture_path, 'rt')
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
        """Test that we can retrieve the cities local to the event"""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        file_path = shake_event.cities_to_shapefile()
        assert os.path.exists(file_path)

    def test_cities_search_boxes_to_shape(self):
        """Test that we can retrieve the search boxes used to find cities."""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        file_path = shake_event.city_search_boxes_to_shapefile()
        assert os.path.exists(file_path)

    def test_calculate_fatalities(self):
        """Test that we can calculate fatalities."""
        LOGGER.debug(QGIS_APP.showSettings())
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        result, fatalities_html = shake_event.calculate_impacts()

        expected_result = (
            '/tmp/inasafe/realtime/shakemaps-extracted'
            '/20120726022003/impact-nearest.tif')
        message = 'Got:\n%s\nExpected:\n%s\n' % (result, expected_result)
        assert result == expected_result, message

        expected_result = (
            '/tmp/inasafe/realtime/shakemaps-extracted'
            '/20120726022003/impacts.html')

        message = 'Got:\n%s\nExpected:\n%s\n' % (
            fatalities_html,
            expected_result)
        assert fatalities_html == expected_result, message

        expected_fatalities = {2: 0.0,  # rounded from 0.47386375223673427,
                               3: 0.0,  # rounded from 0.024892573693488258,
                               4: 0.0,
                               5: 0.0,
                               6: 0.0,
                               7: 0.0,
                               8: 0.0,
                               9: 0.0}

        message = 'Got:\n%s\nExpected:\n%s\n' % (
            shake_event.fatality_counts, expected_fatalities)
        assert shake_event.fatality_counts == expected_fatalities, message

    def test_bounds_to_rect(self):
        """Test that we can calculate the event bounds properly"""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        bounds = shake_event.bounds_to_rectangle().toString()
        expected_result = (
            '122.4500000000000028,-2.2100000000000000 : '
            '126.4500000000000028,1.7900000000000000')
        message = 'Got:\n%s\nExpected:\n%s\n' % (bounds, expected_result)
        assert bounds == expected_result, message

    def test_romanize(self):
        """Test we can convert MMI values to float."""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)

        values = range(2, 10)
        expected_result = ['II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
        result = []
        for value in values:
            result.append(shake_event.romanize(value))
        message = 'Got:\n%s\nExpected:\n%s\n' % (result, expected_result)
        assert result == expected_result, message

    def test_sorted_impacted_cities(self):
        """Test getting impacted cities sorted by mmi then population."""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        table = shake_event.sorted_impacted_cities()

        file_path = unique_filename(
            prefix='test_sorted_impacted_cities',
            suffix='.txt',
            dir=temp_dir('test'))
        cities_file = file(file_path, 'wt')
        cities_file.writelines(str(table))
        cities_file.close()
        table = str(table).replace(', \'', ',\n\'')
        table += '\n'

        fixture_path = os.path.join(
            data_dir(), 'tests', 'test_sorted_impacted_cities.txt')
        cities_file = file(fixture_path, 'rt')
        expected_string = cities_file.read()
        cities_file.close()
        expected_string = expected_string.replace(', \'', ',\n\'')

        self.max_diff = None
        self.assertEqual(expected_string, table)

    def test_impacted_cities_table(self):
        """Test getting impacted cities table."""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        table, path = shake_event.impacted_cities_table()
        expected_string = [
            '<td>Tondano</td><td>33</td><td>I</td>',
            '<td>Luwuk</td><td>47</td><td>I</td>',
            '<td>Bitung</td><td>137</td><td>I</td>',
            '<td>Manado</td><td>451</td><td>I</td>',
            '<td>Gorontalo</td><td>144</td><td>II</td>']
        table = table.toNewlineFreeString().replace('   ', '')
        for myString in expected_string:
            self.assertIn(myString, table)

        self.max_diff = None
        expected_path = (
            '/tmp/inasafe/realtime/shakemaps-extracted/'
            '20120726022003/affected-cities.html')
        message = 'Got:\n%s\nExpected:\n%s\n' % (path, expected_path)
        assert path == expected_path, message

    def test_fatalities_table(self):
        """Test rendering a fatalities table."""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        shake_event.calculate_impacts()
        result = shake_event.impact_table()
        # TODO compare actual content of impact table...
        expected_result = (
            '/tmp/inasafe/realtime/shakemaps-extracted/'
            '20120726022003/impacts.html')
        message = ('Got:\n%s\nExpected:\n%s' %
                   (result, expected_result))
        assert result == expected_result, message

    def test_event_info_dict(self):
        """Test we can get a dictionary of location info nicely."""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        result = shake_event.event_dict()
        expected_dict = {'place-name': PyQt4.QtCore.QString(u'n/a'),
                         'depth-name': PyQt4.QtCore.QString(u'Depth'),
                         'fatalities-name': PyQt4.QtCore.QString(
                             u'Estimated fatalities'),
                         'fatalities-count': u'0',  # 44 only after render
                         'elapsed-time': u'',  # empty as it will change
                         'legend-name': PyQt4.QtCore.QString(
                             u'Population density'),
                         'fatalities-range': '0 - 100',
                         'longitude-name': PyQt4.QtCore.QString(u'Longitude'),
                         'located-label': PyQt4.QtCore.QString(u'Located'),
                         'distance-unit': PyQt4.QtCore.QString(u'km'),
                         'bearing-compass': u'n/a',
                         'elapsed-time-name': PyQt4.QtCore.QString(
                             u'Elapsed time since event'),
                         'exposure-table-name': PyQt4.QtCore.QString(
                             u'Estimated number of people affected by each '
                             u'MMI level'),
                         'longitude-value': u'124\xb027\'0.00"E',
                         'city-table-name': PyQt4.QtCore.QString(
                             u'Places Affected'),
                         'bearing-text': PyQt4.QtCore.QString(u'bearing'),
                         'limitations': PyQt4.QtCore.QString(
                             u'This impact estimation is automatically '
                             u'generated and only takes into account the '
                             u'population and cities affected by different '
                             u'levels of ground shaking. The estimate is '
                             u'based on ground shaking data from BMKG, '
                             u'population density data from asiapop.org, '
                             u'place information from geonames.org and '
                             u'software developed by BNPB. Limitations in '
                             u'the estimates of ground shaking, '
                             u'population  data and place names datasets may'
                             u' result in significant misrepresentation of '
                             u'the on-the-ground situation in the figures '
                             u'shown here. Consequently decisions should not'
                             u' be made solely on the information presented '
                             u'here and should always be verified by ground '
                             u'truthing and other reliable information '
                             u'sources. The fatality calculation assumes '
                             u'that no fatalities occur for shake levels '
                             u'below MMI 4. Fatality counts of less than 50 '
                             u'are disregarded.'),
                         'depth-unit': PyQt4.QtCore.QString(u'km'),
                         'latitude-name': PyQt4.QtCore.QString(u'Latitude'),
                         'mmi': '5.0',
                         'map-name': PyQt4.QtCore.QString(
                             u'Estimated Earthquake Impact'),
                         'date': '26-7-2012',
                         'bearing-degrees': '0.00\xb0',
                         'formatted-date-time': '26-Jul-12 02:15:35 ',
                         'distance': '0.00',
                         'direction-relation': PyQt4.QtCore.QString(u'of'),
                         'credits': PyQt4.QtCore.QString(
                             u'Supported by the Australia-Indonesia Facility'
                             u' for Disaster Reduction, Geoscience Australia '
                             u'and the World Bank-GFDRR.'),
                         'latitude-value': u'0\xb012\'36.00"S',
                         'time': '2:15:35', 'depth-value': '11.0'}
        result['elapsed-time'] = u''
        message = 'Got:\n%s\nExpected:\n%s\n' % (result, expected_dict)
        self.max_diff = None
        difference = DictDiffer(result, expected_dict)
        print difference.all()
        self.assertDictEqual(expected_dict, result, message)

    def test_event_info_string(self):
        """Test we can get a location info string nicely."""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)
        degree_symbol = unichr(176)
        expected_result = (
            'M 5.0 26-7-2012 2:15:35 Latitude: 0%s12\'36.00"S Longitude: '
            '124%s27\'0.00"E Depth: 11.0km Located 0.00km n/a of n/a'
            % (degree_symbol, degree_symbol))
        result = shake_event.event_info()
        message = ('Got:\n%s\nExpected:\n%s\n' %
                   (result, expected_result))
        assert result == expected_result, message

    def test_bearing_to_cardinal(self):
        """Test we can convert a bearing to a cardinal direction."""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id)

        # Ints should work
        expected_result = 'SSE'
        result = shake_event.bearing_to_cardinal(160)
        message = ('Got:\n%s\nExpected:\n%s\n' %
                   (result, expected_result))
        assert result == expected_result, message

        # Floats should work
        expected_result = 'SW'
        result = shake_event.bearing_to_cardinal(225.4)
        message = ('Got:\n%s\nExpected:\n%s\n' %
                   (result, expected_result))
        assert result == expected_result, message

        # non numeric data as input should return None
        expected_result = None
        result = shake_event.bearing_to_cardinal('foo')
        message = ('Got:\n%s\nExpected:\n%s\n' %
                   (result, expected_result))
        assert result == expected_result, message

    def test_i18n(self):
        """See if internationalisation is working."""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id, locale='id')
        shaking = shake_event.mmi_shaking(5)
        expected_shaking = 'Sedang'
        self.assertEqual(expected_shaking, shaking)

    def test_extract_date_time(self):
        """Check that we extract date and time correctly."""
        shake_id = '20120726022003'
        shake_event = ShakeEvent(shake_id, locale='en')
        shake_event.extract_datetime('2012-08-07T01:55:12WIB')
        self.assertEqual(1, shake_event.hour)
        self.assertEqual(55, shake_event.minute)
        self.assertEqual(12, shake_event.second)
        shake_event.extract_datetime('2013-02-07T22:22:37WIB')
        self.assertEqual(22, shake_event.hour)
        self.assertEqual(22, shake_event.minute)
        self.assertEqual(37, shake_event.second)


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
