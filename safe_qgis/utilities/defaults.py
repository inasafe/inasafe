# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **IS Utilities implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '29/10/2013'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

from PyQt4 import QtCore

# This call needs to be made directly to safe.defaults and not over
# safe_interface since safe_interface calls safe.api which calls
# safe.impact_functions.core
# calling safe.impact_functions.core calls safe.impact_functions.__init__
# which will load the function using the safe.defaults instead of the monkey
# patched safe_qgis.defaults (see safe_qgis.__init__)
from safe.defaults import DEFAULTS

def breakdown_defaults(default=None):
    """Get a dictionary of default values to be used for post processing.

    .. note: This method takes the DEFAULTS from safe and modifies them
        according to user preferences defined in QSettings.

    :param default: A key of the defaults dictionary. Use this to
        optionally retrieve only a specific default.
    :type default: str

    :returns: A dictionary of defaults values to be used or the default
        value if a key is passed. None if the requested default value is not
        valid.
    :rtype: dict, str, None
    """
    print "QGIS defaults CALL"
    settings = QtCore.QSettings()
    defaults = DEFAULTS

    value = settings.value(
        'inasafe/defaultFemaleRatio',
        DEFAULTS['FEM_RATIO'], type=float)
    defaults['FEM_RATIO'] = float(value)

    if default is None:
        return defaults
    elif default in defaults:
        return defaults[default]
    else:
        return None


def disclaimer():
    """Get a standard disclaimer.

    :returns: Standard disclaimer string for InaSAFE.
    :rtype: str
    """
    #import tr here to avoid side effects with safe (see notes above in import
    #section.
    from safe_qgis.utilities.utilities import tr
    text = tr(
        'InaSAFE has been jointly developed by Indonesian '
        'Government-BNPB, Australian Government-AIFDR and the World '
        'Bank-GFDRR. These agencies and the individual software '
        'developers of InaSAFE take no responsibility for the '
        'correctness of outputs from InaSAFE or decisions derived as '
        'a consequence.')
    return text