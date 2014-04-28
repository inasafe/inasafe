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
from safe.postprocessors.gender_postprocessor import GenderPostprocessor

POSTPROCESSOR = GenderPostprocessor()


class TestGenderPostprocessor(unittest.TestCase):
    def setUp(self):
        """Run before each test."""

        params = {'impact_total': 146458,
                  'female_ratio': 0.51}

        POSTPROCESSOR.setup(params)

    def tearDown(self):
        """Run after each test."""
        POSTPROCESSOR.clear()

    def test_setup_wrong_ratios(self):
        # ratios_total < 1 should pass
        POSTPROCESSOR.clear()
        params = {'impact_total': 146458,
                  'female_ratio': 0.9}
        POSTPROCESSOR.setup(params)

        # ratios_total > 1 should not pass
        POSTPROCESSOR.clear()
        params = {'impact_total': 146458,
                  'female_ratio': 1.1}
        with self.assertRaises(PostProcessorError):
            POSTPROCESSOR.setup(params)

    def test_process(self):
        POSTPROCESSOR.process()
        results = POSTPROCESSOR.results()
        assert results['Female population (affected)']['value'] == '74,694'
        assert results['Weekly hygiene packs']['value'] == '59,284'
        key = 'Additional weekly rice kg for pregnant and lactating women'
        assert results[key]['value'] == '6,960'


if __name__ == '__main__':
    suite = unittest.makeSuite(TestGenderPostprocessor, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
