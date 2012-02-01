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
__version__ = '0.0.1'
__date__ = '29/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import traceback
import tempfile


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
        s += '<span class="label important">Problem:</span> ' + errmsg
        s += '</div>'
        s += '<div>'
        s += '<span class="label warning">Traceback:</span> '
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
    myPath = os.path.join(myDir, 'riab')
    if theSubDirectory is not None:
        myPath = os.path.join(myPath, 'theSubDirectory')
    if not os.path.exists(myPath):
        os.makedirs(myPath)

    return myPath
