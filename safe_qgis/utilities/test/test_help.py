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

import unittest
# Needed though not used below
from safe_qgis.utilities.utilities_for_testing import get_qgis_app
from safe_qgis.utilities.help import show_context_help

QGISAPP, CANVAS, IFACE, PARENT = get_qgis_app()


class HelpTest(unittest.TestCase):
    """Test that context help works."""

    def test_keywords_help(self):
        """Test help works with context set to 'keywords'"""

        # TODO this test is largely meaningless - try to come up with a
        # better approach...
        show_context_help(context='keywords')


if __name__ == '__main__':
    suite = unittest.makeSuite(HelpTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
