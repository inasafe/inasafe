# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'import_dialog_base.ui'
#
# Created: Mon Jun 24 12:04:58 2013
#      by: PyQt4 UI code generator 4.9
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
        ImportDialogBase.resize(506, 500)
        self.gridLayout_2 = QtGui.QGridLayout(ImportDialogBase)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(ImportDialogBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.minLatitude = QtGui.QLineEdit(self.groupBox)
        self.minLatitude.setObjectName(_fromUtf8("minLatitude"))
        self.gridLayout.addWidget(self.minLatitude, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 2, 1, 1)
        self.minLongitude = QtGui.QLineEdit(self.groupBox)
        self.minLongitude.setObjectName(_fromUtf8("minLongitude"))
        self.gridLayout.addWidget(self.minLongitude, 2, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 2, 1, 1, 1)
        self.maxLongitude = QtGui.QLineEdit(self.groupBox)
        self.maxLongitude.setObjectName(_fromUtf8("maxLongitude"))
        self.gridLayout.addWidget(self.maxLongitude, 2, 2, 1, 1)
        self.maxLatitude = QtGui.QLineEdit(self.groupBox)
        self.maxLatitude.setObjectName(_fromUtf8("maxLatitude"))
        self.gridLayout.addWidget(self.maxLatitude, 3, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 3, 0, 1, 1)
        self.outputDirectoryLabel = QtGui.QLabel(ImportDialogBase)
        self.outputDirectoryLabel.setObjectName(_fromUtf8("outputDirectoryLabel"))
        self.gridLayout_2.addWidget(self.outputDirectoryLabel, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.outDir = QtGui.QLineEdit(ImportDialogBase)
        self.outDir.setText(_fromUtf8(""))
        self.outDir.setObjectName(_fromUtf8("outDir"))
        self.horizontalLayout.addWidget(self.outDir)
        self.pBtnDir = QtGui.QToolButton(ImportDialogBase)
        self.pBtnDir.setObjectName(_fromUtf8("pBtnDir"))
        self.horizontalLayout.addWidget(self.pBtnDir)
        self.gridLayout_2.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ImportDialogBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 4, 0, 1, 1)
        self.webView = QtWebKit.QWebView(ImportDialogBase)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.gridLayout_2.addWidget(self.webView, 0, 0, 1, 1)

        self.retranslateUi(ImportDialogBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ImportDialogBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ImportDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(ImportDialogBase)

    def retranslateUi(self, ImportDialogBase):
        ImportDialogBase.setWindowTitle(QtGui.QApplication.translate("ImportDialogBase", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ImportDialogBase", "Bounding box", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ImportDialogBase", "Minimum latitude", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ImportDialogBase", "Minimum longitude", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ImportDialogBase", "Maximum longitude", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ImportDialogBase", "Maximum latitude", None, QtGui.QApplication.UnicodeUTF8))
        self.outputDirectoryLabel.setText(QtGui.QApplication.translate("ImportDialogBase", "Output directory", None, QtGui.QApplication.UnicodeUTF8))
        self.pBtnDir.setText(QtGui.QApplication.translate("ImportDialogBase", "...", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import QtWebKit
