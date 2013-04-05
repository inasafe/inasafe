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
    QGroupBox, QLineEdit, QDialog,
    QLabel, QCheckBox, QFormLayout, QWidget)
from function_options_dialog_base import (Ui_FunctionOptionsDialogBase)

from safe_interface import (safeTr,
                            get_postprocessor_human_name)
from third_party.odict import OrderedDict

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

        self._result = None
        self.values = OrderedDict()

    def bind(self, theObject, theProperty, theType):
        """Create a function that return the QWidget property
        of object and convert the value to type.

        Args:
           * theObject - QWidget instance
           * theProperty - the name of property inside QWidget instance
           * theType - a function to convert the property value
        Returns:
           a function that return the property value of theObject
        """
        return lambda: theType(theObject.property(theProperty).toPyObject())

    def buildForm(self, theParams):
        """we build a form from impact functions parameter

        .. note:: see http://tinyurl.com/pyqt-differences

        Args:
           * params - parameters to be edited
        Returns:
           not applicable
        """

        for myKey, myValue in theParams.items():
            if myKey == 'postprocessors':
                self.buildPostProcessorForm(myValue)
            else:
                self.values[myKey] = self.buildWidget(
                    self.configLayout,
                    myKey,
                    myValue)

    def buildPostProcessorForm(self, theParams):
        """Build Post Processor Tab

        Args:
           * theParams - dictionary containing element of form
        Returns:
           not applicable
        """

        # create postprocessors tab
        myTab = QWidget()
        myFormLayout = QFormLayout(myTab)
        myFormLayout.setLabelAlignment(Qt.AlignLeft)
        self.tabWidget.addTab(myTab, self.tr('Postprocessors'))
        self.tabWidget.tabBar().setVisible(True)

        # create element for the tab
        myValues = OrderedDict()
        for myLabel, myOptions in theParams.items():
            myInputValues = OrderedDict()

            # NOTE (gigih) : 'params' is assumed as dictionary
            if 'params' in myOptions:
                myGroupBox = QGroupBox()
                myGroupBox.setCheckable(True)
                myGroupBox.setTitle(get_postprocessor_human_name(myLabel))

                # NOTE (gigih): is 'on' always exist??
                myGroupBox.setChecked(myOptions.get('on'))
                myInputValues['on'] = self.bind(myGroupBox, 'checked', bool)

                myLayout = QFormLayout(myGroupBox)
                myGroupBox.setLayout(myLayout)

                # create widget element from 'params'
                myInputValues['params'] = OrderedDict()
                for myKey, myValue in myOptions['params'].items():
                    myInputValues['params'][myKey] = self.buildWidget(
                        myLayout, myKey, myValue)

                myFormLayout.addRow(myGroupBox, None)

            elif 'on' in myOptions:
                myCheckBox = QCheckBox()
                myCheckBox.setText(get_postprocessor_human_name(myLabel))
                myCheckBox.setChecked(myOptions['on'])

                myInputValues['on'] = self.bind(myCheckBox, 'checked', bool)
                myFormLayout.addRow(myCheckBox, None)
            else:
                raise NotImplementedError('This case is not handled for now')

            myValues[myLabel] = myInputValues

        self.values['postprocessors'] = myValues

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
            myValue = ', '.join([str(x) for x in theValue])
            # NOTE: we assume that all element in list have same type
            myType = type(theValue[0])
            myFunc = lambda x: [myType(y) for y in str(x).split(',')]
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
        """Parse the input value of widget.
        Args:
            * theInput: dictionary that holds all value of element

        Returns:
            a dictionary that can be consumed for impact functions.

        Raises:
            * ValueError - occurs when some input cannot be converted
                           to suitable type.
        """

        myResult = OrderedDict()
        for myName, myValue in theInput.items():
            if hasattr(myValue, '__call__'):
                myResult[myName] = myValue()
            elif isinstance(myValue, dict):
                myResult[myName] = self.parseInput(myValue)
            else:
                myResult[myName] = myValue

        return myResult

    def accept(self):
        """Override the default accept function

        .. note:: see http://tinyurl.com/pyqt-differences

        Args:

        Returns:
           not applicable
        """

        try:
            self._result = self.parseInput(self.values)
            self.done(QDialog.Accepted)
        except (SyntaxError, ValueError) as myEx:
            myText = self.tr("Unexpected error: %s " % myEx)
            self.lblErrorMessage.setText(myText)

    def result(self):
        return self._result
