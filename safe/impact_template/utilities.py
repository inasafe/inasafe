# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Template Utilities**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
import os
import json

from safe.common.exceptions import MissingImpactReport

from safe.impact_template.generic_report_template import (
    GenericReportTemplate)
from safe.impact_template.population_report_template import (
    PopulationReportTemplate)
from safe.impact_template.polygon_people_report_template import (
    PolygonPeopleReportTemplate)
from safe.impact_template.land_cover_report_template import (
    LandCoverReportTemplate)

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'utilities'
__date__ = '4/25/16'
__copyright__ = 'imajimatika@gmail.com'


def get_report_template(
        impact_layer_path=None, json_file=None, impact_data=None):
    """Return matching report template object.

    :param impact_layer_path: Path to impact layer.
    :type impact_layer_path: str

    :param json_file: Path to json impact data.
    :type json_file: str

    :param impact_data: Dictionary that represent impact data.
    :type impact_data: dict

    :returns: Report template object
    :rtype: GenericReportTemplate, BuildingReportTemplate
    """
    # Check for impact layer path first
    if impact_layer_path:
        impact_data_path = os.path.splitext(impact_layer_path)[0] + '.json'
        json_file = impact_data_path
    if json_file:
        if os.path.exists(json_file):
            with open(json_file) as json_file:
                impact_data = json.load(json_file)

    if not impact_data:
        raise MissingImpactReport

    if impact_data['exposure'] in ['building', 'road', 'place']:
        return GenericReportTemplate(impact_data=impact_data)
    elif impact_data['exposure'] == 'population':
        return PopulationReportTemplate(impact_data=impact_data)
    elif impact_data['exposure'] == 'polygon people':
        return PolygonPeopleReportTemplate(impact_data=impact_data)
    elif impact_data['exposure'] == 'land cover':
        return LandCoverReportTemplate(impact_data=impact_data)
    else:
        raise MissingImpactReport(
            'The exposure %s is not recognized' % impact_data.get('exposure'))
