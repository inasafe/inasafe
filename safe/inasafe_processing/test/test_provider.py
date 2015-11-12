# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid / DFAT -
**New Metadata for SAFE.**

Contact : etienne@kartoza.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

import unittest
import logging

from safe.test.utilities import get_qgis_app

# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

LOGGER = logging.getLogger('InaSAFE')

from processing.core.Processing import Processing

from safe.inasafe_processing.provider import InaSafeProvider


class ProviderTest(unittest.TestCase):

    def setUp(self):

        self.provider = InaSafeProvider()
        Processing.addProvider(self.provider, True)

    def tearDown(self):
        Processing.removeProvider(self.provider)

    def test_provider(self):
        """Test if processing can load InaSAFE."""
        msg = 'Wrong number of processing algorithm loaded.'
        self.assertEqual(len(self.provider.alglist), 6, msg)

        msg = 'InaSAFE should be activated by default in Processing.'
        self.assertEqual(self.provider.activate, True, msg)

        msg = 'Wrong processing provide.'
        for algorithm in self.provider.alglist:
            self.assertEqual(algorithm.provider, self.provider, msg)

if __name__ == '__main__':
    suite = unittest.makeSuite(ProviderTest, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
