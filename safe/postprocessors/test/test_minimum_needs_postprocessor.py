# -*- coding: utf-8 -*-
"""**Postprocessors package.**

"""

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '13/03/2014'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import unittest

from safe.postprocessors.minimum_needs_postprocessor import \
    MinimumNeedsPostprocessor
from safe.defaults import default_minimum_needs

POSTPROCESSOR = MinimumNeedsPostprocessor()


class TestMinimumNeedsPostprocessor(unittest.TestCase):
    def setUp(self):
        """Run before each test."""

        params = {
            'impact_total': 146458,
            'function_params': {
                'minimum needs': default_minimum_needs()
            }
        }

        POSTPROCESSOR.setup(params)

    def tearDown(self):
        """Run after each test."""
        POSTPROCESSOR.clear()

    def test_process(self):
        POSTPROCESSOR.process()
        results = POSTPROCESSOR.results()
        assert results['Rice [kg]']['value'] == '410,082'
        assert results['Drinking Water [l]']['value'] == '2,563,015'
        assert results['Clean Water [l]']['value'] == '9,812,686'
        assert results['Family Kits']['value'] == '29,292'
        assert results['Toilets']['value'] == '7,323'


if __name__ == '__main__':
    suite = unittest.makeSuite(TestMinimumNeedsPostprocessor, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
