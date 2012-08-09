import unittest
import numpy
import sys
import os
from os.path import join

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from common.testing import TESTDATA, HAZDATA, EXPDATA, DATADIR
from raster import Raster
from vector import Vector
from storage.core import read_layer
from clipping import *


class Test_Clipping(unittest.TestCase):
    """Tests for clipping module
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_clip_raster_by_polygons(self):
        """Raster grids can be clipped by polygon layers
        """

        # Name input files
        poly = join(TESTDATA, 'kabupaten_jakarta_singlepart.shp')
        grid = join(EXPDATA, 'glp10ag.asc')
        test = join(TESTDATA, 'population_kabupaten.shp')

        # Get layers using API
        P = read_layer(poly)
        R = read_layer(grid)
        T = read_layer(test)

        print len(P)
        print len(R)

        # Clip
        C = clip_raster_by_polygons(R, P)

        # Verify result
        attributes = []
        for c in C:
            values = c[1]
            s = numpy.sum(values)
            attributes.append({'population': s})

        print attributes, len(attributes)
        ref = T.get_data()
        print ref, len(ref)

        for i, a in enumerate(attributes):
            print attributes[i]
            print ref[i]['SUM']

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_Clipping, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
