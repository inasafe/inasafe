# coding=utf-8
"""Common functionality used by regression tests
"""
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
