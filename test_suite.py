# coding=utf-8
"""
Test Suite for InaSAFE.

Contact : etienne at kartoza dot com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import sys
import os
import unittest
from osgeo import gdal
from PyQt4 import Qt
from safe.utilities.gis import qgis_version

__author__ = 'etiennetrimaille'
__revision__ = '$Format:%H$'
__date__ = '14/06/2016'
__copyright__ = (
    'Copyright 2012, Australia Indonesia Facility for Disaster Reduction')


def _run_tests(test_suite, package_name):
    """Core function to test a test suite."""
    count = test_suite.countTestCases()
    print '########'
    print '%s tests has been discovered in %s' % (count, package_name)
    print 'QGIS : %s' % qgis_version()
    print 'Python GDAL : %s' % gdal.VersionInfo('VERSION_NUM')
    print 'QT : %s' % Qt.QT_VERSION
    print 'Run slow tests : %s' % (not os.environ.get('ON_TRAVIS', False))
    print '########'
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(test_suite)


def test_package(package='safe'):
    """Test package.
    This function is called by travis without arguments.

    :param package: The package to test.
    :type package: str
    """
    test_loader = unittest.defaultTestLoader
    try:
        test_suite = test_loader.discover(package)
    except ImportError:
        test_suite = unittest.TestSuite()
    _run_tests(test_suite, package)


def test_manually():
    """Test manually a test class.

    You can change this function as much as you want.
    """
    from safe.impact_statistics.test.test_postprocessor_manager import \
        PostprocessorManagerTest
    test_suite = unittest.makeSuite(PostprocessorManagerTest, 'test')
    _run_tests(test_suite, 'custom test class')


if __name__ == '__main__':
    test_package()
