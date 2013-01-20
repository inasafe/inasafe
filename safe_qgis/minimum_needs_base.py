# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'minimum_needs_base.ui'
#
# Created: Sun Jan 20 15:39:53 2013
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
        MinimumNeedsBase.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(MinimumNeedsBase)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(MinimumNeedsBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), MinimumNeedsBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), MinimumNeedsBase.reject)
        QtCore.QMetaObject.connectSlotsByName(MinimumNeedsBase)

    def retranslateUi(self, MinimumNeedsBase):
        MinimumNeedsBase.setWindowTitle(QtGui.QApplication.translate("MinimumNeedsBase", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

