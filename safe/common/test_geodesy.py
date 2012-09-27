
import unittest
import numpy
from geodesy import Point


class TestCase(unittest.TestCase):

    def setUp(self):
        self.eps = 0.001    # Accept 0.1 % relative error

        self.RSISE = Point(-35.27456, 149.12065)
        self.Home = Point(-35.25629, 149.12494)     # 28 Scrivener Street, ACT
        self.Syd = Point(-33.93479, 151.16794)      # Sydney Airport
        self.Nadi = Point(-17.75330, 177.45148)     # Nadi Airport
        self.Kobenhavn = Point(55.70248, 12.58364)  # Kobenhavn, Denmark
        self.Muncar = Point(-8.43, 114.33)          # Muncar, Indonesia

    def testBearingNorth(self):
        """Bearing due north (0 deg) correct within double precision
        """

        eps = 1.0e-12

        p1 = Point(0.0, 0.0)
        p2 = Point(1.0, 0.0)

        b = p1.bearing_to(p2)
        msg = 'Computed northward bearing: %d, Should have been: %d' % (b, 0)
        assert numpy.allclose(b, 0, rtol=eps, atol=eps), msg

    def testBearingSouth(self):
        """Bearing due south (180 deg) is correct within double precision
        """

        eps = 1.0e-12
        B = 180  # True bearing

        p1 = Point(0.0, 0.0)
        p2 = Point(1.0, 0.0)

        b = p2.bearing_to(p1)
        msg = 'Computed southward bearing %d. Expected %d' % (b, B)
        assert numpy.allclose(b, B, rtol=eps, atol=eps), msg

    def testBearingEast(self):
        """Bearing due west (270 deg) is correct within double precision
        """

        eps = 1.0e-12
        B = 90  # True bearing

        p1 = Point(0.0, 0.0)
        p3 = Point(0.0, 1.0)

        b = p1.bearing_to(p3)
        msg = 'Computed southward bearing %d. Expected %d' % (b, B)
        assert numpy.allclose(b, B, rtol=eps, atol=eps), msg

    def testBearingWest(self):
        """Bearing due west (270 deg) is correct within double precision
        """

        eps = 1.0e-12
        B = 270  # True bearing

        p1 = Point(0.0, 0.0)
        p3 = Point(0.0, 1.0)

        b = p3.bearing_to(p1)
        msg = 'Computed southward bearing %d. Expected %d' % (b, B)
        assert numpy.allclose(b, B, rtol=eps, atol=eps), msg

    def testRSISE2Home(self):
        """Distance and bearing of real example (RSISE -> Home) are correct
        """

        D = 2068.855  # True Distance to Home
        B = 11        # True Bearing to Home

        d = self.RSISE.distance_to(self.Home)
        msg = 'Dist from RSISE to Home %f. Expected %f' % (d, D)
        assert numpy.allclose(d, D, rtol=1.0e-6), msg

        b = self.RSISE.bearing_to(self.Home)
        msg = 'Bearing from RSISE to Home %i. Expected %i' % (b, B)
        assert b == B, msg

    def testRSISE2Sydney(self):
        """Distance and bearing of real example (RSISE -> Syd) are correct
        """

        D = 239407.67  # True Distance to Sydney Airport
        B = 52         # True Bearing to Sydney Airport

        d = self.RSISE.distance_to(self.Syd)
        msg = 'Dist from RSISE to Sydney airport %f. Expected %f' % (d, D)
        assert numpy.allclose(d, D, rtol=1.0e-6), msg

        b = self.RSISE.bearing_to(self.Syd)
        msg = 'Bearing from RSISE to Sydney airport %i. Expected %i' % (b, B)
        assert b == B, msg

    def testRSISE2Nadi(self):
        """Distance and bearing of real example (RSISE -> Nadi) are correct
        """

        D = 3406100   # True Distance to Nadi Airport
        B = 63        # True Bearing to Nadi Airport

        d = self.RSISE.distance_to(self.Nadi)
        msg = 'Dist from RSISE to Nadi airport %f. Expected %f' % (d, D)
        assert numpy.allclose(d, D, rtol=1.0e-4), msg

        b = self.RSISE.bearing_to(self.Nadi)
        msg = 'Bearing from RSISE to Nadi airport %i. Expected %i' % (b, B)
        assert b == B, msg

    def testRSISE2Kobenhavn(self):
        """Distance and bearing of real example (RSISE -> Kbh) are correct
        """
        D = 16025 * 1000   # True Distance to Kobenhavn
        B = 319            # True Bearing to Kobenhavn

        d = self.RSISE.distance_to(self.Kobenhavn)
        msg = 'Dist from RSISE to Kobenhavn %f. Expected %f' % (d, D)
        assert numpy.allclose(d, D, rtol=1.0e-3), msg

        b = self.RSISE.bearing_to(self.Kobenhavn)
        msg = 'Bearing from RSISE to Nadi airport %i. Expected %i' % (b, B)
        assert b == B, msg

    def testEarthquake2Muncar(self):
        """Distance and bearing of real example (quake -> Muncar) are correct
        """

        # Test data from http://www.movable-type.co.uk/scripts/latlong.html
        D = 151318  # True Distance [m]

        B = 26  # 26 19 42 / 26 13 57  # Bearing to between points (start, end)

        p1 = Point(latitude=-9.65, longitude=113.72)

        d = p1.distance_to(self.Muncar)
        msg = 'Dist to Muncar failed %f. Expected %f' % (d, D)
        assert numpy.allclose(d, D), msg

        b = p1.bearing_to(self.Muncar)
        msg = 'Bearing to Muncar %i. Expected %i' % (b, B)
        assert b == B, msg

    def test_equator_example(self):
        """Distance and bearing of real example (near equator) are correct
        """

        # Test data from http://www.movable-type.co.uk/scripts/latlong.html
        D = 11448.0959593  # True Distance [m]

        p1 = Point(latitude=-0.59, longitude=117.10)
        p2 = Point(latitude=-0.50, longitude=117.15)

        d = p1.distance_to(p2)
        msg = 'Dist to point failed %f. Expected %f' % (d, D)
        assert numpy.allclose(d, D, rtol=1.0e-3), msg

    def test_generate_circle(self):
        """A circle with a given radius can be generated correctly
        """

        # Generate a circle around Sydney airport with radius 3km
        radius = 3000
        C = self.Syd.generate_circle(radius)

        # Check distance around the circle
        # Note that not every point will be exactly 3000m
        # because the circle in defined in geographic coordinates
        for c in C:
            p = Point(c[1], c[0])
            d = self.Syd.distance_to(p)
            msg = ('Radius %f not with in expected tolerance. Expected %d'
                   % (d, radius))
            assert numpy.allclose(d, radius, rtol=2.0e-1), msg

        # Store and view
        #from safe.storage.vector import Vector
        #Vector(geometry=[C],
        #       geometry_type='polygon').write_to_file('circle.shp')
        #Vector(geometry=C,
        #       geometry_type='point').write_to_file('circle_as_points.shp')
        #Vector(geometry=[[self.Syd.longitude, self.Syd.latitude]],
        #       geometry_type='point',
        #       data=None).write_to_file('center.shp')

if __name__ == '__main__':
    mysuite = unittest.makeSuite(TestCase, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(mysuite)
