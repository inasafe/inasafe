# coding=utf-8
"""Tests for pivot table implementation."""
import unittest

from safe.utilities.pivot_table import FlatTable, PivotTable

class PivotTableTest(unittest.TestCase):
    """Tests for reading and writing of raster and vector data
    """

    def setUp(self):

        self.flat_table = FlatTable("road_type", "hazard")
        self.flat_table.add_value(10, road_type="primary", hazard="high")
        self.flat_table.add_value(20, road_type="primary", hazard="medium")
        self.flat_table.add_value(30, road_type="residential", hazard="medium")
        self.flat_table.add_value(40, road_type="secondary", hazard="low")
        self.flat_table.add_value(50, road_type="residential", hazard="low")

    def test_1(self):

        pivot_table = PivotTable(self.flat_table,
                                 row_field="road_type",
                                 column_field="hazard")

        self.assertEqual(pivot_table.rows, ['residential', 'primary', 'secondary'])
        self.assertEqual(pivot_table.columns, ['high', 'medium', 'low'])
        self.assertEqual(pivot_table.data, [[0, 30, 50], [10, 20, 0], [0, 0, 40]])
        self.assertEqual(pivot_table.total, 150)
        self.assertEqual(pivot_table.total_rows, [80, 30, 40])
        self.assertEqual(pivot_table.total_columns, [10, 50, 90])
