# coding=utf-8
"""Common functionality used by regression tests
"""
import os
import logging

from numpy.testing import Tester

from safe.common.version import get_version


LOGGER = logging.getLogger('InaSAFE')


class SafeTester(Tester):
    """Tester class for testing SAFE package."""
    def _show_system_info(self):
        print 'safe version %s' % get_version()
        super(SafeTester, self)._show_system_info()


# usage: >>> from safe.common.testing import test_safe
#        >>> test_safe()
test_safe = SafeTester().test

# Find parent parent directory to path
# NOTE: This must match Makefile target testdata
# FIXME (Ole): Use environment variable for this.
# Assuming test data three lvls up
pardir = os.path.abspath(os.path.join(os.path.realpath(os.path.dirname(
    __file__)),
    '..',
    '..',
    '..'))

# Location of test data
DATANAME = 'inasafe_data'
DATADIR = os.path.join(pardir, DATANAME)

# Bundled test data
TESTDATA = os.path.join(DATADIR, 'test')  # Artificial datasets
HAZDATA = os.path.join(DATADIR, 'hazard')  # Real hazard layers
EXPDATA = os.path.join(DATADIR, 'exposure')  # Real exposure layers
BOUNDDATA = os.path.join(DATADIR, 'boundaries')  # Real exposure layers
