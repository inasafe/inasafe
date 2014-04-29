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

POSTPROCESSOR = MinimumNeedsPostprocessor()


class TestMinimumneedsPostprocessor(unittest.TestCase):
    def setUp(self):
        """Run before each test."""

        params = {
            'impact_total': 146458,
            'function_params': {
                'minimum needs': {
                    'Rice': 2.8,
                    'Drinking Water': 17.5,
                    'Water': 105,
                    'Family Kits': 0.2,
                    'Toilets': 0.05
                }
            }
        }

        POSTPROCESSOR.setup(params)

    def tearDown(self):
        """Run after each test."""
        POSTPROCESSOR.clear()

    def test_process(self):
        POSTPROCESSOR.process()
        results = POSTPROCESSOR.results()
        assert results['Rice']['value'] == '410,082'
        assert results['Drinking Water']['value'] == '2,563,015'
        assert results['Water']['value'] == '15,378,090'
        assert results['Family Kits']['value'] == '29,292'
        assert results['Toilets']['value'] == '7,323'


if __name__ == '__main__':
    suite = unittest.makeSuite(TestMinimumneedsPostprocessor, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
