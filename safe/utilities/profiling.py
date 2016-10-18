# coding=utf-8

"""This module contains logic for performance profiling.

This code was taken from http://stackoverflow.com/a/3620972

"""

import time
from functools import wraps

__copyright__ = "Vadim Shender (original poster in stack overflow), InaSAFE"
__license__ = "Creative Commons"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

PROF_DATA = {}


def profile(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        start_time = time.time()

        ret = fn(*args, **kwargs)

        elapsed_time = time.time() - start_time

        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = [0, []]
        PROF_DATA[fn.__name__][0] += 1
        PROF_DATA[fn.__name__][1].append(elapsed_time)

        return ret

    return with_profiling

def profiling_log():
    """Get the profiling logs."""
    return PROF_DATA


def clear_prof_data():
    global PROF_DATA
    PROF_DATA = {}
