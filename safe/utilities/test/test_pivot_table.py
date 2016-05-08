# coding=utf-8
"""Tests for pivot table implementation."""
import unittest
import json

from safe.utilities.pivot_table import FlatTable, PivotTable


class PivotTableTest(unittest.TestCase):
    """Tests for reading and writing of raster and vector data."""

    def setUp(self):

        self.flat_table = FlatTable("road_type", "hazard")
        self.flat_table.add_value(10, road_type="primary", hazard="high")
        self.flat_table.add_value(20, road_type="primary", hazard="medium")
        self.flat_table.add_value(30, road_type="residential", hazard="medium")
        self.flat_table.add_value(40, road_type="secondary", hazard="low")
        self.flat_table.add_value(50, road_type="residential", hazard="low")

    def test_basic(self):

        pivot_table = PivotTable(
            self.flat_table, row_field="road_type", column_field="hazard")

        self.assertEqual(
            pivot_table.rows, ['residential', 'primary', 'secondary'])
        self.assertEqual(pivot_table.columns, ['high', 'medium', 'low'])
        self.assertEqual(
            pivot_table.data, [[0, 30, 50], [10, 20, 0], [0, 0, 40]])
        self.assertEqual(pivot_table.total, 150)
        self.assertEqual(pivot_table.total_rows, [80, 30, 40])
        self.assertEqual(pivot_table.total_columns, [10, 50, 90])

    def test_one_column(self):

        pivot_table = PivotTable(self.flat_table, row_field='road_type')

        self.assertEqual(
            pivot_table.rows, ['residential', 'primary', 'secondary'])
        self.assertEqual(pivot_table.columns, [''])
        self.assertEqual(pivot_table.data, [[80], [30], [40]])
        self.assertEqual(pivot_table.total, 150)
        self.assertEqual(pivot_table.total_rows, [80, 30, 40])
        self.assertEqual(pivot_table.total_columns, [150])

    def test_one_row(self):

        pivot_table = PivotTable(self.flat_table, column_field='hazard')

        self.assertEqual(pivot_table.rows, [''])
        self.assertEqual(pivot_table.columns, ['high', 'medium', 'low'])
        self.assertEqual(pivot_table.data, [[10, 50, 90]])
        self.assertEqual(pivot_table.total, 150)
        self.assertEqual(pivot_table.total_rows, [150])
        self.assertEqual(pivot_table.total_columns, [10, 50, 90])

    def test_filter(self):

        pivot_table = PivotTable(
            self.flat_table,
            column_field='hazard',
            filter_field='road_type',
            filter_value='primary')

        self.assertEqual(pivot_table.rows, [''])
        self.assertEqual(pivot_table.columns, ['high', 'medium', 'low'])
        self.assertEqual(pivot_table.data, [[10, 20, 0]])
        self.assertEqual(pivot_table.total, 30)
        self.assertEqual(pivot_table.total_rows, [30])
        self.assertEqual(pivot_table.total_columns, [10, 20, 0])

    def test_to_json(self):
        """Test for JSON-fy the flat table"""
        json_string = self.flat_table.to_json()
        object = json.loads(json_string)
        self.assertEquals(tuple(object['groups']), self.flat_table.groups)
        self.assertEquals(len(object['data']), len(self.flat_table.data))
        print json_string

    def test_from_json(self):
        json_string = (
            '{"data": [["residential", "low", 50], '
            '["residential", "medium", 30], ["secondary", "low", 40], '
            '["primary", "high", 10], ["primary", "medium", 20]], '
            '"groups": ["road_type", "hazard"]}')
        flat_table = FlatTable()
        flat_table.from_json(json_string)
        expected_groups = ["road_type", "hazard"]
        for i in range(len(flat_table.groups)):
            self.assertEquals(expected_groups[i], flat_table.groups[i])
        self.assertEquals(flat_table.data[('residential', 'low')], 50)
        self.assertEquals(flat_table.data[('residential', 'medium')], 30)
        self.assertEquals(flat_table.data[('secondary', 'low')], 40)
        self.assertEquals(flat_table.data[('primary', 'high')], 10)
        self.assertEquals(flat_table.data[('primary', 'medium')], 20)