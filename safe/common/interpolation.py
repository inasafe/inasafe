# coding=utf-8
""" **Commonalities used in both 1d and 2d interpolation**

This module provides commonalities shared between interpolation1d and
interpolation2d. This includes input data validation methods.
"""


import numpy

from safe.common.exceptions import BoundsError, InaSAFEError


def validate_mode(mode):
    """Validate that the mode is an allowable value.

    :param mode: Determines the interpolation order.
        Options are:

            * 'constant' - piecewise constant nearest neighbour interpolation
            * 'linear' - bilinear interpolation using the two nearest \
              neighbours (default)
    :type mode: str

    :raises: InaSAFEError
    """

    msg = (
        'Only mode "linear" and "constant" are implemented. I got "%s"' % mode)
    if mode not in ['linear', 'constant']:
        raise InaSAFEError(msg)


def validate_coordinate_vector(coordinates, coordinate_name):
    """Validate that the coordinates vector are valid

    :param coordinates: The coordinates vector
    :type coordinates: numpy.ndarray

    :param coordinate_name: The user recognizable name of the coordinates.
    :type coordinate_name: str

    :raise: Exception, InaSAFEError
    :returns: Coordinates cast as a numpy arry
    """
    try:
        coordinates = numpy.array(coordinates)
    except Exception, e:
        msg = (
            'Input vector %s could not be converted to numpy array: '
            '%s' % (coordinate_name, str(e)))
        raise Exception(msg)
    if not min(coordinates) == coordinates[0]:
        msg = (
            'Input vector %s must be monotoneously increasing. '
            'I got min(%s) == %.15f, but coordinates[0] == %.15f' % (
                coordinate_name, coordinate_name, min(coordinates),
                coordinates[0]))
        raise InaSAFEError(msg)
    if not max(coordinates) == coordinates[-1]:
        msg = (
            'Input vector coordinates must be monotoneously increasing. I got '
            'max(coordinates) == %.15f, but coordinates[-1] == %.15f' % (
                max(coordinates), coordinates[-1]))
        raise InaSAFEError(msg)
    return coordinates


def validate_inputs(
        x=None, y=None, z=None, points=None, bounds_error=None):
    """Check inputs for interpolate1d and interpolate2d functions

    :param x: 1D array of x-coordinates on which to interpolate
    :type x: numpy.ndarray

    :param y: 1D array of y-coordinates on which to interpolate
    :type z: numpy.ndarray

    :param z: array of values for each x
    :type z: numpy.ndarray

    :param points: 1D array of coordinates where interpolated values are sought
    :type points: numpy.ndarray

    :param bounds_error: Flag to indicate whether an exception will be raised
        when interpolated values are requested outside the domain of the
        input data. If False, nan is returned for those values.
    :type bounds_error: bool

    :returns: x, z and points

    :raises: RuntimeError, Exception
    """
    x = validate_coordinate_vector(x, 'x')

    if y is None:
        dimensions = 1
    else:
        dimensions = 2
        y = validate_coordinate_vector(y, 'y')

    try:
        z = numpy.array(z)
    except Exception, e:
        msg = (
            'Input vector z could not be converted to a numpy array: '
            '%s' % str(e))
        raise Exception(msg)

    if len(z.shape) != dimensions:
        msg = 'z must be a %iD numpy array got a: %dD' % (
            dimensions, len(z.shape))
        raise Exception(msg)

    Nx = len(x)
    points = numpy.array(points)
    if not len(points.shape) == dimensions:
        msg = 'Interpolation points must be a %id array' % dimensions
        raise RuntimeError(msg)

    if dimensions == 1:
        (m,) = z.shape
        if not Nx == m:
            msg = (
                'Input array z must have same length as x (%i).'
                'However, Z has length %i.' % (Nx, m))
            raise RuntimeError(msg)

        # Get interpolation points
        xi = points[:]

    else:
        (m, n) = z.shape
        Ny = len(y)
        if not (Nx == m and Ny == n):
            msg = (
                'Input array Z must have dimensions %i x %i corresponding to '
                'the lengths of the input coordinates x and y. However, '
                'Z has dimensions %i x %i.' % (Nx, Ny, m, n))
            raise InaSAFEError(msg)

        # Get interpolation points
        points = numpy.array(points)
        xi = points[:, 0]
        eta = points[:, 1]

    if bounds_error:
        xi0 = min(xi)
        xi1 = max(xi)

        if xi0 < x[0]:
            msg = (
                'Interpolation point xi=%f was less than the smallest '
                'value in domain (x=%f) and bounds_error was requested.'
                % (xi0, x[0]))
            raise BoundsError(msg)

        if xi1 > x[-1]:
            msg = (
                'Interpolation point xi=%f was greater than the largest '
                'value in domain (x=%f) and bounds_error was requested.'
                % (xi1, x[-1]))
            raise BoundsError(msg)

        if dimensions == 2:
            # noinspection PyUnboundLocalVariable
            eta0 = min(eta)
            eta1 = max(eta)

            if eta0 < y[0]:
                msg = (
                    'Interpolation point eta=%f was less than the smallest '
                    'value in domain (y=%f) and bounds_error was requested.'
                    % (eta0, y[0]))
                raise BoundsError(msg)

            if eta1 > y[-1]:
                msg = (
                    'Interpolation point eta=%f was greater than the largest '
                    'value in domain (y=%f) and bounds_error was requested.'
                    % (eta1, y[-1]))
                raise BoundsError(msg)

    if dimensions == 1:
        return x, z, xi
    else:
        return x, y, z, xi, eta
