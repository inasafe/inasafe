# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Land Cover Template Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'land_cover_report_template'
__date__ = '5/9/16'
__copyright__ = 'imajimatika@gmail.com'

import logging
from safe import messaging as m
from safe.common.utilities import format_decimal
from safe.utilities.i18n import tr
from safe.messaging.styles import INFO_STYLE, SUB_INFO_STYLE
from safe.utilities.pivot_table import FlatTable, PivotTable
from safe.impact_template.template_base import TemplateBase

LOGGER = logging.getLogger('InaSAFE')


class LandCoverReportTemplate(TemplateBase):
    """Report Template for Land Cover.

    ..versionadded: 3.4
    """

    def __init__(
            self, impact_layer_path=None, json_file=None, impact_data=None):
        """Initialize Template.

        :param impact_layer_path: Path to impact layer.
        :type impact_layer_path: str

        :param json_file: Path to json impact data.
        :type json_file: str

        :param impact_data: Dictionary that represent impact data.
        :type impact_data: dict
        """

        super(LandCoverReportTemplate, self).__init__(
            impact_layer_path=impact_layer_path,
            json_file=json_file,
            impact_data=impact_data)
        self.ordered_columns = self.impact_data.get('ordered columns')
        self.affected_columns = self.impact_data.get('affected columns')
        self.impact_table = self.impact_data.get('impact table')
        self.zone_field = self.impact_data.get('zone field')

    def generate_message_report(self):
        """Generate impact report as message object.

        :returns: The report.
        :rtype: safe.messaging.Message
        """
        message = m.Message()
        message.add(self.format_question())
        message.add(self.format_impact_summary())
        message.add(self.format_action_check_list())
        message.add(self.format_notes())
        if self.postprocessing:
            message.add(self.format_postprocessing())
        return message

    def format_impact_summary(self):
        """The impact summary as per category

        :returns: The impact summary.
        :rtype: safe.message.Message
        """
        flat_table = FlatTable().from_dict(
            groups=self.impact_table['groups'],
            data=self.impact_table['data'],
        )

        LOGGER.debug(self.impact_table['groups'])
        LOGGER.debug(self.impact_table['data'])

        LOGGER.debug(flat_table.groups)
        LOGGER.debug(flat_table.data)

        pivot_table = PivotTable(
            flat_table,
            row_field='landcover',
            column_field='hazard',
            columns=self.ordered_columns,
            affected_columns=self.affected_columns)

        report = {'impacted': pivot_table}

        # breakdown by zones
        if self.zone_field is not None:
            report['impacted_zones'] = {}
            for zone in flat_table.group_values('zone'):
                table = PivotTable(
                    flat_table,
                    row_field="landcover",
                    column_field='hazard',
                    columns=self.ordered_columns,
                    affected_columns=self.affected_columns,
                    filter_field="zone",
                    filter_value=zone)
                report['impacted_zones'][zone] = table

        message = m.Message(style_class='container')
        affected_text = tr('Affected Area (ha)')

        show_affected = True if len(self.affected_columns) else False
        if show_affected:
            msg = tr(
                '* Percentage of affected area compare to the total area for '
                'the land cover type.')
            self.notes['fields'].append(msg)

        table = format_pivot_table(
            report['impacted'],
            header_text=affected_text,
            total_columns=True,
            total_affected=show_affected,
            total_percent_affected=show_affected,
            bar_chart=False)
        message.add(table)

        if 'impacted_zones' in report:
            message.add(m.Heading(
                tr('Analysis Results by Aggregation Area'), **INFO_STYLE))
            for zone, table in report['impacted_zones'].items():
                message.add(m.Heading(zone.lower().title(), **SUB_INFO_STYLE))
                m_table = format_pivot_table(
                    table,
                    header_text=affected_text,
                    total_columns=True,
                    total_affected=show_affected,
                    total_percent_affected=show_affected,
                    bar_chart=False)
                message.add(m_table)

        return message.to_html(suppress_newlines=True)


def _svg_bar_chart_hazard(levels, max_level):

    if max_level == 0:
        return ""  # no data -> empty chart

    levels_percent = [round(level * 100. / max_level) for level in levels]
    return '<svg width="100%%" height="16">' \
           '<rect x="0" y="0" width="%.0f%%" height="4" ' \
           'style="fill:rgb(255,180,180)" />' \
           '<rect x="0" y="6" width="%.0f%%" height="4" ' \
           'style="fill:rgb(240,240,50)" />' \
           '<rect x="0" y="12" width="%.0f%%" height="4" ' \
           'style="fill:rgb(180,255,180)" />' \
           '</svg>' % (levels_percent[0], levels_percent[1], levels_percent[2])


def format_pivot_table(
        pivot_table,
        caption=None,
        header_text='',
        total_columns=False,
        total_rows=False,
        total_affected=False,
        total_percent_affected=False,
        bar_chart=False):

    table = m.Table(style_class='table table-condensed table-striped')
    table.caption = caption

    row = m.Row()
    row.add(m.Cell(header_text, header=True))
    if bar_chart:
        row.add(m.Cell('', header=True, attributes='width="100%"'))
    for column_name in pivot_table.columns:
        row.add(m.Cell(column_name, header=True, align='right'))
    if total_rows:
        row.add(m.Cell(tr('All'), header=True, align='right'))
    if total_affected:
        row.add(m.Cell(tr('Affected'), header=True, align='right'))
    if total_percent_affected:
        row.add(m.Cell(tr('Affected (%) *'), header=True, align='right'))
    table.add(row)

    max_value = max(max(row) for row in pivot_table.data)

    for row_name, data_row, total_row, affected, percent_affected in zip(
            pivot_table.rows, pivot_table.data, pivot_table.total_rows,
            pivot_table.total_rows_affected,
            pivot_table.total_percent_rows_affected):
        row = m.Row()
        row.add(m.Cell(row_name))
        if bar_chart:
            svg = _svg_bar_chart_hazard(data_row, max_value)
            row.add(m.Cell(svg, header=False))
        for column_value in data_row:
            row.add(m.Cell(format_decimal(0.1, column_value), align='right'))
        if total_rows:
            row.add(m.Cell(
                format_decimal(0.1, total_row), align='right', header=True))
        if total_affected:
            row.add(m.Cell(
                format_decimal(0.1, affected), align='right', header=True))
        if total_percent_affected:
            row.add(m.Cell(
                format_decimal(
                    0.1, percent_affected), align='right', header=True))
        table.add(row)

    if total_columns:
        row = m.Row()
        row.add(m.Cell(tr('All'), header=True))
        if bar_chart:
            row.add(m.Cell('', header=False))
        for column_value in pivot_table.total_columns:
            row.add(m.Cell(
                format_decimal(0.1, column_value), align='right', header=True))
        if total_rows:
            row.add(m.Cell(format_decimal(
                0.1, pivot_table.total), align='right', header=True))
        if total_affected:
            row.add(m.Cell(format_decimal(
                0.1, pivot_table.total_affected), align='right', header=True))
        if total_percent_affected:
            row.add(m.Cell(format_decimal(
                0.1,
                pivot_table.total_percent_affected),
                align='right', header=True))
        table.add(row)

    return table
