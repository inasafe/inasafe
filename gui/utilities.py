"""
Disaster risk assessment tool developed by AusAid -
  **Riab Utilitles implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.2.0'
__date__ = '29/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import traceback
import tempfile
from PyQt4.QtCore import QCoreApplication
from qgis.core import QgsMapLayer, QgsCoordinateReferenceSystem


def tr(theText):
    """We define a tr() alias here since the utilities implementation below
    is not a class and does not inherit from QObject.
    .. note:: see http://tinyurl.com/pyqt-differences
    Args:
       theText - string to be translated
    Returns:
       Translated version of the given string if available, otherwise
       the original string.
    """
    myContext = "Utilities"
    return QCoreApplication.translate(myContext, theText)


def getExceptionWithStacktrace(e, html=False):
    """Convert exception into a string and and stack trace

    Input
        e: Exception object
        html: Optional flat if output is to wrapped as html

    Output
        Exception with stack trace info suitable for display
    """

    info = ''.join(traceback.format_tb(sys.exc_info()[2]))
    errmsg = str(e)

    if not html:
        return errmsg + "\n" + info
    else:
        # Wrap string in html
        s = '<div>'
        s += tr('<span class="label important">Problem:</span> ') + errmsg
        s += '</div>'
        s += '<div>'
        s += tr('<span class="label warning">Traceback:</span> ')
        s += '<pre id="traceback" class="prettyprint">\n'
        s += info
        s += '</pre></div>'

        return s


def getTempDir(theSubDirectory=None):
    """Obtain the temporary working directory for the operating system.

    A riab subdirectory will automatically be created under this and
    if specified, a user subdirectory under that.

    Args:
        theSubDirectory - optional argument which will cause an additional
                subirectory to be created e.g. /tmp/riab/foo/

    Returns:
        Path to the output clipped layer (placed in the
        system temp dir).

    Raises:
       Any errors from the underlying system calls.
    """
    myDir = tempfile.gettempdir()
    if os.name is 'nt':  # Windows
        myDir = 'c://temp'
    elif os.name is 'posix':  # linux, osx
        myDir = '/tmp'
    myPath = os.path.join(myDir, 'riab')
    if theSubDirectory is not None:
        myPath = os.path.join(myPath, 'theSubDirectory')
    if not os.path.exists(myPath):
        os.makedirs(myPath)

    return myPath


def getWGS84resolution(theLayer, theGeoExtent=None):
    """Return resolution of raster layer in EPSG:4326

    Input
        theLayer: Raster layer
        theGeoExtent: Bounding box in EPSG:4326
        # FIXME (Ole), the second argumunt should be obtained within
                       this function to make it independent
    Output
        resolution.

    If input layer is already in EPSG:4326, simply return the resolution
    If not, work it out based on EPSG:4326 representations of its extent
    """

    msg = tr('Input layer to getWGS84resolution must be a raster layer. '
           'I got: %s' % str(theLayer.type())[1:-1])
    if not theLayer.type() == QgsMapLayer.RasterLayer:
        raise RuntimeError(msg)

    if theLayer.crs().authid() == 'EPSG:4326':
        # If it is already in EPSG:4326, simply use the native resolution
        myCellSize = theLayer.rasterUnitsPerPixel()
    else:
        # Otherwise, work it out based on EPSG:4326 representations of
        # its extent

        # Reproject extent to EPSG:4326
        myGeoCrs = QgsCoordinateReferenceSystem()
        myGeoCrs.createFromEpsg(4326)

        # Estimate cellsize
        # FIXME (Ole): Get geoextent from layer
        myColumns = theLayer.width()
        myGeoWidth = abs(theGeoExtent[3] - theGeoExtent[0])
        myCellSize = myGeoWidth / myColumns

    return myCellSize
