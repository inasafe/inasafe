# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Road Exposure Report Mixin Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from safe.definitionsv4.value_maps import place_class_order
from safe.common.exceptions import KeywordNotFoundError
from safe.impact_reports.road_exposure_report_mixin import \
    RoadExposureReportMixin
from safe.utilities.i18n import tr

__author__ = 'Etienne Trimaille <etienne@kartoza.com>'


class PlaceExposureReportMixin(RoadExposureReportMixin):
    """Place specific report.

    .. versionadded:: 3.5
    """

    def __init__(self):
        """Place specific report mixin.

        .. versionadded:: 3.5
        """
        super(PlaceExposureReportMixin, self).__init__()
        self.exposure_report = 'place'
        self.attribute = tr('Place Type')
        self.order = place_class_order

    @property
    def impact_summary_headings(self):
        """Headings for the impact summary.

        If population_field is found in the metadata, we are dealing with
        population.

        :return: Headings
        :rtype: list
        """
        try:
            # self.exposure is defined in the IF
            self.exposure.keyword('population_field')
            return [tr('Places'), tr('Population')]
        except KeywordNotFoundError:
            return [tr('Places'), tr('Count')]

    @staticmethod
    def label_with_unit(label):
        """Get the label with the correct unit. There is not unit for places.

        :param label: The label.
        :type label: str

        :return: The label with the unit.
        :rtype: str
        """
        return label

    def generate_data(self):
        """Create a dictionary contains impact data.

        :returns: The impact report data.
        :rtype: dict
        """
        extra_data = {
            'impact table': self.impact_table(),
        }
        data = super(PlaceExposureReportMixin, self).generate_data()
        data.update(extra_data)
        return data
