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
import qgis  # NOQA  For SIP API to V2 if run outside of QGIS

try:
    from pip import main as pipmain
except:
    from pip._internal import main as pipmain

try:
    import coverage
except ImportError:
    pipmain(['install', 'coverage'])
    import coverage
import tempfile
from osgeo import gdal
from qgis.PyQt import Qt
from safe.utilities.gis import qgis_version

__author__ = 'etiennetrimaille'
__revision__ = '$Format:%H$'
__date__ = '14/06/2016'
__copyright__ = (
    'Copyright 2012, Australia Indonesia Facility for Disaster Reduction')


def _run_tests(test_suite, package_name, with_coverage=False):
    """Core function to test a test suite."""
    count = test_suite.countTestCases()
    # fix_print_with_import
    print('########')
    # fix_print_with_import
    print('%s tests has been discovered in %s' % (count, package_name))
    # fix_print_with_import
    print('QGIS : %s' % qgis_version())
    # fix_print_with_import
    print('Python GDAL : %s' % gdal.VersionInfo('VERSION_NUM'))
    # fix_print_with_import
    print('QT : %s' % Qt.QT_VERSION)
    # fix_print_with_import
    print('Run slow tests : %s' % (not os.environ.get('ON_TRAVIS', False)))
    # fix_print_with_import
    print('########')
    if with_coverage:
        cov = coverage.Coverage(
            source=['safe/'],
            omit=['*/test/*', 'safe/definitions/*'],
        )
        cov.start()

    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(test_suite)

    if with_coverage:
        cov.stop()
        cov.save()
        report = tempfile.NamedTemporaryFile(delete=False)
        cov.report(file=report)
        # Produce HTML reports in the `htmlcov` folder and open index.html
        # cov.html_report()
        report.close()
        with open(report.name, 'r') as fin:
            # fix_print_with_import
            print(fin.read())


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


def test_environment():
    """Test package with an environment variable."""
    package = os.environ.get('TESTING_PACKAGE', 'safe')
    test_loader = unittest.defaultTestLoader
    test_suite = test_loader.discover(package)
    _run_tests(test_suite, package)


def test_manually():
    """Test manually a test class.

    You can change this function as much as you want.
    """
    from .safe.gis.vector.test.test_assign_highest_value import \
        TestAssignHighestValueVector
    test_suite = unittest.makeSuite(TestAssignHighestValueVector, 'test')
    _run_tests(test_suite, 'custom test class')


def test_qgis3():
    """Transient function to re-enable QGIS3 ready tests on Travis selectively.
    """
    test_package('safe.utilities')
    test_package('safe.common')
    test_package('safe.gis')
    test_package('safe.datastore')
    test_package('safe.definitions')
    test_package('safe.impact_function')
    test_package('safe.messaging')
    test_package('safe.metadata')
    #test_package('safe.gui')  # Still Failing



if __name__ == '__main__':
    #test_package()
    test_qgis3()
