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


def suite():
    test_loader = unittest.defaultTestLoader
    test_suite = test_loader.discover('safe')
    return test_suite


def run_all():
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite())

if __name__ == '__main__':
    run_all()
