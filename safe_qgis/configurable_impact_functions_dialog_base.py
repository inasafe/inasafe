# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'configurable_impact_functions_dialog_base.ui'
#
# Created: Tue Oct  9 17:24:50 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_configurableImpactFunctionsDialogBase(object):
    def setupUi(self, configurableImpactFunctionsDialogBase):
        configurableImpactFunctionsDialogBase.setObjectName(_fromUtf8("configurableImpactFunctionsDialogBase"))
        configurableImpactFunctionsDialogBase.resize(594, 391)
        self.editableImpactFunctionsButtonBox = QtGui.QDialogButtonBox(configurableImpactFunctionsDialogBase)
        self.editableImpactFunctionsButtonBox.setGeometry(QtCore.QRect(30, 340, 541, 32))
        self.editableImpactFunctionsButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.editableImpactFunctionsButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.editableImpactFunctionsButtonBox.setObjectName(_fromUtf8("editableImpactFunctionsButtonBox"))
        self.formLayoutWidget = QtGui.QWidget(configurableImpactFunctionsDialogBase)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 80, 561, 231))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.editableImpactFunctionsFormLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.editableImpactFunctionsFormLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.editableImpactFunctionsFormLayout.setMargin(0)
        self.editableImpactFunctionsFormLayout.setObjectName(_fromUtf8("editableImpactFunctionsFormLayout"))
        self.impFuncConfLabel = QtGui.QLabel(configurableImpactFunctionsDialogBase)
        self.impFuncConfLabel.setGeometry(QtCore.QRect(10, 10, 561, 61))
        self.impFuncConfLabel.setText(_fromUtf8(""))
        self.impFuncConfLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.impFuncConfLabel.setWordWrap(True)
        self.impFuncConfLabel.setObjectName(_fromUtf8("impFuncConfLabel"))
        self.impFuncConfErrLabel = QtGui.QLabel(configurableImpactFunctionsDialogBase)
        self.impFuncConfErrLabel.setGeometry(QtCore.QRect(10, 336, 371, 41))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.impFuncConfErrLabel.setFont(font)
        self.impFuncConfErrLabel.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0)"))
        self.impFuncConfErrLabel.setText(_fromUtf8(""))
        self.impFuncConfErrLabel.setTextFormat(QtCore.Qt.RichText)
        self.impFuncConfErrLabel.setWordWrap(True)
        self.impFuncConfErrLabel.setObjectName(_fromUtf8("impFuncConfErrLabel"))

        self.retranslateUi(configurableImpactFunctionsDialogBase)
        QtCore.QObject.connect(self.editableImpactFunctionsButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), configurableImpactFunctionsDialogBase.accept)
        QtCore.QObject.connect(self.editableImpactFunctionsButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), configurableImpactFunctionsDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(configurableImpactFunctionsDialogBase)

    def retranslateUi(self, configurableImpactFunctionsDialogBase):
        configurableImpactFunctionsDialogBase.setWindowTitle(QtGui.QApplication.translate("configurableImpactFunctionsDialogBase", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

