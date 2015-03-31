# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Function Manager**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'Christian Christelis <christian@kartoza.com>'

from safe.common.tables import Table, TableRow


class ReportMixin(object):
    def generate_html_report(self, *args):
        """
        :param args: The arguments to be passed to the reoprt

        :returns: The report in html format.
        :rtype: basestring
        """
        return self.parse_to_html(
            self.generate_report(*args))

    def generate_report(self, *args):
        """Defining the interface.
        :param args: The arguments needed by the derived class.
            (This might be phased out as we rather use the class members)
        :returns: An itemized breakdown of the report.
        :rtype: list
        """
        return []

    def action_checklist(self, *args):
        """The actions to be taken in for the impact on this exposure type.
        :param args: The arguments needed by the derived class.

        :returns: The action checklist.
        :rtype: list
        """
        return []

    def impact_summary(self, *args):
        """The impact summary.
        :param args: The arguments needed by the derived class.

        :returns: The action checklist.
        :rtype: list
        """
        return []

    def notes(self):
        """Additional notes to be used.

        :return: The notes to be added to this report

        ..Notes:
        Notes are very much specific to IFs so it is expected that this method
        is overwritten in the IF if needed.
        """
        return []

    @staticmethod
    def parse_to_html(report):
        """Convert a json compatible list of results to a tabulated version.

        :param report: A json compatible reoprt
        :type report: list

        :returns: Returns a tabulated version of the report
        :rtype: basestring
        """
        tabulated_report = []
        for row in report:
            row_template = {
                'content': '',
                'condition': True,
                'arguments': (),
                'header': False
            }
            row_template.update(row)
            if not row_template['condition']:
                continue
            if row_template['arguments']:
                content = row_template['content'] % row_template['arguments']
            else:
                content = row_template['content']
            if row_template['header']:
                table_row = TableRow(content, header=True)
            else:
                table_row = TableRow(content)
            tabulated_report.append(table_row)

        html_tabulated_report = Table(tabulated_report).toNewlineFreeString()
        return html_tabulated_report
