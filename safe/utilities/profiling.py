# coding=utf-8

"""This module contains logic for performance profiling.

This code was taken from http://stackoverflow.com/a/3620972

"""


import inspect
import time
from functools import wraps

from safe.utilities.memory_checker import get_free_memory
from safe.utilities.settings import setting

__copyright__ = "Vadim Shender (original poster in stack overflow), InaSAFE"
__license__ = "Creative Commons"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class Tree():
    """Internal representation of the tree."""

    def __init__(self, key):

        # Name of the current function
        self.key = key
        self.parent = None

        # Time of creation
        self._start_time = time.time()

        # Time at the end.
        self._end_time = None

        if setting(key='memory_profile', expected_type=bool):
            # memory at creation
            self._start_memory = get_free_memory()

            # memory at termination
            self._end_memory = None

        # Children
        self.children = []

    def ended(self):
        """We call this method when the function is finished."""
        self._end_time = time.time()

        if setting(key='memory_profile', expected_type=bool):
            self._end_memory = get_free_memory()

    @property
    def elapsed_time(self):
        """To know the duration of the function.

        This property might return None if the function is still running.
        """
        if self._end_time:
            elapsed_time = round(self._end_time - self._start_time, 3)
            return elapsed_time
        else:
            return None

    @property
    def memory_used(self):
        """To know the allocated memory at function termination.

        ..versionadded:: 4.1

        This property might return None if the function is still running.

        This function should help to show memory leaks or ram greedy code.
        """
        if self._end_memory:
            memory_used = self._end_memory - self._start_memory
            return memory_used
        else:
            return None

    def append(self, node):
        """To append a new child."""
        if node.parent == self.key and not self.elapsed_time:
            self.children.append(node)
        else:
            # Recursive call
            for child in self.children:
                if not child.elapsed_time:
                    child.append(node)

    def __str__(self):
        # It might be a private function.
        step = self.key.lstrip('_')

        # Replace _ by a space
        step = step.replace('_', ' ')

        # Capitalize first letter
        step = step.capitalize()

        return step


ROOT = None


def profile(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        global ROOT

        current_frame = inspect.currentframe()
        parent_frame = inspect.getouterframes(current_frame)[1]
        parent_name = parent_frame[3]

        current_step = Tree(fn.__name__)

        if ROOT:
            current_step.parent = parent_name
            ROOT.append(current_step)
        else:
            ROOT = current_step

        ret = fn(*args, **kwargs)

        current_step.ended()
        return ret

    return with_profiling


def profiling_log():
    """Get the profiling logs."""
    global ROOT
    return ROOT


def clear_prof_data():
    global ROOT
    ROOT = None
