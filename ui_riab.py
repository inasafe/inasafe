# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_riab.ui'
#
# Created: Tue Jan 10 09:20:17 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Riab(object):
    def setupUi(self, Riab):
        Riab.setObjectName(_fromUtf8("Riab"))
        Riab.resize(702, 411)
        Riab.setWindowTitle(QtGui.QApplication.translate("Riab", "Riab", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout_4 = QtGui.QGridLayout(Riab)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.splitter = QtGui.QSplitter(Riab)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.groupBox_3 = QtGui.QGroupBox(self.splitter)
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Riab", "Layers", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.lstLayers = QtGui.QListWidget(self.groupBox_3)
        self.lstLayers.setObjectName(_fromUtf8("lstLayers"))
        self.gridLayout_3.addWidget(self.lstLayers, 0, 0, 1, 1)
        self.lblLogo = QtGui.QLabel(self.groupBox_3)
        self.lblLogo.setText(QtGui.QApplication.translate("Riab", "Logo", None, QtGui.QApplication.UnicodeUTF8))
        self.lblLogo.setObjectName(_fromUtf8("lblLogo"))
        self.gridLayout_3.addWidget(self.lblLogo, 1, 0, 1, 1)
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(self.layoutWidget)
        self.groupBox.setTitle(QtGui.QApplication.translate("Riab", "Calculation", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setText(QtGui.QApplication.translate("Riab", "Hazard", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cboHazard = QtGui.QComboBox(self.groupBox)
        self.cboHazard.setObjectName(_fromUtf8("cboHazard"))
        self.cboHazard.addItem(_fromUtf8(""))
        self.cboHazard.setItemText(0, QtGui.QApplication.translate("Riab", "Flood Depth (design) Jakarta", None, QtGui.QApplication.UnicodeUTF8))
        self.cboHazard.addItem(_fromUtf8(""))
        self.cboHazard.setItemText(1, QtGui.QApplication.translate("Riab", "Sumatran Fault Magnitude 7.8 Scenario", None, QtGui.QApplication.UnicodeUTF8))
        self.cboHazard.addItem(_fromUtf8(""))
        self.cboHazard.setItemText(2, QtGui.QApplication.translate("Riab", "Yogyakarta 2006 Earthquake", None, QtGui.QApplication.UnicodeUTF8))
        self.cboHazard.addItem(_fromUtf8(""))
        self.cboHazard.setItemText(3, QtGui.QApplication.translate("Riab", "Padang 2009 Earthquake", None, QtGui.QApplication.UnicodeUTF8))
        self.cboHazard.addItem(_fromUtf8(""))
        self.cboHazard.setItemText(4, QtGui.QApplication.translate("Riab", "Mentawai Magnitude 9.0 Scenario", None, QtGui.QApplication.UnicodeUTF8))
        self.cboHazard.addItem(_fromUtf8(""))
        self.cboHazard.setItemText(5, QtGui.QApplication.translate("Riab", "Indonesian Earthquake Hazard Map", None, QtGui.QApplication.UnicodeUTF8))
        self.cboHazard.addItem(_fromUtf8(""))
        self.cboHazard.setItemText(6, QtGui.QApplication.translate("Riab", "Maumere Tsunami Inundation", None, QtGui.QApplication.UnicodeUTF8))
        self.cboHazard.addItem(_fromUtf8(""))
        self.cboHazard.setItemText(7, QtGui.QApplication.translate("Riab", "Gede VEI4 Scenario", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout.addWidget(self.cboHazard, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setText(QtGui.QApplication.translate("Riab", "Exposure", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.cboExposure = QtGui.QComboBox(self.groupBox)
        self.cboExposure.setObjectName(_fromUtf8("cboExposure"))
        self.cboExposure.addItem(_fromUtf8(""))
        self.cboExposure.setItemText(0, QtGui.QApplication.translate("Riab", "Population Density Estimate (5kmx5km)", None, QtGui.QApplication.UnicodeUTF8))
        self.cboExposure.addItem(_fromUtf8(""))
        self.cboExposure.setItemText(1, QtGui.QApplication.translate("Riab", "OSM Building Footprints 2011-11-10", None, QtGui.QApplication.UnicodeUTF8))
        self.cboExposure.addItem(_fromUtf8(""))
        self.cboExposure.setItemText(2, QtGui.QApplication.translate("Riab", "AIBEP Schools", None, QtGui.QApplication.UnicodeUTF8))
        self.cboExposure.addItem(_fromUtf8(""))
        self.cboExposure.setItemText(3, QtGui.QApplication.translate("Riab", "Indonesia Highway", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout.addWidget(self.cboExposure, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setText(QtGui.QApplication.translate("Riab", "Function", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.cboFunction = QtGui.QComboBox(self.groupBox)
        self.cboFunction.setObjectName(_fromUtf8("cboFunction"))
        self.cboFunction.addItem(_fromUtf8(""))
        self.cboFunction.setItemText(0, QtGui.QApplication.translate("Riab", "Flood Building Impact Function", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout.addWidget(self.cboFunction, 2, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(self.layoutWidget)
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Riab", "Results", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.wvResults = QtWebKit.QWebView(self.groupBox_2)
        self.wvResults.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.wvResults.setObjectName(_fromUtf8("wvResults"))
        self.gridLayout_2.addWidget(self.wvResults, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.gridLayout_4.addWidget(self.splitter, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Riab)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_4.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(Riab)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Riab.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Riab.reject)
        QtCore.QMetaObject.connectSlotsByName(Riab)

    def retranslateUi(self, Riab):
        pass

from PyQt4 import QtWebKit
