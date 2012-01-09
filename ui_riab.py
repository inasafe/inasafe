# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_riab.ui'
#
# Created: Mon Jan  9 16:46:11 2012
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
        Riab.resize(400, 300)
        Riab.setWindowTitle(QtGui.QApplication.translate("Riab", "Riab", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonBox = QtGui.QDialogButtonBox(Riab)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(Riab)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Riab.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Riab.reject)
        QtCore.QMetaObject.connectSlotsByName(Riab)

    def retranslateUi(self, Riab):
        pass

