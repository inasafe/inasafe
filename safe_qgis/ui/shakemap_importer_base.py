# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'shakemap_importer_base.ui'
#
# Created: Mon Aug 26 11:48:31 2013
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

class Ui_ShakemapImporterBase(object):
    def setupUi(self, ShakemapImporterBase):
        ShakemapImporterBase.setObjectName(_fromUtf8("ShakemapImporterBase"))
        ShakemapImporterBase.resize(625, 545)
        self.gridLayout_4 = QtGui.QGridLayout(ShakemapImporterBase)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.webView = QtWebKit.QWebView(ShakemapImporterBase)
        self.webView.setProperty("url", QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.gridLayout_4.addWidget(self.webView, 0, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(ShakemapImporterBase)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblInput = QtGui.QLabel(self.groupBox_2)
        self.lblInput.setEnabled(True)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lblInput.setFont(font)
        self.lblInput.setText(_fromUtf8(""))
        self.lblInput.setObjectName(_fromUtf8("lblInput"))
        self.gridLayout_2.addWidget(self.lblInput, 0, 0, 1, 1)
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 1, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.leInputPath = QtGui.QLineEdit(self.groupBox_2)
        self.leInputPath.setEnabled(True)
        self.leInputPath.setObjectName(_fromUtf8("leInputPath"))
        self.horizontalLayout_2.addWidget(self.leInputPath)
        self.tBtnOpenInput = QtGui.QToolButton(self.groupBox_2)
        self.tBtnOpenInput.setEnabled(True)
        self.tBtnOpenInput.setObjectName(_fromUtf8("tBtnOpenInput"))
        self.horizontalLayout_2.addWidget(self.tBtnOpenInput)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 1, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(ShakemapImporterBase)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.leOutputPath = QtGui.QLineEdit(self.groupBox_3)
        self.leOutputPath.setEnabled(False)
        self.leOutputPath.setObjectName(_fromUtf8("leOutputPath"))
        self.horizontalLayout.addWidget(self.leOutputPath)
        self.tBtnOpenOutput = QtGui.QToolButton(self.groupBox_3)
        self.tBtnOpenOutput.setEnabled(False)
        self.tBtnOpenOutput.setObjectName(_fromUtf8("tBtnOpenOutput"))
        self.horizontalLayout.addWidget(self.tBtnOpenOutput)
        self.gridLayout_3.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_3)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_3.addWidget(self.label_2, 2, 0, 1, 1)
        self.cBDefaultOutputLocation = QtGui.QCheckBox(self.groupBox_3)
        self.cBDefaultOutputLocation.setChecked(True)
        self.cBDefaultOutputLocation.setObjectName(_fromUtf8("cBDefaultOutputLocation"))
        self.gridLayout_3.addWidget(self.cBDefaultOutputLocation, 0, 0, 1, 1)
        self.cBLoadLayer = QtGui.QCheckBox(self.groupBox_3)
        self.cBLoadLayer.setEnabled(True)
        self.cBLoadLayer.setChecked(True)
        self.cBLoadLayer.setObjectName(_fromUtf8("cBLoadLayer"))
        self.gridLayout_3.addWidget(self.cBLoadLayer, 3, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_3, 2, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(ShakemapImporterBase)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.radNearest = QtGui.QRadioButton(self.groupBox)
        self.radNearest.setChecked(True)
        self.radNearest.setObjectName(_fromUtf8("radNearest"))
        self.gridLayout.addWidget(self.radNearest, 0, 0, 1, 1)
        self.radInvDist = QtGui.QRadioButton(self.groupBox)
        self.radInvDist.setObjectName(_fromUtf8("radInvDist"))
        self.gridLayout.addWidget(self.radInvDist, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ShakemapImporterBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_4.addWidget(self.buttonBox, 4, 0, 1, 1)

        self.retranslateUi(ShakemapImporterBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ShakemapImporterBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ShakemapImporterBase.reject)
        QtCore.QObject.connect(self.cBDefaultOutputLocation, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.leOutputPath.setDisabled)
        QtCore.QObject.connect(self.cBDefaultOutputLocation, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.tBtnOpenOutput.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(ShakemapImporterBase)

    def retranslateUi(self, ShakemapImporterBase):
        ShakemapImporterBase.setWindowTitle(_translate("ShakemapImporterBase", "InaSAFE - Shakemap Importer", None))
        self.groupBox_2.setTitle(_translate("ShakemapImporterBase", "Input", None))
        self.label.setText(_translate("ShakemapImporterBase", "The input should be a grid.xml file", None))
        self.tBtnOpenInput.setText(_translate("ShakemapImporterBase", "...", None))
        self.groupBox_3.setTitle(_translate("ShakemapImporterBase", "Output", None))
        self.tBtnOpenOutput.setText(_translate("ShakemapImporterBase", "...", None))
        self.label_2.setText(_translate("ShakemapImporterBase", "The output will be a .tif raster file", None))
        self.cBDefaultOutputLocation.setText(_translate("ShakemapImporterBase", "Same directory as input file", None))
        self.cBLoadLayer.setText(_translate("ShakemapImporterBase", "Add output layer to QGIS project", None))
        self.groupBox.setTitle(_translate("ShakemapImporterBase", "Algorithm", None))
        self.radNearest.setText(_translate("ShakemapImporterBase", "Nearest neighbour", None))
        self.radInvDist.setText(_translate("ShakemapImporterBase", "Inverse Distance", None))

from PyQt4 import QtWebKit
