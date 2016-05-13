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

from safe.utilities.pivot_table import FlatTable
from safe.impact_reports.report_mixin_base import ReportMixin


class LandCoverReportMixin(ReportMixin):
    """Land cover specific report.
    """

    def __init__(
            self, question, impact_layer, target_field, columns_order,
            land_cover_field, zone_field):
        """Initialize method.

        :param question: Question for this IF.
        :type question: str

        :param impact_layer: Output impact layer from a land cover IF
        :type impact_layer: Layer

        :param target_field: Field name in impact layer with hazard type
        :type target_field: basestring

        :param columns_order: The columns order in the report.
        :type columns_order: list

        :param land_cover_field: Field name in impact layer with land cover
        :type land_cover_field: str

        :param zone_field: Field name in impact layer with aggregation zone
            (None if aggregation is not being done)
        :type zone_field: str

        """
        self.impact_layer = impact_layer
        self.target_field = target_field
        self.columns_order = columns_order
        self.land_cover_field = land_cover_field
        self.zone_field = zone_field
        self.question = question

    def generate_data(self):
        """Create a dictionary contains impact data.

        :returns: The impact report data.
        :rtype: dict
        """

        return {
            'exposure': 'land cover',
            'question': self.question,
            'impact summary': '',  # Set this as empty string
            'zone field': self.zone_field,
            'columns order': self.columns_order,
            'impact table': self.impact_table(),
            'action check list': self.action_checklist(),
            'notes': self.notes()
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
