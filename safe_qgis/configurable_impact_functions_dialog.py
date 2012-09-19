"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Functions Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'oz@tanoshiistudio.com'
__version__ = '0.5.0'
__revision__ = '$Format:%H$'
__date__ = '17/09/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from PyQt4 import (QtGui, QtCore, QtWebKit,)
from configurable_impact_functions_dialog_base import Ui_configurableImpactFunctionsDialogBase

class ConfigurableImpactFunctionsDialog(QtGui.QDialog, Ui_configurableImpactFunctionsDialogBase):
    '''ConfigurableImpactFunctions Dialog for InaSAFE.
    '''


    def __init__(self, theParent=None):
        '''Constructor for the dialog.

                This dialog will show the user the form for editing
                impact functions parameters if any.

        Args:
           * theParent - Optional widget to use as parent
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        '''
        QtGui.QDialog.__init__(self, theParent)
        
    def buildFormFromImpactFunctionsParameter(self, params):
        pass