"""
Disaster risk assessment tool developed by AusAid - **GUI Keywords Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '21/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from PyQt4 import QtGui  # QtCore
#from PyQt4.QtCore import pyqtSignature
#from ui_riabdock import Ui_RiabDock
#from utilities import getExceptionWithStacktrace
from riabkeywordsdialogbase import Ui_RiabKeywordsDialogBase

# Don't remove this even if it is flagged as unused by your ide
# it is needed for qrc:/ url resolution. See Qt Resources docs.
import resources

#see if we can import pydev - see development docs for details
try:
    from pydevd import *
    print 'Remote debugging is enabled.'
    DEBUG = True
except Exception, e:
    print 'Debugging was disabled'


class RiabKeywordsDialog(QtGui.QDialog, Ui_RiabKeywordsDialogBase):
    """Dialog implementation class for the Risk In A Box keywords editor."""

    def __init__(self, iface, guiContext=True):
        """Constructor for the dialog.

        Args:

           * iface - a Quantum GIS QGisAppInterface instance.

        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        QtGui.QDialog.__init__(self, None)
        self.setupUi(self)
        # Save reference to the QGIS interface
        self.iface = iface
