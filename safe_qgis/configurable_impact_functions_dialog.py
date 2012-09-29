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

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

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
        self.setupUi(self)
        # Connect up the buttons.
        self.ui.saveButton.clicked.connect(self.accept)
        self.ui.cancelButton.clicked.connect(self.reject)
        
    def buildFormFromImpactFunctionsParameter(self, theFunction, params):
        #create dict of keys
        #build the gui from params
        #if save set it to the function based on dict of keys
        #otherwise neglect it
        self.formItemCounters = 0
        keys = params.keys()
        for key in keys:
            self._addFormItem(key, params[key])
        self.show()

    def _addFormItem(self, key, data):
        self.formLayoutWidget
        label = QtGui.QLabel(self.formLayoutWidget)
        label.setObjectName(_fromUtf8(key + "Label"))
        self.editableImpactFunctionsFormLayout.setWidget(self.formItemCounters, QtGui.QFormLayout.LabelRole, label)
        lineEdit = QtGui.QLineEdit(self.formLayoutWidget)
        lineEdit.setText(str(data))
        lineEdit.setObjectName(_fromUtf8(key + "LineEdit"))
        self.editableImpactFunctionsFormLayout.setWidget(self.formItemCounters, QtGui.QFormLayout.FieldRole, lineEdit)
        self.formItemCounters += 1