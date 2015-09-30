# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Function Report Mixin Base Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'Christian Christelis <christian@kartoza.com>'

import safe.messaging as m


class ReportMixin(object):
    """Report Mixin Interface.

    .. versionadded:: 3.1
    """

    def generate_html_report(self):
        """Generate an HTML report.

        :returns: The report in html format.
        :rtype: basestring
        """
        return self.parse_to_html(self.generate_report())

    def generate_report(self):
        """Defining the interface.

        :returns: An itemized breakdown of the report.
        :rtype: list
        """
        return []

    def action_checklist(self):
        """The actions to be taken in for the impact on this exposure type.

        :returns: The action checklist.
        :rtype: list
        """
        return []

    def impact_summary(self):
        """The impact summary.

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

        :param report: A json compatible report
        :type report: list

        :returns: Returns a tabulated version of the report
        :rtype: basestring
        """
        message = m.Message(style_class='container')
        table = m.Table(
            style_class='table table-condensed table-striped')
        table.caption = None

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
            content = row_template['content']
            if row_template['arguments']:
                arguments = row_template['arguments']
                if hasattr(content, '__iter__'):
                    message = (
                        'Problem formatting arguments into content.'
                        'The element count of the arguments must equal '
                        'the element count of the content.')
                    if len(content) != len(arguments):
                        raise Exception(message)
                    # pylint: disable=bad-builtin
                    # pylint: disable=deprecated-lambda
                    content = map(lambda c, a: c % a, content, arguments)
                    # pylint: enable=deprecated-lambda
                    # pylint: enable=bad-builtin
                else:
                    content = row_template['content'] % arguments

            if row_template['header']:
                # Start a new table if we encounter a header
                message.add(table)
                table = m.Table(
                    style_class='table table-condensed table-striped')
                table_row = m.Row(content, header=True)
            else:
                table_row = m.Row(content)
            table.add(table_row)

        message.add(table)
        message = message.to_html(
            suppress_newlines=True,
            in_div_flag=True)
        return message

    @property
    def blank_line(self):
        """Blank line of content."""
        return {'content': ''}
