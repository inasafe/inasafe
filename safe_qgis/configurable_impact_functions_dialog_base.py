# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'configurable_impact_functions_dialog_base.ui'
#
# Created: Fri Oct  5 16:37:50 2012
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
        self.editableImpactFunctionsButtonBox.setGeometry(QtCore.QRect(30, 350, 541, 32))
        self.editableImpactFunctionsButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.editableImpactFunctionsButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.editableImpactFunctionsButtonBox.setObjectName(_fromUtf8("editableImpactFunctionsButtonBox"))
        self.formLayoutWidget = QtGui.QWidget(configurableImpactFunctionsDialogBase)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 80, 561, 261))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.editableImpactFunctionsFormLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.editableImpactFunctionsFormLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.editableImpactFunctionsFormLayout.setMargin(0)
        self.editableImpactFunctionsFormLayout.setObjectName(_fromUtf8("editableImpactFunctionsFormLayout"))
        self.webViewConfImpFuncDesc = QtWebKit.QWebView(configurableImpactFunctionsDialogBase)
        self.webViewConfImpFuncDesc.setGeometry(QtCore.QRect(10, 10, 561, 61))
        self.webViewConfImpFuncDesc.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webViewConfImpFuncDesc.setObjectName(_fromUtf8("webViewConfImpFuncDesc"))

        self.retranslateUi(configurableImpactFunctionsDialogBase)
        QtCore.QObject.connect(self.editableImpactFunctionsButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), configurableImpactFunctionsDialogBase.accept)
        QtCore.QObject.connect(self.editableImpactFunctionsButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), configurableImpactFunctionsDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(configurableImpactFunctionsDialogBase)

    def retranslateUi(self, configurableImpactFunctionsDialogBase):
        configurableImpactFunctionsDialogBase.setWindowTitle(QtGui.QApplication.translate("configurableImpactFunctionsDialogBase", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import QtWebKit
