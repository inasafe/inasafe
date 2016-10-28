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

PROF_DATA = []
TOTAL_TIME = 0


def profile(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        global TOTAL_TIME

        start_time = time.time()
        PROF_DATA.append([fn.__name__, None])
        index = len(PROF_DATA) - 1

        ret = fn(*args, **kwargs)

        elapsed_time = time.time() - start_time
        TOTAL_TIME += elapsed_time

        elapsed_time = round(time.time() - start_time, 3)
        PROF_DATA[index] = ([fn.__name__, elapsed_time])

        return ret

    return with_profiling


def profiling_log():
    """Get the profiling logs."""
    return PROF_DATA, TOTAL_TIME


def clear_prof_data():
    global PROF_DATA, TOTAL_TIME
    PROF_DATA = []
    TOTAL_TIME = 0
