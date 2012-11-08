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
__revision__ = '$Format:%H$'
__date__ = '01/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import ast
from PyQt4 import QtGui, QtCore
from function_options_dialog_base import (
            Ui_FunctionOptionsDialogBase)

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


# FIXME (Tim and Ole): Change to ConfigurationDialog throughout
#                      Maybe also change filename and Base name accordingly.
class FunctionOptionsDialog(QtGui.QDialog,
                Ui_FunctionOptionsDialogBase):
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
        self.setWindowTitle(self.tr('Impact function configuration'))

    def buildForm(self, theFunction, params):
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

    def _addFormItem(self, theParameterKey, theParameterValue):
        """Add a new form element dynamically from a key value pair.

        Args:
            * theParameterKey: str Mandatory string referencing the key in the
                function configurable parameters dictionary.
            * theParameterValue: object Mandatory representing the value
                referenced by the key.

        Returns:
            None

        Raises:
            None

        """
        myLabel = QtGui.QLabel(self.formLayoutWidget)
        myLabel.setObjectName(_fromUtf8(theParameterKey + "Label"))
        myKey = theParameterKey
        myKey = myKey.replace('_', ' ')
        myKey = myKey.capitalize()
        myLabel.setText(myKey)
        myLabel.setToolTip(str(type(theParameterValue)))
        self.editableImpactFunctionsFormLayout.setWidget(self.formItemCounters,
                                        QtGui.QFormLayout.LabelRole, myLabel)
        myLineEdit = QtGui.QLineEdit(self.formLayoutWidget)
        myLineEdit.setText(str(theParameterValue))
        myLineEdit.setObjectName(_fromUtf8(theParameterKey + 'LineEdit'))
        myLineEdit.setCursorPosition(0)
        self.editableImpactFunctionsFormLayout.setWidget(self.formItemCounters,
                                        QtGui.QFormLayout.FieldRole,
                                        myLineEdit)

        #FIXME (MB) temporary fix through hiding for issue 365
        if theParameterKey == 'postprocessors':
            myLineEdit.hide()
            myLabel.hide()
        self.formItemCounters += 1

    def setDialogInfo(self, theFunctionID):
        myText = ''
        impactFunctionName = theFunctionID
        myText += self.tr('Parameters for impact function "%1" that can be '
                          'modified are:').arg(impactFunctionName)
        myLabel = self.impFuncConfLabel
        myLabel.setText(myText)

    def accept(self):
        """Override the default accept function

        .. note:: see http://tinyurl.com/pyqt-differences

        Args:
           theFunction - theFunction to be modified
           params - parameters to be edited
        Returns:
           not applicable
        """
        noError = False
        myFunction = self.theFunction
        for key in self.keys:
            try:
                lineEdit = self.findChild(QtGui.QLineEdit,
                                          _fromUtf8(key + "LineEdit"))
                lineEditText = lineEdit.text()
                convText = str(lineEditText)
                myFunction.parameters[key] = ast.literal_eval(convText)
            except ValueError:
                text = ("Unexpected error: ValueError" +
                ". Please consult Python language reference for correct " +
                "format of data type.")
                label = self.impFuncConfErrLabel
                label.setText(text)
                noError = True
        if (not noError):
            self.close()
