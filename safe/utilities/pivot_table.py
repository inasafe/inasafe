# coding=utf-8
"""InaSAFE Disaster risk assessment tool developed by AusAid

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""


class FlatTable(object):

    def __init__(self, *args):
        self.groups = args
        self.data = {}

    def add_value(self, value, **kwargs):
        key = tuple(kwargs[group] for group in self.groups)
        if key not in self.data:
            self.data[key] = 0
        self.data[key] += value

    def group_values(self, group_name):
        """Return all distinct group values for given group"""
        group_index = self.groups.index(group_name)
        values = set()
        for key in self.data:
            values.add(key[group_index])
        return values


class PivotTable(object):

    def __init__(self, flat_table,
                 row_field=None, column_field=None,
                 filter_field=None, filter_value=None):
        """ Make a pivot table out of the source data """

        if row_field is not None:
            flat_row_index = flat_table.groups.index(row_field)
        if column_field is not None:
            flat_column_index = flat_table.groups.index(column_field)
        if filter_field is not None:
            flat_filter_index = flat_table.groups.index(filter_field)

        sums = {}  # key = (row, column), value = sum
        for flat_key, flat_value in flat_table.data.iteritems():
            # apply filtering
            if filter_field is not None:
                if flat_key[flat_filter_index] != filter_value:
                    continue

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
        if column_field is None:
            self.columns = ['']
        else:
            self.columns = list(flat_table.group_values(column_field))

        self.total = 0
        self.total_rows = [0] * len(self.rows)
        self.total_columns = [0] * len(self.columns)
        self.data = [[] for i in xrange(len(self.rows))]
        for i in xrange(len(self.rows)):
            self.data[i] = [0] * len(self.columns)

        for (sum_row, sum_column), sum_value in sums.iteritems():
            sum_row_index = self.rows.index(sum_row)
            sum_column_index = self.columns.index(sum_column)
            self.data[sum_row_index][sum_column_index] = sum_value

            self.total_rows[sum_row_index] += sum_value
            self.total_columns[sum_column_index] += sum_value
            self.total += sum_value

    def __repr__(self):
        pivot = '<PivotTable total=%f\n total_rows=%s\n total_columns=%s\n ' \
                'rows=%s\n columns=%s\n data=%s>' % (
                    self.total,
                    repr(self.total_rows),
                    repr(self.total_columns),
                    repr(self.rows),
                    repr(self.columns),
                    repr(self.data))
        return pivot
