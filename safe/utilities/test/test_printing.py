__author__ = 'timlinux'

import unittest
from safe.utilities.printing import (
    mm_to_points,
    points_to_mm,
    dpi_to_meters)


class TestPrinting(unittest.TestCase):

    def test_mm_to_points(self):
        """Test that conversions between pixel and page dimensions work."""

        dpi = 300
        pixels = 300
        mm = 25.4  # 1 inch
        result = points_to_mm(pixels, dpi)
        message = "Expected: %s\nGot: %s" % (mm, result)
        assert result == mm, message
        result = mm_to_points(mm, dpi)
        message = "Expected: %s\nGot: %s" % (pixels, result)
        assert result == pixels, message

    def test_dpi_to_meters(self):
        """Test conversion from dpi to dpm."""
        dpi = 300
        dpm = dpi_to_meters(dpi)
        expected_dpm = 11811.023622
        message = (
            'Conversion from dpi to dpm failed\n'
            ' Got: %s Expected: %s\n' %
            (dpm, expected_dpm))
        self.assertAlmostEqual(dpm, expected_dpm, msg=message)


if __name__ == '__main__':
    unittest.main()
