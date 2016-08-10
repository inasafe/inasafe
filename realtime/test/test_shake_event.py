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
__author__ = 'tim@kartoza.com'
__version__ = '0.5.0'
__date__ = '2/08/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import difflib
import logging
import os
import shutil
import unittest
import datetime
import pytz

import requests
from qgis.core import QgsFeatureRequest

from realtime.push_rest import InaSAFEDjangoREST
from realtime.earthquake.push_shake import \
    push_shake_event_to_rest
from realtime.earthquake.shake_event import ShakeEvent
from realtime.utilities import base_data_dir
from realtime.utilities import (
    shakemap_extract_dir,
    data_dir,
    realtime_logger_name)
from safe.common.utilities import temp_dir, unique_filename
from safe.common.version import get_version
from safe.test.utilities import standard_data_path, get_qgis_app

# The logger is initialised in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

# Shake ID for this test
shakes_id = ['20131105060809', '20150918201057']
SHAKE_ID = shakes_id[0]
SHAKE_ID_2 = shakes_id[1]


class TestShakeEvent(unittest.TestCase):
    """Tests relating to shake events"""
    # noinspection PyPep8Naming
    def setUp(self):
        """Copy our cached dataset from the fixture dir to the cache dir."""
        # Since ShakeEvent will be using sftp_shake_data, we'll copy the grid
        # file inside 20131105060809 folder to
        # shakemap_extract_dir/20131105060809/grid.xml
        shake_path = standard_data_path('hazard', 'shake_data')

        for shake_id in shakes_id:
            input_path = os.path.abspath(
                os.path.join(shake_path, shake_id, 'output/grid.xml'))
            target_folder = os.path.join(
                shakemap_extract_dir(), shake_id)
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            target_path = os.path.abspath(
                    os.path.join(target_folder, 'grid.xml'))
            shutil.copyfile(input_path, target_path)

    # noinspection PyPep8Naming
    def tearDown(self):
        """Delete the cached data."""
        for shake_id in shakes_id:
            target_path = os.path.join(shakemap_extract_dir(), shake_id)
            shutil.rmtree(target_path)

    def test_grid_file_path(self):
        """Test grid_file_path works using cached data."""
        expected_path = os.path.join(
            shakemap_extract_dir(), SHAKE_ID, 'grid.xml')
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            data_is_local_flag=True)
        grid_path = shake_event.grid_file_path()
        self.assertEquals(expected_path, grid_path)

    def test_to_string(self):
        """Test __str__ works properly."""
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            data_is_local_flag=True)
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
            'time: 2013-11-05 06:08:09+07:07\n'
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

    def test_local_cities(self):
        """Test that we can retrieve the cities local to the event"""
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            data_is_local_flag=True)
        # Get teh mem layer
        cities_layer = shake_event.local_cities_memory_layer()
        provider = cities_layer.dataProvider()

        expected_feature_count = 3
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

    def test_mmi_potential_damage(self):
        """Test mmi_potential_damage function."""
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            data_is_local_flag=True)
        values = range(1, 11)
        expected_result = ['None', 'None', 'None', 'None', 'Very light',
                           'Light', 'Moderate', 'Mod/Heavy', 'Heavy',
                           'Very heavy']
        result = []
        for value in values:
            result.append(shake_event.mmi_potential_damage(value))
        message = 'Got:\n%s\nExpected:\n%s\n' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

    def test_cities_to_shape(self):
        """Test that we can retrieve the cities local to the event."""
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            data_is_local_flag=True)
        file_path = shake_event.cities_to_shapefile()
        self.assertTrue(os.path.exists(file_path))

    def test_cities_search_boxes_to_shape(self):
        """Test that we can retrieve the search boxes used to find cities."""
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            data_is_local_flag=True)
        file_path = shake_event.city_search_boxes_to_shapefile()
        self.assertTrue(os.path.exists(file_path))

    def test_calculate_fatalities(self):
        """Test that we can calculate fatalities."""
        LOGGER.debug(QGIS_APP.showSettings())
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            data_is_local_flag=True)
        result, fatalities_html = shake_event.calculate_impacts()

        # Get the os environment INASAFE_WORK_DIR if it exists
        inasafe_work_dir = base_data_dir()

        expected_result = os.path.join(
            inasafe_work_dir,
            'shakemaps-extracted/20131105060809/impact-nearest.tif')
        message = 'Got: %s, Expected: %s' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

        expected_result = os.path.join(
            inasafe_work_dir,
            'shakemaps-extracted/20131105060809/impacts.html')

        message = 'Got: %s, Expected: %s' % (fatalities_html, expected_result)
        self.assertEqual(fatalities_html, expected_result, message)

        expected_fatalities = {2: 0.0,
                               3: 0.0,
                               4: 0.0,
                               5: 0.0,
                               6: 0.0,
                               7: 0.0,
                               8: 0.0,
                               9: 0.0,
                               10: 0.0}
        message = 'Got: %s, Expected: %s' % (
            shake_event.fatality_counts, expected_fatalities)
        self.assertDictEqual(
            shake_event.fatality_counts, expected_fatalities, message)

    def test_sorted_impacted_cities(self):
        """Test getting impacted cities sorted by mmi then population."""
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            data_is_local_flag=True)
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
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            data_is_local_flag=True)
        table, path = shake_event.impacted_cities_table()
        table_dict = table.to_dict()
        expected_string = [
            {
                'name': 'Jayapura',
                'population': '256'
            },
            {
                'name': 'Sentani',
                'population': '111'
            },
            {
                'name': 'Waris',
                'population': '48'
            }
        ]
        for i in range(1, len(table.rows)):
            self.assertEqual(
                table_dict['rows'][i]['cells'][1]
                ['content']['text'][0]['text'],
                expected_string[i - 1].get('name'))
            self.assertEqual(
                table_dict['rows'][i]['cells'][2]
                ['content']['text'][0]['text'],
                expected_string[i - 1].get('population'))

        self.max_diff = None

        # Get the os environment INASAFE_WORK_DIR if it exists
        inasafe_work_dir = base_data_dir()
        expected_path = os.path.join(
            inasafe_work_dir,
            'shakemaps-extracted/20131105060809/affected-cities.html')
        message = 'Got:\n%s\nExpected:\n%s\n' % (path, expected_path)
        self.assertEqual(path, expected_path, message)

    def test_fatalities_table(self):
        """Test rendering a fatalities table."""
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            data_is_local_flag=True)
        shake_event.calculate_impacts()
        result = shake_event.impact_table()

        # TODO compare actual content of impact table...

        # Get the os environment INASAFE_WORK_DIR if it exists
        inasafe_work_dir = base_data_dir()
        expected_result = os.path.join(
            inasafe_work_dir,
            'shakemaps-extracted/20131105060809/impacts.html')
        message = 'Got:\n%s\nExpected:\n%s' % (result, expected_result)
        self.assertEqual(result, expected_result, message)

    def test_event_info_dict(self):
        """Test we can get a dictionary of location info nicely."""
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            data_is_local_flag=True)
        result = shake_event.event_dict()
        software_tag = ('This report was created using InaSAFE version %s. '
                        'Visit http://inasafe.org for more information.' %
                        get_version())

        # noinspection PyUnresolvedReferences
        expected_dict = {
            'place-name': u'Jayapura',
            'shake-grid-location': u'Papua',
            'depth-name': u'Depth',
            'fatalities-name': u'Estimated fatalities',
            'fatalities-count': u'0',  # 44 only after render
            'elapsed-time': u'',  # empty as it will change
            'legend-name': u'Population count per grid cell',
            'fatalities-range': '0 - 100',
            'longitude-name': u'Longitude',
            'located-label': u'Located',
            'distance-unit': u'km',
            'bearing-compass': u'NNW',
            'elapsed-time-name': u'Elapsed time since event',
            'exposure-table-name': u'Estimated number of people '
                                   u'affected by each MMI level',
            'longitude-value': u'140\xb037\u203212.00\u2033E',
            'city-table-name': u'Nearby Places',
            'bearing-text': u'bearing',
            'limitations': (
                u'This impact estimation is automatically generated and only '
                u'takes into account the population and cities affected by '
                u'different levels of ground shaking. The estimate is based '
                u'on ground shaking data from BMKG, population count data '
                u'derived by Australian Government from worldpop.org.uk, '
                u'place information from geonames.org and software developed '
                u'by BNPB. Limitations in the estimates of ground shaking, '
                u'population and place names datasets may result in '
                u'significant misrepresentation of the on-the-ground '
                u'situation in the figures shown here. Consequently '
                u'decisions should not be made solely on the information '
                u'presented here and should always be verified by ground '
                u'truthing and other reliable information sources. The '
                u'fatality calculation assumes that no fatalities occur '
                u'for shake levels below MMI 4. Fatality counts of less than '
                u'50 are disregarded.'),
            'depth-unit': u'km',
            'latitude-name': u'Latitude',
            'mmi': '3.6',
            'map-name': u'Estimated Earthquake Impact',
            'date': '5-11-2013',
            'bearing-degrees': '-28.72\xb0',
            'formatted-date-time': '05-Nov-13 06:08:09 +0707',
            'distance': '0.02',
            'direction-relation': u'of',
            'software-tag': software_tag,
            'credits': (
                u'Supported by the Australian Government, Geoscience '
                u'Australia and the World Bank-GFDRR.'),
            'latitude-value': u'2\xb025\u203248.00\u2033S',
            'time': '6:8:9',
            'depth-value': '10.0'}
        result['elapsed-time'] = u''
        message = 'Got:\n%s\nExpected:\n%s\n' % (result, expected_dict)
        self.max_diff = None
        difference = DictDiffer(result, expected_dict)
        LOGGER.debug(difference.all())
        self.assertDictEqual(expected_dict, result, message)

    def test_event_info_string(self):
        """Test we can get a location info string nicely."""
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            data_is_local_flag=True)
        expected_result = (
            u"M 3.6 5-11-2013 6:8:9 "
            u"Latitude: 2°25′48.00″S "
            u"Longitude: 140°37′12.00″E "
            u"Depth: 10.0km Located 0.02km NNW of Papua")
        result = shake_event.event_info()
        message = ('Got:\n%s\nExpected:\n%s\n' %
                   (result, expected_result))
        self.assertEqual(result, expected_result, message)

    def test_render_map(self):
        """Test render_map function in shake_event."""
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            data_is_local_flag=True)
        # Render Map
        shake_event.render_map()
        # There should be exist:
        # 1. SHAKE_ID-en.pdf
        # 2. SHAKE_ID-en.png
        # 3. SHAKE_ID-thumb-en.png
        # 4. SHAKE_ID-metadata-en.pickle
        # 5. mmi-cities.shp, shx, dbf, prj, qml
        # 6. mmi-contours-nearest.shp, shx, dbf, prj, qml
        # 7. city-search-boxes.shp, shx, dbf, prj, qml
        # 8. composer-template.qpt
        # 9. project.qgs
        target_dir = os.path.join(shakemap_extract_dir(), SHAKE_ID)
        shapefile_extension = ['shp', 'shx', 'dbf', 'prj', 'qml']
        # 1
        pdf_path = os.path.join(target_dir, '%s-en.pdf' % SHAKE_ID)
        message = 'PDF Report is not generated successfully in %s' % pdf_path
        self.assertTrue(os.path.exists(pdf_path), message)
        # 2
        png_path = os.path.join(target_dir, '%s-en.png' % SHAKE_ID)
        message = 'PNG Report is not generated successfully in %s' % png_path
        self.assertTrue(os.path.exists(png_path), message)
        # 3
        thumbnail_path = os.path.join(target_dir, '%s-thumb-en.png' % SHAKE_ID)
        message = 'PNG Thumbnail is not generated successfully in %s' % (
            thumbnail_path)
        self.assertTrue(os.path.exists(thumbnail_path), message)
        # 4
        metadata_path = os.path.join(
            target_dir, '%s-metadata-en.pickle' % SHAKE_ID)
        message = 'Metadata file is not generated successfully in %s' % (
            metadata_path)
        self.assertTrue(os.path.exists(metadata_path), message)
        # 5. mmi-cities.shp, shx, dbf, prj, qml
        mmi_cities_path = os.path.join(target_dir, 'mmi-cities.shp')
        for extension in shapefile_extension:
            file_path = mmi_cities_path.replace('shp', extension)
            message = 'mmi-cities.%s is not generated successfully in %s' % (
                extension, file_path)
            self.assertTrue(os.path.exists(file_path), message)
        # 6. mmi-contours-nearest.shp, shx, dbf, prj, qml
        mmi_contours_path = os.path.join(
            target_dir, 'mmi-contours-nearest.shp')
        for extension in shapefile_extension:
            file_path = mmi_contours_path.replace('shp', extension)
            message = (
                'mmi-contours-nearest.%s is not generated successfully in '
                '%s') % (extension, file_path)
            self.assertTrue(os.path.exists(file_path), message)
        # 7. city-search-boxes.shp, shx, dbf, prj, qml
        city_search_boxes_path = os.path.join(
            target_dir, 'city-search-boxes.shp')
        for extension in shapefile_extension:
            file_path = city_search_boxes_path.replace('shp', extension)
            message = (
                'city-search-boxes.%s is not generated successfully in '
                '%s') % (extension, file_path)
            self.assertTrue(os.path.exists(file_path), message)
        # 8
        composer_template_path = os.path.join(
            target_dir, 'composer-template.qpt')
        message = (
            'Composer template file is not generated successfully in %s' %
            composer_template_path)
        self.assertTrue(os.path.exists(composer_template_path), message)
        # 9
        qgs_project_path = os.path.join(
            target_dir, 'project.qgs')
        message = 'QGIS Project file is not generated successfully in %s' % (
            qgs_project_path)
        self.assertTrue(os.path.exists(qgs_project_path), message)

    def test_bearing_to_cardinal(self):
        """Test we can convert a bearing to a cardinal direction."""
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            data_is_local_flag=True)

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
        working_dir = shakemap_extract_dir()
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID,
            locale='id',
            data_is_local_flag=True)
        shaking = shake_event.mmi_shaking(5)
        expected_shaking = 'Sedang'
        self.assertEqual(expected_shaking, shaking)

    def test_login_to_realtime(self):
        # get logged in session
        inasafe_django = InaSAFEDjangoREST()
        self.assertTrue(inasafe_django.is_logged_in)

    def _push_to_realtime(self):
        # only do the test if realtime test server is configured
        inasafe_django = InaSAFEDjangoREST()
        if inasafe_django.is_configured():

            working_dir = shakemap_extract_dir()
            shake_event = ShakeEvent(
                working_dir=working_dir,
                event_id=SHAKE_ID,
                locale='en',
                data_is_local_flag=True)
            # generate report
            shake_event.render_map()
            # push to realtime django
            push_shake_event_to_rest(shake_event)
            # check shake event exists
            session = inasafe_django.rest
            response = session.earthquake(SHAKE_ID).GET()
            self.assertEqual(response.status_code, requests.codes.ok)

            event_dict = shake_event.event_dict()
            earthquake_data = {
                'shake_id': shake_event.event_id,
                'magnitude': float(event_dict.get('mmi')),
                'depth': float(event_dict.get('depth-value')),
                'time': shake_event.shake_grid.time,
                'location': {
                    'type': 'Point',
                    'coordinates': [
                        shake_event.shake_grid.longitude,
                        shake_event.shake_grid.latitude
                    ]
                },
                'location_description': event_dict.get('shake-grid-location')
            }

            for key, value in earthquake_data.iteritems():
                if isinstance(value, datetime.datetime):
                    self.assertEqual(
                        datetime.datetime.strptime(
                                response.json()[key], '%Y-%m-%dT%H:%M:%SZ'
                        ).replace(tzinfo=pytz.utc),
                        value
                    )
                else:
                    self.assertEqual(response.json()[key], value)

    def test_uses_grid_location(self):
        """Test regarding issue #2438
        """
        working_dir = shakemap_extract_dir()
        # population_path =
        shake_event = ShakeEvent(
            working_dir=working_dir,
            event_id=SHAKE_ID_2,
            locale='en',
            force_flag=True,
            data_is_local_flag=True,
            # population_raster_path=population_path
        )
        expected_location = 'Yogyakarta'
        self.assertEqual(
            shake_event.event_dict()['shake-grid-location'],
            expected_location)

        inasafe_django = InaSAFEDjangoREST()

        if inasafe_django.is_configured():
            # generate report
            shake_event.render_map()
            # push to realtime django
            retval = push_shake_event_to_rest(shake_event)
            self.assertTrue(retval)
            # check shake event exists
            session = inasafe_django.rest
            response = session.earthquake(SHAKE_ID_2).GET()
            self.assertEqual(response.status_code, requests.codes.ok)

            self.assertEqual(
                response.json()['location_description'],
                shake_event.event_dict()['shake-grid-location'])


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
