# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'converter_dialog_base.ui'
#
# Created: Tue Feb 12 11:33:30 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ConverterDialogBase(object):
    def setupUi(self, ConverterDialogBase):
        ConverterDialogBase.setObjectName(_fromUtf8("ConverterDialogBase"))
        ConverterDialogBase.resize(399, 316)
        self.buttonBox = QtGui.QDialogButtonBox(ConverterDialogBase)
        self.buttonBox.setGeometry(QtCore.QRect(10, 270, 381, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label_1 = QtGui.QLabel(ConverterDialogBase)
        self.label_1.setGeometry(QtCore.QRect(10, 20, 381, 34))
        self.label_1.setWordWrap(True)
        self.label_1.setObjectName(_fromUtf8("label_1"))
        self.lblInput = QtGui.QLabel(ConverterDialogBase)
        self.lblInput.setEnabled(True)
        self.lblInput.setGeometry(QtCore.QRect(10, 70, 99, 17))
        self.lblInput.setObjectName(_fromUtf8("lblInput"))
        self.leInputPath = QtGui.QLineEdit(ConverterDialogBase)
        self.leInputPath.setEnabled(True)
        self.leInputPath.setGeometry(QtCore.QRect(10, 90, 351, 27))
        self.leInputPath.setObjectName(_fromUtf8("leInputPath"))
        self.tBtnOpenInput = QtGui.QToolButton(ConverterDialogBase)
        self.tBtnOpenInput.setEnabled(True)
        self.tBtnOpenInput.setGeometry(QtCore.QRect(370, 90, 23, 25))
        self.tBtnOpenInput.setObjectName(_fromUtf8("tBtnOpenInput"))
        self.lblOutput = QtGui.QLabel(ConverterDialogBase)
        self.lblOutput.setEnabled(True)
        self.lblOutput.setGeometry(QtCore.QRect(10, 140, 128, 17))
        self.lblOutput.setObjectName(_fromUtf8("lblOutput"))
        self.tBtnOpenOutput = QtGui.QToolButton(ConverterDialogBase)
        self.tBtnOpenOutput.setEnabled(True)
        self.tBtnOpenOutput.setGeometry(QtCore.QRect(370, 180, 23, 25))
        self.tBtnOpenOutput.setObjectName(_fromUtf8("tBtnOpenOutput"))
        self.leOutputPath = QtGui.QLineEdit(ConverterDialogBase)
        self.leOutputPath.setEnabled(True)
        self.leOutputPath.setGeometry(QtCore.QRect(10, 180, 351, 27))
        self.leOutputPath.setObjectName(_fromUtf8("leOutputPath"))
        self.cBDefaultOuputLocation = QtGui.QCheckBox(ConverterDialogBase)
        self.cBDefaultOuputLocation.setGeometry(QtCore.QRect(10, 160, 165, 22))
        self.cBDefaultOuputLocation.setObjectName(_fromUtf8("cBDefaultOuputLocation"))
        self.cBLoadLayer = QtGui.QCheckBox(ConverterDialogBase)
        self.cBLoadLayer.setGeometry(QtCore.QRect(20, 240, 193, 22))
        self.cBLoadLayer.setObjectName(_fromUtf8("cBLoadLayer"))

        self.retranslateUi(ConverterDialogBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ConverterDialogBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ConverterDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(ConverterDialogBase)

    def retranslateUi(self, ConverterDialogBase):
        ConverterDialogBase.setWindowTitle(QtGui.QApplication.translate("ConverterDialogBase", "InaSAFE - Converter", None, QtGui.QApplication.UnicodeUTF8))
        self.label_1.setText(QtGui.QApplication.translate("ConverterDialogBase", "Convert raw gird file (.xml) to raster file (.tif). Please select your raw grid file:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblInput.setText(QtGui.QApplication.translate("ConverterDialogBase", "Input : Grid file", None, QtGui.QApplication.UnicodeUTF8))
        self.tBtnOpenInput.setText(QtGui.QApplication.translate("ConverterDialogBase", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOutput.setText(QtGui.QApplication.translate("ConverterDialogBase", "Output : Raster file", None, QtGui.QApplication.UnicodeUTF8))
        self.tBtnOpenOutput.setText(QtGui.QApplication.translate("ConverterDialogBase", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.cBDefaultOuputLocation.setText(QtGui.QApplication.translate("ConverterDialogBase", "Use default location", None, QtGui.QApplication.UnicodeUTF8))
        self.cBLoadLayer.setText(QtGui.QApplication.translate("ConverterDialogBase", "Load output file to QGIS", None, QtGui.QApplication.UnicodeUTF8))

