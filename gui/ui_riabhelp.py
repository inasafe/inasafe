# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_riabhelp.ui'
#
# Created: Tue Feb 21 12:34:53 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RiabHelp(object):
    def setupUi(self, RiabHelp):
        RiabHelp.setObjectName(_fromUtf8("RiabHelp"))
        RiabHelp.resize(727, 403)
        RiabHelp.setWindowTitle(QtGui.QApplication.translate("RiabHelp", "Risk In A Box Help", None, QtGui.QApplication.UnicodeUTF8))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/riab/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        RiabHelp.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(RiabHelp)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.webView = QtWebKit.QWebView(RiabHelp)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.gridLayout.addWidget(self.webView, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(RiabHelp)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(RiabHelp)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RiabHelp.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RiabHelp.reject)
        QtCore.QMetaObject.connectSlotsByName(RiabHelp)

    def retranslateUi(self, RiabHelp):
        pass

from PyQt4 import QtWebKit
import resources_rc
