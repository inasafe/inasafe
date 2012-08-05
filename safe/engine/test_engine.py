import unittest
import cPickle
import numpy
import sys
import os
from os.path import join

# Import InaSAFE modules
from safe.engine.core import calculate_impact

from safe.storage.core import read_layer
from safe.storage.core import write_vector_data
from safe.storage.core import write_raster_data
from safe.storage.vector import Vector
from safe.storage.utilities import unique_filename, DEFAULT_ATTRIBUTE

from safe.common.polygon import separate_points_by_polygon, clip_lines_by_polygon
from safe.common.polygon import is_inside_polygon
from safe.common.interpolation2d import interpolate_raster
from safe.common.numerics import normal_cdf, lognormal_cdf, erf, ensure_numeric
from safe.common.numerics import nanallclose
from safe.common.utilities import VerificationError
from safe.common.testing import TESTDATA, HAZDATA, EXPDATA

from safe.impact_functions import get_plugins

# These imports are needed for impact function registration - dont remove
# If any of these get reinstated as "official" public impact functions,
# remove from here and update test to use the real one.
from impact_functions_for_testing import empirical_fatality_model
from impact_functions_for_testing import allen_fatality_model
from impact_functions_for_testing import unspecific_building_impact_model
from impact_functions_for_testing import NEXIS_building_impact_model
from impact_functions_for_testing import HKV_flood_study
from impact_functions_for_testing import BNPB_earthquake_guidelines
from impact_functions_for_testing import general_ashload_impact
from impact_functions_for_testing import flood_road_impact


def linear_function(x, y):
    """Auxiliary function for use with interpolation test
    """

    return x + y / 2.0


def lembang_damage_function(x):
    if x < 6.0:
        value = 0.0
    else:
        value = (0.692 * (x ** 4) -
                 15.82 * (x ** 3) +
                 135.0 * (x ** 2) -
                 509.0 * x +
                 714.4)
    return value


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


class Test_Engine(unittest.TestCase):

    def test_earthquake_fatality_estimation_allen(self):
        """Fatalities from ground shaking can be computed correctly 1
           using aligned rasters
        """

        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = '%s/Earthquake_Ground_Shaking_clip.tif' % TESTDATA
        exposure_filename = '%s/Population_2010_clip.tif' % TESTDATA

        # Calculate impact using API
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        plugin_name = 'Earthquake Fatality Function'
        plugin_list = get_plugins(plugin_name)
        assert len(plugin_list) == 1
        assert plugin_list[0].keys()[0] == plugin_name

        IF = plugin_list[0][plugin_name]

        # Call calculation engine
        impact_layer = calculate_impact(layers=[H, E],
                                        impact_fcn=IF)
        impact_filename = impact_layer.get_filename()

        # Do calculation manually and check result
        hazard_raster = read_layer(hazard_filename)
        H = hazard_raster.get_data(nan=0)

        exposure_raster = read_layer(exposure_filename)
        E = exposure_raster.get_data(nan=0)

        # Calculate impact manually
        a = 0.97429
        b = 11.037
        F = 10 ** (a * H - b) * E

        # Verify correctness of result
        C = impact_layer.get_data(nan=0)

        # Compare shape and extrema
        msg = ('Shape of calculated raster differs from reference raster: '
               'C=%s, F=%s' % (C.shape, F.shape))
        assert numpy.allclose(C.shape, F.shape, rtol=1e-12, atol=1e-12), msg

        msg = ('Minimum of calculated raster differs from reference raster: '
               'C=%s, F=%s' % (numpy.min(C), numpy.min(F)))
        assert numpy.allclose(numpy.min(C), numpy.min(F),
                              rtol=1e-12, atol=1e-12), msg
        msg = ('Maximum of calculated raster differs from reference raster: '
               'C=%s, F=%s' % (numpy.max(C), numpy.max(F)))
        assert numpy.allclose(numpy.max(C), numpy.max(F),
                              rtol=1e-12, atol=1e-12), msg

        # Compare every single value numerically
        msg = 'Array values of written raster array were not as expected'
        assert numpy.allclose(C, F, rtol=1e-12, atol=1e-12), msg

        # Check that extrema are in range
        xmin, xmax = impact_layer.get_extrema()
        assert numpy.alltrue(C >= xmin)
        assert numpy.alltrue(C <= xmax)
        assert numpy.alltrue(C >= 0)

    def test_ITB_earthquake_fatality_estimation(self):
        """Fatalities from ground shaking can be computed correctly
           using the ITB fatality model (Test data from Hadi Ghasemi).
        """

        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = '%s/itb_test_mmi.asc' % TESTDATA
        exposure_filename = '%s/itb_test_pop.asc' % TESTDATA
        fatality_filename = '%s/itb_test_fat.asc' % TESTDATA

        # Calculate impact using API
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        plugin_name = 'I T B Fatality Function'
        plugin_list = get_plugins(plugin_name)
        assert len(plugin_list) == 1
        assert plugin_list[0].keys()[0] == plugin_name

        IF = plugin_list[0][plugin_name]

        # Call calculation engine
        impact_layer = calculate_impact(layers=[H, E],
                                        impact_fcn=IF)
        impact_filename = impact_layer.get_filename()

        I = read_layer(impact_filename)
        calculated_result = I.get_data()
#        print calculated_result.shape
        keywords = I.get_keywords()
#        print "keywords", keywords
        population = float(keywords['total_population'])
        fatalities = float(keywords['total_fatalities'])

        # Check aggregated values
        expected_population = int(round(85424650. / 1000)) * 1000
        msg = ('Expected population was %f, I got %f'
               % (expected_population, population))
        assert population == expected_population, msg

        expected_fatalities = int(round(40871.3028 / 1000)) * 1000
        msg = ('Expected fatalities was %f, I got %f'
               % (expected_fatalities, fatalities))
        assert numpy.allclose(fatalities, expected_fatalities,
        rtol=1.0e-5), msg

        # Compare with reference data
        F = read_layer(fatality_filename)
        fatality_result = F.get_data()

#        print fatality_result

        msg = ('Calculated fatality map did not match expected result: '
               'I got %s\n'
               'Expected %s' % (calculated_result, fatality_result))
        assert nanallclose(calculated_result, fatality_result,
                           rtol=1.0e-4), msg

        # Check for expected numbers (from Hadi Ghasemi) in keywords
        # NOTE: Commented out because function no longer needs to return
        # individual exposure numbers.
        #for population_count in [2649040.0, 50273440.0, 7969610.0,
        #                         19320620.0, 5211940.0]:
        #    assert str(int(population_count / 1000)) in \
        #        keywords['impact_summary']

        # Check that aggregated number of fatilites is as expected
        all = int(numpy.sum([31.8937368131,
                             2539.26369372,
                             1688.72362573,
                             17174.9261705,
                             19436.834531]))
        msg = 'Aggregated number of fatalities not as expected: %i' % all
        assert all == 40871, msg

        x = int(round(float(all) / 1000)) * 1000
        msg = 'Did not find expected value %i in summary' % x
        assert str(x) in keywords['impact_summary'], msg

        # Individual check does not work anymore, because the function
        # now only returns
        # the aggregate number of fatalities
        #for fatality_count in [31.8937368131, 2539.26369372,
        #                       1688.72362573, 17174.9261705, 19436.834531]:
        #    x = str(int(fatality_count))
        #    summary = keywords['impact_summary']
        #    msg = 'Expected %s in impact_summary: %s' % (x, summary)
        #    print x in summary #, msg
        #    #assert x in summary, msg

    def test_earthquake_fatality_estimation_ghasemi(self):
        """Fatalities from ground shaking can be computed correctly 2
           using the Hadi Ghasemi function.
        """

        # FIXME (Ole): Maybe this is no longer relevant (20120501)

        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = '%s/Earthquake_Ground_Shaking_clip.tif' % TESTDATA
        exposure_filename = '%s/Population_2010_clip.tif' % TESTDATA

        # Calculate impact using API
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        plugin_name = 'Empirical Fatality Function'
        plugin_list = get_plugins(plugin_name)
        assert len(plugin_list) == 1
        assert plugin_list[0].keys()[0] == plugin_name

        IF = plugin_list[0][plugin_name]

        # Call calculation engine
        impact_layer = calculate_impact(layers=[H, E],
                                        impact_fcn=IF)
        impact_filename = impact_layer.get_filename()

        # Do calculation manually and check result
        hazard_raster = read_layer(hazard_filename)
        H = hazard_raster.get_data(nan=0)

        exposure_raster = read_layer(exposure_filename)
        E = exposure_raster.get_data(nan=0)

        # Verify correctness of result
        C = impact_layer.get_data(nan=0)

        # Calculate impact manually
        # FIXME (Ole): Jono will do this
        return

        # Compare shape and extrema
        msg = ('Shape of calculated raster differs from reference raster: '
               'C=%s, F=%s' % (C.shape, F.shape))
        assert numpy.allclose(C.shape, F.shape, rtol=1e-12, atol=1e-12), msg

        msg = ('Minimum of calculated raster differs from reference raster: '
               'C=%s, F=%s' % (numpy.min(C), numpy.min(F)))
        assert numpy.allclose(numpy.min(C), numpy.min(F),
                              rtol=1e-12, atol=1e-12), msg
        msg = ('Maximum of calculated raster differs from reference raster: '
               'C=%s, F=%s' % (numpy.max(C), numpy.max(F)))
        assert numpy.allclose(numpy.max(C), numpy.max(F),
                              rtol=1e-12, atol=1e-12), msg

        # Compare every single value numerically
        msg = 'Array values of written raster array were not as expected'
        assert numpy.allclose(C, F, rtol=1e-12, atol=1e-12), msg

        # Check that extrema are in range
        xmin, xmax = impact_layer.get_extrema()
        assert numpy.alltrue(C >= xmin)
        assert numpy.alltrue(C <= xmax)
        assert numpy.alltrue(C >= 0)

    def test_earthquake_impact_on_women_example(self):
        """Earthquake impact on women example works
        """

        # This only tests that the function runs and has the right
        # strings in the output. No test of quantitative numbers
        # (because we can't).

        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = '%s/Earthquake_Ground_Shaking_clip.tif' % TESTDATA
        exposure_filename = '%s/Population_2010_clip.tif' % TESTDATA

        # Calculate impact using API
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        plugin_name = 'Earthquake Women Impact Function'
        plugin_list = get_plugins(plugin_name)
        assert len(plugin_list) == 1
        assert plugin_list[0].keys()[0] == plugin_name

        IF = plugin_list[0][plugin_name]

        # Call calculation engine
        impact_layer = calculate_impact(layers=[H, E],
                                        impact_fcn=IF)
        impact_filename = impact_layer.get_filename()

        I = read_layer(impact_filename)  # Can read result

        assert 'women displaced' in impact_layer.get_impact_summary()
        assert 'pregnant' in impact_layer.get_impact_summary()

    def test_jakarta_flood_study(self):
        """HKV Jakarta flood study calculated correctly using aligned rasters
        """

        # FIXME (Ole): Redo with population as shapefile later

        # Name file names for hazard level, exposure and expected fatalities

        population = 'Population_Jakarta_geographic.asc'
        plugin_name = 'HKVtest'

        # Expected values from HKV
        expected_values = [2485442, 1537920]
        expected_strings = ['<b>2480</b>', '<b>1533</b>']

        i = 0
        for filename in ['Flood_Current_Depth_Jakarta_geographic.asc',
                         'Flood_Design_Depth_Jakarta_geographic.asc']:

            hazard_filename = join(HAZDATA, filename)
            exposure_filename = join(TESTDATA, population)

            # Get layers using API
            H = read_layer(hazard_filename)
            E = read_layer(exposure_filename)

            plugin_list = get_plugins(plugin_name)
            assert len(plugin_list) == 1
            assert plugin_list[0].keys()[0] == plugin_name

            IF = plugin_list[0][plugin_name]
            # Call impact calculation engine
            impact_layer = calculate_impact(layers=[H, E],
                                            impact_fcn=IF)
            impact_filename = impact_layer.get_filename()

            # Do calculation manually and check result
            hazard_raster = read_layer(hazard_filename)
            H = hazard_raster.get_data(nan=0)

            exposure_raster = read_layer(exposure_filename)
            P = exposure_raster.get_data(nan=0)

            # Calculate impact manually
            pixel_area = 2500
            I = numpy.where(H > 0.1, P, 0) / 100000.0 * pixel_area

            # Verify correctness against results from HKV
            res = sum(I.flat)
            ref = expected_values[i]
            #print filename, 'Result=%f' % res, ' Expected=%f' % ref
            #print 'Pct relative error=%f' % (abs(res-ref)*100./ref)

            msg = 'Got result %f but expected %f' % (res, ref)
            assert numpy.allclose(res, ref, rtol=1.0e-2), msg

            # Verify correctness of result
            calculated_raster = read_layer(impact_filename)
            C = calculated_raster.get_data(nan=0)

            # Check impact_summary
            impact_summary = calculated_raster.get_impact_summary()
            expct = expected_strings[i]  # Number of people affected (HTML)
            msg = ('impact_summary %s did not contain expected '
                   'string %s' % (impact_summary, expct))
            assert expct in impact_summary, msg

            # Compare shape and extrema
            msg = ('Shape of calculated raster differs from reference raster: '
                   'C=%s, I=%s' % (C.shape, I.shape))
            assert numpy.allclose(C.shape, I.shape,
                                  rtol=1e-12, atol=1e-12), msg

            msg = ('Minimum of calculated raster differs from reference '
                   'raster: '
                   'C=%s, I=%s' % (numpy.min(C), numpy.min(I)))
            assert numpy.allclose(numpy.min(C), numpy.min(I),
                                  rtol=1e-12, atol=1e-12), msg
            msg = ('Maximum of calculated raster differs from reference '
                   'raster: '
                   'C=%s, I=%s' % (numpy.max(C), numpy.max(I)))
            assert numpy.allclose(numpy.max(C), numpy.max(I),
                                  rtol=1e-12, atol=1e-12), msg

            # Compare every single value numerically
            msg = 'Array values of written raster array were not as expected'
            assert numpy.allclose(C, I, rtol=1e-12, atol=1e-12), msg

            # Check that extrema are in range
            xmin, xmax = calculated_raster.get_extrema()
            assert numpy.alltrue(C >= xmin)
            assert numpy.alltrue(C <= xmax)
            assert numpy.alltrue(C >= 0)

            i += 1

    test_jakarta_flood_study.slow = 1

    def test_flood_building_impact_function(self):
        """Flood building impact function works

        This test also exercises interpolation of hazard level (raster) to
        building locations (vector data).
        """

        for haz_filename in ['Flood_Current_Depth_Jakarta_geographic.asc',
                             'Flood_Design_Depth_Jakarta_geographic.asc']:

            # Name file names for hazard level and exposure
            hazard_filename = '%s/%s' % (HAZDATA, haz_filename)
            exposure_filename = ('%s/OSM_building_polygons_20110905.shp'
                                 % TESTDATA)

            # Calculate impact using API
            H = read_layer(hazard_filename)
            E = read_layer(exposure_filename)

            plugin_name = 'FloodBuildingImpactFunction'
            plugin_list = get_plugins(plugin_name)
            assert len(plugin_list) == 1
            assert plugin_list[0].keys()[0] == plugin_name

            IF = plugin_list[0][plugin_name]

            impact_vector = calculate_impact(layers=[H, E],
                                             impact_fcn=IF)
            impact_filename = impact_vector.get_filename()

            # Extract calculated result
            icoordinates = impact_vector.get_geometry()
            iattributes = impact_vector.get_data()

            # FIXME (Ole): check some numbers
    test_flood_building_impact_function.slow = 1

    def test_earthquake_damage_schools(self):
        """Lembang building damage from ground shaking works

        This test also exercises interpolation of hazard level (raster) to
        building locations (vector data).
        """

        # Name file names for hazard level and exposure
        exp_filename = '%s/test_buildings.shp' % TESTDATA
        for haz_filename in [join(TESTDATA, 'lembang_mmi_hazmap.asc'),
                             join(TESTDATA,   # NaN's
                                  'Earthquake_Ground_Shaking_clip.tif'),
                             join(HAZDATA, 'Lembang_Earthquake_Scenario.asc')]:

            # Calculate impact using API
            H = read_layer(haz_filename)
            E = read_layer(exp_filename)

            plugin_name = 'Earthquake Building Damage Function'
            plugin_list = get_plugins(plugin_name)
            assert len(plugin_list) == 1
            assert plugin_list[0].keys()[0] == plugin_name

            IF = plugin_list[0][plugin_name]

            impact_vector = calculate_impact(layers=[H, E],
                                             impact_fcn=IF)
            impact_filename = impact_vector.get_filename()

            # Read input data
            hazard_raster = read_layer(haz_filename)
            A = hazard_raster.get_data()
            mmi_min, mmi_max = hazard_raster.get_extrema()

            exposure_vector = read_layer(exp_filename)
            coordinates = exposure_vector.get_geometry()
            attributes = exposure_vector.get_data()

            # Extract calculated result
            icoordinates = impact_vector.get_geometry()
            iattributes = impact_vector.get_data()

            # First check that interpolated MMI was done as expected
            fid = open('%s/test_buildings_percentage_loss_and_mmi.txt'
                       % TESTDATA)
            reference_points = []
            MMI = []
            DAM = []
            for line in fid.readlines()[1:]:
                fields = line.strip().split(',')

                lon = float(fields[4][1:-1])
                lat = float(fields[3][1:-1])
                mmi = float(fields[-1][1:-1])
                dam = float(fields[-2][1:-1])

                reference_points.append((lon, lat))
                MMI.append(mmi)
                DAM.append(dam)

            # Verify that coordinates are consistent
            msg = 'Interpolated coordinates do not match those of test data'
            assert numpy.allclose(icoordinates, reference_points), msg

            # Verify interpolated MMI with test result
            min_damage = sys.maxint
            max_damage = -min_damage
            for i in range(len(MMI)):
                lon, lat = icoordinates[i][:]
                calculated_mmi = iattributes[i]['MMI']

                if numpy.isnan(calculated_mmi):
                    continue

                # Check that interpolated points are within range
                msg = ('Interpolated mmi %f from file %s was outside '
                       'extrema: [%f, %f] at location '
                       '[%f, %f].' % (calculated_mmi, haz_filename,
                                      mmi_min, mmi_max, lon, lat))
                assert mmi_min <= calculated_mmi <= mmi_max, msg

                # Set up some tolerances for comparison with test set.
                if 'Lembang_Earthquake' in haz_filename:
                    pct = 3
                else:
                    pct = 2

                # Check that interpolated result is within specified tolerance
                msg = ('Calculated MMI %f deviated more than %.1f%% from '
                       'what was expected %f' % (calculated_mmi, pct, MMI[i]))
                assert numpy.allclose(calculated_mmi, MMI[i],
                                      rtol=float(pct) / 100), msg

                calculated_dam = iattributes[i]['DAMAGE']
                if calculated_dam > max_damage:
                    max_damage = calculated_dam

                if calculated_dam < min_damage:
                    min_damage = calculated_dam

                ref_dam = lembang_damage_function(calculated_mmi)
                msg = ('Calculated damage was not as expected')
                assert numpy.allclose(calculated_dam, ref_dam,
                                      rtol=1.0e-12), msg

                # Test that test data is correct by calculating damage based
                # on reference MMI.
                # FIXME (Ole): UNCOMMENT WHEN WE GET THE CORRECT DATASET
                #expected_test_damage = lembang_damage_function(MMI[i])
                #msg = ('Test data is inconsistent: i = %i, MMI = %f,'
                #       'expected_test_damage = %f, '
                #       'actual_test_damage = %f' % (i, MMI[i],
                #                                    expected_test_damage,
                #                                    DAM[i]))
                #if not numpy.allclose(expected_test_damage,
                #                      DAM[i], rtol=1.0e-12):
                #    print msg

                # Note this test doesn't work, but the question is whether the
                # independent test data is correct.
                # Also small fluctuations in MMI can cause very large changes
                # in computed damage for this example.
                # print mmi, MMI[i], calculated_damage, DAM[i]
                #msg = ('Calculated damage was not as expected for point %i:'
                #       'Got %f, expected %f' % (i, calculated_dam, DAM[i]))
                #assert numpy.allclose(calculated_dam, DAM[i], rtol=0.8), msg

            assert min_damage >= 0
            assert max_damage <= 100
            #print 'Extrema', mmi_filename, min_damage, max_damage
            #print len(MMI)

    def test_earthquake_impact_OSM_data(self):
        """Earthquake layer interpolation to OSM building data works

        The impact function used is based on the guidelines plugin

        This test also exercises interpolation of hazard level (raster) to
        building locations (vector data).
        """

        # FIXME: Still needs some reference data to compare to
        for mmi_filename in ['Shakemap_Padang_2009.asc',
                             # Time consuming
                             #'Earthquake_Ground_Shaking.asc',
                             'Lembang_Earthquake_Scenario.asc']:

            # Name file names for hazard level and exposure
            hazard_filename = '%s/%s' % (HAZDATA, mmi_filename)
            exposure_filename = ('%s/OSM_building_polygons_20110905.shp'
                                 % TESTDATA)

            # Calculate impact using API
            H = read_layer(hazard_filename)
            E = read_layer(exposure_filename)

            plugin_name = 'Earthquake Guidelines Function'
            plugin_list = get_plugins(plugin_name)
            assert len(plugin_list) == 1
            assert plugin_list[0].keys()[0] == plugin_name

            IF = plugin_list[0][plugin_name]
            impact_vector = calculate_impact(layers=[H, E],
                                             impact_fcn=IF)
            impact_filename = impact_vector.get_filename()

            # Read input data
            hazard_raster = read_layer(hazard_filename)
            A = hazard_raster.get_data()
            mmi_min, mmi_max = hazard_raster.get_extrema()

            exposure_vector = read_layer(exposure_filename)
            coordinates = exposure_vector.get_geometry()
            attributes = exposure_vector.get_data()

            # Extract calculated result
            icoordinates = impact_vector.get_geometry()
            iattributes = impact_vector.get_data()

            # Verify interpolated MMI with test result
            for i in range(len(iattributes)):
                calculated_mmi = iattributes[i]['MMI']

                if numpy.isnan(calculated_mmi):
                    continue

                # Check that interpolated points are within range
                msg = ('Interpolated mmi %f from file %s was outside '
                       'extrema: [%f, %f] at point %i '
                       % (calculated_mmi, hazard_filename,
                          mmi_min, mmi_max, i))
                assert mmi_min <= calculated_mmi <= mmi_max, msg

                calculated_dam = iattributes[i]['DMGLEVEL']
                assert calculated_dam in [1, 2, 3]

    test_earthquake_impact_OSM_data.slow = 1

    def test_tsunami_loss_use_case(self):
        """Building loss from tsunami use case works
        """

        # This test merely exercises the use case as there is
        # no reference data. It does check the sanity of values as
        # far as possible.

        hazard_filename = ('%s/tsunami_max_inundation_depth_4326.tif'
                            % TESTDATA)
        exposure_filename = ('%s/tsunami_building_exposure.shp' % TESTDATA)
        exposure_with_depth_filename = ('%s/tsunami_building_exposure'
                                        '.shp' % TESTDATA)
        reference_impact_filename = ('%s/tsunami_building_assessment'
                                     '.shp' % TESTDATA)

        # Calculate impact using API
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        plugin_name = 'Tsunami Building Loss Function'
        plugin_list = get_plugins(plugin_name)
        assert len(plugin_list) == 1
        assert plugin_list[0].keys()[0] == plugin_name

        IF = plugin_list[0][plugin_name]
        impact_vector = calculate_impact(layers=[H, E],
                                         impact_fcn=IF)
        impact_filename = impact_vector.get_filename()
        # Read calculated result
        impact_vector = read_layer(impact_filename)  # Read to have truncation
        icoordinates = impact_vector.get_geometry()
        iattributes = impact_vector.get_data()
        N = len(icoordinates)

        # Ensure that calculated point locations coincide with
        # original exposure point locations
        ref_exp = read_layer(exposure_filename)
        refcoordinates = ref_exp.get_geometry()

        assert N == len(refcoordinates)
        msg = ('Coordinates of impact results do not match those of '
               'exposure data')
        assert numpy.allclose(icoordinates, refcoordinates), msg

        # Ensure that calculated point locations coincide with
        # original exposure point (with depth) locations
        ref_depth = read_layer(exposure_with_depth_filename)
        refdepth_coordinates = ref_depth.get_geometry()
        #refdepth_attributes = ref_depth.get_data()
        assert N == len(refdepth_coordinates)
        msg = ('Coordinates of impact results do not match those of '
               'exposure data (with depth)')
        assert numpy.allclose(icoordinates, refdepth_coordinates), msg

        # Read reference results
        #hazard_raster = read_layer(hazard_filename)
        #A = hazard_raster.get_data()
        #depth_min, depth_max = hazard_raster.get_extrema()

        ref_impact = read_layer(reference_impact_filename)
        #refimpact_coordinates = ref_impact.get_geometry()
        refimpact_attributes = ref_impact.get_data()

        # Check for None
        for i in range(N):
            if refimpact_attributes[i] is None:
                msg = 'Element %i was None' % i
                raise Exception(msg)

        # Check sanity of calculated attributes
        for i in range(N):
            #lon, lat = icoordinates[i]

            depth = iattributes[i]['DEPTH']

            # Ignore NaN's
            if numpy.isnan(depth):
                continue

            structural_damage = iattributes[i]['STRUCT_DAM']
            contents_damage = iattributes[i]['CONTENTS_D']
            for imp in [structural_damage, contents_damage]:
                msg = ('Percent damage was outside range [0,1] at depth %f: %f'
                       % (depth, imp))
                assert 0 <= imp <= 1, msg

            structural_loss = iattributes[i]['STRUCT_LOS']
            contents_loss = iattributes[i]['CONTENTS_L']
            if depth < 0.3:
                assert structural_loss == 0.0
                assert contents_loss == 0.0
            else:
                assert structural_loss > 0.0
                assert contents_loss > 0.0

            number_of_people = iattributes[i]['NEXIS_PEOP']
            people_affected = iattributes[i]['PEOPLE_AFF']
            people_severely_affected = iattributes[i]['PEOPLE_SEV']

            if 0.01 < depth < 1.0:
                assert people_affected == number_of_people
            else:
                assert people_affected == 0

            if depth >= 1.0:
                assert people_severely_affected == number_of_people
            else:
                assert people_severely_affected == 0

            # Contents and structural damage is done according
            # to different damage curves and should therefore be different
            if depth > 0 and contents_damage > 0:
                assert contents_damage != structural_damage

    def test_tephra_load_impact(self):
        """Hypothetical tephra load scenario can be computed

        This test also exercises reprojection of UTM data
        """

        # File names for hazard level and exposure

        # FIXME - when we know how to reproject, replace hazard
        # file with UTM version (i.e. without _geographic).
        hazard_filename = join(TESTDATA,
                                       'Ashload_Gede_VEI4_geographic.asc')
        exposure_filename = join(TESTDATA, 'test_buildings.shp')

        # Calculate impact using API
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        plugin_name = 'Tephra Building Impact Function'
        plugin_list = get_plugins(plugin_name)
        assert len(plugin_list) == 1
        assert plugin_list[0].keys()[0] == plugin_name

        IF = plugin_list[0][plugin_name]
        impact_vector = calculate_impact(layers=[H, E],
                                         impact_fcn=IF)
        impact_filename = impact_vector.get_filename()

        # Read input data
        hazard_raster = read_layer(hazard_filename)
        A = hazard_raster.get_data()
        load_min, load_max = hazard_raster.get_extrema()

        exposure_vector = read_layer(exposure_filename)
        coordinates = exposure_vector.get_geometry()
        attributes = exposure_vector.get_data()

        # Extract calculated result
        coordinates = impact_vector.get_geometry()
        attributes = impact_vector.get_data()

        # Test that results are as expected
        # FIXME: Change test when we decide what values should actually be
        #        calculated :-) :-) :-)
        for a in attributes:
            load = a['ASHLOAD']
            impact = a['DAMAGE']

            # Test interpolation
            msg = 'Load %.15f was outside bounds [%f, %f]' % (load,
                                                           load_min,
                                                           load_max)
            if not numpy.isnan(load):
                assert load_min <= load <= load_max, msg

            # Test calcalated values
            #if 0.01 <= load < 90.0:
            #    assert impact == 1
            #elif 90.0 <= load < 150.0:
            #    assert impact == 2
            #elif 150.0 <= load < 300.0:
            #    assert impact == 3
            #elif load >= 300.0:
            #    assert impact == 4
            #else:
            #    assert impact == 0

            if 0.01 <= load < 0.5:
                assert impact == 0
            elif 0.5 <= load < 2.0:
                assert impact == 1
            elif 2.0 <= load < 10.0:
                assert impact == 2
            elif load >= 10.0:
                assert impact == 3
            else:
                assert impact == 0

    def test_interpolation_wrapper(self):
        """Interpolation library works for linear function
        """

        # Create test data
        lon_ul = 100  # Longitude of upper left corner
        lat_ul = 10   # Latitude of upper left corner
        numlon = 8    # Number of longitudes
        numlat = 5    # Number of latitudes
        dlon = 1
        dlat = -1

        # Define array where latitudes are rows and longitude columns
        A = numpy.zeros((numlat, numlon))

        # Establish coordinates for lower left corner
        lat_ll = lat_ul - numlat
        lon_ll = lon_ul

        # Define pixel centers along each direction
        longitudes = numpy.linspace(lon_ll + 0.5,
                                    lon_ll + numlon - 0.5, numlon)
        latitudes = numpy.linspace(lat_ll + 0.5,
                                   lat_ll + numlat - 0.5, numlat)

        # Define raster with latitudes going bottom-up (south to north).
        # Longitudes go left-right (west to east)
        for i in range(numlat):
            for j in range(numlon):
                A[numlat - 1 - i, j] = linear_function(longitudes[j],
                                                   latitudes[i])

        # Test first that original points are reproduced correctly
        for i, eta in enumerate(latitudes):
            for j, xi in enumerate(longitudes):

                val = interpolate_raster(longitudes, latitudes, A,
                                         [(xi, eta)], mode='linear')[0]
                assert numpy.allclose(val,
                                      linear_function(xi, eta),
                                      rtol=1e-12, atol=1e-12)

        # Then test that genuinly interpolated points are correct
        xis = numpy.linspace(lon_ll + 1, lon_ll + numlon - 1, 10 * numlon)
        etas = numpy.linspace(lat_ll + 1, lat_ll + numlat - 1, 10 * numlat)
        for xi in xis:
            for eta in etas:
                val = interpolate_raster(longitudes, latitudes, A,
                                         [(xi, eta)], mode='linear')[0]
                assert numpy.allclose(val,
                                      linear_function(xi, eta),
                                      rtol=1e-12, atol=1e-12)

    test_interpolation_wrapper.slow = 1

    def test_interpolation_functions(self):
        """Interpolation using Raster and Vector objects
        """

        # Create test data
        lon_ul = 100  # Longitude of upper left corner
        lat_ul = 10   # Latitude of upper left corner
        numlon = 8    # Number of longitudes
        numlat = 5    # Number of latitudes
        dlon = 1
        dlat = -1

        # Define array where latitudes are rows and longitude columns
        A = numpy.zeros((numlat, numlon))

        # Establish coordinates for lower left corner
        lat_ll = lat_ul - numlat
        lon_ll = lon_ul

        # Define pixel centers along each direction
        longitudes = numpy.linspace(lon_ll + 0.5,
                                    lon_ll + numlon - 0.5,
                                    numlon)
        latitudes = numpy.linspace(lat_ll + 0.5,
                                   lat_ll + numlat - 0.5,
                                   numlat)

        # Define raster with latitudes going bottom-up (south to north).
        # Longitudes go left-right (west to east)
        for i in range(numlat):
            for j in range(numlon):
                A[numlat - 1 - i, j] = linear_function(longitudes[j],
                                                       latitudes[i])

        # Write array to a raster file
        geotransform = (lon_ul, dlon, 0, lat_ul, 0, dlat)
        projection = ('GEOGCS["GCS_WGS_1984",'
                      'DATUM["WGS_1984",'
                      'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
                      'PRIMEM["Greenwich",0.0],'
                      'UNIT["Degree",0.0174532925199433]]')

        raster_filename = unique_filename(suffix='.tif')
        write_raster_data(A,
                          projection,
                          geotransform,
                          raster_filename)

        # Write test interpolation point to a vector file
        coordinates = []
        for xi in longitudes:
            for eta in latitudes:
                coordinates.append((xi, eta))

        vector_filename = unique_filename(suffix='.shp')
        write_vector_data(data=None,
                          projection=projection,
                          geometry=coordinates,
                          filename=vector_filename)

        # Read both datasets back in
        R = read_layer(raster_filename)
        V = read_layer(vector_filename)

        # Then test that axes and data returned by R are correct
        x, y = R.get_geometry()
        msg = 'X axes was %s, should have been %s' % (longitudes, x)
        assert numpy.allclose(longitudes, x), msg
        msg = 'Y axes was %s, should have been %s' % (latitudes, y)
        assert numpy.allclose(latitudes, y), msg
        AA = R.get_data()
        msg = 'Raster data was %s, should have been %s' % (AA, A)
        assert numpy.allclose(AA, A), msg

        # Test interpolation function
        I = R.interpolate(V, attribute_name='value')
        Icoordinates = I.get_geometry()
        Iattributes = I.get_data()

        assert numpy.allclose(Icoordinates, coordinates)

        # Test that interpolated points are correct
        for i, (xi, eta) in enumerate(Icoordinates):

            z = Iattributes[i]['value']
            #print xi, eta, z, linear_function(xi, eta)
            assert numpy.allclose(z, linear_function(xi, eta),
                                  rtol=1e-12)

        # FIXME (Ole): Need test for values outside grid.
        #              They should be NaN or something

        # Cleanup
        # FIXME (Ole): Shape files are a collection of files. How to remove?
        os.remove(vector_filename)

    def test_interpolation_lembang(self):
        """Interpolation using Lembang data set
        """

        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = '%s/lembang_mmi_hazmap.asc' % TESTDATA
        exposure_filename = '%s/test_buildings.shp' % TESTDATA

        # Read input data
        hazard_raster = read_layer(hazard_filename)
        A = hazard_raster.get_data()
        mmi_min, mmi_max = hazard_raster.get_extrema()

        exposure_vector = read_layer(exposure_filename)
        coordinates = exposure_vector.get_geometry()
        attributes = exposure_vector.get_data()

        # Test interpolation function
        I = hazard_raster.interpolate(exposure_vector,
                                      attribute_name='MMI')
        Icoordinates = I.get_geometry()
        Iattributes = I.get_data()
        assert numpy.allclose(Icoordinates, coordinates)

        # Check that interpolated MMI was done as expected
        fid = open('%s/test_buildings_percentage_loss_and_mmi.txt' % TESTDATA)
        reference_points = []
        MMI = []
        DAM = []
        for line in fid.readlines()[1:]:
            fields = line.strip().split(',')

            lon = float(fields[4][1:-1])
            lat = float(fields[3][1:-1])
            mmi = float(fields[-1][1:-1])

            reference_points.append((lon, lat))
            MMI.append(mmi)

        # Verify that coordinates are consistent
        msg = 'Interpolated coordinates do not match those of test data'
        assert numpy.allclose(Icoordinates, reference_points), msg

        # Verify interpolated MMI with test result
        for i in range(len(MMI)):
            calculated_mmi = Iattributes[i]['MMI']

            # Check that interpolated points are within range
            msg = ('Interpolated MMI %f was outside extrema: '
                   '[%f, %f]. ' % (calculated_mmi, mmi_min, mmi_max))
            assert mmi_min <= calculated_mmi <= mmi_max, msg

            # Check that result is within 2% - this is good enough
            # as this was calculated using EQRM and thus different.
            assert numpy.allclose(calculated_mmi, MMI[i], rtol=0.02)

            # Check that all original attributes were carried through
            # according to issue #101
            for key in attributes[i]:
                msg = 'Expected key %s in interpolated attributes' % key
                assert key in Iattributes[i], msg

                Ival = Iattributes[i][key]
                val = attributes[i][key]
                msg = ('Interpolated attribute %s did not have the '
                       'expected value %s. I got %s' % (key, val, Ival))
                assert Ival == val, msg

    def test_interpolation_tsunami(self):
        """Interpolation using tsunami data set works

        This is test for issue #19 about interpolation overshoot
        """

        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = ('%s/tsunami_max_inundation_depth_utm56s.tif'
                            % TESTDATA)
        exposure_filename = ('%s/tsunami_building_exposure.shp' % TESTDATA)

        # Read input data
        hazard_raster = read_layer(hazard_filename)
        A = hazard_raster.get_data()
        depth_min, depth_max = hazard_raster.get_extrema()

        exposure_vector = read_layer(exposure_filename)
        coordinates = exposure_vector.get_geometry()
        attributes = exposure_vector.get_data()

        # Test interpolation function
        I = hazard_raster.interpolate(exposure_vector,
                                      attribute_name='depth')
        Icoordinates = I.get_geometry()
        Iattributes = I.get_data()
        assert numpy.allclose(Icoordinates, coordinates)

        # Verify interpolated values with test result
        for i in range(len(Icoordinates)):

            interpolated_depth = Iattributes[i]['depth']
            # Check that interpolated points are within range
            msg = ('Interpolated depth %f at point %i was outside extrema: '
                   '[%f, %f]. ' % (interpolated_depth, i,
                                   depth_min, depth_max))

            if not numpy.isnan(interpolated_depth):
                assert depth_min <= interpolated_depth <= depth_max, msg

    def test_interpolation_tsunami_maumere(self):
        """Interpolation using tsunami data set from Maumere

        This is a test for interpolation (issue #19)
        """

        # Name file names for hazard level, exposure and expected fatalities
        hazard_filename = ('%s/maumere_aos_depth_20m_land_wgs84.asc'
                           % HAZDATA)
        exposure_filename = ('%s/maumere_pop_prj.shp' % TESTDATA)

        # Read input data
        H = read_layer(hazard_filename)
        A = H.get_data()
        depth_min, depth_max = H.get_extrema()

        # Compare extrema to values read off QGIS for this layer
        assert numpy.allclose([depth_min, depth_max], [0.0, 16.68],
                              rtol=1.0e-6, atol=1.0e-10)

        E = read_layer(exposure_filename)
        coordinates = E.get_geometry()
        attributes = E.get_data()

        # Test the interpolation function
        I = H.interpolate(E, attribute_name='depth')
        Icoordinates = I.get_geometry()
        Iattributes = I.get_data()
        assert numpy.allclose(Icoordinates, coordinates)

        N = len(Icoordinates)
        assert N == 891

        # Verify interpolated values with test result
        for i in range(N):

            interpolated_depth = Iattributes[i]['depth']
            pointid = attributes[i]['POINTID']

            if pointid == 263:

                #print i, pointid, attributes[i],
                #print interpolated_depth, coordinates[i]

                # Check that location is correct
                assert numpy.allclose(coordinates[i],
                                      [122.20367299, -8.61300358])

                # This is known to be outside inundation area so should
                # near zero
                assert numpy.allclose(interpolated_depth, 0.0,
                                      rtol=1.0e-12, atol=1.0e-12)

            if pointid == 148:
                # Check that location is correct
                assert numpy.allclose(coordinates[i],
                                      [122.2045912, -8.608483265])

                # This is in an inundated area with a surrounding depths of
                # 4.531, 3.911
                # 2.675, 2.583
                assert interpolated_depth < 4.531
                assert interpolated_depth < 3.911
                assert interpolated_depth > 2.583
                assert interpolated_depth > 2.675

                # This is a characterisation test for bilinear interpolation
                assert numpy.allclose(interpolated_depth, 3.62477204455,
                                      rtol=1.0e-12, atol=1.0e-12)

            # Check that interpolated points are within range
            msg = ('Interpolated depth %f at point %i was outside extrema: '
                   '[%f, %f]. ' % (interpolated_depth, i,
                                   depth_min, depth_max))

            if not numpy.isnan(interpolated_depth):
                assert depth_min <= interpolated_depth <= depth_max, msg

    def test_polygon_clipping(self):
        """Clipping using real polygon and point data from Maumere
        """

        # Test data
        polygon_filename = ('%s/test_poly.txt' % TESTDATA)  # Polygon 799
        points_filename = ('%s/test_points.txt' % TESTDATA)

        # Read
        polygon = []
        fid = open(polygon_filename)
        for line in fid.readlines():
            fields = line.strip().split(',')
            polygon.append([float(fields[0]), float(fields[1])])
        polygon = ensure_numeric(polygon)

        points = []
        fid = open(points_filename)
        for line in fid.readlines():
            fields = line.strip().split(',')
            points.append([float(fields[0]), float(fields[1])])
        points = ensure_numeric(points)

        # Clip
        indices, count = separate_points_by_polygon(points, polygon)

        # Expected number of points inside
        assert count == 458

        # First 10 inside
        assert numpy.alltrue(indices[:10] == [2279, 2290, 2297, 2306, 2307,
                                              2313, 2316, 2319, 2321, 2322])

        # Last 10 outside
        assert numpy.alltrue(indices[-10:] == [9, 8, 7, 6, 5, 4, 3, 2, 1, 0])

        # Store for viewing in e.g. QGis
        if False:  # True:
            Vector(geometry=[polygon]).write_to_file('test_poly.shp')
            pts_inside = points[indices[:count]]
            Vector(geometry=pts_inside).write_to_file('test_points_in.shp')
            pts_outside = points[indices[count:]]
            Vector(geometry=pts_outside).write_to_file('test_points_out.shp')

    def test_interpolation_from_polygons_one_poly(self):
        """Point interpolation using one polygon from Maumere works

        This is a test for interpolation (issue #48)
        """

        # Name file names for hazard level and exposure
        hazard_filename = ('%s/tsunami_polygon_WGS84.shp' % TESTDATA)
        exposure_filename = ('%s/building_Maumere.shp' % TESTDATA)

        # Read input data
        H = read_layer(hazard_filename)
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()

        # Cut down to make test quick
        # Polygon #799 is the one used in separate test
        H = Vector(data=H_attributes[799:800],
                   geometry=H_geometry[799:800],
                   projection=H.get_projection())
        #H.write_to_file('MM_799.shp')  # E.g. to view with QGis

        E = read_layer(exposure_filename)
        E_geometry = E.get_geometry()
        E_attributes = E.get_data()

        # Test interpolation function
        I = H.interpolate(E, name='depth',
                          attribute_name=None)  # Take all attributes across

        I_geometry = I.get_geometry()
        I_attributes = I.get_data()

        N = len(I_attributes)
        assert N == len(E_attributes)

        # Assert that expected attribute names exist
        I_names = I.get_attribute_names()
        H_names = H.get_attribute_names()
        E_names = E.get_attribute_names()
        for name in H_names:
            msg = 'Did not find hazard name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        for name in E_names:
            msg = 'Did not find exposure name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # Verify interpolated values with test result
        count = 0
        for i in range(N):
            category = I_attributes[i]['Catergory']  # The typo is as the data
            if category is not None:
                count += 1

        msg = ('Expected 458 points tagged with category, '
               'but got only %i' % count)
        assert count == 458, msg

    test_interpolation_from_polygons_one_poly.slow = 1

    def test_interpolation_from_polygons_multiple(self):
        """Point interpolation using multiple polygons from Maumere works

        This is a test for interpolation (issue #48)
        """

        # FIXME (Ole): Really should move this and subsequent tests to
        #              test_io.py

        # Name file names for hazard and exposure
        hazard_filename = ('%s/tsunami_polygon_WGS84.shp' % TESTDATA)
        exposure_filename = ('%s/building_Maumere.shp' % TESTDATA)

        # Read input data
        H = read_layer(hazard_filename)
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()

        # Full version
        H = Vector(data=H_attributes,
                   geometry=H_geometry,
                   projection=H.get_projection())

        E = read_layer(exposure_filename)
        E_geometry = E.get_geometry()
        E_attributes = E.get_data()

        # Test interpolation function
        I = H.interpolate(E, name='depth',
                          attribute_name=None)  # Take all attributes across
        #I.write_to_file('MM_res.shp')

        I_geometry = I.get_geometry()
        I_attributes = I.get_data()

        N = len(I_attributes)
        assert N == len(E_attributes)

        # Assert that expected attribute names exist
        I_names = I.get_attribute_names()
        H_names = H.get_attribute_names()
        E_names = E.get_attribute_names()
        for name in H_names:
            msg = 'Did not find hazard name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        for name in E_names:
            msg = 'Did not find exposure name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # Verify interpolated values with test result
        counts = {}
        for i in range(N):
            attrs = I_attributes[i]
            msg = ('Did not find default attribute %s in %s'
                   % (DEFAULT_ATTRIBUTE, attrs.keys()))
            assert DEFAULT_ATTRIBUTE in attrs, msg

            # Count items using default attribute
            if DEFAULT_ATTRIBUTE not in counts:
                counts[DEFAULT_ATTRIBUTE] = 0
                counts['Not ' + DEFAULT_ATTRIBUTE] = 0

            if attrs[DEFAULT_ATTRIBUTE] is True:
                counts[DEFAULT_ATTRIBUTE] += 1
            else:
                counts['Not ' + DEFAULT_ATTRIBUTE] += 1

            # Count items in each specific category
            category = attrs['Catergory']  # The typo is as the data
            if category not in counts:
                counts[category] = 0
            counts[category] += 1

        if len(H) == 192:
            # In case we used cut down version
            msg = ('Expected 100 points tagged with category "High", '
                   'but got only %i' % counts['High'])
            assert counts['High'] == 100, msg

            msg = ('Expected 739 points tagged with category "Very High", '
                   'but got only %i' % counts['Very High'])
            assert counts['Very High'] == 739, msg

            # Check default attribute too
            msg = ('Expected 839 points tagged with default attribute "%s", '
                   'but got only %i' % (DEFAULT_ATTRIBUTE,
                                        counts[DEFAULT_ATTRIBUTE]))
            assert counts[DEFAULT_ATTRIBUTE] == 839, msg

            msg = 'Affected and not affected does not add up'
            assert (counts[DEFAULT_ATTRIBUTE] +
                    counts['Not ' + DEFAULT_ATTRIBUTE]) == len(E), msg

        if len(H) == 1032:
            # The full version
            msg = ('Expected 2258 points tagged with category "High", '
                   'but got only %i' % counts['High'])
            assert counts['High'] == 2258, msg

            msg = ('Expected 1190 points tagged with category "Very High", '
                   'but got only %i' % counts['Very High'])
            assert counts['Very High'] == 1190, msg

            # Check default attribute too
            msg = ('Expected 3452 points tagged with default attribute '
                   '"%s = True", '
                   'but got only %i' % (DEFAULT_ATTRIBUTE,
                                        counts[DEFAULT_ATTRIBUTE]))
            assert counts[DEFAULT_ATTRIBUTE] == 3452, msg

            msg = ('Expected 76 points tagged with default attribute '
                   '"%s = False", '
                   'but got only %i' % (DEFAULT_ATTRIBUTE,
                                        counts['Not ' + DEFAULT_ATTRIBUTE]))
            assert counts['Not ' + DEFAULT_ATTRIBUTE] == 76, msg

            msg = 'Affected and not affected does not add up'
            assert (counts[DEFAULT_ATTRIBUTE] +
                    counts['Not ' + DEFAULT_ATTRIBUTE]) == len(E), msg

        #for key in counts:
        #    print key, counts[key]

    test_interpolation_from_polygons_multiple.slow = 1

    @numpy.testing.dec.skipif(True, 'Re-enable after fixing issue #48')
    def test_point_interpolation_from_polygons_one_attribute(self):
        """Point interpolation from multiple polygons works with attribute

        This is a test for interpolation (issue #48)
        """

        # FIXME: test passes, but it is not tested that
        #        nothing *but* the requested attribute
        #        has been carried over. Do we need this?

        # Name file names for hazard and exposure
        hazard_filename = ('%s/tsunami_polygon_WGS84.shp' % TESTDATA)
        exposure_filename = ('%s/building_Maumere.shp' % TESTDATA)

        # Read input data
        H = read_layer(hazard_filename)
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()

        # Cut down to make test quick
        H = Vector(data=H_attributes[658:850],
                   geometry=H_geometry[658:850],
                   projection=H.get_projection())
        #H.write_to_file('MM_cut.shp')  # E.g. to view with QGis

        E = read_layer(exposure_filename)
        E_geometry = E.get_geometry()
        E_attributes = E.get_data()

        # Test interpolation function
        I = H.interpolate(E, name='depth',
                          attribute='Catergory')  # Spelling is as in test data
        #I.write_to_file('MM_res.shp')

        I_geometry = I.get_geometry()
        I_attributes = I.get_data()

        N = len(I_attributes)
        assert N == len(E_attributes)

        # Assert that expected attribute names exist
        I_names = I.get_attribute_names()
        H_names = H.get_attribute_names()
        E_names = E.get_attribute_names()

        name = 'Catergory'
        msg = 'Did not find hazard name "%s" in %s' % (name, I_names)
        assert name in I_names, msg

        print I_names

        for name in E_names:
            msg = 'Did not find exposure name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # Verify interpolated values with test result
        counts = {}
        for i in range(N):
            category = I_attributes[i]['Catergory']  # The typo is as the data
            if category not in counts:
                counts[category] = 0

            counts[category] += 1

        msg = ('Expected 100 points tagged with category "High", '
               'but got only %i' % counts['High'])
        assert counts['High'] == 100, msg

        msg = ('Expected 739 points tagged with category "Very High", '
               'but got only %i' % counts['Very High'])
        assert counts['Very High'] == 739, msg

    def test_interpolation_from_polygons_error_handling(self):
        """Interpolation using polygons handles input errors as expected

        This catches situation where input data have different projections
        This is a test for interpolation (issue #48)
        """

        # Input data
        hazard_filename = ('%s/tsunami_polygon.shp' % TESTDATA)  # UTM
        exposure_filename = ('%s/building_Maumere.shp' % TESTDATA)  # GEO

        # Read input data
        H = read_layer(hazard_filename)
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()

        E = read_layer(exposure_filename)
        E_geometry = E.get_geometry()
        E_attributes = E.get_data()

        # Check projection mismatch is caught
        try:
            H.interpolate(E)
        except VerificationError, e:
            msg = ('Projection mismatch shoud have been caught: %s'
                   % str(e))
            assert 'Projections' in str(e), msg
        else:
            msg = 'Should have raised error about projection mismatch'
            raise Exception(msg)
    test_interpolation_from_polygons_error_handling.slow = 1

    def test_line_clipping_by_polygon(self):
        """Multiple lines are clipped correctly by complex polygon
        """

        # Test data

        # Polygon 799  (520 x 2)
        polygon_filename = ('%s/test_poly.txt' % TESTDATA)
        # 156 composite lines
        lines_filename = ('%s/test_lines.pck' % TESTDATA)

        # Read
        test_polygon = []
        fid = open(polygon_filename)
        for line in fid.readlines():
            fields = line.strip().split(',')
            test_polygon.append([float(fields[0]), float(fields[1])])
        test_polygon = ensure_numeric(test_polygon)

        fid = open(lines_filename)
        test_lines = cPickle.load(fid)
        fid.close()

        # Clip
        #for i in range(len(lines)):
        #    inside_line_segments, outside_line_segments = \
        #        clip_lines_by_polygon([lines[i]], polygon)
        #
        #    if len(inside_line_segments) > 0:
        #        print
        #        print 'Found', i, len(lines[i]), len(outside_line_segments)
        #
        #        print
        #        print 'Line'
        #        for j in range(lines[i].shape[0]):
        #            print '[%f, %f], ' % (lines[i][j, 0], lines[i][j, 1])
        #        print

        # Clip
        inside_line_segments, outside_line_segments = \
            clip_lines_by_polygon(test_lines, test_polygon)

        # These lines have compontes both inside and outside
        assert len(inside_line_segments) > 0
        assert len(outside_line_segments) > 0

        # Check that midpoints of each segment are correctly placed
        inside_centroids = []
        for seg in inside_line_segments:
            midpoint = (seg[0] + seg[1]) / 2
            inside_centroids.append(midpoint)
            assert is_inside_polygon(midpoint, test_polygon)

        outside_centroids = []
        for seg in outside_line_segments:
            midpoint = (seg[0] + seg[1]) / 2
            outside_centroids.append(midpoint)
            assert not is_inside_polygon(midpoint, test_polygon)

        # Possibly generate files for visual inspection with e.g. QGis
        if False:
            # Store as shape files for visual inspection e.g. by QGis
            P = Vector(geometry=[test_polygon])
            P.write_to_file('test_polygon.shp')

            L = Vector(geometry=test_lines, geometry_type='line')
            L.write_to_file('test_lines.shp')

            L = Vector(geometry=inside_line_segments, geometry_type='line')
            L.write_to_file('inside_lines.shp')

            L = Vector(geometry=outside_line_segments, geometry_type='line')
            L.write_to_file('outside_lines.shp')

            L = Vector(geometry=inside_centroids, geometry_type='point')
            L.write_to_file('inside_centroids.shp')

            L = Vector(geometry=outside_centroids, geometry_type='point')
            L.write_to_file('outside_centroids.shp')

        # Characterisation test based on against visual inspection with QGIS
        #print inside_line_segments[10]
        #print outside_line_segments[5]
        assert numpy.allclose(inside_line_segments[10],
                              [[122.24672045, -8.63255444],
                               [122.24699685, -8.63265486],
                               [122.24793801, -8.63292556],
                               [122.24829356, -8.63304013],
                               [122.25118524, -8.63364424],
                               [122.25520475, -8.63433717],
                               [122.25695448, -8.63469273]])

        assert numpy.allclose(outside_line_segments[5],
                              [[122.18321143, -8.58901526],
                               [122.18353015, -8.58890024],
                               [122.18370883, -8.58884135],
                               [122.18376524, -8.58881115],
                               [122.18381025, -8.58878405],
                               [122.1838646, -8.58875119],
                               [122.18389685, -8.58873165],
                               [122.18394329, -8.58869283],
                               [122.18401084, -8.58862284],
                               [122.18408657, -8.58853526],
                               [122.18414936, -8.58845887],
                               [122.18425204, -8.58832279],
                               [122.18449009, -8.58804974],
                               [122.18457453, -8.58798668],
                               [122.18466284, -8.5878697]])

    test_line_clipping_by_polygon.slow = 1

    def test_line_interpolation_from_polygons_one_poly(self):
        """Line clipping and interpolation using one polygon works

        This is a test for road interpolation (issue #55)
        """

        # Name file names for hazard level and exposure
        hazard_filename = ('%s/tsunami_polygon_WGS84.shp' % TESTDATA)
        exposure_filename = ('%s/roads_Maumere.shp' % TESTDATA)

        # Read input data
        H = read_layer(hazard_filename)
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()

        # Cut down to polygon #799 to make test quick
        H = Vector(data=H_attributes[799:800],
                   geometry=H_geometry[799:800],
                   projection=H.get_projection())
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()

        E = read_layer(exposure_filename)
        E_geometry = E.get_geometry()
        E_attributes = E.get_data()

        # Test interpolation function
        I = H.interpolate(E, name='depth',
                          attribute_name=None)  # Take all attributes across
        I_geometry = I.get_geometry()
        I_attributes = I.get_data()

        N = len(I_attributes)

        # Possibly generate files for visual inspection with e.g. QGis
        if False:  # True:
            L = Vector(geometry=H_geometry, geometry_type='polygon',
                       data=H_attributes)
            L.write_to_file('test_polygon.shp')

            L = Vector(geometry=I_geometry, geometry_type='line',
                       data=I_attributes)
            L.write_to_file('interpolated_lines.shp')

        # Assert that expected attribute names exist
        I_names = I.get_attribute_names()
        H_names = H.get_attribute_names()
        E_names = E.get_attribute_names()
        for name in H_names:
            msg = 'Did not find hazard name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        for name in E_names:
            msg = 'Did not find exposure name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # Verify interpolated values with test result
        count = 0
        counts = {}
        for i in range(N):

            # Check that default attribute is present
            attrs = I_attributes[i]
            msg = ('Did not find default attribute %s in %s'
                   % (DEFAULT_ATTRIBUTE, attrs.keys()))
            assert DEFAULT_ATTRIBUTE in attrs, msg

            # Count items using default attribute
            if DEFAULT_ATTRIBUTE not in counts:
                counts[DEFAULT_ATTRIBUTE] = 0
                counts['Not ' + DEFAULT_ATTRIBUTE] = 0

            if attrs[DEFAULT_ATTRIBUTE] is True:
                counts[DEFAULT_ATTRIBUTE] += 1
            else:
                counts['Not ' + DEFAULT_ATTRIBUTE] += 1

            # Check specific attribute
            category = I_attributes[i]['Catergory']  # The typo is as the data
            if category is not None:
                assert category.lower() in ['high', 'very high']
                count += 1

        msg = ('Expected 14 points tagged with category, '
               'but got only %i' % count)
        assert count == 14, msg

        assert len(I_geometry) == 181

        assert I_attributes[129]['Catergory'] == 'Very High'
        assert I_attributes[135]['Catergory'] is None

        # Check default attribute too
        msg = ('Expected 14 segments tagged with default attribute '
               '"%s = True", '
               'but got only %i' % (DEFAULT_ATTRIBUTE,
                                    counts[DEFAULT_ATTRIBUTE]))
        assert counts[DEFAULT_ATTRIBUTE] == 14, msg

        msg = ('Expected 167 points tagged with default attribute '
               '"%s = False", '
               'but got only %i' % (DEFAULT_ATTRIBUTE,
                                    counts['Not ' + DEFAULT_ATTRIBUTE]))
        assert counts['Not ' + DEFAULT_ATTRIBUTE] == 167, msg

        msg = 'Affected and not affected does not add up'
        assert (counts[DEFAULT_ATTRIBUTE] +
                counts['Not ' + DEFAULT_ATTRIBUTE]) == len(I), msg

    test_line_interpolation_from_polygons_one_poly.slow = 1

    @numpy.testing.dec.skipif(True, 'Re-enable after fixing issue #55')
    def test_line_interpolation_from_polygons_one_attribute(self):
        """Line interpolation using one polygon works with attribute

        This is a test for road interpolation (issue #55)
        """

        # FIXME: test passes, but functionality is not really there.
        # Do we need it?

        # Name file names for hazard level and exposure
        hazard_filename = ('%s/tsunami_polygon_WGS84.shp' % TESTDATA)
        exposure_filename = ('%s/roads_Maumere.shp' % TESTDATA)

        # Read input data
        H = read_layer(hazard_filename)
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()

        # Cut down to polygon #799 to make test quick
        H = Vector(data=H_attributes[799:800],
                   geometry=H_geometry[799:800],
                   projection=H.get_projection())
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()

        E = read_layer(exposure_filename)
        E_geometry = E.get_geometry()
        E_attributes = E.get_data()

        # Test interpolation function
        I = H.interpolate(E, name='depth',
                          attribute='Catergory')  # Spelling is as in test data
        I_geometry = I.get_geometry()
        I_attributes = I.get_data()

        N = len(I_attributes)

        # Possibly generate files for visual inspection with e.g. QGis
        if False:
            L = Vector(geometry=H_geometry, geometry_type='polygon',
                       data=H_attributes)
            L.write_to_file('test_polygon.shp')

            L = Vector(geometry=I_geometry, geometry_type='line',
                       data=I_attributes)
            L.write_to_file('interpolated_lines.shp')

        # Assert that expected attribute names exist
        I_names = I.get_attribute_names()
        H_names = H.get_attribute_names()
        E_names = E.get_attribute_names()

        name = 'Catergory'
        msg = 'Did not find hazard name "%s" in %s' % (name, I_names)
        assert name in I_names, msg

        for name in E_names:
            msg = 'Did not find exposure name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # Verify interpolated values with test result
        counts = {}
        for i in range(N):

            # Check specific attribute
            category = I_attributes[i]['Catergory']  # The typo is as the data
            if category not in counts:
                counts[category] = 0

            counts[category] += 1

        msg = ('Expected 14 segments tagged with category "Very High", '
               'but got only %i' % counts['Very High'])
        assert counts['Very High'] == 14, msg

    @numpy.testing.dec.skipif(True, 'Re-enable after fixing issue #55')
    def test_line_interpolation_from_polygons(self):
        """Line clipping and interpolation using multiple polygons works

        This is a test for road interpolation (issue #55)
        """

        # NOT YET FULLY DONE

        # Name file names for hazard level and exposure
        hazard_filename = ('%s/tsunami_polygon_WGS84.shp' % TESTDATA)
        exposure_filename = ('%s/roads_Maumere.shp' % TESTDATA)

        # Read input data
        H = read_layer(hazard_filename)
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()

        # MakeCut down to a few polygons
        H = Vector(data=H_attributes[799:],
                   geometry=H_geometry[799:],
                   projection=H.get_projection())
        H_attributes = H.get_data()
        H_geometry = H.get_geometry()

        E = read_layer(exposure_filename)
        E_geometry = E.get_geometry()
        E_attributes = E.get_data()

        # Test interpolation function
        I = H.interpolate(E, name='depth',
                          attribute=None)  # Take all attributes across
        I_geometry = I.get_geometry()
        I_attributes = I.get_data()

        N = len(I_attributes)

        # Possibly generate files for visual inspection with e.g. QGis
        if False:  # True:
            L = Vector(geometry=H_geometry, geometry_type='polygon',
                       data=H_attributes)
            L.write_to_file('test_polygon.shp')

            L = Vector(geometry=I_geometry, geometry_type='line',
                       data=I_attributes)
            L.write_to_file('interpolated_lines.shp')

        # Assert that expected attribute names exist
        I_names = I.get_attribute_names()
        H_names = H.get_attribute_names()
        E_names = E.get_attribute_names()
        for name in H_names:
            msg = 'Did not find hazard name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        for name in E_names:
            msg = 'Did not find exposure name "%s" in %s' % (name, I_names)
            assert name in I_names, msg

        # Verify interpolated values with test result
        count = 0
        counts = {}
        for i in range(N):

            # Check that default attribute is present
            attrs = I_attributes[i]
            msg = ('Did not find default attribute %s in %s'
                   % (DEFAULT_ATTRIBUTE, attrs.keys()))
            assert DEFAULT_ATTRIBUTE in attrs, msg

            # Count items using default attribute
            if DEFAULT_ATTRIBUTE not in counts:
                counts[DEFAULT_ATTRIBUTE] = 0
                counts['Not ' + DEFAULT_ATTRIBUTE] = 0

            if attrs[DEFAULT_ATTRIBUTE] is True:
                counts[DEFAULT_ATTRIBUTE] += 1
            else:
                counts['Not ' + DEFAULT_ATTRIBUTE] += 1

            # Check specific attribute
            category = I_attributes[i]['Catergory']  # The typo is as the data
            if category is not None:
                assert category.lower() in ['high', 'very high']
                count += 1

        msg = ('Expected 59 points tagged with category, '
               'but got %i' % count)
        assert count == 59, msg

        # FIXME (Ole): Not finished (5/3/12)
        return

        print len(I_geometry)
        assert len(I_geometry) == 181

        assert I_attributes[129]['Catergory'] == 'Very High'
        assert I_attributes[135]['Catergory'] is None

        # Check default attribute too
        msg = ('Expected 14 segments tagged with default attribute '
               '"%s = True", '
               'but got only %i' % (DEFAULT_ATTRIBUTE,
                                    counts[DEFAULT_ATTRIBUTE]))
        assert counts[DEFAULT_ATTRIBUTE] == 14, msg

        msg = ('Expected 167 points tagged with default attribute '
               '"%s = False", '
               'but got only %i' % (DEFAULT_ATTRIBUTE,
                                    counts['Not ' + DEFAULT_ATTRIBUTE]))
        assert counts['Not ' + DEFAULT_ATTRIBUTE] == 167, msg

        msg = 'Affected and not affected does not add up'
        assert (counts[DEFAULT_ATTRIBUTE] +
                counts['Not ' + DEFAULT_ATTRIBUTE]) == len(I), msg

    def test_layer_integrity_raises_exception(self):
        """Layers without keywords raise exception
        """

        population = 'Population_Jakarta_geographic.asc'
        plugin_name = 'HKVtest'

        hazard_layers = ['Flood_Current_Depth_Jakarta_geographic.asc',
                         'Flood_Design_Depth_Jakarta_geographic.asc']

        for i, filename in enumerate(hazard_layers):
            hazard_filename = join(HAZDATA, filename)
            exposure_filename = join(TESTDATA, population)

            # Get layers using API
            H = read_layer(hazard_filename)
            E = read_layer(exposure_filename)

            plugin_list = get_plugins(plugin_name)
            IF = plugin_list[0][plugin_name]

            # Call impact calculation engine normally
            impact_layer = calculate_impact(layers=[H, E],
                                            impact_fcn=IF)

            # Make keyword value empty and verify exception is raised
            expected_category = E.keywords['category']
            E.keywords['category'] = ''
            try:
                impact_layer = calculate_impact(layers=[H, E],
                                                impact_fcn=IF)
            except VerificationError, e:
                # Check expected error message
                assert 'No value found' in str(e)
            else:
                msg = 'Empty keyword value should have raised exception'
                raise Exception(msg)

            # Restore for next test
            E.keywords['category'] = expected_category

            # Remove critical keywords and verify exception is raised
            if i == 0:
                del H.keywords['category']
            else:
                del H.keywords['subcategory']

            try:
                impact_layer = calculate_impact(layers=[H, E],
                                                impact_fcn=IF)
            except Exception, e:
                # Check expected error message
                assert 'did not have required keyword' in str(e)
            else:
                msg = 'Missing keyword should have raised exception'
                raise Exception(msg)

    def test_padang_building_examples(self):
        """Padang building impact calculation works through the API
        """

        plugin_name = 'Padang Earthquake Building Damage Function'

        # Test for a range of hazard layers
        for mmi_filename in ['Shakemap_Padang_2009.asc']:
                             #'Lembang_Earthquake_Scenario.asc']:

            # Upload input data
            hazard_filename = join(HAZDATA, mmi_filename)
            exposure_filename = join(TESTDATA, 'Padang_WGS84.shp')

            # Call calculation routine
            bbox = '96.956, -5.51, 104.63933, 2.289497'

            # Get layers using API
            H = read_layer(hazard_filename)
            E = read_layer(exposure_filename)

            plugin_list = get_plugins(plugin_name)
            assert len(plugin_list) == 1
            assert plugin_list[0].keys()[0] == plugin_name
            IF = plugin_list[0][plugin_name]

            # Call impact calculation engine
            impact_vector = calculate_impact(layers=[H, E],
                                             impact_fcn=IF)
            impact_filename = impact_vector.get_filename()

            # Read hazard data for reference
            hazard_raster = read_layer(hazard_filename)
            A = hazard_raster.get_data()
            mmi_min, mmi_max = hazard_raster.get_extrema()

            # Extract calculated result
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

                building_class = attributes[i]['VCLASS']

                # Check calculated damage
                calculated_dam = attributes[i]['DAMAGE']
                print calculated_mmi
                verified_dam = padang_check_results(calculated_mmi,
                                                    building_class)
                #print calculated_mmi, building_class, calculated_dam
                if verified_dam:
                    msg = ('Calculated damage was not as expected '
                             'for hazard layer %s. I got %f '
                           'but expected %f' % (hazard_filename,
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

    test_padang_building_examples.slow = 1

    def test_itb_building_function(self):
        """Damage ratio (estimated repair cost relative to replacement cost)
           can be computed using the ITB building vulnerability model.
           (Test data from Hyeuk Ryu).
           As of July 4, 2012, the vulnerability model used to generate
           the reference values is dummy one, and it will be updated with
           the ITB's model later.
        """

        # Name file names for hazard level, exposure and expected impact
        hazard_filename = '%s/Shakemap_Padang_2009.asc' % HAZDATA
        exposure_filename = '%s/Padang_WGS84.shp' % TESTDATA
        damage_filename = '%s/reference_result_itb.csv' % TESTDATA

        a = open(damage_filename).readlines()[1:]
        ref_damage = []
        for item in a:
            b = item.strip('\n').split(',')
            ref_damage.append(float(b[2]))
        ref_damage = numpy.array(ref_damage)

        # Calculate impact using API
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        plugin_name = 'I T B Earthquake Building Damage Function'
        plugin_list = get_plugins(plugin_name)
        assert len(plugin_list) == 1
        assert plugin_list[0].keys()[0] == plugin_name
        IF = plugin_list[0][plugin_name]

        # Call impact calculation engine
        impact_vector = calculate_impact(layers=[H, E],
                                             impact_fcn=IF)
        attributes = impact_vector.get_data()

#        calculated_damage = []
        for i in range(len(attributes)):
            calculated_damage = attributes[i]['DAMAGE']
            bldg_class = attributes[i]['ITB_Class']
            msg = ('Calculated damage did not match expected result: \n'
               'I got %s\n'
               'Expected %s for bldg type: %s' % (calculated_damage,
                                                  ref_damage[i], bldg_class))
            assert nanallclose(calculated_damage, ref_damage[i],
                               # Reference data is single precision
                               atol=1.0e-6), msg

#        print calculated_damage.shape
#        bldg_class = attributes[:]['VCLASS']
#        impact_filename = impact_vector.get_filename()
#        I = read_layer(impact_filename)
#        calculated_result = I.get_data()

#        keywords = I.get_keywords()

#        print keywords
#        print calculated_damage
    test_itb_building_function.slow = 1

    def test_flood_on_roads(self):
        """Jakarta flood impact on roads calculated correctly
        """
        floods = 'Flood_Current_Depth_Jakarta_geographic.asc'
        roads = 'indonesia_highway_sample.shp'
        plugin_name = 'Flood Road Impact Function'

        hazard_filename = join(HAZDATA, floods)
        exposure_filename = join(TESTDATA, roads)

        # Get layers using API
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        plugin_list = get_plugins(plugin_name)
        IF = plugin_list[0][plugin_name]

        impact_layer = calculate_impact(layers=[H, E],
                                        impact_fcn=IF)

    def test_erf(self):
        """Test ERF approximation

        Reference data obtained from scipy as follows:
        A = (numpy.arange(20) - 10.) / 2
        F = scipy.special.erf(A)

        See also table at http://en.wikipedia.org/wiki/Error_function
        """

        # Simple tests
        assert numpy.allclose(erf(0), 0.0, rtol=1.0e-6, atol=1.0e-6)

        x = erf(1)
        r = 0.842700792949715
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        x = erf(0.5)
        r = 0.5204999
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        x = erf(3)
        r = 0.999977909503001
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        # Reference data
        R = [-1., -1., -0.99999998, -0.99999926, -0.99997791, -0.99959305,
              -0.99532227, -0.96610515, -0.84270079, -0.52049988, 0.,
              0.52049988, 0.84270079, 0.96610515, 0.99532227, 0.99959305,
              0.99997791, 0.99999926, 0.99999998, 1.]

        A = (numpy.arange(20) - 10.) / 2
        X = erf(A)
        msg = ('ERF was not correct. I got %s but expected %s' %
               (str(X), str(R)))
        assert numpy.allclose(X, R, atol=1.0e-6, rtol=1.0e-12), msg

    def test_normal_cdf(self):
        """Test Normal Cumulative Distribution Function

        Reference data obtained from scipy as follows:

        A = (numpy.arange(20) - 10.) / 5
        R = scipy.stats.norm.cdf(A)
        """

        # Simple tests
        x = normal_cdf(0.0)
        r = 0.5
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        x = normal_cdf(0.5)
        r = 0.69146246127401312
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        x = normal_cdf(3.50)
        r = 0.99976737092096446
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        # Out of bounds
        x = normal_cdf(-6)
        r = 0
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-6), msg

        x = normal_cdf(10)
        r = 1
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        # Reference data
        R = [0.02275013, 0.03593032, 0.05479929, 0.08075666, 0.11506967,
             0.15865525, 0.2118554, 0.27425312, 0.34457826, 0.42074029, 0.5,
             0.57925971, 0.65542174, 0.72574688, 0.7881446, 0.84134475,
             0.88493033, 0.91924334, 0.94520071, 0.96406968]

        A = (numpy.arange(20) - 10.) / 5
        X = normal_cdf(A)
        msg = ('CDF was not correct. I got %s but expected %s' %
               (str(X), str(R)))
        assert numpy.allclose(X, R, atol=1.0e-6, rtol=1.0e-12), msg

    def test_lognormal_cdf(self):
        """Test Log-normal Cumulative Distribution Function

        Reference data obtained from scipy as follows:

        A = (numpy.arange(20) - 10.) / 5
        R = scipy.stats.lognorm.cdf(A)
        """

        # Suppress warnings about invalid value in multiply and divide zero
        # http://comments.gmane.org/gmane.comp.python.numeric.general/43218
        # http://docs.scipy.org/doc/numpy/reference/generated/numpy.seterr.html
        old_numpy_setting = numpy.seterr(divide='ignore')

        # Simple tests
        x = lognormal_cdf(0.0)
        r = normal_cdf(numpy.log(0.0))
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg
        numpy.seterr(**old_numpy_setting)

        x = lognormal_cdf(0.5)
        r = normal_cdf(numpy.log(0.5))
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        x = lognormal_cdf(3.50)
        r = normal_cdf(numpy.log(3.5))
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-12), msg

        # Out of bounds
        x = lognormal_cdf(10)
        r = normal_cdf(numpy.log(10))
        msg = 'Expected %.12f, but got %.12f' % (r, x)
        assert numpy.allclose(x, r, rtol=1.0e-6, atol=1.0e-6), msg

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_Engine, 'test_itb')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
