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

import ast
from PyQt4 import (QtGui, QtCore)
from configurable_impact_functions_dialog_base import (
            Ui_configurableImpactFunctionsDialogBase)

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class ConfigurableImpactFunctionsDialog(QtGui.QDialog,
                Ui_configurableImpactFunctionsDialogBase):
    """ConfigurableImpactFunctions Dialog for InaSAFE."""

    def __init__(self, theParent=None):
        """Constructor for the dialog.

                This dialog will show the user the form for editing
                impact functions parameters if any.

        Args:
           * theParent - Optional widget to use as parent
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        QtGui.QDialog.__init__(self, theParent)
        self.setupUi(self)

    def buildFormFromImpactFunctionsParameter(self, theFunction, params):
        """we build a form from impact functions parameter

        .. note:: see http://tinyurl.com/pyqt-differences

        Args:
           theFunction - theFunction to be modified
           params - parameters to be edited
        Returns:
           not applicable
        """
        self.theFunction = theFunction
        self.formItemCounters = 0
        self.keys = params.keys()
        for key in self.keys:
            self._addFormItem(key, params[key])

    def _addFormItem(self, key, data):
        label = QtGui.QLabel(self.formLayoutWidget)
        label.setObjectName(_fromUtf8(key + "Label"))
        label.setText(key)
        self.editableImpactFunctionsFormLayout.setWidget(self.formItemCounters,
                                        QtGui.QFormLayout.LabelRole, label)
        lineEdit = QtGui.QLineEdit(self.formLayoutWidget)
        lineEdit.setText(str(data))
        lineEdit.setObjectName(_fromUtf8(key + "LineEdit"))
        self.editableImpactFunctionsFormLayout.setWidget(self.formItemCounters,
                                        QtGui.QFormLayout.FieldRole, lineEdit)
        self.formItemCounters += 1

    def accept(self):
        func = self.theFunction
        for key in self.keys:
            lineEdit = self.findChild(QtGui.QLineEdit,
                                      _fromUtf8(key + "LineEdit"))
            lineEditText = lineEdit.text()
            convText = str(lineEditText)
            func.parameters[key] = ast.literal_eval(convText)
        self.close()
