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

from safe.api import PostProcessorError
from safe.postprocessors.age_postprocessor import AgePostprocessor

POSTPROCESSOR = AgePostprocessor()


class TestAgePostprocessor(unittest.TestCase):
    def setUp(self):
        """Run before each test."""

        params = {'impact_total': 146458,
                  'youth_ratio': 0.263,
                  'elderly_ratio': 0.078,
                  'adult_ratio': 0.659}

        POSTPROCESSOR.setup(params)

    def tearDown(self):
        """Run after each test."""
        POSTPROCESSOR.clear()

    def test_setup_wrong_ratios(self):
        """Test for checking if the ratio is wrong (total is more than one)."""
        # ratios_total < 1 should pass
        POSTPROCESSOR.clear()
        params = {'impact_total': 146458,
                  'youth_ratio': 0.1,
                  'elderly_ratio': 0.1,
                  'adult_ratio': 0.6}
        POSTPROCESSOR.setup(params)

        # ratios_total > 1 should not pass
        POSTPROCESSOR.clear()
        params = {'impact_total': 146458,
                  'youth_ratio': 0.1,
                  'elderly_ratio': 0.1,
                  'adult_ratio': 0.9}
        with self.assertRaises(PostProcessorError):
            POSTPROCESSOR.setup(params)

    def test_process(self):
        """Test for Postprocessor's process."""
        POSTPROCESSOR.process()
        results = POSTPROCESSOR.results()
        from pprint import pprint
        pprint(results)
        assert results['Youth count (affected)']['value'] == '38,518'
        assert results['Adult count (affected)']['value'] == '96,516'
        assert results['Elderly count (affected)']['value'] == '11,424'


if __name__ == '__main__':
    suite = unittest.makeSuite(TestAgePostprocessor, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
