# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Analysis Utilities .**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""
import os
# noinspection PyPackageRequirements
from PyQt4.QtCore import QDir

from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe.reportv4.report_metadata import ReportMetadata
from safe.definitionsv4.report import standard_impact_report_metadata
from safe.reportv4.impact_report import ImpactReport as ImpactReportV4

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def generate_impact_report(impact_function, iface):
    """Generate the impact report from an impact function.

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface

    """
    # get minimum needs profile
    minimum_needs = NeedsProfile()
    minimum_needs.load()

    # create impact report instance
    report_metadata = ReportMetadata(
        metadata_dict=standard_impact_report_metadata)
    impact_report = ImpactReportV4(
        iface,
        report_metadata,
        impact_function=impact_function,
        minimum_needs_profile=minimum_needs)

    # generate report folder

    # no other option for now
    # TODO: retrieve the information from data store
    if isinstance(impact_function.datastore.uri, QDir):
        layer_dir = impact_function.datastore.uri.absolutePath()
    else:
        # No other way for now
        return

    # We will generate it on the fly without storing it after datastore
    # supports
    impact_report.output_folder = os.path.join(layer_dir, 'output')
    impact_report.process_component()
