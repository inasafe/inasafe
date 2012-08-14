# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'help_base.ui'
#
# Created: Tue Aug 14 19:12:05 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_HelpBase(object):
    def setupUi(self, HelpBase):
        HelpBase.setObjectName(_fromUtf8("HelpBase"))
        HelpBase.resize(727, 403)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/inasafe/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        HelpBase.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(HelpBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.webView = QtWebKit.QWebView(HelpBase)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.gridLayout.addWidget(self.webView, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(HelpBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(HelpBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), HelpBase.reject)
        QtCore.QMetaObject.connectSlotsByName(HelpBase)

    def retranslateUi(self, HelpBase):
        HelpBase.setWindowTitle(QtGui.QApplication.translate("HelpBase", "InaSAFE Help", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import QtWebKit
import resources_rc
