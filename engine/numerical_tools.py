#!/usr/bin/env python
"""Auxiliary numerical tools

"""

from math import acos, pi, sqrt
from warnings import warn

import numpy as num

#After having migrated to numpy we should use the native NAN.
#num.seterr(divide='warn')
num.seterr(divide='ignore') # Ignore division error here for the time being
NAN = (num.array([1])/0.)[0]

# Static variable used by get_machine_precision
machine_precision = None


def safe_acos(x):
    """Safely compute acos

    Protect against cases where input argument x is outside the allowed
    interval [-1.0, 1.0] by no more than machine precision
    """

    error_msg = 'Input to acos is outside allowed domain [-1.0, 1.0].'+\
                'I got %.12f' %x
    warning_msg = 'Changing argument to acos from %.18f to %.1f' %(x, sign(x))

    eps = get_machine_precision() # Machine precision
    if x < -1.0:
        if x < -1.0 - eps:
            raise ValueError, errmsg
        else:
            warn(warning_msg)
            x = -1.0

    if x > 1.0:
        if x > 1.0 + eps:
            raise ValueError, errmsg
        else:
            print 'NOTE: changing argument to acos from %.18f to 1.0' % x
            x = 1.0

    return acos(x)


def sign(x):
    if x > 0: return 1
    if x < 0: return -1
    if x == 0: return 0


def is_scalar(x):
    """True if x is a scalar (constant numeric value)
    """

    from types import IntType, FloatType
    if type(x) in [IntType, FloatType]:
        return True
    else:
        return False

def angle(v1, v2=None):
    """Compute angle between 2D vectors v1 and v2.

    If v2 is not specified it will default
    to e1 (the unit vector in the x-direction)

    The angle is measured as a number in [0, 2pi] from v2 to v1.
    """

    # Prepare two numeric vectors
    if v2 is None:
        v2 = [1.0, 0.0] # Unit vector along the x-axis

    v1 = ensure_numeric(v1, num.float)
    v2 = ensure_numeric(v2, num.float)

    # Normalise
    v1 = v1/num.sqrt(num.sum(v1**2))
    v2 = v2/num.sqrt(num.sum(v2**2))

    # Compute angle
    p = num.inner(v1, v2)
    c = num.inner(v1, normal_vector(v2))    # Projection onto normal
                                            # (negative cross product)

    theta = safe_acos(p)


    # Correct if v1 is in quadrant 3 or 4 with respect to v2 (as the x-axis)
    # If v2 was the unit vector [1,0] this would correspond to the test
    # if v1[1] < 0: theta = 2*pi-theta
    # In general we use the sign of the projection onto the normal.
    if c < 0:
       #Quadrant 3 or 4
       theta = 2*pi-theta

    return theta


def anglediff(v0, v1):
    """Compute difference between angle of vector v0 (x0, y0) and v1 (x1, y1).
    This is used for determining the ordering of vertices,
    e.g. for checking if they are counter clockwise.

    Always return a positive value
    """

    from math import pi

    a0 = angle(v0)
    a1 = angle(v1)

    #Ensure that difference will be positive
    if a0 < a1:
        a0 += 2*pi

    return a0-a1

def normal_vector(v):
    """Normal vector to v.

    Returns vector 90 degrees counter clockwise to and of same length as v
    """

    return num.array([-v[1], v[0]], num.float)


#def crossproduct_length(v1, v2):
#    return v1[0]*v2[1]-v2[0]*v1[1]


def mean(x):
    """Mean value of a vector
    """
    return(float(num.sum(x))/len(x))


def cov(x, y=None):
    """Covariance of vectors x and y.

    If y is None: return cov(x, x)
    """

    if y is None:
        y = x

    x = ensure_numeric(x)
    y = ensure_numeric(y)
    msg = 'Lengths must be equal: len(x) == %d, len(y) == %d' %(len(x), len(y))
    assert(len(x)==len(y)), msg

    N = len(x)
    cx = x - mean(x)
    cy = y - mean(y)

    p = num.inner(cx,cy)/N
    return(p)


def err(x, y=0, n=2, relative=True):
    """Relative error of ||x-y|| to ||y||
       n = 2:    Two norm
       n = None: Max norm

       If denominator evaluates to zero or
       if y is omitted or
       if keyword relative is False,
       absolute error is returned

       If there is x and y, n=2 and relative=False, this will calc;
       sqrt(sum_over_x&y((xi - yi)^2))

       Given this value (err), to calc the root mean square deviation, do
       err/sqrt(n)
       where n is the number of elements,(len(x))
    """

    x = ensure_numeric(x)
    if y:
        y = ensure_numeric(y)

    if n == 2:
        err = norm(x-y)
        if relative is True:
            try:
                err = err/norm(y)
            except:
                pass

    else:
        err = max(abs(x-y))
        if relative is True:
            try:
                err = err/max(abs(y))
            except:
                pass

    return err


def norm(x):
    """2-norm of x
    """

    y = num.ravel(x)
    p = num.sqrt(num.inner(y,y))
    return p


def corr(x, y=None):
    """Correlation of x and y
    If y is None return autocorrelation of x
    """

    from math import sqrt
    if y is None:
        y = x

    varx = cov(x)
    vary = cov(y)

    if varx == 0 or vary == 0:
        C = 0
    else:
        C = cov(x,y)/sqrt(varx * vary)

    return(C)



##
# @brief Ensure that a sequence is a numeric array of the required type.
# @param A The sequence object to convert to a numeric array.
# @param typecode The required numeric type of object A (a numeric dtype).
# @return A numeric array of the required type.
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

    Note that num.array(A, dtype) will sometimes copy.  Use 'copy=False' to
    copy only when required.

    This function is necessary as array(A) can cause memory overflow.
    """

#    if isinstance(A, basestring):
#        msg = 'Sorry, cannot handle strings in ensure_numeric()'
#        raise Exception, msg

    if typecode is None:
        if isinstance(A, num.ndarray):
            return A
        else:
            return num.array(A)
    else:
        return num.array(A, dtype=typecode, copy=False)


def histogram(a, bins, relative=False):
    """Standard histogram straight from the numeric manual

    If relative is True, values will be normalised againts the total and
    thus represent frequencies rather than counts.
    """

    n = num.searchsorted(num.sort(a), bins)
    n = num.concatenate([n, [len(a)]], axis=0)    #??default#

    hist = n[1:]-n[:-1]

    if relative is True:
        hist = hist/float(num.sum(hist))

    return hist

def create_bins(data, number_of_bins = None):
    """Safely create bins for use with histogram
    If data contains only one point or is constant, one bin will be created.
    If number_of_bins in omitted 10 bins will be created
    """

    mx = max(data)
    mn = min(data)

    if mx == mn:
        bins = num.array([mn])
    else:
        if number_of_bins is None:
            number_of_bins = 10

        bins = num.arange(mn, mx, (mx-mn)/number_of_bins)

    return bins



def get_machine_precision():
    """Calculate the machine precision for Floats

    Depends on static variable machine_precision in this module
    as this would otherwise require too much computation.
    """

    global machine_precision

    if machine_precision is None:
        epsilon = 1.
        while epsilon/2 + 1. > 1.:
            epsilon /= 2

        machine_precision = epsilon

    return machine_precision

####################################################################
#Python versions of function that are also implemented in numerical_tools_ext.c
# FIXME (Ole): Delete these and update tests
#

def gradient_python(x0, y0, x1, y1, x2, y2, q0, q1, q2):
    """
    """

    det = (y2-y0)*(x1-x0) - (y1-y0)*(x2-x0)
    a = (y2-y0)*(q1-q0) - (y1-y0)*(q2-q0)
    a /= det

    b = (x1-x0)*(q2-q0) - (x2-x0)*(q1-q0)
    b /= det

    return a, b


def gradient2_python(x0, y0, x1, y1, q0, q1):
    """Compute radient based on two points and enforce zero gradient
    in the direction orthogonal to (x1-x0), (y1-y0)
    """

    #Old code
    #det = x0*y1 - x1*y0
    #if det != 0.0:
    #    a = (y1*q0 - y0*q1)/det
    #    b = (x0*q1 - x1*q0)/det

    #Correct code (ON)
    det = (x1-x0)**2 + (y1-y0)**2
    if det != 0.0:
        a = (x1-x0)*(q1-q0)/det
        b = (y1-y0)*(q1-q0)/det

    return a, b

################################################################################
# Decision functions for numeric package objects.
# It is a little tricky to decide if a numpy thing is of type float.
# These functions hide numpy-specific details of how we do this.
################################################################################

##
# @brief Decide if an object is a numeric package object with datatype of float.
# @param obj The object to decide on.
# @return True if 'obj' is a numeric package object, and some sort of float.
def is_num_float(obj):
    '''Is an object a numeric package float object?'''

    try:
        return obj.dtype.char in num.typecodes['Float']
    except AttributeError:
        return False

##
# @brief Decide if an object is a numeric package object with datatype of int.
# @param obj The object to decide on.
# @return True if 'obj' is a numeric package object, and some sort of int.
def is_num_int(obj):
    '''Is an object a numeric package int object?'''

    try:
        return obj.dtype.char in num.typecodes['Integer']
    except AttributeError:
        return False


#-----------------
# Initialise module

gradient = gradient_python
gradient2 = gradient2_python


if __name__ == '__main__':
    pass


