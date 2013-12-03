# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Memory Checker.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '22/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import logging

from PyQt4.QtCore import QCoreApplication

from safe_qgis.safe_interface import get_free_memory
from safe_qgis.safe_interface import messaging as m
from safe_qgis.safe_interface import DYNAMIC_MESSAGE_SIGNAL
from safe_qgis.safe_interface import styles
from third_party.pydispatch import dispatcher

PROGRESS_UPDATE_STYLE = styles.PROGRESS_UPDATE_STYLE
INFO_STYLE = styles.INFO_STYLE
WARNING_STYLE = styles.WARNING_STYLE
KEYWORD_STYLE = styles.KEYWORD_STYLE

LOGGER = logging.getLogger('InaSAFE')


def tr(string):
    """We implement this ourselves since we do not inherit QObject.


    :param string: The string for translation.
    :type string: str

    :returns: Translated version of string.
    :rtype: str
    """
    return QCoreApplication.translate('MemoryChecker', string)


def send_message(message):
    """Send a message using the dispatcher.

    :param message: A Message object to be sent to a message viewer.
    :type message: Message
    """
    dispatcher.send(
        signal=DYNAMIC_MESSAGE_SIGNAL,
        sender=dispatcher.Anonymous,
        message=message)


def check_memory_usage(buffered_geo_extent, cell_size):
    """Helper to check if analysis is feasible when extents change.

    For simplicity, we will do all our calculations in geocrs.

    :param buffered_geo_extent: An extent in the for [xmin, ymin, xmax, ymax]
    :type buffered_geo_extent: list

    :param cell_size: The size of a cell (assumes in the X direction).
    :type cell_size: float

    :returns: True if it appears we have enough memory (or we can't compute
        it), False if it appears we do not have enough.
    :rtype: bool

    :raises: A Message containing notes about how much memory is needed
        for a single raster and if this is likely to result in an error.

    :returns: True if it is supposed that there is sufficient memory,
        False if it is supposed that too little memory exists.
    :rtype: bool
    """
    message = m.Message()
    check_heading = m.Heading(
        tr('Checking available memory'), **PROGRESS_UPDATE_STYLE)
    message.add(check_heading)

    width = buffered_geo_extent[2] - buffered_geo_extent[0]
    height = buffered_geo_extent[3] - buffered_geo_extent[1]
    try:
        #noinspection PyAugmentAssignment
        width = width / cell_size
        #noinspection PyAugmentAssignment
        height = height / cell_size
    except TypeError:
        # Could have been a vector layer for example
        reason = tr(
            'Computed cellsize was None. Memory check currently only works '
            'for raster input layers.')
        message.add(reason)
        send_message(message)
        return True  # assume enough mem since we have no vector check logic

    bullet_list = m.BulletedList()
    bullet = m.Paragraph(
        m.ImportantText(tr('Width: ')), str(width))
    bullet_list.add(bullet)
    bullet = m.Paragraph(
        m.ImportantText(tr('Height: ')), str(height))
    bullet_list.add(bullet)
    bullet = m.Paragraph(
        m.ImportantText(tr('Cell Size: ')), str(cell_size))
    bullet_list.add(bullet)
    message.add(bullet_list)

    # Compute mem requirement in MB (assuming numpy uses 8 bytes by per
    # cell) see this link:
    # http://stackoverflow.com/questions/11784329/
    #      python-memory-usage-of-numpy-arrays
    # Also note that the on-disk requirement of the clipped tifs is about
    # half this since the tifs as in single precision,
    # whereas numpy arrays are in double precision.
    requirement = ((width * height * 8) / 1024 / 1024)
    try:
        free_memory = get_free_memory()
    except ValueError:
        error_heading = m.Heading(tr('Memory check error'), **WARNING_STYLE)
        error_message = tr('Could not determine free memory')
        message.add(error_heading)
        message.add(error_message)
        send_message(message)
        LOGGER.exception(message)
        return True  # still let the user try to run their analysis

    # We work on the assumption that if more than 10% of the available
    # memory is occupied by a single layer we could run out of memory
    # (depending on the impact function). This is because multiple
    # in memory copies of the layer are often made during processing.
    warning_limit = 10
    usage_indicator = (float(requirement) / float(free_memory)) * 100
    counts_message = tr(
        'Memory requirement: about %d mb per raster layer ('
        '%d mb available)') % (requirement, free_memory)
    usage_message = tr('Memory used / available: %d/%d') % (
        usage_indicator, warning_limit)
    message.add(counts_message)
    message.add(usage_message)

    if warning_limit <= usage_indicator:
        warning_heading = m.Heading(
            tr('Potential memory issue'), **WARNING_STYLE)
        warning_message = tr(
            'There may not be enough free memory to run this analysis. You can'
            ' attempt to run the analysis anyway, but note that your computer '
            'may become unresponsive during execution, and / or the analysis '
            'may fail due to insufficient memory. Proceed at your own risk.')
        suggestion_heading = m.Heading(
            tr('Suggestion'), **INFO_STYLE)
        suggestion = tr(
            'Try zooming in to a smaller area or using a raster layer with a '
            'coarser resolution to speed up execution and reduce memory '
            'requirements. You could also try adding more RAM to your '
            'computer.')

        message.add(warning_heading)
        message.add(warning_message)
        message.add(suggestion_heading)
        message.add(suggestion)
        send_message(message)
        LOGGER.info(message.to_text())
        return False

    send_message(message)
    LOGGER.info(message.to_text())
    return True
