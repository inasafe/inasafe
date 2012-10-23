"""**Module for 1D interpolation**

This module:

* provides piecewise constant (nearest neighbour) and bilinear interpolation
* is fast (based on numpy vector operations)
* depends only on numpy
* guarantees that interpolated values never exceed the two nearest neighbours
* handles missing values in domain sensibly using NaN
* is unit tested with a range of common and corner cases

See interpolation2d.py for documentation of the mathematical derivation used.
"""

import numpy
# pylint: disable=W0105


def interpolate1d(x, z, points, mode='linear', bounds_error=False):
    """Fundamental 2D interpolation routine

    Args:
        * x: 1D array of x-coordinates on which to interpolate
        * z: 1D array of values for each x
        * points: 1D array of coordinates where interpolated values are sought
        * mode: Determines the interpolation order. Options are:
            * 'constant' - piecewise constant nearest neighbour interpolation
            * 'linear' - bilinear interpolation using the two nearest \
              neighbours (default)
        * bounds_error: Boolean flag. If True (default) an exception will
                        be raised when interpolated values are requested
                        outside the domain of the input data. If False, nan
                        is returned for those values
    Returns:
        * 1D array with same length as points with interpolated values

    Note:
        Input coordinates x are assumed to be monotonically increasing,
        but need not be equidistantly spaced.

        z is assumed to have dimension M where M = len(x).
    """

    # Input checks
    x, z, xi = check_inputs(x, z, points, mode, bounds_error)

    # Identify elements that are outside interpolation domain or NaN
    outside = (xi < x[0]) + (xi > x[-1])
    outside += numpy.isnan(xi)

    inside = -outside
    xi = xi[inside]

    # Find upper neighbours for each interpolation point
    idx = numpy.searchsorted(x, xi, side='left')

    # Internal check (index == 0 is OK)
    msg = ('Interpolation point outside domain. This should never happen. '
           'Please email Ole.Moller.Nielsen@gmail.com')
    if len(idx) > 0:
        if not max(idx) < len(x):
            raise RuntimeError(msg)

    # Get the two neighbours for each interpolation point
    x0 = x[idx - 1]
    x1 = x[idx]

    z0 = z[idx - 1]
    z1 = z[idx]

    # Coefficient for weighting between lower and upper bounds
    alpha = (xi - x0) / (x1 - x0)

    if mode == 'linear':
        # Bilinear interpolation formula
        dx = z1 - z0
        zeta = z0 + alpha * dx
    else:
        # Piecewise constant (as verified in input_check)

        # Set up masks for the quadrants
        left = alpha < 0.5

        # Initialise result array with all elements set to right neighbour
        zeta = z1

        # Then set the left neigbours
        zeta[left] = z0[left]

    # Self test
    if len(zeta) > 0:
        mzeta = numpy.nanmax(zeta)
        mz = numpy.nanmax(z)
        msg = ('Internal check failed. Max interpolated value %.15f '
               'exceeds max grid value %.15f ' % (mzeta, mz))
        if not(numpy.isnan(mzeta) or numpy.isnan(mz)):
            if not mzeta <= mz:
                raise RuntimeError(msg)

    # Populate result with interpolated values for points inside domain
    # and NaN for values outside
    r = numpy.zeros(len(points))
    r[inside] = zeta
    r[outside] = numpy.nan

    return r


def check_inputs(x, z, points, mode, bounds_error):
    """Check inputs for interpolate1d function
    """

    msg = 'Only mode "linear" and "constant" are implemented. I got %s' % mode
    if mode not in ['linear', 'constant']:
        raise RuntimeError(msg)

    x = numpy.array(x)

    msg = ('Input vector x must be monotoneously increasing. I got '
           'min(x) == %.15f, but x[0] == %.15f' % (min(x), x[0]))
    if not min(x) == x[0]:
        raise RuntimeError(msg)

    msg = ('Input vector x must be monotoneously increasing. I got '
           'max(x) == %.15f, but x[-1] == %.15f' % (max(x), x[-1]))
    if not max(x) == x[-1]:
        raise RuntimeError(msg)

    msg = 'Z must be a 1d numpy array'
    try:
        z = numpy.array(z)
    except Exception, e:
        msg += '%s: %s' % (msg, e)
        raise Exception(msg)

    if not len(z.shape) == 1:
        raise RuntimeError(msg)

    m = len(z)
    Nx = len(x)
    msg = ('Input array z must have same length as x (%i).'
           'However, Z has length %i.' % (Nx, m))
    if not Nx == m:
        raise RuntimeError(msg)

    # Get interpolation points
    points = numpy.array(points)
    msg = 'Interpolation points must be a 1d array'
    if not len(points.shape) == 1:
        raise RuntimeError(msg)
    xi = points[:]

    if bounds_error:
        msg = ('Interpolation point %f was less than the smallest value in '
               'domain %f and bounds_error was requested.' % (xi[0], x[0]))
        if xi[0] < x[0]:
            raise Exception(msg)

        msg = ('Interpolation point %f was greater than the largest value in '
               'domain %f and bounds_error was requested.' % (xi[-1], x[-1]))
        if xi[-1] > x[-1]:
            raise Exception(msg)

    return x, z, xi

# Mathematical derivation of the interpolation formula used
"""
Bilinear interpolation is based on the standard 1D linear interpolation
formula:

Given points (x0, y0) and (x1, x0) and a value of x where x0 <= x <= x1,
the linearly interpolated value y at x is given as

alpha*(y1-y0) + y0

or

alpha*y1 + (1-alpha)*y0                (1)

where alpha = (x-x0)/(x1-x0)           (1a)


Piecewise constant interpolation can be implemented using the same coefficients
(1a) that are used for bilinear interpolation as they are a measure of
the relative distance to the left and lower neigbours. A value of 0 will pick
the lower bound whereas a value of 1 will pick the higher bound.
Hence z can be assigned to its nearest neigbour as follows

    | z0   alpha < 0.5    # lower value
z = |
    | z1   alpha >= 0.5   # higher value

"""
# pylint: enable=W0105
