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

from safe_qgis.safe_interface import get_free_memory, tr

LOGGER = logging.getLogger('InaSAFE')


def checkMemoryUsage(
        theBufferedGeoExtent,
        theCellSize):
    """Slot to check if analysis is feasible when extents change.

    For simplicity, we will do all our calcs in geocrs.

    Args:
        theBufferedGeoExtent,
        theCellSize

    Returns:
        str: A string containing notes about how much memory is needed
            for a single raster and if this is likely to result in an
            error.

    .. note:: The dock is also updated with a message indicating if the
        memory usage is likely to be too much for the current system.

    """
    myWidth = theBufferedGeoExtent[2] - theBufferedGeoExtent[0]
    myHeight = theBufferedGeoExtent[3] - theBufferedGeoExtent[1]
    try:
        myWidth = myWidth / theCellSize
        myHeight = myHeight / theCellSize
    except TypeError:
        # Could have been a vector layer for example
        LOGGER.info('Error: Computed cellsize was None.')
        return None

    LOGGER.info('Width: %s' % myWidth)
    LOGGER.info('Height: %s' % myHeight)
    LOGGER.info('Pixel Size: %s' % theCellSize)

    # Compute mem requirement in MB (assuming numpy uses 8 bytes by per
    # cell) see this link:
    # http://stackoverflow.com/questions/11784329/
    #      python-memory-usage-of-numpy-arrays
    # Also note that the on-disk requirement of the clipped tifs is about
    # half this since the tifs as in single precision,
    # whereas numpy arrays are in double precision.
    myRequirement = ((myWidth * myHeight * 8) / 1024 / 1024)
    try:
        myFreeMemory = get_free_memory()
    except ValueError:
        myMessage = 'Could not determine free memory'
        LOGGER.exception(myMessage)
        return None

    # We work on the assumption that if more than 10% of the available
    # memory is occupied by a single layer we could run out of memory
    # (depending on the impact function). This is because multiple
    # in memory copies of the layer are often made during processing.
    myWarningLimit = 10
    myUsageIndicator = (float(myRequirement) / float(myFreeMemory)) * 100
    myCountsMessage = ('Memory requirement: about %imb per raster layer ('
                       '%imb available). %.2f / %s' %
                       (myRequirement, myFreeMemory, myUsageIndicator,
                        myWarningLimit))
    myMessage = None
    if myWarningLimit <= myUsageIndicator:
        myMessage = tr(
            'There may not be enough free memory to run this analysis. You can '
            'attempt to run the analysis anyway, but note that your computer '
            'may become unresponsive during execution, and / or the analysis '
            'may fail due to insufficient memory. Proceed at your own risk.')
        mySuggestion = tr(
            'Try zooming in to a smaller area or using a raster layer with a '
            'coarser resolution to speed up execution and reduce memory '
            'requirements. You could also try adding more RAM to your '
            'computer.')
        myHtmlMessage = ('<table class="condensed">'
                         '<tr><th class="warning '
                         'button-cell">%s</th></tr>\n'
                         '<tr><td>%s</td></tr>\n'
                         '<tr><th class="problem '
                         'button-cell">%s</th></tr>\n'
                         '<tr><td>%s</td></tr>\n</table>' %
                         (
                             tr('Memory usage:'),
                             myMessage,
                             tr('Suggestion'),
                             mySuggestion))
        _, myReadyMessage = self.validate()
        myReadyMessage += myHtmlMessage
        self.displayHtml(myReadyMessage)

    LOGGER.info(myCountsMessage)
    # Caller will assume enough memory if myMessage is None
    return myMessage
