# coding=utf-8
"""
Test Suite for InaSAFE.

Contact : etienne at kartoza dot com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'etiennetrimaille'
__revision__ = '$Format:%H$'
__date__ = '14/06/2016'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import sys
import unittest


def test_package(package='safe'):
    """Test package.

    :param package: The package to test.
    :type package: str
    """
    test_loader = unittest.defaultTestLoader
    try:
        test_suite = test_loader.discover(package)
        return test_suite
    except ImportError:
        return unittest.TestSuite()


def test_manually():
    """Run a test module."""
    from safe.impact_statistics.test.test_postprocessor_manager import \
        PostprocessorManagerTest
    test_suite = unittest.makeSuite(PostprocessorManagerTest, 'test')
    return test_suite


def run(package='safe'):
    """Run tests.

    :param package: The package to test.
    :type package: str
    """
    test_suite = test_package(package)
    # test_suite = test_manually()
    # package = 'PostprocessorManagerTest'

    count = test_suite.countTestCases()
    print '########'
    print '%s tests has been discovered in %s' % (count, package)
    print '########'
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(test_suite)

if __name__ == '__main__':
    run()
