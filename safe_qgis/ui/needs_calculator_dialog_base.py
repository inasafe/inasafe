# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'needs_calculator_dialog_base.ui'
#
# Created: Mon Nov 17 10:30:49 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_NeedsCalculatorDialogBase(object):
    def setupUi(self, NeedsCalculatorDialogBase):
        NeedsCalculatorDialogBase.setObjectName(_fromUtf8("NeedsCalculatorDialogBase"))
        NeedsCalculatorDialogBase.resize(539, 437)
        self.gridLayout = QtGui.QGridLayout(NeedsCalculatorDialogBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.webView = QtWebKit.QWebView(NeedsCalculatorDialogBase)
        self.webView.setProperty("url", QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.gridLayout.addWidget(self.webView, 0, 0, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(NeedsCalculatorDialogBase)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.cboPolygonLayers = QtGui.QComboBox(NeedsCalculatorDialogBase)
        self.cboPolygonLayers.setObjectName(_fromUtf8("cboPolygonLayers"))
        self.gridLayout_2.addWidget(self.cboPolygonLayers, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(NeedsCalculatorDialogBase)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)
        self.cboFields = QtGui.QComboBox(NeedsCalculatorDialogBase)
        self.cboFields.setObjectName(_fromUtf8("cboFields"))
        self.gridLayout_2.addWidget(self.cboFields, 1, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 1, 0, 1, 1)
        self.button_box = QtGui.QDialogButtonBox(NeedsCalculatorDialogBase)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        self.gridLayout.addWidget(self.button_box, 2, 0, 1, 1)

        self.retranslateUi(NeedsCalculatorDialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), NeedsCalculatorDialogBase.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), NeedsCalculatorDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(NeedsCalculatorDialogBase)

    def retranslateUi(self, NeedsCalculatorDialogBase):
        NeedsCalculatorDialogBase.setWindowTitle(_translate("NeedsCalculatorDialogBase", "Minumum Needs Calculator", None))
        self.label.setText(_translate("NeedsCalculatorDialogBase", "Affected people Layer", None))
        self.label_3.setText(_translate("NeedsCalculatorDialogBase", "Affected people field", None))

from PyQt4 import QtWebKit
