# coding=utf-8
"""InaSAFE Disaster risk assessment tool developed by AusAid

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""
from builtins import range
from builtins import object

import json


class FlatTable(object):
    """ Flat table object - used as a source of data for pivot tables.
    After constructing the object, repeatedly call "add_value" method
    for each row of the input table. FlatTable stores only fields
    that are important for the creation of pivot tables later. It also
    aggregates values of rows where specified fields have the same value,
    saving memory by not storing all source data.

    An example of use for the flat table - afterwards it can be converted
    into a pivot table:

    flat_table = FlatTable('hazard_type', 'road_type', 'district')

    for f in layer.getFeatures():
        flat_table.add_value(
            f.geometry().length(),
            hazard_type=f['hazard'],
            road_type=f['road'],
            zone=f['zone'])
    """

    def __init__(self, *args):
        """ Construct flat table, fields are passe"""
        self.groups = args
        self.data = {}

    def add_value(self, value, **kwargs):
        key = tuple(kwargs[group] for group in self.groups)
        if key not in self.data:
            self.data[key] = 0
        self.data[key] += value

    def get_value(self, **kwargs):
        """Return the value for a specific key."""
        key = tuple(kwargs[group] for group in self.groups)
        if key not in self.data:
            self.data[key] = 0
        return self.data[key]

    def group_values(self, group_name):
        """Return all distinct group values for given group."""
        group_index = self.groups.index(group_name)
        values = set()
        for key in self.data:
            values.add(key[group_index])
        return values

    def to_json(self):
        """Return json representation of FlatTable

        :returns: JSON string.
        :rtype: str
        """
        return json.dumps(self.to_dict())

    def from_json(self, json_string):
        """Override current FlatTable using data from json.

        :param json_string: JSON String
        :type json_string: str
        """

        object = json.loads(json_string)
        self.from_dict(object['groups'], object['data'])

        return self

    def to_dict(self):
        """Return common list python object.
        :returns: Dictionary of groups and data
        :rtype: dict
        """
        list_data = []
        for key, value in list(self.data.items()):
            row = list(key)
            row.append(value)
            list_data.append(row)
        return {
            'groups': self.groups,
            'data': list_data
        }

    def from_dict(self, groups, data):
        """Populate FlatTable based on groups and data.

        :param groups: List of group name.
        :type groups: list

        :param data: Dictionary of raw table.
        :type data: list

        example of groups: ["road_type", "hazard"]
        example of data: [
            ["residential", "low", 50],
            ["residential", "medium", 30],
            ["secondary", "low", 40],
            ["primary", "high", 10],
            ["primary", "medium", 20]
            ]
        """
        self.groups = tuple(groups)
        for item in data:
            kwargs = {}
            for i in range(len(self.groups)):
                kwargs[self.groups[i]] = item[i]
            self.add_value(item[-1], **kwargs)

        return self


class PivotTable(object):
    """ Pivot tables as known from spreadsheet software.

    Pivot table restructures the input data table. For example,
    a table with fields "hazard_type", "road_type", "district", "length"
    and rows where each row tells length of roads of particular road type
    affected by a particular hazard in a particular district. Now if we
    need any kind of summary table from these data, we use create a pivot
    table:

    PivotTable(flat_table, row_field="road_type", column_field="hazard_type")

    This will generate a table like this:
                    High   Medium   Low    Total
    Highway          3.5    4.3     0.2     8.0
    Residential      1.2    2.2     1.0     4.4
    Total            4.7    6.5     1.2    12.4

    The returned pivot table will have attributes defined as follows (assuming
    "t" is the returned table):

    >>> t.total
    12.4
    >>> t.total_rows
    [8.0, 4.4]
    >>> t.total_columns
    [4.7, 6.5, 1.2]
    >>> t.rows
    ["Highway", "Residential"]
    >>> t.columns
    ["High", "Medium", "Low"]
    >>> t.data
    [[3.5, 4.3, 0.2], [1.2, 2.2, 1.0]]

    The summary table includes data from all districts. If we wanted to focus
    only on district named "West Side":

    PivotTable(flat_table, row_field="road_type", column_field="hazard_type",
               filter_field="district", filter_value="West Side")

    """

    def __init__(self, flat_table,
                 row_field=None, column_field=None,
                 filter_field=None, filter_value=None,
                 columns=None, affected_columns=None):
        """ Make a pivot table out of the source data

        :param flat_table: Flat table with input data for pivot table
        :type flat_table: FlatTable

        :param row_field: Field name from flat table to use for rows.
            If None, there will be just one row in the pivot table
        :type row_field: str

        :param column_field: Field name from flat table to use for columns.
            If None, there will be just one column in the pivot table
        :type column_field: str

        :param filter_field: Field name from flat table which will be
            used for filtering. To be used together with filter_value.
            If None, no filtering will be applied.
        :type filter_field: str

        :param filter_value: Value of filter_field that will pass filtering,
            all other values will be skipped for pivot table
        :type filter_value: any

        :param columns: List of columns to be present. If not defined,
            the list of columns will be determined from unique column_field
            values. If defined, it explicitly defines order of columns
            and it includes columns even if they were not in input data.
        :param columns: list

        :param affected_columns: List of columns which are considered affected.
            It has to used with column_field.
        :type affected_columns: list
        """

        if affected_columns is None:
            affected_columns = []

        if len(flat_table.data) == 0:
            raise ValueError('No input data')

        if row_field is not None:
            flat_row_index = flat_table.groups.index(row_field)
        if column_field is not None:
            flat_column_index = flat_table.groups.index(column_field)
        if filter_field is not None:
            flat_filter_index = flat_table.groups.index(filter_field)

        sums = {}  # key = (row, column), value = sum
        sums_affected = {}  # key = row, value = sum
        for flat_key, flat_value in flat_table.data.items():
            # apply filtering
            if filter_field is not None:
                if flat_key[flat_filter_index] != filter_value:
                    continue

            if column_field is not None:
                current_value = flat_key[flat_column_index]
                if current_value in affected_columns:
                    if row_field is not None:
                        row_key = flat_key[flat_row_index]
                    else:
                        row_key = ''

                    if row_key not in list(sums_affected.keys()):
                        sums_affected[row_key] = 0
                    sums_affected[row_key] += flat_value

            if column_field is not None and row_field is not None:
                key = flat_key[flat_row_index], flat_key[flat_column_index]
            elif row_field is not None:
                key = (flat_key[flat_row_index], '')
            elif column_field is not None:
                key = ('', flat_key[flat_column_index])

            if key not in sums:
                sums[key] = 0
            sums[key] += flat_value

        # TODO: configurable order of rows
        # - undefined
        # - using row label
        # - using column's values
        # - custom (using function)

        # determine rows
        if row_field is None:
            self.rows = ['']
        else:
            self.rows = list(flat_table.group_values(row_field))

        # determine columns
        if columns is not None:
            self.columns = columns
        elif column_field is None:
            self.columns = ['']
        else:
            self.columns = list(flat_table.group_values(column_field))

        self.affected_columns = affected_columns

        self.total = 0.0
        self.total_rows = [0.0] * len(self.rows)
        self.total_columns = [0.0] * len(self.columns)
        self.data = [[] for i in range(len(self.rows))]
        for i in range(len(self.rows)):
            self.data[i] = [0.0] * len(self.columns)

        for (sum_row, sum_column), sum_value in sums.items():
            sum_row_index = self.rows.index(sum_row)
            sum_column_index = self.columns.index(sum_column)
            self.data[sum_row_index][sum_column_index] = sum_value

            self.total_rows[sum_row_index] += sum_value
            self.total_columns[sum_column_index] += sum_value
            self.total += sum_value

        self.total_rows_affected = [0.0] * len(self.rows)
        self.total_affected = 0.0
        for row, value in sums_affected.items():
            self.total_affected += value
            sum_row_index = self.rows.index(row)
            self.total_rows_affected[sum_row_index] = value

        self.total_percent_rows_affected = [0.0] * len(self.rows)
        for row, value in enumerate(self.total_rows_affected):
            try:
                percent = value * 100 / self.total_rows[row]
                self.total_percent_rows_affected[row] = percent
            except ZeroDivisionError:
                pass
        try:
            percent = self.total_affected * 100 / self.total
            self.total_percent_affected = percent
        except ZeroDivisionError:
            self.total_percent_affected = None

    def __repr__(self):
        """Dump object content in a readable format."""
        pivot = '<PivotTable ' \
                'total=%f\n ' \
                'total_rows=%s\n ' \
                'total_columns=%s\n ' \
                'total_rows_affected=%s\n ' \
                'total_affected=%s\n ' \
                'rows=%s\n ' \
                'columns=%s\n ' \
                'affected columns=%s\n' \
                'data=%s>' % (
                    self.total,
                    repr(self.total_rows),
                    repr(self.total_columns),
                    repr(self.total_rows_affected),
                    repr(self.total_affected),
                    repr(self.rows),
                    repr(self.columns),
                    repr(self.affected_columns),
                    repr(self.data))
        return pivot
