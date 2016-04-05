# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Land cover Exposure Report Mixin Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'Martin Dobias'

from safe.utilities.i18n import tr
from safe.common.utilities import format_decimal
from safe.impact_reports.report_mixin_base import ReportMixin
import safe.messaging as m


class LandCoverExposureReportMixin(ReportMixin):
    """Land cover specific report.

    .. versionadded:: 3.3
    """

    def __init__(self):
        """Building specific report mixin.

        .. versionadded:: 3.3
        """
        self.question = ''

    def generate_report(self):
        """Breakdown by building type.

        :returns: The report.
        :rtype: safe.messaging.Message
        """
        message = m.Message()
        message.add(m.Paragraph(self.question))
        message.add(self.impact_summary())
        return message

    def impact_summary(self):
        """The impact summary as per category.

        :returns: The impact summary.
        :rtype: safe.messaging.Message
        """

        impact_per_landcover = {}
        impact_per_hazard = {}
        for key, area in self.imp_landcovers.iteritems():
            landcover_type, hazard_type = key

            if landcover_type not in impact_per_landcover:
                impact_per_landcover[landcover_type] = 0
            impact_per_landcover[landcover_type] += area

            if hazard_type not in impact_per_hazard:
                impact_per_hazard[hazard_type] = 0
            impact_per_hazard[hazard_type] += area

        hazard_classes = [u'high', u'medium', u'low']

        message = m.Message(style_class='container')
        table = m.Table(style_class='table table-condensed table-striped')
        table.caption = None
        row = m.Row()
        row.add(m.Cell(tr('Affected Area (ha)'), header=True))
        for cls in hazard_classes:
            row.add(m.Cell(cls, header=True))
        table.add(row)

        row = m.Row()
        row.add(m.Cell(tr('All')))
        for cls in hazard_classes:
            area = impact_per_hazard.get(cls, 0)
            row.add(m.Cell(format_decimal(0.1, area), align='right'))
        table.add(row)

        #row = m.Row()
        #row.add(m.Cell(tr('Breakdown by land cover type'), header=True))
        #for cls in hazard_classes:
        #    row.add(m.Cell(cls, header=True))
        #table.add(row)

        for landcover_type in sorted(impact_per_landcover.keys()):
            row = m.Row()
            row.add(m.Cell(landcover_type))
            for cls in hazard_classes:
                area = self.imp_landcovers.get((landcover_type,cls), 0)
                row.add(m.Cell(format_decimal(0.1, area), align='right'))
            table.add(row)

        message.add(table)
        return message
