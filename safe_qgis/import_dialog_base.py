# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'import_dialog.ui'
#
# Created: Mon Dec  3 15:57:27 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportDialogBase(object):
    def setupUi(self, ImportDialogBase):
        ImportDialogBase.setObjectName(_fromUtf8("ImportDialogBase"))
        ImportDialogBase.resize(614, 427)
        self.buttonBox = QtGui.QDialogButtonBox(ImportDialogBase)
        self.buttonBox.setGeometry(QtCore.QRect(230, 360, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.minLongitude = QtGui.QLineEdit(ImportDialogBase)
        self.minLongitude.setGeometry(QtCore.QRect(170, 70, 113, 22))
        self.minLongitude.setObjectName(_fromUtf8("minLongitude"))
        self.minLatitude = QtGui.QLineEdit(ImportDialogBase)
        self.minLatitude.setGeometry(QtCore.QRect(170, 110, 113, 22))
        self.minLatitude.setObjectName(_fromUtf8("minLatitude"))
        self.maxLongitude = QtGui.QLineEdit(ImportDialogBase)
        self.maxLongitude.setGeometry(QtCore.QRect(170, 150, 113, 22))
        self.maxLongitude.setObjectName(_fromUtf8("maxLongitude"))
        self.maxLatitude = QtGui.QLineEdit(ImportDialogBase)
        self.maxLatitude.setGeometry(QtCore.QRect(170, 190, 113, 22))
        self.maxLatitude.setObjectName(_fromUtf8("maxLatitude"))
        self.label = QtGui.QLabel(ImportDialogBase)
        self.label.setGeometry(QtCore.QRect(40, 70, 111, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(ImportDialogBase)
        self.label_2.setGeometry(QtCore.QRect(40, 110, 101, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(ImportDialogBase)
        self.label_3.setGeometry(QtCore.QRect(40, 160, 101, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(ImportDialogBase)
        self.label_4.setGeometry(QtCore.QRect(40, 190, 91, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))

        self.retranslateUi(ImportDialogBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ImportDialogBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ImportDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(ImportDialogBase)

    def retranslateUi(self, ImportDialogBase):
        ImportDialogBase.setWindowTitle(QtGui.QApplication.translate("ImportDialogBase", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ImportDialogBase", "Min. Longitude", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ImportDialogBase", "Min. Latitude", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ImportDialogBase", "Max. Longitude", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ImportDialogBase", "Max. Latitude", None, QtGui.QApplication.UnicodeUTF8))

