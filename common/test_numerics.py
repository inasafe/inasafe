import unittest
import numpy
import sys
import os

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from numerics import *

class Test_Numerics(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_axes2points(self):
        """Grid axes can be converted to point coordinates for all pixels
        """

        # Test 1
	x = numpy.linspace(1, 3, 3)
	y = numpy.linspace(10, 20, 2)
	P = axes2points(x, y)
        assert numpy.allclose(P, [[1.,  10.],
                                  [1.,  20.],
                                  [2.,  10.],
                                  [2.,  20.],
                                  [3.,  10.],
                                  [3.,  20.]],
                              rtol=0.0, atol=0.0)

        # Test 2
	x = numpy.linspace(1, 5, 11)
	y = numpy.linspace(10, 20, 5)
	P = axes2points(x, y)
        assert numpy.allclose(P[6, :], [1.4, 12.5])


if __name__ == '__main__':
    suite = unittest.makeSuite(Test_Numerics, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


