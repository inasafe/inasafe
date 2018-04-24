# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**ImpactCalculator.**

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from safe import messaging as m
from safe.utilities.i18n import tr

LOGO_ELEMENT = m.Brand()


def generate_insufficient_overlap_message(
        e,
        exposure_geoextent,
        exposure_layer,
        hazard_geoextent,
        hazard_layer,
        viewport_geoextent):
    """Generate insufficient overlap message.

    :param e: An exception.
    :type e: Exception

    :param exposure_geoextent: Extent of the exposure layer in the form
        [xmin, ymin, xmax, ymax] in EPSG:4326.
    :type exposure_geoextent: list

    :param exposure_layer: Exposure layer.
    :type exposure_layer: QgsMapLayer

    :param hazard_geoextent: Extent of the hazard layer in the form
        [xmin, ymin, xmax, ymax] in EPSG:4326.
    :type hazard_geoextent: list

    :param hazard_layer:  Hazard layer instance.
    :type hazard_layer: QgsMapLayer

    :param viewport_geoextent: Viewport extents
        as a list [xmin, ymin, xmax, ymax] in EPSG:4326.
    :type viewport_geoextent: list

    :return: An InaSAFE message object.
    :rtype: safe.messaging.Message
    """
    description = tr(
        'There was insufficient overlap between the input layers and / or the '
        'layers and the viewable area. Please select two overlapping layers '
        'and zoom or pan to them or disable viewable area clipping in the '
        'options dialog. Full details follow:')
    message = m.Message(description)
    text = m.Paragraph(tr('Failed to obtain the optimal extent given:'))
    message.add(text)
    analysis_inputs = m.BulletedList()
    # We must use Qt string interpolators for tr to work properly
    analysis_inputs.add(tr('Hazard: %s') % (hazard_layer.source()))
    analysis_inputs.add(tr('Exposure: %s') % (exposure_layer.source()))
    analysis_inputs.add(
        tr('Viewable area Geo Extent: %s') % (
            viewport_geoextent))
    analysis_inputs.add(
        tr('Hazard Geo Extent: %s') % (
            hazard_geoextent))
    analysis_inputs.add(
        tr('Exposure Geo Extent: %s') % (
            exposure_geoextent))
    analysis_inputs.add(
        tr('Details: %s') % (
            e))
    message.add(analysis_inputs)

    return message
