# coding=utf-8
"""Tests for pivot table implementation."""
from builtins import range
import unittest
import json

from safe.utilities.pivot_table import FlatTable, PivotTable


class PivotTableTest(unittest.TestCase):
    """Tests for reading and writing of raster and vector data."""

    def setUp(self):
        """
        This will generate a table like this:
        Affected columns : high and medium

        road_type     |         hazard        |             Totals
                      |                       |             Total     Percent
                      |  high   medium  low   |  Total     affected  affected
        residential   |    0      30     50   |    80         30        37.5
        primary       |   10      20      0   |    30         30         100
        secondary     |    0       0     40   |    40          0           0

        Total         |   10      50     90   |   150         60          40
        """
        self.affected_columns = ['medium', 'high']
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
        self.assertEqual(pivot_table.total_affected, 0)
        self.assertEqual(pivot_table.total_rows_affected, [0, 0, 0])

    def test_one_column(self):
        pivot_table = PivotTable(self.flat_table, row_field='road_type')

        self.assertEqual(
            pivot_table.rows, ['residential', 'primary', 'secondary'])
        self.assertEqual(pivot_table.columns, [''])
        self.assertEqual(pivot_table.data, [[80], [30], [40]])
        self.assertEqual(pivot_table.total, 150)
        self.assertEqual(pivot_table.total_rows, [80, 30, 40])
        self.assertEqual(pivot_table.total_columns, [150])
        self.assertEqual(pivot_table.total_affected, 0)
        self.assertEqual(pivot_table.total_rows_affected, [0, 0, 0])

    def test_one_row(self):
        pivot_table = PivotTable(self.flat_table, column_field='hazard')

        self.assertEqual(pivot_table.rows, [''])
        self.assertEqual(pivot_table.columns, ['high', 'medium', 'low'])
        self.assertEqual(pivot_table.data, [[10, 50, 90]])
        self.assertEqual(pivot_table.total, 150)
        self.assertEqual(pivot_table.total_rows, [150])
        self.assertEqual(pivot_table.total_columns, [10, 50, 90])

        pivot_table = PivotTable(
            self.flat_table, column_field='hazard',
            affected_columns=self.affected_columns)
        self.assertEqual(pivot_table.total_rows_affected, [60])
        self.assertEqual(pivot_table.total_affected, 60)
        self.assertEqual(pivot_table.total_percent_affected, 40)
        self.assertEqual(pivot_table.total_percent_rows_affected, [40])

    def test_affected(self):
        pivot_table = PivotTable(
            self.flat_table,
            row_field='road_type',
            column_field='hazard',
            affected_columns=self.affected_columns)
        self.assertEqual(pivot_table.total_affected, 60)
        self.assertEqual(pivot_table.total_rows_affected, [30, 30, 0])
        self.assertEqual(pivot_table.affected_columns, ['medium', 'high'])
        self.assertEqual(pivot_table.total_percent_affected, 40)
        self.assertEqual(
            pivot_table.total_percent_rows_affected, [37.5, 100.0, 0])

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

        pivot_table = PivotTable(
            self.flat_table,
            column_field='hazard',
            filter_field='road_type',
            filter_value='primary',
            affected_columns=self.affected_columns)
        self.assertEqual(pivot_table.total_affected, 30)
        self.assertEqual(pivot_table.total_rows_affected, [30])

    def test_to_dict(self):
        """Test for to_dict the FlatTable"""
        flat_table_dict = self.flat_table.to_dict()
        self.assertEquals(flat_table_dict['groups'], self.flat_table.groups)
        self.assertEquals(
            len(flat_table_dict['data']), len(self.flat_table.data))

    def test_to_json(self):
        """Test for JSON-fy the FlatTable"""
        json_string = self.flat_table.to_json()
        flat_table_dict = json.loads(json_string)
        self.assertEquals(
            tuple(flat_table_dict['groups']), self.flat_table.groups)
        self.assertEquals(
            len(flat_table_dict['data']), len(self.flat_table.data))

    def test_from_json(self):
        """Test FlatTable from_json method"""
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

    def test_from_dict(self):
        """Test FlatTable from_dict method"""
        groups = ["road_type", "hazard"]
        data = [
            ["residential", "low", 50],
            ["residential", "medium", 30],
            ["secondary", "low", 40],
            ["primary", "high", 10],
            ["primary", "medium", 20]
        ]
        flat_table = FlatTable()
        flat_table.from_dict(groups, data)

        for i in range(len(flat_table.groups)):
            self.assertEquals(groups[i], flat_table.groups[i])
        self.assertEquals(flat_table.data[('residential', 'low')], 50)
        self.assertEquals(flat_table.data[('residential', 'medium')], 30)
        self.assertEquals(flat_table.data[('secondary', 'low')], 40)
        self.assertEquals(flat_table.data[('primary', 'high')], 10)
        self.assertEquals(flat_table.data[('primary', 'medium')], 20)

        groups = [u'landcover', u'hazard', u'zone']
        data = [
            [u'Forest', u'high', None, 5172.100048073517],
            [u'Population', u'high', None, 20689.8283632199],
            [u'Forest', u'low', None, 5171.381989317935],
            [u'Population', u'medium', None, 10347.048486941067],
            [u'Meadow', u'high', None, 5172.81413353821],
            [u'Population', u'low', None, 10342.763978632318],
            [u'Meadow', u'medium', None, 5173.5242434723095]
        ]

        flat_table = FlatTable()
        flat_table.from_dict(groups, data)

        for i in range(len(flat_table.groups)):
            self.assertEquals(groups[i], flat_table.groups[i])

        self.assertEquals(flat_table.data[
            ('Forest', 'high', None)], 5172.100048073517)

    def test_to_from_json(self):
        """Test FlatTable from_dict method"""
        json_string = self.flat_table.to_json()
        flat_table = FlatTable()
        flat_table.from_json(json_string)

        self.assertEquals(flat_table.data[('residential', 'low')], 50)
        self.assertEquals(flat_table.data[('residential', 'medium')], 30)
        self.assertEquals(flat_table.data[('secondary', 'low')], 40)
        self.assertEquals(flat_table.data[('primary', 'high')], 10)
        self.assertEquals(flat_table.data[('primary', 'medium')], 20)


if __name__ == '__main__':
    suite = unittest.makeSuite(PivotTableTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
