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
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (
    QGroupBox, QLineEdit, QLabel, QCheckBox, QFormLayout, QWidget)
from function_options_dialog_base import (Ui_FunctionOptionsDialogBase)

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
        self.tabWidget.tabBar().setVisible(False)

        self.values = {}

    def bind(self, object, propertyName, type):
        return lambda: type(object.property(propertyName).toPyObject())

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

        for myKey, myValue in theParams.items():
            if myKey == 'postprocessors':
                self._addPostProcessorFormItem(myValue)
            else:
                self.values[myKey] = self.buildWidget(
                    self.configLayout,
                    myKey,
                    myValue)

    def _addPostProcessorFormItem(self, theParams):
        # create postprocessors tab
        myTab = QWidget()
        myFormLayout = QFormLayout(myTab)
        myFormLayout.setLabelAlignment(Qt.AlignLeft)
        self.tabWidget.addTab(myTab, self.tr('Postprocessors'))
        self.tabWidget.tabBar().setVisible(True)

        # create element for the tab
        myValues = {}
        for myLabel, myOptions in theParams.items():
            myInputValues = {}

            # NOTE (gigih) : 'params' is assumed as dictionary
            if 'params' in myOptions:
                myGroupBox = QGroupBox()
                myGroupBox.setCheckable(True)
                myGroupBox.setTitle(myLabel)

                # NOTE (gigih): is 'on' always exist??
                myGroupBox.setChecked(myOptions.get('on'))
                myInputValues['on'] = self.bind(myGroupBox, 'checked', bool)

                myLayout = QFormLayout(myGroupBox)
                myGroupBox.setLayout(myLayout)

                myInputValues['params'] = {}
                for myKey, myValue in  myOptions['params'].items():
                    myInputValues['params'][myKey] = self.buildWidget(
                        myLayout, myKey, myValue)


                myFormLayout.addRow(myGroupBox, None)

            elif myOptions.has_key('on'):
                myCheckBox = QCheckBox()
                myCheckBox.setText(myLabel)
                myCheckBox.setChecked(myOptions['on'])

                myInputValues['on'] = self.bind(myCheckBox, 'checked', bool)
                myFormLayout.addRow(myCheckBox, None)
            else:
                raise NotImplementedError('This case is not handled for now')

            myValues[myLabel] = myInputValues

        self.values['postprocessors'] = myValues
        print self.values['postprocessors']

    def buildWidget(self, theFormLayout, theName, theValue):
        """Create a new form element dynamically based from theValue type.
        The element will be inserted to theFormLayout.

        Args:
            * theFormLayout: QFormLayout Mandatory a layout instance
            * theName: str Mandatory string referencing the key in the
                function configurable parameters dictionary.
            * theValue: object Mandatory representing the value
                referenced by the key.

        Returns:
            a function that return the value of widget

        Raises:
            None

        """

        # create label
        if isinstance(theName, str):
            myLabel = QLabel()
            myLabel.setObjectName(_fromUtf8(theName + "Label"))
            myLabelText = theName.replace('_', ' ').capitalize()
            myLabel.setText(safeTr(myLabelText))
            myLabel.setToolTip(str(type(theValue)))
        else:
            myLabel = theName

        # create widget based on the type of theValue variable
        if isinstance(theValue, list):
            myWidget = QLineEdit()
            myValue = ', '.join(map(str, theValue))
            # NOTE: we assume that all element in list have same type
            myType = type(theValue[0])
            myFunc = lambda x: map(myType, str(x).split(','))
        elif isinstance(theValue, dict):
            myWidget = QLineEdit()
            myValue = str(theValue)
            myFunc = lambda x: ast.literal_eval(str(x))
        else:
            myWidget = QLineEdit()
            myValue = str(theValue)
            myFunc = type(theValue)

        myWidget.setText(myValue)
        theFormLayout.addRow(myLabel, myWidget)

        return self.bind(myWidget, 'text', myFunc)

    def setDialogInfo(self, theFunctionID):

        myText = ''
        impactFunctionName = theFunctionID
        myText += self.tr('Parameters for impact function "%1" that can be '
                          'modified are:').arg(impactFunctionName)
        myLabel = self.lblFunctionDescription
        myLabel.setText(myText)

    def parseInput(self, theInput):
#        print "theInput : %s" % theInput
        myResult = {}
        for myName, myValue in theInput.items():
            if hasattr(myValue, '__call__'):
                myResult[myName] = myValue()
            elif isinstance(myValue, dict):
                myResult[myName] = self.parseInput(myValue)
            else:
                myResult[myName] = myValue
           # print "(%s, %s) Result : %s" % (myName, myValue, myResult)

        return myResult

    def accept(self):
        """Override the default accept function

        .. note:: see http://tinyurl.com/pyqt-differences

        Args:
           theFunction - theFunction to be modified
           params - parameters to be edited
        Returns:
           not applicable
        """

        try:
            myResult = self.parseInput(self.values)
            self.theFunction.parameters = myResult
            self.close()
        except Exception as myEx:
            myText = self.tr("Unexpected error: %s " % myEx)
            self.lblErrorMessage.setText(myText)


if __name__ == '__main__':

    class FunctionMock:
        parameters = {}

    theFunctionID = 'Flood Evacuation Function'
    theFunction = FunctionMock()
    theParams = {
        'thresholds': [1.0],
        'postprocessors': {
            'Gender': {'on': True},
            'Age': {
                'on': True,
                'params': {
                    'youth_ratio': 0.263,
                    'elder_ratio': 0.078,
                    'adult_ratio': 0.659}
            }
        }
    }

    import sys
    app = QtGui.QApplication(sys.argv)

    a = FunctionOptionsDialog()
    a.setDialogInfo(theFunctionID)
    a.buildForm(theFunction, theParams)
    a.show()

    app.exec_()

    print "theParams : %s" % theParams
    print "result: %s" % theFunction.parameters
