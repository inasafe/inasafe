# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Population Template Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'population_report_template'
__date__ = '4/25/16'
__copyright__ = 'imajimatika@gmail.com'

import safe.messaging as m
from safe.messaging import styles
from safe.utilities.utilities import tr
from safe.common.utilities import format_int
from safe.impact_template.generic_report_template import GenericReportTemplate


class PopulationReportTemplate(GenericReportTemplate):
    """Report Template for Population.

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
        super(PopulationReportTemplate, self).__init__(
            impact_layer_path=impact_layer_path,
            json_file=json_file,
            impact_data=impact_data)
        self.minimum_needs = self.impact_data.get('minimum needs')

    def format_impact_table(self):
        """Breakdown by population.

        :returns: The population breakdown report.
        :rtype: list
        """
        message = m.Message(style_class='container')
        message.add(m.Heading(
            tr('Evacuated population minimum needs'),
            **styles.INFO_STYLE))
        table = m.Table(
            style_class='table table-condensed table-striped')
        table.caption = None
        for frequency, needs in self.minimum_needs.items():
            row = m.Row()
            row.add(m.Cell(
                tr('Relief items to be provided %s' % frequency),
                header=True
            ))
            row.add(m.Cell(tr('Total'), header=True, align='right'))
            table.add(row)
            for resource in needs:
                row = m.Row()
                row.add(m.Cell(tr(resource['table name'])))
                row.add(m.Cell(
                    tr(format_int(resource['amount'])),
                    align='right'
                ))
                table.add(row)

        message.add(table)

        return message
