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
from PyQt4.QtCore import QRect, QObject, QVariant
from PyQt4.QtGui import QTabWidget, QLineEdit, QLabel, QCheckBox, QFormLayout, QWidget
from function_options_dialog_base import (
            Ui_FunctionOptionsDialogBase)

from safe_interface import safeTr

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
        self.setWindowTitle(self.tr('InaSAFE impact function configuration'))

        self.inputs = {}


    def buildForm(self, theFunction, theParams):
        """we build a form from impact functions parameter

        .. note:: see http://tinyurl.com/pyqt-differences

        Args:
           * theFunction - theFunction to be modified
           * params - parameters to be edited
        Returns:
           not applicable
        """

        self.theFunction = theFunction

        if 'postprocessors' in theParams:
            self._addPostProcessorFormItem(theParams['postprocessors'])

        myParams = filter(lambda x: x[0] != 'postprocessors', theParams.items())
        for (myKey, myValue) in myParams:
            self._addFormItem(myKey, myValue)

    def _addPostProcessorFormItem(self, theParams):
        myTabWidget = QtGui.QTabWidget(self)
        myTabWidget.setGeometry(QRect(10, 80, 561, 231))

        # create other options tab
        myOptionTab = QWidget()
        self.editableImpactFunctionsFormLayout.setParent(myOptionTab)
        myTabWidget.addTab(myOptionTab, self.tr('options'))

        # create postprocessors tab
        myPostProcessorsTab = QWidget()
        myFormLayout = QFormLayout(myPostProcessorsTab)
        myTabWidget.addTab(myPostProcessorsTab, self.tr('postprocessors'))


        for myLabel, myOptions in theParams.items():
            myCheckBox = QCheckBox()
            myCheckBox.setText(myLabel)

            myWidget = None

            if myOptions.get('on') is True:
                myCheckBox.setChecked(True)

            if 'params' in myOptions:
                myWidget = QLineEdit()
                myWidget.setText(str(myOptions['params']))
            
            myFormLayout.addRow(myCheckBox, myWidget)


    def _addFormItem(self, theName, theValue):
        """Add a new form element dynamically from a key value pair.

        Args:
            * theName: str Mandatory string referencing the key in the
                function configurable parameters dictionary.
            * theValue: object Mandatory representing the value
                referenced by the key.

        Returns:
            None

        Raises:
            None

        """
        myLabel = QLabel(self.formLayoutWidget)
        myLabel.setObjectName(_fromUtf8(theName + "Label"))
        myLabelText = theName.replace('_', ' ').capitalize()
        myLabel.setText(safeTr(myLabelText))
        myLabel.setToolTip(str(type(theValue)))

        myLineEdit = QLineEdit(self.formLayoutWidget)
        myObjectName = _fromUtf8(theName + 'LineEdit')
        myLineEdit.setObjectName(myObjectName)
        myLineEdit.setCursorPosition(0)

        if isinstance(theValue, list):
            myValue = ', '.join(map(str, theValue))
            myLineEdit.setText(myValue)
            self.inputs[theName] = lambda: map( float, str(myLineEdit.text()).split(',') )
        else:
            myValue = str(theValue)
            myLineEdit.setText(myValue)
            self.inputs[theName] = lambda: type(theValue)(myLineEdit.text())

        self.editableImpactFunctionsFormLayout.addRow(myLabel, myLineEdit)

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
        hasError = False
        myFunction = self.theFunction

        for myName, myValueFunc in self.inputs.items():
            try:
                myFunction.parameters[myName] = myValueFunc()
            except Exception as myEx:
                myText = self.tr("Unexpected error: " + str(myEx))
                self.impFuncConfErrLabel.setText(myText)
                hasError = True

        if not hasError:
            self.close()

if __name__ == '__main__':

    class FunctionMock:
        parameters = {}

    theFunctionID = 'Flood Evacuation Function'
    theFunction = FunctionMock()
    theParams =  {
        'thresholds': [1.0],
        'postprocessors': {
            'Gender': {'on': True},
            'Age': {
                'on': True,
                'params': {'youth_ratio': 0.263, 'elder_ratio': 0.078, 'adult_ratio': 0.659}
            }
        }
    }


    import sys
    app = QtGui.QApplication(sys.argv)

    a = FunctionOptionsDialog()
    a.setDialogInfo(theFunctionID)
    a.buildForm(theFunction, theParams)
    a.show()

    sys.exit(app.exec_())