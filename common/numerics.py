"""Numerical tools
"""

import numpy


def ensure_numeric(A, typecode=None):
    """Ensure that sequence is a numeric array.

    Inputs:
        A: Sequence. If A is already a numeric array it will be returned
                     unaltered
                     If not, an attempt is made to convert it to a numeric
                     array
        A: Scalar.   Return 0-dimensional array containing that value. Note
                     that a 0-dim array DOES NOT HAVE A LENGTH UNDER numpy.
        A: String.   Array of ASCII values (numpy can't handle this)

        typecode:    numeric type. If specified, use this in the conversion.
                     If not, let numeric package decide.
                     typecode will always be one of num.float, num.int, etc.

    Note that numpy.array(A, dtype) will sometimes copy.  Use 'copy=False' to
    copy only when required.

    This function is necessary as array(A) can cause memory overflow.
    """

    if isinstance(A, basestring):
        msg = 'Sorry, cannot handle strings in ensure_numeric()'
        raise Exception(msg)

    if typecode is None:
        if isinstance(A, numpy.ndarray):
            return A
        else:
            return numpy.array(A)
    else:
        return numpy.array(A, dtype=typecode, copy=False)


def nanallclose(x, y, rtol=1.0e-5, atol=1.0e-8):
    """Numpy allclose function which allows NaN

    Input
        x, y: Either scalars or numpy arrays

    Output
        True or False

    Returns True if all non-nan elements pass.
    """

    xn = numpy.isnan(x)
    yn = numpy.isnan(y)
    if numpy.any(xn != yn):
        # Presence of NaNs is not the same in x and y
        return False

    if numpy.all(xn):
        # Everything is NaN.
        # This will also take care of x and y being NaN scalars
        return True

    # Filter NaN's out
    if numpy.any(xn):
        x = x[-xn]
        y = y[-yn]

    # Compare non NaN's and return
    return numpy.allclose(x, y, rtol=rtol, atol=atol)


def normal_cdf(x, mu=0, sigma=1):
    """Cumulative Normal Distribution Function

    Input
        x: scalar or array of real numbers
        mu: Mean value. Default 0
        sigma: Standard deviation. Default 1

    Output
        An approximation of the cdf of the normal

    CDF of the normal distribution is defined as
    \frac12 [1 + erf(\frac{x - \mu}{\sigma \sqrt{2}})], x \in \R

    Source: http://en.wikipedia.org/wiki/Normal_distribution
    """

    arg = (x - mu) / (sigma * numpy.sqrt(2))
    res = (1 + erf(arg)) / 2

    return res


def lognormal_cdf(x, median=1, sigma=1):
    """Cumulative Log Normal Distribution Function

    Input
        x: scalar or array of real numbers
        mu: Median (exp(mean of log(x)). Default 1
        sigma: Log normal standard deviation. Default 1

    Output
        An approximation of the cdf of the normal

    CDF of the normal distribution is defined as
    \frac12 [1 + erf(\frac{x - \mu}{\sigma \sqrt{2}})], x \in \R

    Source: http://en.wikipedia.org/wiki/Normal_distribution
    """

    return normal_cdf(numpy.log(x), mu=numpy.log(median), sigma=sigma)


def erf(z):
    """Approximation to ERF

    from:
    http://www.cs.princeton.edu/introcs/21function/ErrorFunction.java.html
    Implements the Gauss error function.
    erf(z) = 2 / sqrt(pi) * integral(exp(-t*t), t = 0..z)

    Fractional error in math formula less than 1.2 * 10 ^ -7.
    although subject to catastrophic cancellation when z in very close to 0
    from Chebyshev fitting formula for erf(z) from Numerical Recipes, 6.2

    Source:
    http://stackoverflow.com/questions/457408/
    is-there-an-easily-available-implementation-of-erf-for-python
    """

    # Input check
    try:
        len(z)
    except:
        scalar = True
        z = [z]
    else:
        scalar = False

    z = numpy.array(z)

    # Begin algorithm
    t = 1.0 / (1.0 + 0.5 * numpy.abs(z))

    # Use Horner's method
    ans = 1 - t * numpy.exp(-z * z - 1.26551223 +
                           t * (1.00002368 +
                           t * (0.37409196 +
                           t * (0.09678418 +
                           t * (-0.18628806 +
                           t * (0.27886807 +
                           t * (-1.13520398 +
                           t * (1.48851587 +
                           t * (-0.82215223 +
                           t * (0.17087277))))))))))

    neg = (z < 0.0)  # Mask for negative input values
    ans[neg] = -ans[neg]

    if scalar:
        return ans[0]
    else:
        return ans


def grid2points(A, G):
    """Convert grid data to point data

    Input
        A: Array of pixel values
        G: 6-tuple used to locate A geographically
           (top left x, w-e pixel resolution, rotation,
            top left y, rotation, n-s pixel resolution)

    Output
        P: Nx2 array of point coordinates
        V: N array of point values
    """

    # FIXME (Ole): Remember to account for pixel registration by
    # offsetting by half a cellsize. Test this with test_grid.asc

    print A
    print G

    M, N = A.shape

    dx = G[1]
    xmin = G[0]
    xmax = xmin + dx * N

    x = numpy.linspace(start=xmin,
                       stop=xmax,
                       num=N,
                       endpoint=False)
    print x, len(x)

    dy = G[5]
    ymax = G[3]
    ymin = 0

    y = numpy.linspace(start=xmin,
                       stop=xmax,
                       num=N,
                       endpoint=False)
    print x, len(x)

