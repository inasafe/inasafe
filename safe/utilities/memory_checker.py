# coding=utf-8

"""Memory checker."""
from builtins import str

import logging

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA pylint: disable=unused-import
from qgis.PyQt.QtCore import QCoreApplication
from pydispatch import dispatcher

from safe import messaging as m
from safe.common.signals import send_dynamic_message, send_static_message
from safe.common.utilities import get_free_memory
from safe.messaging import styles

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

PROGRESS_UPDATE_STYLE = styles.PROGRESS_UPDATE_STYLE
SUGGESTION_STYLE = styles.GREEN_LEVEL_4_STYLE
WARNING_STYLE = styles.RED_LEVEL_4_STYLE
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
        # noinspection PyAugmentAssignment
        width = width / cell_size
        # noinspection PyAugmentAssignment
        height = height / cell_size
    except TypeError:
        # Could have been a vector layer for example
        reason = tr(
            'Computed cellsize was None. Memory check currently only works '
            'for raster input layers.')
        message.add(reason)
        send_dynamic_message(dispatcher.Anonymous, message)
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
        send_dynamic_message(dispatcher.Anonymous, message)
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
            tr('Suggestion'), **SUGGESTION_STYLE)
        suggestion = tr(
            'Try zooming in to a smaller area or using a raster layer with a '
            'coarser resolution to speed up execution and reduce memory '
            'requirements. You could also try adding more RAM to your '
            'computer.')

        message.add(warning_heading)
        message.add(warning_message)
        message.add(suggestion_heading)
        message.add(suggestion)
        send_dynamic_message(dispatcher.Anonymous, message)
        # LOGGER.info(message.to_text())
        return False

    send_dynamic_message(dispatcher.Anonymous, message)
    # LOGGER.info(message.to_text())
    return True


def memory_error():
    """Display an error when there is not enough memory."""
    warning_heading = m.Heading(
        tr('Memory issue'), **WARNING_STYLE)
    warning_message = tr(
        'There is not enough free memory to run this analysis.')
    suggestion_heading = m.Heading(
        tr('Suggestion'), **SUGGESTION_STYLE)
    suggestion = tr(
        'Try zooming in to a smaller area or using a raster layer with a '
        'coarser resolution to speed up execution and reduce memory '
        'requirements. You could also try adding more RAM to your computer.')

    message = m.Message()
    message.add(warning_heading)
    message.add(warning_message)
    message.add(suggestion_heading)
    message.add(suggestion)
    send_static_message(dispatcher.Anonymous, message)
