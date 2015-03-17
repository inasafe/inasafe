# coding=utf-8
"""Works with real library impact functions rather than test examples
"""

import unittest


class TestRealImpactFunctions(unittest.TestCase):
    """Tests of SAFE calculations
    """

    def test_filtering_of_impact_functions(self):
        """Impact functions are filtered correctly
        """
        pass

if __name__ == '__main__':
    suite = unittest.makeSuite(TestRealImpactFunctions)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
