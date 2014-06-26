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
__author__ = 'Marco Bernasocchi'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os
import logging

import numpy.testing
import numpy

from os.path import join
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from qgis.core import (
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsMapLayerRegistry)

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe_qgis import breakdown_defaults
from safe_qgis.safe_interface import (
    UNITDATA,
    TESTDATA,
    BOUNDDATA,
    Raster,
    Vector)

from safe_qgis.utilities.utilities_for_testing import (
    set_canvas_crs,
    set_jakarta_extent,
    GEOCRS)

from safe_qgis.widgets.dock import Dock
from safe_qgis.impact_statistics.aggregator import Aggregator
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.utilities.utilities import (
    extent_to_geo_array)

from safe_qgis.utilities.utilities_for_testing import (
    load_standard_layers,
    setup_scenario,
    load_layers)

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
        load_standard_layers(DOCK)
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

        # Set extent as Jakarta extent
        geo_crs = QgsCoordinateReferenceSystem()
        geo_crs.createFromSrid(4326)
        self.extent = extent_to_geo_array(CANVAS.extent(), geo_crs)

    def tearDown(self):
        """Run after each test."""
        # Let's use a fresh registry, canvas, and dock for each test!
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        DOCK.cboHazard.clear()
        DOCK.cboExposure.clear()

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
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta singlepart with None keyword')
        assert result, message
        # Press RUN
        DOCK.accept()
        DOCK.runtime_keywords_dialog.accept()
        attribute = DOCK.aggregator.attributes[attribute_key]
        message = ('The aggregation should be None. Found: %s' % attribute)
        assert attribute is None, message

    def test_setup_target_field(self):
        """Test setup up target field is correct
        """
        layer = QgsVectorLayer(
            os.path.join(BOUNDDATA, 'kabupaten_jakarta.shp'),
            'test aggregation',
            'ogr')
        aggregator = Aggregator(self.extent, None)
        self.assertFalse(aggregator._setup_target_field(layer))

        impact_layer_name = os.path.join(TESTDATA,
                                         'aggregation_test_impact_vector.shp')
        impact_layer = QgsVectorLayer(impact_layer_name,
                                      'test', 'ogr')
        self.assertTrue(aggregator._setup_target_field(impact_layer))

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

    def _create_aggregator(self,
                           use_aoi_mode,
                           use_native_zonal_stats):
        """Helper to create aggregator"""

        aggregation_layer = QgsVectorLayer(
            os.path.join(BOUNDDATA, 'kabupaten_jakarta.shp'),
            'test aggregation',
            'ogr')
        # Dummy layers. Them are used in aggregator._prepare_layer
        # The extent of the layers must be equal to aggregator.extent
        hazard_layer = exposure_layer = aggregation_layer
        # setting up
        if not use_aoi_mode:
            aggregator = Aggregator(self.extent, aggregation_layer)
        else:
            aggregator = Aggregator(self.extent, None)
        aggregator.set_layers(hazard_layer, exposure_layer)
        aggregator.validate_keywords()
        aggregator.use_native_zonal_stats = use_native_zonal_stats

        return aggregator

    def _aggregate(
            self,
            impact_layer,
            expected_results,
            use_native_zonal_stats=False,
            use_aoi_mode=False,
            impact_layer_attributes=None):
        """Helper to calculate aggregation.

        Expected results is split into two lists - one list contains numeric
        attributes, the other strings. This is done so that we can use numpy
        .testing.assert_allclose which doesn't work on strings

        impact_layer_attributes is a list of expected attributes
        for aggregator.impact_layer_attributes (used for vector aggregation)
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

        aggregator = self._create_aggregator(
            use_aoi_mode, use_native_zonal_stats
        )
        aggregator.aggregate(impact_layer)

        provider = aggregator.layer.dataProvider()
        string_results = []
        numeric_results = []

        for feature in provider.getFeatures():
            feature_string_results = []
            feature_numeric_results = []
            attributes = feature.attributes()
            for attr in attributes:
                try:
                    value = float(attr)
                    feature_numeric_results.append(value)
                except ValueError:
                    feature_string_results.append(str(attr))

            numeric_results.append(feature_numeric_results)
            string_results.append(feature_string_results)

        # check string attributes
        self.assertEqual(expected_string_results, string_results)
        # check numeric attributes with a 0.01% tolerance compared to the
        # native QGIS stats
        numpy.testing.assert_allclose(
            expected_numeric_results, numeric_results, rtol=0.01)

        if impact_layer_attributes is not None:
            self.assertListEqual(
                aggregator.impact_layer_attributes,
                impact_layer_attributes
            )

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

        # Aggregation in sum mode
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
        expected_results = [  # Count of inundated polygons:
            ['JAKARTA BARAT', '2'],
            ['JAKARTA PUSAT', '0'],
            ['JAKARTA SELATAN', '0'],
            ['JAKARTA UTARA', '1'],
            ['JAKARTA TIMUR', '0']
        ]
        self._aggregate(impact_layer, expected_results)
        expected_results = [
            ['Entire area', '3']
        ]
        self._aggregate(impact_layer, expected_results, use_aoi_mode=True)

        # Aggregation in class_count mode
        data_path = os.path.join(
            UNITDATA,
            'impact',
            'aggregation_test_impact_vector_class_count.shp')
        impact_layer = Vector(
            data=data_path,
            name='test vector impact')
        expected_results = [
            ['Entire area', '2', '3', '0']
        ]
        self._aggregate(impact_layer, expected_results, use_aoi_mode=True)
        expected_results = [
            ['JAKARTA BARAT', '1', '2', '0'],
            ['JAKARTA PUSAT', '1', '0', '0'],
            ['JAKARTA SELATAN', '0', '0', '0'],
            ['JAKARTA UTARA', '0', '1', '0'],
            ['JAKARTA TIMUR', '0', '0', '0']
        ]
        impact_layer_attributes = [
            [   # JAKARTA BARAT
                {'INUNDATED': 1,
                 'depth': 2.0,
                 'type': None,
                 'name': None,
                 'osm_id': None},
                {'INUNDATED': 1,
                 'depth': 2.0,
                 'type': None,
                 'name': None,
                 'osm_id': None},
                {'INUNDATED': 0,
                 'depth': None,
                 'type': None,
                 'name': None,
                 'osm_id': None}
            ],
            [   # JAKARTA PUSAT
                {'INUNDATED': 0,
                 'depth': None,
                 'type': None,
                 'name': None,
                 'osm_id': None}
            ],
            [
                # JAKARTA SELATAN
            ],
            [   # JAKARTA UTARA
                {'INUNDATED': 1,
                 'depth': None,
                 'type': None,
                 'name': None,
                 'osm_id': None}
            ],
            [
                # JAKARTA TIMUR
            ]
        ]
        self._aggregate(impact_layer,
                        expected_results,
                        impact_layer_attributes=impact_layer_attributes)

    def test_line_aggregation(self):
        """Test if line aggregation works
        """

        data_path = os.path.join(
            UNITDATA,
            'impact',
            'aggregation_test_roads.shp')
        impact_layer = Vector(
            data=data_path,
            name='test vector impact')

        expected_results = [
            [u'JAKARTA BARAT', 0],
            [u'JAKARTA PUSAT', 4356],
            [u'JAKARTA SELATAN', 0],
            [u'JAKARTA UTARA', 4986],
            [u'JAKARTA TIMUR', 5809]
        ]
        impact_layer_attributes = [
            [
                {
                    'KAB_NAME': u'JAKARTA BARAT',
                    'flooded': 0.0,
                    'length': 7230.864654,
                    'id': 2,
                    'aggr_sum': 7230.864654
                }
            ],
            [
                {
                    'KAB_NAME': u'JAKARTA PUSAT',
                    'flooded': 4356.161093,
                    'length': 4356.161093,
                    'id': 3,
                    'aggr_sum': 4356.161093
                }
            ],
            [
                {
                    'KAB_NAME': u'JAKARTA SELATAN',
                    'flooded': 0.0,
                    'length': 3633.317287,
                    'id': 4,
                    'aggr_sum': 3633.317287
                }
            ],
            [
                {
                    'KAB_NAME': u'JAKARTA UTARA',
                    'flooded': 4985.831677,
                    'length': 4985.831677,
                    'id': 1,
                    'aggr_sum': 4985.831677
                }
            ],
            [
                {
                    'KAB_NAME': u'JAKARTA TIMUR',
                    'flooded': 0.0,
                    'length': 4503.033629,
                    'id': 4,
                    'aggr_sum': 4503.033629
                },
                {
                    'KAB_NAME': u'JAKARTA TIMUR',
                    'flooded': 5809.142247,
                    'length': 5809.142247,
                    'id': 1,
                    'aggr_sum': 5809.142247
                }
            ]
        ]
        self._aggregate(
            impact_layer,
            expected_results,
            impact_layer_attributes=impact_layer_attributes)

    def test_set_layers(self):
        """
        Test set up aggregator's layers work
        """

        hazard = QgsVectorLayer(
            os.path.join(
                UNITDATA,
                'hazard',
                'multipart_polygons_osm_4326.shp'),
            'hazard',
            'ogr'
        )
        exposure = QgsVectorLayer(
            os.path.join(
                UNITDATA,
                'exposure',
                'buildings_osm_4326.shp'),
            'impact',
            'ogr'
        )

        aggregation_layer = QgsVectorLayer(
            os.path.join(BOUNDDATA, 'kabupaten_jakarta.shp'),
            'test aggregation',
            'ogr')

        # Test in
        #   aoi mode (use None)
        #   not aoi mode (use aggregation_layer)
        for agg_layer in [None, aggregation_layer]:
            aggregator = Aggregator(self.extent, None)
            aggregator.set_layers(hazard, exposure)
            self.assertEquals(aggregator.exposure_layer, exposure)
            self.assertEquals(aggregator.hazard_layer, hazard)
            layer = aggregator.layer
            extent = layer.extent()
            x_min, y_min, x_max, y_max = \
                extent.xMinimum(), extent.yMinimum(), \
                extent.xMaximum(), extent.yMaximum()
            self.assertAlmostEquals(self.extent[0], x_min)
            self.assertAlmostEquals(self.extent[1], y_min)
            self.assertAlmostEquals(self.extent[2], x_max)
            self.assertAlmostEquals(self.extent[3], y_max)
            self.assertTrue(aggregator.safe_layer.is_vector)
            _ = agg_layer

    def test_set_sum_field_name(self):
        """Test sum_field_name work
        """
        aggregator = self._create_aggregator(False, False)
        self.assertEquals(aggregator.sum_field_name(), 'aggr_sum')

        aggregator.set_sum_field_name('SUMM_AGGR')
        self.assertEquals(aggregator.sum_field_name(), 'SUMM_AGGR')
    test_set_sum_field_name.slow = False

    def test_get_centroids(self):
        """Test get_centroids work"""
        aggregator = self._create_aggregator(False, False)

        polygon1 = numpy.array([[0, 0], [0, 1], [1, 0], [0, 0]])
        polygon2 = numpy.array([[0, 0], [1, 1], [1, 0], [0, 0]])
        polygons = [polygon1, polygon2]

        centroids = aggregator._get_centroids(polygons)
        # noinspection PyTypeChecker
        self.assertEquals(len(centroids), 2)

        centroids = aggregator._get_centroids([polygon1])
        # noinspection PyTypeChecker
        self.assertEquals(len(centroids), 1)
    test_get_centroids.slow = False


if __name__ == '__main__':
    suite = unittest.makeSuite(AggregatorTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
