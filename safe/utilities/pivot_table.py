# coding=utf-8
"""InaSAFE Disaster risk assessment tool developed by AusAid

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""


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

    def group_values(self, group_name):
        """Return all distinct group values for given group"""
        group_index = self.groups.index(group_name)
        values = set()
        for key in self.data:
            values.add(key[group_index])
        return values


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
                 columns=None):
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
        """

        if row_field is not None:
            flat_row_index = flat_table.groups.index(row_field)
        if column_field is not None:
            flat_column_index = flat_table.groups.index(column_field)
        if filter_field is not None:
            flat_filter_index = flat_table.groups.index(filter_field)

        if len(flat_table.data) == 0:
            raise ValueError("no input data")

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
        if columns is not None:
            self.columns = columns
        elif column_field is None:
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
        """ Dump object content in a readable format """
        pivot = '<PivotTable total=%f\n total_rows=%s\n total_columns=%s\n ' \
                'rows=%s\n columns=%s\n data=%s>' % (
                    self.total,
                    repr(self.total_rows),
                    repr(self.total_columns),
                    repr(self.rows),
                    repr(self.columns),
                    repr(self.data))
        return pivot
