"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Help Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '20/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import logging
from PyQt4 import (QtGui, QtCore)

LOGGER = logging.getLogger('InaSAFE')


class Help(QtGui.QDialog):
    """Help dialog class for the Risk In A Box plugin.

    .. todo:: Add navigation buttons. See url for example of how to do so.
       http://www.rkblog.rk.edu.pl/w/p/webkit-pyqt-rendering-web-pages/

    """

    def __init__(self, theParent=None, theContext=None):
        """Constructor for the dialog.

        This dialog will show the user help documentation.

        Args:
           * theParent - Optional widget to use as parent
           * theContext - Optional - page name (without path)
             of a document in the user-docs subdirectory.
             e.g. 'keywords'
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        self.parent = theParent
        self.context = theContext
        QtGui.QDialog.__init__(self, self.parent)
        self.showContextHelp()

    def showContextHelp(self):
        """Load the help text into the wvResults widget."""
        if 'LANG' in os.environ:
            myLocale = os.environ['LANG']
        else:
            myLocale = 'en'

        # Check if a translation of the chosen locale exists, otherwise
        # revert to en (English).
        myRootPath = os.path.dirname(__file__)
        myRootPath = os.path.abspath(os.path.join(myRootPath,
                                     '..',
                                     'docs',
                                     'output',
                                     'html'))

        if (os.path.exists(
                os.path.join(myRootPath, myLocale)) and myLocale != 'en'):
            myRootPath = os.path.join(myRootPath, myLocale)
        else:
            myRootPath = os.path.join(myRootPath, 'en')

        myPath = os.path.abspath(os.path.join(myRootPath,
                                              'user-docs',
                                              'README.html'))

        if self.context is not None:
            myContextPath = os.path.abspath(os.path.join(myRootPath,
                                            'user-docs',
                                            self.context + '.html'))
            LOGGER.debug(os.path.isfile(myContextPath))
            if os.path.isfile(myContextPath):
                myPath = myContextPath

        if not os.path.isfile(myPath):
            QtGui.QMessageBox.warning(
                self.parent, self.tr('InaSAFE'),
                (self.tr('Documentation could not be found at:\n'
                         '%1').arg(myPath)))
        else:
            myUrl = QtCore.QUrl('file:///' + myPath)
            QtGui.QDesktopServices.openUrl(myUrl)
