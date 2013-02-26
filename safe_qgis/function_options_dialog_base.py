# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'function_options_dialog_base.ui'
#
# Created: Tue Nov 13 11:58:11 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FunctionOptionsDialogBase(object):
    def setupUi(self, FunctionOptionsDialogBase):
        FunctionOptionsDialogBase.setObjectName(_fromUtf8("FunctionOptionsDialogBase"))
        FunctionOptionsDialogBase.resize(594, 391)
        self.buttonBox = QtGui.QDialogButtonBox(FunctionOptionsDialogBase)
        self.buttonBox.setGeometry(QtCore.QRect(30, 340, 541, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.lblFunctionDescription = QtGui.QLabel(FunctionOptionsDialogBase)
        self.lblFunctionDescription.setGeometry(QtCore.QRect(10, 10, 561, 61))
        self.lblFunctionDescription.setText(_fromUtf8(""))
        self.lblFunctionDescription.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblFunctionDescription.setWordWrap(True)
        self.lblFunctionDescription.setObjectName(_fromUtf8("lblFunctionDescription"))
        self.lblErrorMessage = QtGui.QLabel(FunctionOptionsDialogBase)
        self.lblErrorMessage.setGeometry(QtCore.QRect(10, 336, 371, 41))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lblErrorMessage.setFont(font)
        self.lblErrorMessage.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0)"))
        self.lblErrorMessage.setText(_fromUtf8(""))
        self.lblErrorMessage.setTextFormat(QtCore.Qt.RichText)
        self.lblErrorMessage.setWordWrap(True)
        self.lblErrorMessage.setObjectName(_fromUtf8("lblErrorMessage"))
        self.tabWidget = QtGui.QTabWidget(FunctionOptionsDialogBase)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setGeometry(QtCore.QRect(10, 50, 571, 271))
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setUsesScrollButtons(False)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.formLayoutWidget = QtGui.QWidget(self.tab)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 0, 541, 231))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.configLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.configLayout.setMargin(0)
        self.configLayout.setObjectName(_fromUtf8("configLayout"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))

        self.retranslateUi(FunctionOptionsDialogBase)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FunctionOptionsDialogBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FunctionOptionsDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(FunctionOptionsDialogBase)

    def retranslateUi(self, FunctionOptionsDialogBase):
        FunctionOptionsDialogBase.setWindowTitle(QtGui.QApplication.translate("FunctionOptionsDialogBase", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("FunctionOptionsDialogBase", "Options", None, QtGui.QApplication.UnicodeUTF8))

