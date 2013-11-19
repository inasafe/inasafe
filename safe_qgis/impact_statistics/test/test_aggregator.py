# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe_qgis import breakdown_defaults

__author__ = 'Marco Bernasocchi'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os
import logging

import numpy.testing

from os.path import join
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from qgis.core import QgsVectorLayer

from safe_qgis.safe_interface import (
    TESTDATA,
    BOUNDDATA,
    Raster,
    Vector,
    safe_read_layer)

from safe_qgis.utilities.utilities_for_testing import (
    get_qgis_app,
    set_canvas_crs,
    set_jakarta_extent,
    GEOCRS)

from safe_qgis.widgets.dock import Dock
from safe_qgis.impact_statistics.aggregator import Aggregator
from safe_qgis.utilities.clipper import clip_layer
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.utilities.utilities import (
    extent_to_geo_array)

from safe_qgis.utilities.utilities_for_testing import (
    load_standard_layers,
    setup_scenario,
    load_layers)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
DOCK = Dock(IFACE)

LOGGER = logging.getLogger('InaSAFE')


#noinspection PyArgumentList
class AggregatorTest(unittest.TestCase):
    """Test the InaSAFE GUI"""

    #noinspection PyPep8Naming
    def setUp(self):
        """Fixture run before all tests"""

        self.maxDiff = None  # show full diff for assert errors

        os.environ['LANG'] = 'en'
        DOCK.show_only_visible_layers_flag = True
        load_standard_layers()
        DOCK.cboHazard.setCurrentIndex(0)
        DOCK.cboExposure.setCurrentIndex(0)
        DOCK.cboFunction.setCurrentIndex(0)
        DOCK.run_in_thread_flag = False
        DOCK.show_only_visible_layers_flag = False
        DOCK.set_layer_from_title_flag = False
        DOCK.zoom_to_impact_flag = False
        DOCK.hide_exposure_flag = False
        DOCK.show_intermediate_layers = False
        set_jakarta_extent()

        self._keywordIO = KeywordIO()
        self._defaults = breakdown_defaults()

    def test_combo_aggregation_loaded_project(self):
        """Aggregation combo changes properly according loaded layers"""
        layer_list = [
            DOCK.tr('Entire area'),
            DOCK.tr('kabupaten jakarta singlepart')]
        current_layers = [DOCK.cboAggregation.itemText(i) for i in range(
            DOCK.cboAggregation.count())]

        message = (
            'The aggregation combobox should have:\n %s \nFound: %s'
            % (layer_list, current_layers))
        self.assertEquals(current_layers, layer_list, message)

    def test_aggregation_attribute_in_keywords(self):
        """Aggregation attribute is chosen correctly when present in keywords.
        """
        attribute_key = breakdown_defaults('AGGR_ATTR_KEY')

        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta singlepart',
            aggregation_enabled_flag=True)
        assert result, message
        # Press RUN
        DOCK.accept()
        DOCK.runtime_keywords_dialog.accept()
        attribute = DOCK.aggregator.attributes[attribute_key]
        message = ('The aggregation should be KAB_NAME. Found: %s' % attribute)
        self.assertEqual(attribute, 'KAB_NAME', message)

    def test_check_aggregation_single_attribute(self):
        """Aggregation attribute is chosen correctly when there is only
        one attr available."""
        file_list = ['kabupaten_jakarta_singlepart_1_good_attr.shp']
        #add additional layers
        load_layers(file_list, clear_flag=False)
        attribute_key = breakdown_defaults('AGGR_ATTR_KEY')

        # with 1 good aggregation attribute using
        # kabupaten_jakarta_singlepart_1_good_attr.shp
        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta singlepart 1 good attr')
        assert result, message
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        DOCK.accept()
        DOCK.runtime_keywords_dialog.accept()
        print attribute_key
        print DOCK.aggregator.attributes
        attribute = DOCK.aggregator.attributes[attribute_key]
        message = (
            'The aggregation should be KAB_NAME. Found: %s' % attribute)
        self.assertEqual(attribute, 'KAB_NAME', message)

    #noinspection PyMethodMayBeStatic
    def test_check_aggregation_no_attributes(self):
        """Aggregation attribute chosen correctly when no attr available."""

        file_list = ['kabupaten_jakarta_singlepart_0_good_attr.shp']
        #add additional layers
        load_layers(file_list, clear_flag=False)
        attribute_key = breakdown_defaults('AGGR_ATTR_KEY')
        # with no good aggregation attribute using
        # kabupaten_jakarta_singlepart_0_good_attr.shp
        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta singlepart 0 good attr')
        assert result, message
        # Press RUN
        DOCK.accept()
        DOCK.runtime_keywords_dialog.accept()
        attribute = DOCK.aggregator.attributes[attribute_key]
        message = (
            'The aggregation should be None. Found: %s' % attribute)
        assert attribute is None, message

    #noinspection PyMethodMayBeStatic
    def test_check_aggregation_none_in_keywords(self):
        """Aggregation attribute is chosen correctly when None in keywords."""

        file_list = ['kabupaten_jakarta_singlepart_with_None_keyword.shp']
        #add additional layers
        load_layers(file_list, clear_flag=False)
        attribute_key = breakdown_defaults('AGGR_ATTR_KEY')
        # with None aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart_with_None_keyword.shp
        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta singlepart with None keyword')
        assert result, message
        # Press RUN
        DOCK.accept()
        DOCK.runtime_keywords_dialog.accept()
        attribute = DOCK.aggregator.attributes[attribute_key]
        message = ('The aggregation should be None. Found: %s' % attribute)
        assert attribute is None, message

    def test_preprocessing(self):
        """Preprocessing results are correct.

        TODO - this needs to be fixed post dock refactor.

        """

        # See qgis project in test data: vector_preprocessing_test.qgs
        #add additional layers
        file_list = ['jakarta_crosskabupaten_polygons.shp']
        load_layers(file_list, clear_flag=False)
        file_list = ['kabupaten_jakarta.shp']
        load_layers(file_list, clear_flag=False, data_directory=BOUNDDATA)

        result, message = setup_scenario(
            DOCK,
            hazard='jakarta_crosskabupaten_polygons',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function Vector Hazard',
            aggregation_layer='kabupaten jakarta',
            aggregation_enabled_flag=True)
        assert result, message

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()
        # Press RUN
        DOCK.accept()
        DOCK.runtime_keywords_dialog.accept()

        expected_feature_count = 20
        message = (
            'The preprocessing should have generated %s features, '
            'found %s' % (
                expected_feature_count,
                DOCK.aggregator.preprocessed_feature_count))
        self.assertEqual(
            expected_feature_count,
            DOCK.aggregator.preprocessed_feature_count,
            message)

    def _aggregate(
            self,
            impact_layer,
            expected_results,
            use_native_zonal_stats=False):
        """Helper to calculate aggregation.

        Expected results is split into two lists - one list contains numeric
        attributes, the other strings. This is done so that we can use numpy
        .testing.assert_allclose which doesn't work on strings
        """

        expected_string_results = []
        expected_numeric_results = []

        for item in expected_results:
            string_results = []
            numeric_results = []
            for field in item:
                try:
                    value = float(field)
                    numeric_results.append(value)
                except ValueError:
                    string_results.append(str(field))

            expected_numeric_results.append(numeric_results)
            expected_string_results.append(string_results)

        aggregation_layer = QgsVectorLayer(
            os.path.join(BOUNDDATA, 'kabupaten_jakarta.shp'),
            'test aggregation',
            'ogr')
        # create a copy of aggregation layer
        geo_extent = extent_to_geo_array(
            aggregation_layer.extent(),
            aggregation_layer.crs())

        aggregation_attribute = self._keywordIO.read_keywords(
            aggregation_layer, self._defaults['AGGR_ATTR_KEY'])
        # noinspection PyArgumentEqualDefault
        aggregation_layer = clip_layer(
            layer=aggregation_layer,
            extent=geo_extent,
            explode_flag=True,
            explode_attribute=aggregation_attribute)

        aggregator = Aggregator(None, aggregation_layer)
        # setting up
        aggregator.is_valid = True
        aggregator.layer = aggregation_layer
        aggregator.safe_layer = safe_read_layer(
            str(aggregator.layer.source()))
        aggregator.aoi_mode = False
        aggregator.use_native_zonal_stats = use_native_zonal_stats
        aggregator.aggregate(impact_layer)

        provider = aggregator.layer.dataProvider()
        string_results = []
        numeric_results = []

        for feature in provider.getFeatures():
            feature_string_results = []
            feature_numeric_results = []
            attributes = feature.attributes()
            for attr in attributes:
                if isinstance(attr, (int, float)):
                    feature_numeric_results.append(attr)
                else:
                    feature_string_results.append(attr)

            numeric_results.append(feature_numeric_results)
            string_results.append(feature_string_results)

        # check string attributes
        self.assertEqual(expected_string_results, string_results)
        # check numeric attributes with a 0.01% tolerance compared to the
        # native QGIS stats
        numpy.testing.assert_allclose(expected_numeric_results,
                                      numeric_results,
                                      rtol=0.01)

    def test_aggregate_raster_impact_python(self):
        """Check aggregation on raster impact using python zonal stats"""
        self._aggregate_raster_impact()

    def test_aggregate_raster_impact_native(self):
        """Check aggregation on raster impact using native qgis zonal stats.

        TODO: this fails on Tim's machine but not on MB or Jenkins.

        """
        self._aggregate_raster_impact(use_native_zonal_stats=True)

    def _aggregate_raster_impact(self, use_native_zonal_stats=False):
        """Check aggregation on raster impact.

        :param use_native_zonal_stats:

        Created from loadStandardLayers.qgs with:
        - a flood in Jakarta like in 2007
        - Penduduk Jakarta
        - need evacuation
        - kabupaten_jakarta_singlepart.shp

        """
        impact_layer = Raster(
            data=os.path.join(TESTDATA, 'aggregation_test_impact_raster.tif'),
            name='test raster impact')

        expected_results = [
            ['JAKARTA BARAT',
             '50540',
             '12015061.8769531',
             '237.733713433976'],
            ['JAKARTA PUSAT',
             '19492',
             '2943702.11401367',
             '151.021040119725'],
            ['JAKARTA SELATAN',
             '57367',
             '1645498.26947021',
             '28.6837078716024'],
            ['JAKARTA UTARA',
             '55004',
             '11332095.7334595',
             '206.023120745027'],
            ['JAKARTA TIMUR',
             '73949',
             '10943934.3182373',
             '147.992999475819']]

        self._aggregate(impact_layer, expected_results, use_native_zonal_stats)

    def test_aggregate_vector_impact(self):
        """Test aggregation results on a vector layer.
        created from loadStandardLayers.qgs with:
        - a flood in Jakarta like in 2007
        - Essential buildings
        - be flooded
        - kabupaten_jakarta_singlepart.shp
        """
        impact_layer = Vector(
            data=os.path.join(TESTDATA, 'aggregation_test_impact_vector.shp'),
            name='test vector impact')

        expected_results = [
            ['JAKARTA BARAT', '87'],
            ['JAKARTA PUSAT', '117'],
            ['JAKARTA SELATAN', '22'],
            ['JAKARTA UTARA', '286'],
            ['JAKARTA TIMUR', '198']
        ]
        self._aggregate(impact_layer, expected_results)

        impact_layer = Vector(
            data=TESTDATA + '/aggregation_test_impact_vector_small.shp',
            name='test vector impact')

        expected_results = [
            ['JAKARTA BARAT', '2'],
            ['JAKARTA PUSAT', '0'],
            ['JAKARTA SELATAN', '0'],
            ['JAKARTA UTARA', '1'],
            ['JAKARTA TIMUR', '0']
        ]

        self._aggregate(impact_layer, expected_results)

if __name__ == '__main__':
    suite = unittest.makeSuite(AggregatorTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
