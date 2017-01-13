# coding=utf-8
"""This module contains constants that are used in definitions."""

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def disclaimer():
    """Get a standard disclaimer.

    :returns: Standard disclaimer string for InaSAFE.
    :rtype: str
    """
    text = tr(
        'InaSAFE has been jointly developed by the Indonesian '
        'Government-BNPB, the Australian Government, the World Bank-GFDRR and '
        'independent contributors. These agencies and the individual software '
        'developers of InaSAFE take no responsibility for the correctness of '
        'outputs from InaSAFE or decisions derived as a consequence.')
    return text


def limitations():
    """Get InaSAFE limitations.

    :return: All limitations on current InaSAFE.
    :rtype: list
    """
    limitation_list = list()
    limitation_list.append(tr('InaSAFE is not a hazard modelling tool.'))
    limitation_list.append(
        tr('Population count data (raster) must be provided in WGS84 '
           'geographic coordinates.'))
    limitation_list.append(
        tr('InaSAFE is a Free and Open Source Software (FOSS) project, '
           'published under the GPL V3 license. As such you may freely '
           'download, share and (if you like) modify the software.'))
    return limitation_list
