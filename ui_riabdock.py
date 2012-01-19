# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_riabdock.ui'
#
# Created: Thu Jan 19 03:38:40 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RiabDock(object):
    def setupUi(self, RiabDock):
        RiabDock.setObjectName(_fromUtf8("RiabDock"))
        RiabDock.resize(394, 547)
        RiabDock.setWindowTitle(QtGui.QApplication.translate("RiabDock", "Risk-In-A-Box", None, QtGui.QApplication.UnicodeUTF8))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox.setTitle(QtGui.QApplication.translate("RiabDock", "Question", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setText(QtGui.QApplication.translate("RiabDock", "In the event of", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_3.addWidget(self.label_6, 0, 0, 1, 1)
        self.label_7 = QtGui.QLabel(self.groupBox)
        self.label_7.setText(QtGui.QApplication.translate("RiabDock", "How many", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_3.addWidget(self.label_7, 2, 0, 1, 1)
        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setText(QtGui.QApplication.translate("RiabDock", "&Will", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_3.addWidget(self.label_8, 5, 0, 1, 1)
        self.cboFunction = QtGui.QComboBox(self.groupBox)
        self.cboFunction.setObjectName(_fromUtf8("cboFunction"))
        self.gridLayout_3.addWidget(self.cboFunction, 6, 0, 1, 1)
        self.cboExposure = QtGui.QComboBox(self.groupBox)
        self.cboExposure.setObjectName(_fromUtf8("cboExposure"))
        self.gridLayout_3.addWidget(self.cboExposure, 4, 0, 1, 1)
        self.cboHazard = QtGui.QComboBox(self.groupBox)
        self.cboHazard.setObjectName(_fromUtf8("cboHazard"))
        self.gridLayout_3.addWidget(self.cboHazard, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.label_9 = QtGui.QLabel(self.dockWidgetContents)
        self.label_9.setText(_fromUtf8(""))
        self.label_9.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/riab/bnpb_logo.png")))
        self.label_9.setScaledContents(False)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout.addWidget(self.label_9, 2, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.dockWidgetContents)
        self.label_4.setText(QtGui.QApplication.translate("RiabDock", "Supported by AusAID and the World Bank", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox_2.setTitle(QtGui.QApplication.translate("RiabDock", "Results", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.wvResults = QtWebKit.QWebView(self.groupBox_2)
        self.wvResults.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.wvResults.setObjectName(_fromUtf8("wvResults"))
        self.gridLayout_2.addWidget(self.wvResults, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1, 1)
        RiabDock.setWidget(self.dockWidgetContents)
        self.label_6.setBuddy(self.cboHazard)
        self.label_7.setBuddy(self.cboExposure)
        self.label_8.setBuddy(self.cboFunction)

        self.retranslateUi(RiabDock)
        QtCore.QMetaObject.connectSlotsByName(RiabDock)

    def retranslateUi(self, RiabDock):
        pass

from PyQt4 import QtWebKit
import resources_rc
import resources_rc
