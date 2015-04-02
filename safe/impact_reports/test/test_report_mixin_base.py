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

__date__ = '02/04/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest

from safe.impact_reports.report_mixin_base import ReportMixin


# noinspection PyArgumentList
class ReportMixinTest(unittest.TestCase):
    """Test the ReportMixin.

    .. versionadded:: 3.1
    """

    # noinspection PyPep8Naming
    def setUp(self):
        """Fixture run before all tests"""
        self.mixin = ReportMixin()

    def tearDown(self):
        """Run after each test."""
        del self.mixin

    def test_0001_interface(self):
        """Test all interface methods give default blanks."""
        message = 'Default value for %s should be blank' % 'generate_report'
        self.assertListEqual(self.mixin.generate_report(), [], message)
        message = 'Default value for %s should be blank' % 'action_checklist'
        self.assertListEqual(self.mixin.action_checklist(), [], message)
        message = 'Default value for %s should be blank' % 'impact_summary'
        self.assertListEqual(self.mixin.impact_summary(), [], message)
        message = 'Default value for %s should be blank' % 'notes'
        self.assertListEqual(self.mixin.notes(), [], message)
        message = 'Default value for %s should be blank' % 'generate_report'
        self.assertListEqual(self.mixin.generate_report(), [], message)
        message = 'The default HTML report should be blank.'
        blank_table = (
            u'<table class="table table-striped condensed"> <tbody> '
            u'</tbody></table>')
        self.assertEqual(self.mixin.generate_html_report(), blank_table, message)

    def test_0002_parse_to_html(self):
        """Test parsing to HTML"""
        table_heading = (
            u'<table class="table table-striped condensed"> <tbody>  <tr>   '
            u'<th colspan="100%">Heading</th>  </tr> </tbody></table>')
        heading = [
            {
                'content': 'Heading',
                'header': True
            }]

        self.assertEqual(
            self.mixin.parse_to_html(heading),
            table_heading,
            'Table Heading.')
        table_heading_list = (
            u'<table class="table table-striped condensed"> <tbody>  <tr>   '
            u'<th>Heading</th>   <th>List</th>  </tr> </tbody></table>')
        heading_list = [
            {
                'content': ['Heading', 'List'],
                'header': True
            }]
        self.assertEqual(
            self.mixin.parse_to_html(heading_list),
            table_heading_list,
            'Table with a heading list.')
        table_row = (
            u'<table class="table table-striped condensed"> <tbody>  <tr>   '
            u'<td colspan="100%">Row</td>  </tr> </tbody></table>')
        row = [
            {
                'content': 'Row'
            }]
        self.assertEqual(
            self.mixin.parse_to_html(row),
            table_row,
            'Table with row.')
        table_row_list = (
            u'<table class="table table-striped condensed"> <tbody>  <tr>   '
            u'<td>Row</td>   <td>List</td>  </tr> </tbody></table>')
        row_list = [
            {
                'content': ['Row', 'List']
            }]
        self.assertEqual(
            self.mixin.parse_to_html(row_list),
            table_row_list,
            'Table with row list.')
        table_variables = (
            u'<table class="table table-striped condensed"> <tbody>  <tr>   '
            u'<td colspan="100%">Fill Value</td>  </tr> </tbody></table>')
        variables = [
            {
                'content': '%s',
                'arguments': ('Fill Value',)
            }]
        self.assertEqual(
            self.mixin.parse_to_html(variables),
            table_variables,
            'Variables.')
        table_variables_list = (
            u'<table class="table table-striped condensed"> <tbody>  <tr>   '
            u'<td>Fill Value</td>   <td>Fill Value Two</td>  </tr> </tbody>'
            u'</table>'
        )
        variables_list = [
            {
                'content': ['%s', '%s'],
                'arguments': [('Fill Value',), ('Fill Value Two',)]
            }]
        self.assertEqual(
            self.mixin.parse_to_html(variables_list),
            table_variables_list,
            'Varibale list.')
        variables_list_badly_formatted = [
            {
                'content': ['%s', '%s', '%s', '%s'],
                'arguments': ('Fill Value',)
            }]
        self.assertRaises(
            AssertionError,
            self.mixin.parse_to_html,
            variables_list_badly_formatted)
        table_conditianal_true = (
            u'<table class="table table-striped condensed"> <tbody>  <tr>   '
            u'<td colspan="100%">Show this</td>  </tr> </tbody></table>')
        conditianal_true = [
            {
                'content': 'Show this',
                'condition': True
            }]
        self.assertEqual(
            self.mixin.parse_to_html(conditianal_true),
            table_conditianal_true,
            'Conditional True.')
        table_coniditional_false = (
            u'<table class="table table-striped condensed"> <tbody> '
            u'</tbody></table>')
        conditianal_false = [
            {
                'content': 'Do not show this',
                'condition': False
            }]
        self.assertEqual(
            self.mixin.parse_to_html(conditianal_false),
            table_coniditional_false,
            'Conditional False.')
        table_all_together = (
            u'<table class="table table-striped condensed"> <tbody>  <tr>   '
            u'<th colspan="100%">Show this</th>  </tr> </tbody></table>')
        all_together = [
            {
                'content': 'Show %s',
                'condition': True,
                'arguments': 'this',
                'header': True
            },
            {
                'content': 'Do not show %s',
                'condition': False,
                'arguments': 'this',
                'header': True
            }
        ]
        self.assertEqual(
            self.mixin.parse_to_html(all_together),
            table_all_together,
            'All Together.')

if __name__ == '__main__':
    suite = unittest.makeSuite(ReportMixinTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
