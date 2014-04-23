# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **About Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '26/02/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from PyQt4 import QtGui
from safe_qgis.ui.about_dialog_base import Ui_AboutDialogBase
from safe_qgis.safe_interface import get_version


class AboutDialog(QtGui.QDialog, Ui_AboutDialogBase):
    """About dialog for the InaSAFE plugin."""

    def __init__(self, parent=None):
        """Constructor for the dialog.

        :param parent: Parent widget of this dialog
        :type parent: QWidget
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr('About InaSAFE %s' % get_version()))
        self.parent = parent

