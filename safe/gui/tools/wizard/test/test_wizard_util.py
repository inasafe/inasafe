import unittest

from safe.gui.tools.wizard.wizard_utils import purposes_for_layer

class TestWizardUtil(unittest.TestCase):
    def test_layer_purpose_for_layer(self):
        expected = ['aggregation', 'exposure', 'hazard']
        self.assertListEqual(expected, purposes_for_layer('polygon'))

        expected = ['exposure', 'hazard']
        self.assertListEqual(expected, purposes_for_layer('raster'))

        expected = ['exposure']
        self.assertListEqual(expected, purposes_for_layer('line'))


if __name__ == '__main__':
    unittest.main()
