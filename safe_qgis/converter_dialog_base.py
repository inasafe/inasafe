# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'converter_dialog_base.ui'
#
# Created: Thu Mar 28 09:42:29 2013
#      by: PyQt4 UI code generator 4.9.3
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
        ConverterDialogBase.resize(393, 346)
        self.buttonBox = QtGui.QDialogButtonBox(ConverterDialogBase)
        self.buttonBox.setGeometry(QtCore.QRect(20, 300, 361, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.lblSubtitle = QtGui.QLabel(ConverterDialogBase)
        self.lblSubtitle.setGeometry(QtCore.QRect(10, 10, 381, 34))
        self.lblSubtitle.setWordWrap(True)
        self.lblSubtitle.setObjectName(_fromUtf8("lblSubtitle"))
        self.lblInput = QtGui.QLabel(ConverterDialogBase)
        self.lblInput.setEnabled(True)
        self.lblInput.setGeometry(QtCore.QRect(10, 50, 371, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblInput.setFont(font)
        self.lblInput.setObjectName(_fromUtf8("lblInput"))
        self.leInputPath = QtGui.QLineEdit(ConverterDialogBase)
        self.leInputPath.setEnabled(True)
        self.leInputPath.setGeometry(QtCore.QRect(10, 70, 351, 27))
        self.leInputPath.setObjectName(_fromUtf8("leInputPath"))
        self.tBtnOpenInput = QtGui.QToolButton(ConverterDialogBase)
        self.tBtnOpenInput.setEnabled(True)
        self.tBtnOpenInput.setGeometry(QtCore.QRect(360, 70, 23, 25))
        self.tBtnOpenInput.setObjectName(_fromUtf8("tBtnOpenInput"))
        self.lblOutput = QtGui.QLabel(ConverterDialogBase)
        self.lblOutput.setEnabled(True)
        self.lblOutput.setGeometry(QtCore.QRect(10, 110, 371, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblOutput.setFont(font)
        self.lblOutput.setObjectName(_fromUtf8("lblOutput"))
        self.tBtnOpenOutput = QtGui.QToolButton(ConverterDialogBase)
        self.tBtnOpenOutput.setEnabled(False)
        self.tBtnOpenOutput.setGeometry(QtCore.QRect(360, 150, 23, 25))
        self.tBtnOpenOutput.setObjectName(_fromUtf8("tBtnOpenOutput"))
        self.leOutputPath = QtGui.QLineEdit(ConverterDialogBase)
        self.leOutputPath.setEnabled(False)
        self.leOutputPath.setGeometry(QtCore.QRect(10, 150, 351, 27))
        self.leOutputPath.setObjectName(_fromUtf8("leOutputPath"))
        self.cBDefaultOutputLocation = QtGui.QCheckBox(ConverterDialogBase)
        self.cBDefaultOutputLocation.setGeometry(QtCore.QRect(10, 130, 371, 22))
        self.cBDefaultOutputLocation.setChecked(True)
        self.cBDefaultOutputLocation.setObjectName(_fromUtf8("cBDefaultOutputLocation"))
        self.cBLoadLayer = QtGui.QCheckBox(ConverterDialogBase)
        self.cBLoadLayer.setEnabled(True)
        self.cBLoadLayer.setGeometry(QtCore.QRect(10, 240, 193, 22))
        self.cBLoadLayer.setChecked(True)
        self.cBLoadLayer.setObjectName(_fromUtf8("cBLoadLayer"))
        self.cboAlgorithm = QtGui.QComboBox(ConverterDialogBase)
        self.cboAlgorithm.setGeometry(QtCore.QRect(10, 210, 371, 25))
        self.cboAlgorithm.setObjectName(_fromUtf8("cboAlgorithm"))
        self.lblAlgotrithm = QtGui.QLabel(ConverterDialogBase)
        self.lblAlgotrithm.setEnabled(True)
        self.lblAlgotrithm.setGeometry(QtCore.QRect(10, 190, 371, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblAlgotrithm.setFont(font)
        self.lblAlgotrithm.setObjectName(_fromUtf8("lblAlgotrithm"))
        self.lblWarning = QtGui.QLabel(ConverterDialogBase)
        self.lblWarning.setGeometry(QtCore.QRect(10, 260, 381, 34))
        font = QtGui.QFont()
        font.setItalic(True)
        self.lblWarning.setFont(font)
        self.lblWarning.setWordWrap(True)
        self.lblWarning.setObjectName(_fromUtf8("lblWarning"))

        self.retranslateUi(ConverterDialogBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ConverterDialogBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ConverterDialogBase.reject)
        QtCore.QObject.connect(self.cBDefaultOutputLocation, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.leOutputPath.setDisabled)
        QtCore.QObject.connect(self.cBDefaultOutputLocation, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.tBtnOpenOutput.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(ConverterDialogBase)

    def retranslateUi(self, ConverterDialogBase):
        ConverterDialogBase.setWindowTitle(QtGui.QApplication.translate("ConverterDialogBase", "InaSAFE - Converter", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSubtitle.setText(QtGui.QApplication.translate("ConverterDialogBase", "Convert raw gird file (.xml) to raster file (.tif). Please select your raw grid file:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblInput.setText(QtGui.QApplication.translate("ConverterDialogBase", "Input : Grid file", None, QtGui.QApplication.UnicodeUTF8))
        self.tBtnOpenInput.setText(QtGui.QApplication.translate("ConverterDialogBase", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOutput.setText(QtGui.QApplication.translate("ConverterDialogBase", "Output : Raster file", None, QtGui.QApplication.UnicodeUTF8))
        self.tBtnOpenOutput.setText(QtGui.QApplication.translate("ConverterDialogBase", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.cBDefaultOutputLocation.setText(QtGui.QApplication.translate("ConverterDialogBase", "Use default location", None, QtGui.QApplication.UnicodeUTF8))
        self.cBLoadLayer.setText(QtGui.QApplication.translate("ConverterDialogBase", "Load output file to QGIS", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAlgotrithm.setText(QtGui.QApplication.translate("ConverterDialogBase", "Algorithm", None, QtGui.QApplication.UnicodeUTF8))
        self.lblWarning.setText(QtGui.QApplication.translate("ConverterDialogBase", "Output filename must be .tif format", None, QtGui.QApplication.UnicodeUTF8))

