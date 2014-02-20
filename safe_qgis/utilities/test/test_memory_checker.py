# coding=utf-8
"""Unit tests for the memory checker module."""

import os
import unittest
from safe_qgis.utilities.memory_checker import check_memory_usage


class TestMemoryChecker(unittest.TestCase):
    """Tests for working with the memory checker module.
    """

    def setUp(self):
        """Test setup."""
        os.environ['LANG'] = 'en'

    def tearDown(self):
        """Test tear down."""
        pass

    def test_breakdown_defaults(self):
        """Test we can get breakdown defaults.
        """
        # Really big area with small cell size
        # should be too much mem
        actual = check_memory_usage(
            buffered_geo_extent=[0, 0, 100000000000000, 100000000000000],
            cell_size=0.0000000000001
        )
        self.assertFalse(actual)
        # Small grid with large cells, should
        # have enough mem
        actual = check_memory_usage(
            buffered_geo_extent=[0, 0, 100, 100],
            cell_size=1
        )
        self.assertTrue(actual)
