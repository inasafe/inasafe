# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'minimum_needs_base.ui'
#
# Created: Wed Jun 26 13:57:36 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MinimumNeedsBase(object):
    def setupUi(self, MinimumNeedsBase):
        MinimumNeedsBase.setObjectName(_fromUtf8("MinimumNeedsBase"))
        MinimumNeedsBase.resize(539, 437)
        self.gridLayout = QtGui.QGridLayout(MinimumNeedsBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.webView = QtWebKit.QWebView(MinimumNeedsBase)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.gridLayout.addWidget(self.webView, 0, 0, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(MinimumNeedsBase)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.cboPolygonLayers = QtGui.QComboBox(MinimumNeedsBase)
        self.cboPolygonLayers.setObjectName(_fromUtf8("cboPolygonLayers"))
        self.gridLayout_2.addWidget(self.cboPolygonLayers, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(MinimumNeedsBase)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)
        self.cboFields = QtGui.QComboBox(MinimumNeedsBase)
        self.cboFields.setObjectName(_fromUtf8("cboFields"))
        self.gridLayout_2.addWidget(self.cboFields, 1, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(MinimumNeedsBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(MinimumNeedsBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), MinimumNeedsBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), MinimumNeedsBase.reject)
        QtCore.QMetaObject.connectSlotsByName(MinimumNeedsBase)

    def retranslateUi(self, MinimumNeedsBase):
        MinimumNeedsBase.setWindowTitle(QtGui.QApplication.translate("MinimumNeedsBase", "Minumum Needs Calculator", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MinimumNeedsBase", "Affected people Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MinimumNeedsBase", "Affected people field", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import QtWebKit
