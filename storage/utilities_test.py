"""Utilities to to support test suite
"""

import os
import types
import numpy

# Find parent parent directory to path
# NOTE: This must match Makefile target testdata
# FIXME (Ole): Use environment variable for this.
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                      '..',
                                      '..'))  # Assuming test data two lvls up

# Location of test data
TESTDATANAME = 'riab_test_data'
TESTREPO = 'http://www.aifdr.org/svn/%s' % TESTDATANAME
TESTDATA = os.path.join(pardir, TESTDATANAME)

DEMODATANAME = 'riab_demo_data'
DEMOREPO = 'http://www.aifdr.org/svn/%s' % DEMODATANAME
DEMODATA = os.path.join(pardir, DEMODATANAME)

# Known feature counts in test data
FEATURE_COUNTS = {'lembang_schools.shp': 144,
                  'tsunami_exposure_BB.shp': 7529,
                  'kecamatan_geo.shp': 42,
                  'Padang_WGS84.shp': 3896,
                  'OSM_building_polygons_20110905.shp': 34960,
                  'indonesia_highway_sample.shp': 2,
                  'OSM_subset.shp': 79}

# For testing
GEOTRANSFORMS = [(105.3000035, 0.008333, 0.0, -5.5667785, 0.0, -0.008333),
                 (105.29857, 0.0112, 0.0, -5.565233000000001, 0.0, -0.0112),
                 (96.956, 0.03074106, 0.0, 2.2894972560001, 0.0, -0.03074106)]


def _same_API(X, Y, exclude=None):
    """Check that public methods of X also exist in Y
    """

    if exclude is None:
        exclude = []

    for name in dir(X):

        # Skip internal symbols
        if name.startswith('_'):
            continue

        # Skip explicitly excluded methods
        if name in exclude:
            continue

        # Check membership of methods
        attr = getattr(X, name)
        if isinstance(attr, types.MethodType):
            if name not in dir(Y):
                msg = ('Method "%s" of "%s" was not found in "%s"'
                       % (name, X, Y))
                raise Exception(msg)


def same_API(X, Y, exclude=None):
    """Check that public methods of X and Y are the same.

    Input
        X, Y: Python objects
        exclude: List of names to exclude from comparison or None
    """

    _same_API(X, Y, exclude=exclude)
    _same_API(Y, X, exclude=exclude)

    return True


def combine_coordinates(x, y):
    """Make list of all combinations of points for x and y coordinates
    """

    points = []
    for px in x:
        for py in y:
            points.append((px, py))
    points = numpy.array(points)

    return points
