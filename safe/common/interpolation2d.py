# coding=utf-8
"""**Module for 2D interpolation over a rectangular mesh**

This module:

* provides piecewise constant (nearest neighbour) and bilinear interpolation
* is fast (based on numpy vector operations)
* depends only on numpy
* guarantees that interpolated values never exceed the four nearest neighbours
* handles missing values in domain sensibly using NaN
* is unit tested with a range of common and corner cases

See end of this file for documentation of the mathematical derivation used.
"""

__author__ = 'Ole Nielsen <ole.moller.nielsen@gmail.com>'
__revision__ = '$Format:%H$'
__date__ = '01/11/2010'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


import logging
import numpy
from safe.common.exceptions import InaSAFEError
from safe.common.interpolation import validate_inputs, validate_mode

LOGGER = logging.getLogger('InaSAFE')
# pylint: disable=W0105


# noinspection PyArgumentEqualDefault,PyTypeChecker
def interpolate2d(x, y, z, points, mode='linear', bounds_error=False):
    """Fundamental 2D interpolation routine

    :param x: 1D array of x-coordinates of the mesh on which to interpolate
    :type x: numpy.ndarray

    :param y: 1D array of y-coordinates of the mesh on which to interpolate
    :type y: numpy.ndarray

    :param z: 2D array of values for each x, y pair
    :type z: numpy.ndarry

    :param points: Nx2 array of coordinates where interpolated values are
        sought
    :type points: numpy.narray

    :param mode: Determines the interpolation order.
        Options are:

            * 'constant' - piecewise constant nearest neighbour interpolation
            * 'linear' - bilinear interpolation using the four
              nearest neighbours (default)

    :type mode: str

    :param bounds_error: If True (default) a BoundsError exception
          will be raised when interpolated values are requested
          outside the domain of the input data. If False, nan
          is returned for those values
    :type bounds_error: bool

    :returns: 1D array with same length as points with interpolated values

    :raises: Exception, BoundsError (see note about bounds_error)

    ..notes::
        Input coordinates x and y are assumed to be monotonically increasing,
        but need not be equidistantly spaced. No such assumption regarding
        ordering of points is made.

        z is assumed to have dimension M x N, where M = len(x) and N = len(y).
        In other words it is assumed that the x values follow the first
        (vertical) axis downwards and y values the second (horizontal) axis
        from left to right.

        If this routine is to be used for interpolation of raster grids where
        data is typically organised with longitudes (x) going from left to
        right and latitudes (y) from left to right then user
        interpolate_raster in this module
    """

    # Input checks
    validate_mode(mode)
    #pylint: disable=W0632
    x, y, z, xi, eta = validate_inputs(
        x=x, y=y, z=z, points=points, bounds_error=bounds_error)
    #pylint: enable=W0632

    # Identify elements that are outside interpolation domain or NaN
    outside = (xi < x[0]) + (eta < y[0]) + (xi > x[-1]) + (eta > y[-1])
    outside += numpy.isnan(xi) + numpy.isnan(eta)

    inside = -outside
    xi = xi[inside]
    eta = eta[inside]

    # Find upper neighbours for each interpolation point
    idx = numpy.searchsorted(x, xi, side='left')
    idy = numpy.searchsorted(y, eta, side='left')

    # Internal check (index == 0 is OK)
    if len(idx) > 0 or len(idy) > 0:
        if (max(idx) >= len(x)) or (max(idy) >= len(y)):
            msg = (
                'Interpolation point outside domain. '
                'This should never happen. '
                'Please email Ole.Moller.Nielsen@gmail.com')
            raise InaSAFEError(msg)

    # Get the four neighbours for each interpolation point
    x0 = x[idx - 1]
    x1 = x[idx]
    y0 = y[idy - 1]
    y1 = y[idy]

    z00 = z[idx - 1, idy - 1]
    z01 = z[idx - 1, idy]
    z10 = z[idx, idy - 1]
    z11 = z[idx, idy]

    # Coefficients for weighting between lower and upper bounds
    old_set = numpy.seterr(invalid='ignore')  # Suppress warnings
    alpha = (xi - x0) / (x1 - x0)
    beta = (eta - y0) / (y1 - y0)
    numpy.seterr(**old_set)  # Restore

    if mode == 'linear':
        # Bilinear interpolation formula
        dx = z10 - z00
        dy = z01 - z00
        z = z00 + alpha * dx + beta * dy + alpha * beta * (z11 - dx - dy - z00)
    else:
        # Piecewise constant (as verified in input_check)

        # Set up masks for the quadrants
        left = alpha < 0.5
        right = -left
        lower = beta < 0.5
        upper = -lower

        lower_left = lower * left
        lower_right = lower * right
        upper_left = upper * left

        # Initialise result array with all elements set to upper right
        z = z11

        # Then set the other quadrants
        z[lower_left] = z00[lower_left]
        z[lower_right] = z10[lower_right]
        z[upper_left] = z01[upper_left]

    # Self test
    if len(z) > 0:
        mz = numpy.nanmax(z)
        mZ = numpy.nanmax(z)
        # noinspection PyStringFormat
        msg = ('Internal check failed. Max interpolated value %.15f '
               'exceeds max grid value %.15f ' % (mz, mZ))
        if not(numpy.isnan(mz) or numpy.isnan(mZ)):
            if not mz <= mZ:
                raise InaSAFEError(msg)

    # Populate result with interpolated values for points inside domain
    # and NaN for values outside
    r = numpy.zeros(len(points))
    r[inside] = z
    r[outside] = numpy.nan

    return r


def interpolate_raster(x, y, z, points, mode='linear', bounds_error=False):
    """2D interpolation of raster data

    It is assumed that data is organised in matrix z as latitudes from
    bottom up along the first dimension and longitudes from west to east
    along the second dimension.

    Further it is assumed that x is the vector of longitudes and y the
    vector of latitudes.

    See interpolate2d for details of the interpolation routine

    :param x: 1D array of x-coordinates of the mesh on which to interpolate
    :type x: numpy.ndarray

    :param y: 1D array of y-coordinates of the mesh on which to interpolate
    :type y: numpy.ndarray

    :param z: 2D array of values for each x, y pair
    :type z: numpy.ndarry

    :param points: Nx2 array of coordinates where interpolated values are
        sought
    :type points: numpy.narray

    :param mode: Determines the interpolation order.
        Options are:

            * 'constant' - piecewise constant nearest neighbour interpolation
            * 'linear' - bilinear interpolation using the four
              nearest neighbours (default)

    :type mode: str

    :param bounds_error: If True (default) a BoundsError exception
          will be raised when interpolated values are requested
          outside the domain of the input data. If False, nan
          is returned for those values
    :type bounds_error: bool

    :returns: 1D array with same length as points with interpolated values

    :raises: Exception, BoundsError (see note about bounds_error)
    """

    # Flip matrix z up-down to interpret latitudes ordered from south to north
    z = numpy.flipud(z)

    # Transpose z to have y coordinates along the first axis and x coordinates
    # along the second axis
    # noinspection PyUnresolvedReferences
    z = z.transpose()

    # Call underlying interpolation routine and return
    res = interpolate2d(x, y, z, points, mode=mode, bounds_error=bounds_error)
    return res


# Mathematical derivation of the interpolation formula used
# noinspection PyStatementEffect
"""
Bilinear interpolation is based on the standard 1D linear interpolation
formula:

Given points (x0, y0) and (x1, x0) and a value of x where x0 <= x <= x1,
the linearly interpolated value y at x is given as

alpha*(y1-y0) + y0

or

alpha*y1 + (1-alpha)*y0                (1)

where alpha = (x-x0)/(x1-x0)           (1a)


2D bilinear interpolation aims at obtaining an interpolated value z at a point
(x,y) which lies inside a square formed by points (x0, y0), (x1, y0),
(x0, y1) and (x1, y1) for which values z00, z10, z01 and z11 are known.

This obtained be first applying equation (1) twice in in the x-direction
to obtain interpolated points q0 and q1 for (x, y0) and (x, y1), respectively.

q0 = alpha*z10 + (1-alpha)*z00         (2)

and

q1 = alpha*z11 + (1-alpha)*z01         (3)


Then using equation (1) in the y-direction on the results from (2) and (3)

z = beta*q1 + (1-beta)*q0              (4)

where beta = (y-y0)/(y1-y0)            (4a)


Substituting (2) and (3) into (4) yields

z = alpha*beta*z11 + beta*z01 - alpha*beta*z01 +
    alpha*z10 + z00 - alpha*z00 - alpha*beta*z10 - beta*z00 +
    alpha*beta*z00
  = alpha*beta*(z11 - z01 - z10 + z00) +
    alpha*(z10 - z00) + beta*(z01 - z00) + z00

which can be further simplified to

z = alpha*beta*(z11 - dx - dy - z00) + alpha*dx + beta*dy + z00  (5)

where
dx = z10 - z00
dy = z01 - z00

Equation (5) is what is implemented in the function interpolate2d above.


Piecewise constant interpolation can be implemented using the same coefficients
(1a) and (4a) that are used for bilinear interpolation as they are a measure of
the relative distance to the left and lower neigbours. A value of 0 will pick
the left or lower bound whereas a value of 1 will pick the right or higher
bound. Hence z can be assigned to its nearest neigbour as follows

    | z00   alpha < 0.5 and beta < 0.5    # lower left corner
    |
    | z10   alpha >= 0.5 and beta < 0.5   # lower right corner
z = |
    | z01   alpha < 0.5 and beta >= 0.5   # upper left corner
    |
    | z11   alpha >= 0.5 and beta >= 0.5  # upper right corner


"""
# pylint: enable=W0105
