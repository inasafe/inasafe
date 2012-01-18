# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_riab.ui'
#
# Created: Wed Jan 18 09:08:15 2012
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
        Riab.resize(702, 493)
        Riab.setWindowTitle(QtGui.QApplication.translate("Riab", "Riab", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout_3 = QtGui.QGridLayout(Riab)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.groupBox = QtGui.QGroupBox(Riab)
        self.groupBox.setTitle(QtGui.QApplication.translate("Riab", "Question", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setText(QtGui.QApplication.translate("Riab", "In the event of", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cboHazard = QtGui.QComboBox(self.groupBox)
        self.cboHazard.setObjectName(_fromUtf8("cboHazard"))
        self.gridLayout.addWidget(self.cboHazard, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setText(QtGui.QApplication.translate("Riab", "How many", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.cboExposure = QtGui.QComboBox(self.groupBox)
        self.cboExposure.setObjectName(_fromUtf8("cboExposure"))
        self.gridLayout.addWidget(self.cboExposure, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setText(QtGui.QApplication.translate("Riab", "&Will", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.cboFunction = QtGui.QComboBox(self.groupBox)
        self.cboFunction.setObjectName(_fromUtf8("cboFunction"))
        self.gridLayout.addWidget(self.cboFunction, 2, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setText(_fromUtf8(""))
        self.label_5.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/riab/bnpb_logo.png")))
        self.label_5.setScaledContents(False)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 0, 2, 3, 1)
        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(Riab)
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Riab", "Results", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.wvResults = QtWebKit.QWebView(self.groupBox_2)
        self.wvResults.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.wvResults.setObjectName(_fromUtf8("wvResults"))
        self.gridLayout_2.addWidget(self.wvResults, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Riab)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 3, 0, 1, 1)
        self.label_4 = QtGui.QLabel(Riab)
        self.label_4.setText(QtGui.QApplication.translate("Riab", "Supported by AusAID and the World Bank", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_3.addWidget(self.label_4, 2, 0, 1, 1)
        self.label.setBuddy(self.cboHazard)
        self.label_2.setBuddy(self.cboExposure)
        self.label_3.setBuddy(self.cboFunction)

        self.retranslateUi(Riab)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Riab.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Riab.reject)
        QtCore.QMetaObject.connectSlotsByName(Riab)
        Riab.setTabOrder(self.cboHazard, self.cboExposure)
        Riab.setTabOrder(self.cboExposure, self.cboFunction)
        Riab.setTabOrder(self.cboFunction, self.wvResults)
        Riab.setTabOrder(self.wvResults, self.buttonBox)

    def retranslateUi(self, Riab):
        pass

from PyQt4 import QtWebKit
import resources_rc
