# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'osm_downloader_base.ui'
#
# Created: Mon Aug 26 12:12:10 2013
#      by: PyQt4 UI code generator 4.10
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

class Ui_OsmDownloaderBase(object):
    def setupUi(self, OsmDownloaderBase):
        OsmDownloaderBase.setObjectName(_fromUtf8("OsmDownloaderBase"))
        OsmDownloaderBase.resize(506, 500)
        self.gridLayout_2 = QtGui.QGridLayout(OsmDownloaderBase)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(OsmDownloaderBase)
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
        self.outputDirectoryLabel = QtGui.QLabel(OsmDownloaderBase)
        self.outputDirectoryLabel.setObjectName(_fromUtf8("outputDirectoryLabel"))
        self.gridLayout_2.addWidget(self.outputDirectoryLabel, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.outDir = QtGui.QLineEdit(OsmDownloaderBase)
        self.outDir.setText(_fromUtf8(""))
        self.outDir.setObjectName(_fromUtf8("outDir"))
        self.horizontalLayout.addWidget(self.outDir)
        self.pBtnDir = QtGui.QToolButton(OsmDownloaderBase)
        self.pBtnDir.setObjectName(_fromUtf8("pBtnDir"))
        self.horizontalLayout.addWidget(self.pBtnDir)
        self.gridLayout_2.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(OsmDownloaderBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 4, 0, 1, 1)
        self.webView = QtWebKit.QWebView(OsmDownloaderBase)
        self.webView.setProperty("url", QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.gridLayout_2.addWidget(self.webView, 0, 0, 1, 1)

        self.retranslateUi(OsmDownloaderBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), OsmDownloaderBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), OsmDownloaderBase.reject)
        QtCore.QMetaObject.connectSlotsByName(OsmDownloaderBase)

    def retranslateUi(self, OsmDownloaderBase):
        OsmDownloaderBase.setWindowTitle(_translate("OsmDownloaderBase", "OSM Downloader", None))
        self.groupBox.setTitle(_translate("OsmDownloaderBase", "Bounding box", None))
        self.label_2.setText(_translate("OsmDownloaderBase", "Minimum latitude", None))
        self.label.setText(_translate("OsmDownloaderBase", "Minimum longitude", None))
        self.label_3.setText(_translate("OsmDownloaderBase", "Maximum longitude", None))
        self.label_4.setText(_translate("OsmDownloaderBase", "Maximum latitude", None))
        self.outputDirectoryLabel.setText(_translate("OsmDownloaderBase", "Output directory", None))
        self.pBtnDir.setText(_translate("OsmDownloaderBase", "...", None))

from PyQt4 import QtWebKit
