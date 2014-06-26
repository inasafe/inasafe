"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__date__ = '21/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# this import required to enable PyQt API v2 - DO NOT REMOVE!
#noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

import unittest

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

# Needed though not used below
from safe_qgis.utilities.help import _show_local_help
from safe_qgis.exceptions import HelpFileMissingError


class HelpTest(unittest.TestCase):
    """Test that context help works."""

    def test_local_help(self):
        """Test local help returns an error if the file is not found."""

        # TODO this test is largely meaningless - try to come up with a
        # better approach...
        self.assertRaises(
            HelpFileMissingError,
            _show_local_help,
            context='idontexist')

    def test_local_help_better(self):
        """Test local help returns no error if the file is not found."""
        # better approach...
        _show_local_help(context='keywords')


if __name__ == '__main__':
    suite = unittest.makeSuite(HelpTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
