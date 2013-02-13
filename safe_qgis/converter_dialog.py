"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Converter Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from PyQt4.QtCore import pyqtSignature

__author__ = 'imajimatika@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '12/2/2013'
__license__ = "GPL"
__copyright__ = 'Copyright 2013, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import logging

from converter_dialog_base import Ui_ConverterDialogBase
from PyQt4 import QtGui

from safe_qgis.safe_interface import get_version

LOGGER = logging.getLogger('InaSAFE')


class ConverterDialog(QtGui.QDialog, Ui_ConverterDialogBase):
    """Converter Dialog for InaSAFE
    """
    def __init__(self, theParent=None):
        """Constructor for the dialog.

                This dialog will show the user converter dialog

        Args:
           * theParent - Optional widget to use as parent
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        QtGui.QDialog.__init__(self, theParent)
        self.parent = theParent
        self.setupUi(self)
        self.setWindowTitle(self.tr('InaSAFE %1 Converter').arg(get_version()))

    def accept(self):
        LOGGER.debug('OK Ok OK oK oK OK')
        self.done(self.Accepted)
        pass

    @pyqtSignature('')  # prevents actions being handled twice
    def on_tBtnOpenInput_clicked(self):
        """Autoconnect slot activated when the open input tool button is
        clicked,
        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myFilename = QtGui.QFileDialog.getOpenFileName(self,
                                            self.tr('Input file'),
                                            'grid.xml',
                                            self.tr('Raw grid file(*.xml)'))
        self.leInputPath.setText(myFilename)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_tBtnOpenOutput_clicked(self):
        """Autoconnect slot activated when the open output tool button is
        clicked,
        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myFilename = QtGui.QFileDialog.getSaveFileName(self,
                                                self.tr('Ouput file'),
                                                'ismailsunni.tif',
                                                self.tr('Raster file(*.tif)'))
        self.leOutputPath.setText(myFilename)
