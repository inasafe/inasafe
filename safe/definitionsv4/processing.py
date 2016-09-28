# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

from safe.utilities.i18n import tr


__author__ = 'etienne@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '27/09/16'
__copyright__ = (
    'Copyright 2012, Australia Indonesia Facility for Disaster Reduction')

"""
Definitions how we call the output and the name of the current step
in our algorithms.
"""

reproject_vector = {
    'step_name': tr('Reprojecting'),
    'output_layer_name': 'reprojected',
}

buffer_vector = {
    'step_name': tr('Buffering'),
    'output_layer_name': 'buffer',
}

reclassify_raster = {
    'step_name': tr('Reclassifying'),
    'output_layer_name': 'reclassified',
}

processing_algorithms = [
    reproject_vector,
    buffer_vector,
    reclassify_raster,
]
