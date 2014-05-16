import numpy
import unittest

# Import InaSAFE modules
from safe.common.interpolation2d import interpolate2d, interpolate_raster
from safe.common.interpolation import BoundsError
from safe.common.interpolation1d import interpolate1d
from safe.common.testing import combine_coordinates
from safe.common.numerics import nan_allclose


def linear_function(x, y):
    """Auxiliary function for use with interpolation test
    """

    return x + y / 2.0


class Test_interpolate(unittest.TestCase):

    def test_linear_interpolation_basic(self):
        """Interpolation library works for linear function - basic test
        """

        # Define pixel centers along each direction
        x = [1.0, 2.0, 4.0]
        y = [5.0, 9.0]

        # Define ny by nx array with corresponding values
        A = numpy.zeros((len(x), len(y)))

        # Define values for each x, y pair as a linear function
        for i in range(len(x)):
            for j in range(len(y)):
                A[i, j] = linear_function(x[i], y[j])

        # Test first that original points are reproduced correctly
        for i, xi in enumerate(x):
            for j, eta in enumerate(y):
                val = interpolate2d(x, y, A, [(xi, eta)], mode='linear')[0]
                ref = linear_function(xi, eta)
                assert numpy.allclose(val, ref, rtol=1e-12, atol=1e-12)

        # Then test that genuinly interpolated points are correct
        xis = numpy.linspace(x[0], x[-1], 10)
        etas = numpy.linspace(y[0], y[-1], 10)
        points = combine_coordinates(xis, etas)

        vals = interpolate2d(x, y, A, points, mode='linear')
        refs = linear_function(points[:, 0], points[:, 1])
        assert numpy.allclose(vals, refs, rtol=1e-12, atol=1e-12)

    def test_constant_interpolation_basic(self):
        """Interpolation library works for piecewise constant function
        """

        # Define pixel centers along each direction
        x = numpy.array([1.0, 2.0, 4.0])
        y = numpy.array([5.0, 9.0])

        # Define ny by nx array with corresponding values
        A = numpy.zeros((len(x), len(y)))

        # Define values for each x, y pair as a linear function
        for i in range(len(x)):
            for j in range(len(y)):
                A[i, j] = linear_function(x[i], y[j])

        # Then test that interpolated points are always assigned value of
        # closest neighbour
        xis = numpy.linspace(x[0], x[-1], 10)
        etas = numpy.linspace(y[0], y[-1], 10)
        points = combine_coordinates(xis, etas)

        vals = interpolate2d(x, y, A, points, mode='constant')

        # Find upper neighbours for each interpolation point
        xi = points[:, 0]
        eta = points[:, 1]
        idx = numpy.searchsorted(x, xi, side='left')
        idy = numpy.searchsorted(y, eta, side='left')

        # Get the four neighbours for each interpolation point
        x0 = x[idx - 1]
        x1 = x[idx]
        y0 = y[idy - 1]
        y1 = y[idy]

        z00 = A[idx - 1, idy - 1]
        z01 = A[idx - 1, idy]
        z10 = A[idx, idy - 1]
        z11 = A[idx, idy]

        # Location coefficients
        alpha = (xi - x0) / (x1 - x0)
        beta = (eta - y0) / (y1 - y0)

        refs = numpy.zeros(len(vals))
        for i in range(len(refs)):
            if alpha[i] < 0.5 and beta[i] < 0.5:
                refs[i] = z00[i]

            if alpha[i] >= 0.5 and beta[i] < 0.5:
                refs[i] = z10[i]

            if alpha[i] < 0.5 and beta[i] >= 0.5:
                refs[i] = z01[i]

            if alpha[i] >= 0.5 and beta[i] >= 0.5:
                refs[i] = z11[i]

        assert numpy.allclose(vals, refs, rtol=1e-12, atol=1e-12)

    def test_linear_interpolation_range(self):
        """Interpolation library works for linear function - a range of cases
        """

        for x in [[1.0, 2.0, 4.0], [-20, -19, 0], numpy.arange(200) + 1000]:
            for y in [[5.0, 9.0], [100, 200, 10000]]:

                # Define ny by nx array with corresponding values
                A = numpy.zeros((len(x), len(y)))

                # Define values for each x, y pair as a linear function
                for i in range(len(x)):
                    for j in range(len(y)):
                        A[i, j] = linear_function(x[i], y[j])

                # Test that linearly interpolated points are correct
                xis = numpy.linspace(x[0], x[-1], 100)
                etas = numpy.linspace(y[0], y[-1], 100)
                points = combine_coordinates(xis, etas)

                vals = interpolate2d(x, y, A, points, mode='linear')
                refs = linear_function(points[:, 0], points[:, 1])
                assert numpy.allclose(vals, refs, rtol=1e-12, atol=1e-12)

    test_linear_interpolation_range.slow = True

    def test_linear_interpolation_nan_points(self):
        """Interpolation library works with interpolation points being NaN

        This is was the reason for bug reported in:
        https://github.com/AIFDR/riab/issues/155
        """

        # Define pixel centers along each direction
        x = [1.0, 2.0, 4.0]
        y = [5.0, 9.0]

        # Define ny by nx array with corresponding values
        A = numpy.zeros((len(x), len(y)))

        # Define values for each x, y pair as a linear function
        for i in range(len(x)):
            for j in range(len(y)):
                A[i, j] = linear_function(x[i], y[j])

        # Then test that interpolated points can contain NaN
        xis = numpy.linspace(x[0], x[-1], 10)
        etas = numpy.linspace(y[0], y[-1], 10)
        xis[6:7] = numpy.nan
        etas[3] = numpy.nan
        points = combine_coordinates(xis, etas)

        vals = interpolate2d(x, y, A, points, mode='linear')
        refs = linear_function(points[:, 0], points[:, 1])
        assert nan_allclose(vals, refs, rtol=1e-12, atol=1e-12)

    def test_linear_interpolation_nan_array(self):
        """Interpolation library works (linear mode) with grid points being NaN
        """

        # Define pixel centers along each direction
        x = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
        y = [4.0, 5.0, 7.0, 9.0, 11.0, 13.0]

        # Define ny by nx array with corresponding values
        A = numpy.zeros((len(x), len(y)))

        # Define values for each x, y pair as a linear function
        for i in range(len(x)):
            for j in range(len(y)):
                A[i, j] = linear_function(x[i], y[j])
        A[2, 3] = numpy.nan  # (x=2.0, y=9.0): NaN

        # Then test that interpolated points can contain NaN
        xis = numpy.linspace(x[0], x[-1], 12)
        etas = numpy.linspace(y[0], y[-1], 10)
        points = combine_coordinates(xis, etas)

        vals = interpolate2d(x, y, A, points, mode='linear')
        refs = linear_function(points[:, 0], points[:, 1])

        # Set reference result with expected NaNs and compare
        for i, (xi, eta) in enumerate(points):
            if (1.0 < xi <= 3.0) and (7.0 < eta <= 11.0):
                refs[i] = numpy.nan

        assert nan_allclose(vals, refs, rtol=1e-12, atol=1e-12)

    def test_interpolation_random_array_and_nan(self):
        """Interpolation library (constant and linear) works with NaN
        """

        # Define pixel centers along each direction
        x = numpy.arange(20) * 1.0
        y = numpy.arange(25) * 1.0

        # Define ny by nx array with corresponding values
        A = numpy.zeros((len(x), len(y)))

        # Define arbitrary values for each x, y pair
        numpy.random.seed(17)
        A = numpy.random.random((len(x), len(y))) * 10

        # Create islands of NaN
        A[5, 13] = numpy.nan
        A[6, 14] = A[6, 18] = numpy.nan
        A[7, 14:18] = numpy.nan
        A[8, 13:18] = numpy.nan
        A[9, 12:19] = numpy.nan
        A[10, 14:17] = numpy.nan
        A[11, 15] = numpy.nan

        A[15, 5:6] = numpy.nan

        # Creat interpolation points
        xis = numpy.linspace(x[0], x[-1], 39)   # Hit all mid points
        etas = numpy.linspace(y[0], y[-1], 73)  # Hit thirds
        points = combine_coordinates(xis, etas)

        for mode in ['linear', 'constant']:
            vals = interpolate2d(x, y, A, points, mode=mode)

            # Calculate reference result with expected NaNs and compare
            i = j = 0
            for k, (xi, eta) in enumerate(points):

                # Find indices of nearest higher value in x and y
                i = numpy.searchsorted(x, xi)
                j = numpy.searchsorted(y, eta)

                if i > 0 and j > 0:

                    # Get four neigbours
                    A00 = A[i - 1, j - 1]
                    A01 = A[i - 1, j]
                    A10 = A[i, j - 1]
                    A11 = A[i, j]

                    if numpy.allclose(xi, x[i]):
                        alpha = 1.0
                    else:
                        alpha = 0.5

                    if numpy.allclose(eta, y[j]):
                        beta = 1.0
                    else:
                        beta = eta - y[j - 1]

                    if mode == 'linear':
                        if numpy.any(numpy.isnan([A00, A01, A10, A11])):
                            ref = numpy.nan
                        else:
                            ref = (A00 * (1 - alpha) * (1 - beta) +
                                   A01 * (1 - alpha) * beta +
                                   A10 * alpha * (1 - beta) +
                                   A11 * alpha * beta)
                    elif mode == 'constant':
                        assert alpha >= 0.5  # Only case in this test

                        if beta < 0.5:
                            ref = A10
                        else:
                            ref = A11
                    else:
                        msg = 'Unknown mode: %s' % mode
                        raise Exception(msg)

                    #print i, j, xi, eta, alpha, beta, vals[k], ref
                    assert nan_allclose(vals[k], ref, rtol=1e-12, atol=1e-12)

    test_interpolation_random_array_and_nan.slow = True

    def test_linear_interpolation_outside_domain(self):
        """Interpolation library sensibly handles values outside the domain
        """

        # Define pixel centers along each direction
        x = [1.0, 2.0, 4.0]
        y = [5.0, 9.0]

        # Define ny by nx array with corresponding values
        A = numpy.zeros((len(x), len(y)))

        # Define values for each x, y pair as a linear function
        for i in range(len(x)):
            for j in range(len(y)):
                A[i, j] = linear_function(x[i], y[j])

        # Simple example first for debugging
        xis = numpy.linspace(0.9, 4.0, 4)
        etas = numpy.linspace(5, 9.1, 3)
        points = combine_coordinates(xis, etas)
        refs = linear_function(points[:, 0], points[:, 1])

        vals = interpolate2d(x, y, A, points, mode='linear',
                             bounds_error=False)
        msg = ('Length of interpolation points %i differs from length '
               'of interpolated values %i' % (len(points), len(vals)))
        assert len(points) == len(vals), msg
        for i, (xi, eta) in enumerate(points):
            if xi < x[0] or xi > x[-1] or eta < y[0] or eta > y[-1]:
                assert numpy.isnan(vals[i])
            else:
                msg = ('Got %.15f for (%f, %f), expected %.15f'
                       % (vals[i], xi, eta, refs[i]))
                assert numpy.allclose(vals[i], refs[i],
                                      rtol=1.0e-12, atol=1.0e-12), msg

        # Try a range of combinations of points outside domain
        # with error_bounds True
        print
        for lox in [x[0], x[0] - 1]:
            for hix in [x[-1], x[-1] + 1]:
                for loy in [y[0], y[0] - 1]:
                    for hiy in [y[-1], y[-1] + 1]:

                        # Then test that points outside domain can be handled
                        xis = numpy.linspace(lox, hix, 4)
                        etas = numpy.linspace(loy, hiy, 4)
                        points = combine_coordinates(xis, etas)

                        if lox < x[0] or hix > x[-1] or \
                                loy < y[0] or hiy > y[-1]:
                            try:
                                vals = interpolate2d(x, y, A, points,
                                                     mode='linear',
                                                     bounds_error=True)
                            except BoundsError, e:
                                assert 'bounds_error was requested' in str(e)
                            else:
                                msg = 'Should have raised bounds error'
                                raise Exception(msg)

        # Try a range of combinations of points outside domain with
        # error_bounds False
        for lox in [x[0], x[0] - 1, x[0] - 10]:
            for hix in [x[-1], x[-1] + 1, x[-1] + 5]:
                for loy in [y[0], y[0] - 1, y[0] - 10]:
                    for hiy in [y[-1], y[-1] + 1, y[-1] + 10]:

                        # Then test that points outside domain can be handled
                        xis = numpy.linspace(lox, hix, 10)
                        etas = numpy.linspace(loy, hiy, 10)
                        points = combine_coordinates(xis, etas)
                        refs = linear_function(points[:, 0], points[:, 1])
                        vals = interpolate2d(x, y, A, points,
                                             mode='linear', bounds_error=False)

                        assert len(points) == len(vals), msg
                        for i, (xi, eta) in enumerate(points):
                            if xi < x[0] or xi > x[-1] or\
                                    eta < y[0] or eta > y[-1]:
                                msg = 'Expected NaN for %f, %f' % (xi, eta)
                                assert numpy.isnan(vals[i]), msg
                            else:
                                msg = ('Got %.15f for (%f, %f), expected '
                                       '%.15f' % (vals[i], xi, eta, refs[i]))
                                assert numpy.allclose(vals[i], refs[i],
                                                      rtol=1.0e-12,
                                                      atol=1.0e-12), msg

    test_linear_interpolation_outside_domain.slow = True

    def test_interpolation_corner_cases(self):
        """Interpolation library returns NaN for incomplete grid points
        """

        # Define four pixel centers
        x = [2.0, 4.0]
        y = [5.0, 9.0]

        # Define ny by nx array with corresponding values
        A = numpy.zeros((len(x), len(y)))

        # Define values for each x, y pair as a linear function
        for i in range(len(x)):
            for j in range(len(y)):
                A[i, j] = linear_function(x[i], y[j])

        # Test that interpolated points are correct
        xis = numpy.linspace(x[0], x[-1], 3)
        etas = numpy.linspace(y[0], y[-1], 3)
        points = combine_coordinates(xis, etas)

        # Interpolate to cropped grids
        for xc, yc, Ac in [([x[0]], [y[0]], numpy.array([[A[0, 0]]])),  # 1 x 1
                           ([x[0]], y, numpy.array([A[0, :]])),  # 1 x 2
                           ]:

            vals = interpolate2d(xc, yc, Ac, points, mode='linear')
            msg = 'Expected NaN when grid %s is incomplete' % str(Ac.shape)
            assert numpy.all(numpy.isnan(vals)), msg

    def test_interpolation_raster_data(self):
        """Interpolation library works for raster data

        This shows interpolation of data arranged with
        latitudes bottom - up and
        longitudes left - right
        """

        # Create test data
        lon_ul = 100  # Longitude of upper left corner
        lat_ul = 10   # Latitude of upper left corner
        numlon = 8    # Number of longitudes
        numlat = 5    # Number of latitudes

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

        # Then test that interpolated points are correct
        xis = numpy.linspace(lon_ll + 1, lon_ll + numlon - 1, 100)
        etas = numpy.linspace(lat_ll + 1, lat_ll + numlat - 1, 100)
        points = combine_coordinates(xis, etas)

        vals = interpolate_raster(longitudes, latitudes, A, points,
                                  mode='linear')
        refs = linear_function(points[:, 0], points[:, 1])

        assert numpy.allclose(vals, refs, rtol=1e-12, atol=1e-12)

    #-----------------------
    # 1D interpolation tests
    #-----------------------

    def test_1d_linear_interpolation_basic(self):
        """Interpolation library works for a 1D linear function - basic test
        """

        # Define pixel centers along each direction
        x = [1.0, 2.0, 4.0]

        # Define array with corresponding values
        A = numpy.zeros((len(x)))

        # Define values for each xas a linear function
        for i in range(len(x)):
            A[i] = linear_function(x[i], 0)

        # Test first that original points are reproduced correctly
        for i, xi in enumerate(x):
            val = interpolate1d(x, A, [xi], mode='linear')[0]
            ref = linear_function(xi, 0)
            assert numpy.allclose(val, ref, rtol=1e-12, atol=1e-12)

        # Then test that genuinly interpolated points are correct
        xis = numpy.linspace(x[0], x[-1], 10)
        points = xis

        vals = interpolate1d(x, A, points, mode='linear')
        refs = linear_function(points, 0)
        assert numpy.allclose(vals, refs, rtol=1e-12, atol=1e-12)

        # Exercise bounds_error flag
        vals = interpolate1d(x, A, points, mode='linear',
                             bounds_error=True)
        refs = linear_function(points, 0)
        assert numpy.allclose(vals, refs, rtol=1e-12, atol=1e-12)

    def test_1d_constant_interpolation_basic(self):
        """Interpolation library works for 1D piecewise constant function
        """

        # Define pixel centers along each direction
        x = numpy.array([1.0, 2.0, 4.0])

        # Define ny by nx array with corresponding values
        A = numpy.zeros((len(x)))

        # Define values for each x, y pair as a linear function
        for i in range(len(x)):
            A[i] = linear_function(x[i], 0)

        # Then test that interpolated points are always assigned value of
        # closest neighbour
        xis = numpy.linspace(x[0], x[-1], 10)
        points = xis

        vals = interpolate1d(x, A, points, mode='constant')

        # Find upper neighbours for each interpolation point
        xi = points[:]
        idx = numpy.searchsorted(x, xi, side='left')

        # Get the neighbours for each interpolation point
        x0 = x[idx - 1]
        x1 = x[idx]

        z0 = A[idx - 1]
        z1 = A[idx]

        # Location coefficients
        alpha = (xi - x0) / (x1 - x0)

        refs = numpy.zeros(len(vals))
        for i in range(len(refs)):
            if alpha[i] < 0.5:
                refs[i] = z0[i]

            if alpha[i] >= 0.5:
                refs[i] = z1[i]

        assert numpy.allclose(vals, refs, rtol=1e-12, atol=1e-12)

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_interpolate, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
