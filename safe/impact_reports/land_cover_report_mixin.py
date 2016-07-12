# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Land Cover Exposure Report Mixin Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'land_cover_report_mixin'
__date__ = '5/5/16'
__copyright__ = 'imajimatika@gmail.com'


from qgis.core import QgsDistanceArea

from safe.utilities.i18n import tr
from safe.utilities.pivot_table import FlatTable
from safe.impact_reports.report_mixin_base import ReportMixin


class LandCoverReportMixin(ReportMixin):
    """Land cover specific report."""

    def __init__(
            self, question, impact_layer, target_field, ordered_columns,
            affected_columns, land_cover_field, zone_field):
        """Initialize method.

        :param question: Question for this IF.
        :type question: str

        :param impact_layer: Output impact layer from a land cover IF
        :type impact_layer: Layer

        :param target_field: Field name in impact layer with hazard type
        :type target_field: basestring

        :param ordered_columns: The columns order in the report.
        :type ordered_columns: list

        :param affected_columns: A subset of ordered_columns for affected.
        :type affected_columns: list

        :param land_cover_field: Field name in impact layer with land cover
        :type land_cover_field: str

        :param zone_field: Field name in impact layer with aggregation zone
            (None if aggregation is not being done)
        :type zone_field: str

        """
        super(LandCoverReportMixin, self).__init__()
        self.exposure_report = 'land cover'
        self.impact_layer = impact_layer
        self.target_field = target_field
        self.ordered_columns = ordered_columns
        self.affected_columns = affected_columns
        self.land_cover_field = land_cover_field
        self.zone_field = zone_field
        self.question = question

    def impact_summary(self):
        # Set this as empty string
        return ''

    def generate_data(self):
        """Create a dictionary contains impact data.

        :returns: The impact report data.
        :rtype: dict
        """

        extra_data = {
            'zone field': self.zone_field,
            'ordered columns': self.ordered_columns,
            'affected columns': self.affected_columns,
            'impact table': self.impact_table(),
        }
        data = super(LandCoverReportMixin, self).generate_data()
        data.update(extra_data)
        return data

    def action_checklist(self):
        """Return the action check list section of the report.

        :return: The action check list as dict.
        :rtype: dict
        """
        title = tr('Action checklist')
        fields = [
            tr('What type of crops are planted in the affected fields?'),
            tr('How long will the activity or function of the land cover be '
               'disturbed?'),
            tr('What proportion of the land cover is damaged?'),
            tr('What potential losses will result from the land cover '
               'damage?'),
            tr('How much productivity will be lost during this event?'),
            tr('Which crops were ready for harvest during this event?'),
            tr('What is the ownership system of the land/crops/field?'),
            tr('Are the land/crops/field accessible after the event?'),
            tr('What urgent actions can be taken to normalize the land/crops/'
               'field?'),
            tr('What tools or equipment are needed for early recovery of the '
               'land/crops/field?')
        ]

        return {
            'title': title,
            'fields': fields
        }

    def impact_table(self):
        """Return data as dictionary"""
        # prepare area calculator object
        area_calc = QgsDistanceArea()
        area_calc.setSourceCrs(self.impact_layer.crs())
        area_calc.setEllipsoid('WGS84')
        area_calc.setEllipsoidalMode(True)

        impacted_table = FlatTable('landcover', 'hazard', 'zone')
        for f in self.impact_layer.getFeatures():
            area = area_calc.measure(f.geometry()) / 1e4
            zone = f[self.zone_field] if self.zone_field is not None else None

            impacted_table.add_value(
                area,
                landcover=f[self.land_cover_field],
                hazard=f[self.target_field],
                zone=zone)

        return impacted_table.to_dict()
