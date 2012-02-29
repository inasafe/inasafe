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


def cdf(x, mu=0, sigma=1, kind='normal'):
    """Cumulative Normal Distribution Function

    Input
        x: scalar or array of real numbers
        mu: Mean value. Default 0
        sigma: Standard deviation. Default 1
        kind: Either 'normal' (default) or 'lognormal'

    Output
        An approximation of the cdf of the normal

    CDF of the normal distribution is defined as
    \frac12 [1 + erf(\frac{x - \mu}{\sigma \sqrt{2}})], x \in \R

    Source: http://en.wikipedia.org/wiki/Normal_distribution
    """

    msg = 'Argument "kind" must be either normal or lognormal'
    if kind not in ['normal', 'lognormal']:
        raise RuntimeError(msg)

    if kind == 'lognormal':
        return cdf(numpy.log(x), mu=mu, sigma=sigma, kind='normal')

    arg = (x - mu) / (sigma * numpy.sqrt(2))
    res = (1 + erf(arg)) / 2

    return res


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
