# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'converter_dialog_base.ui'
#
# Created: Fri Jun  7 09:18:55 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ConverterDialogBase(object):
    def setupUi(self, ConverterDialogBase):
        ConverterDialogBase.setObjectName(_fromUtf8("ConverterDialogBase"))
        ConverterDialogBase.resize(486, 425)
        self.gridLayout = QtGui.QGridLayout(ConverterDialogBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblSubtitle = QtGui.QLabel(ConverterDialogBase)
        self.lblSubtitle.setWordWrap(True)
        self.lblSubtitle.setObjectName(_fromUtf8("lblSubtitle"))
        self.gridLayout.addWidget(self.lblSubtitle, 0, 0, 1, 1)
        self.lblInput = QtGui.QLabel(ConverterDialogBase)
        self.lblInput.setEnabled(True)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblInput.setFont(font)
        self.lblInput.setObjectName(_fromUtf8("lblInput"))
        self.gridLayout.addWidget(self.lblInput, 1, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.leInputPath = QtGui.QLineEdit(ConverterDialogBase)
        self.leInputPath.setEnabled(True)
        self.leInputPath.setObjectName(_fromUtf8("leInputPath"))
        self.horizontalLayout_2.addWidget(self.leInputPath)
        self.tBtnOpenInput = QtGui.QToolButton(ConverterDialogBase)
        self.tBtnOpenInput.setEnabled(True)
        self.tBtnOpenInput.setObjectName(_fromUtf8("tBtnOpenInput"))
        self.horizontalLayout_2.addWidget(self.tBtnOpenInput)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        self.lblOutput = QtGui.QLabel(ConverterDialogBase)
        self.lblOutput.setEnabled(True)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblOutput.setFont(font)
        self.lblOutput.setObjectName(_fromUtf8("lblOutput"))
        self.gridLayout.addWidget(self.lblOutput, 3, 0, 1, 1)
        self.cBDefaultOutputLocation = QtGui.QCheckBox(ConverterDialogBase)
        self.cBDefaultOutputLocation.setChecked(True)
        self.cBDefaultOutputLocation.setObjectName(_fromUtf8("cBDefaultOutputLocation"))
        self.gridLayout.addWidget(self.cBDefaultOutputLocation, 4, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.leOutputPath = QtGui.QLineEdit(ConverterDialogBase)
        self.leOutputPath.setEnabled(False)
        self.leOutputPath.setObjectName(_fromUtf8("leOutputPath"))
        self.horizontalLayout.addWidget(self.leOutputPath)
        self.tBtnOpenOutput = QtGui.QToolButton(ConverterDialogBase)
        self.tBtnOpenOutput.setEnabled(False)
        self.tBtnOpenOutput.setObjectName(_fromUtf8("tBtnOpenOutput"))
        self.horizontalLayout.addWidget(self.tBtnOpenOutput)
        self.gridLayout.addLayout(self.horizontalLayout, 5, 0, 1, 1)
        self.lblAlgotrithm = QtGui.QLabel(ConverterDialogBase)
        self.lblAlgotrithm.setEnabled(True)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblAlgotrithm.setFont(font)
        self.lblAlgotrithm.setObjectName(_fromUtf8("lblAlgotrithm"))
        self.gridLayout.addWidget(self.lblAlgotrithm, 6, 0, 1, 1)
        self.cboAlgorithm = QtGui.QComboBox(ConverterDialogBase)
        self.cboAlgorithm.setObjectName(_fromUtf8("cboAlgorithm"))
        self.gridLayout.addWidget(self.cboAlgorithm, 7, 0, 1, 1)
        self.cBLoadLayer = QtGui.QCheckBox(ConverterDialogBase)
        self.cBLoadLayer.setEnabled(True)
        self.cBLoadLayer.setChecked(True)
        self.cBLoadLayer.setObjectName(_fromUtf8("cBLoadLayer"))
        self.gridLayout.addWidget(self.cBLoadLayer, 8, 0, 1, 1)
        self.lblWarning = QtGui.QLabel(ConverterDialogBase)
        font = QtGui.QFont()
        font.setItalic(True)
        self.lblWarning.setFont(font)
        self.lblWarning.setWordWrap(True)
        self.lblWarning.setObjectName(_fromUtf8("lblWarning"))
        self.gridLayout.addWidget(self.lblWarning, 9, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ConverterDialogBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 1)

        self.retranslateUi(ConverterDialogBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ConverterDialogBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ConverterDialogBase.reject)
        QtCore.QObject.connect(self.cBDefaultOutputLocation, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.leOutputPath.setDisabled)
        QtCore.QObject.connect(self.cBDefaultOutputLocation, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.tBtnOpenOutput.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(ConverterDialogBase)

    def retranslateUi(self, ConverterDialogBase):
        ConverterDialogBase.setWindowTitle(_translate("ConverterDialogBase", "InaSAFE - Converter", None))
        self.lblSubtitle.setText(_translate("ConverterDialogBase", "Convert raw shakemap grid file (.xml) to a raster file (.tif).", None))
        self.lblInput.setText(_translate("ConverterDialogBase", "Input : grid.xml file", None))
        self.tBtnOpenInput.setText(_translate("ConverterDialogBase", "...", None))
        self.lblOutput.setText(_translate("ConverterDialogBase", "Output : Raster file", None))
        self.cBDefaultOutputLocation.setText(_translate("ConverterDialogBase", "Same directory as input file", None))
        self.tBtnOpenOutput.setText(_translate("ConverterDialogBase", "...", None))
        self.lblAlgotrithm.setText(_translate("ConverterDialogBase", "Algorithm", None))
        self.cBLoadLayer.setText(_translate("ConverterDialogBase", "Add output layer to QGIS project", None))
        self.lblWarning.setText(_translate("ConverterDialogBase", "Output filename must end with .tif format", None))

