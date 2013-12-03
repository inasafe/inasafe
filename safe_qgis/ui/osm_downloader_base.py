# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'osm_downloader_base.ui'
#
# Created: Fri Nov 22 11:22:32 2013
#      by: PyQt4 UI code generator 4.10.3
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
        self.feature_type = QtGui.QComboBox(OsmDownloaderBase)
        self.feature_type.setObjectName(_fromUtf8("feature_type"))
        self.feature_type.addItem(_fromUtf8(""))
        self.feature_type.addItem(_fromUtf8(""))
        self.feature_type.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.feature_type, 2, 0, 1, 1)
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
        self.min_latitude = QtGui.QLineEdit(self.groupBox)
        self.min_latitude.setObjectName(_fromUtf8("min_latitude"))
        self.gridLayout.addWidget(self.min_latitude, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 2, 1, 1)
        self.min_longitude = QtGui.QLineEdit(self.groupBox)
        self.min_longitude.setObjectName(_fromUtf8("min_longitude"))
        self.gridLayout.addWidget(self.min_longitude, 2, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 2, 1, 1, 1)
        self.max_longitude = QtGui.QLineEdit(self.groupBox)
        self.max_longitude.setObjectName(_fromUtf8("max_longitude"))
        self.gridLayout.addWidget(self.max_longitude, 2, 2, 1, 1)
        self.max_latitude = QtGui.QLineEdit(self.groupBox)
        self.max_latitude.setObjectName(_fromUtf8("max_latitude"))
        self.gridLayout.addWidget(self.max_latitude, 3, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 5, 0, 1, 1)
        self.output_directory_label = QtGui.QLabel(OsmDownloaderBase)
        self.output_directory_label.setObjectName(_fromUtf8("output_directory_label"))
        self.gridLayout_2.addWidget(self.output_directory_label, 3, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.output_directory = QtGui.QLineEdit(OsmDownloaderBase)
        self.output_directory.setText(_fromUtf8(""))
        self.output_directory.setObjectName(_fromUtf8("output_directory"))
        self.horizontalLayout.addWidget(self.output_directory)
        self.directory_button = QtGui.QToolButton(OsmDownloaderBase)
        self.directory_button.setObjectName(_fromUtf8("directory_button"))
        self.horizontalLayout.addWidget(self.directory_button)
        self.gridLayout_2.addLayout(self.horizontalLayout, 4, 0, 1, 1)
        self.button_box = QtGui.QDialogButtonBox(OsmDownloaderBase)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        self.gridLayout_2.addWidget(self.button_box, 6, 0, 1, 1)
        self.web_view = QtWebKit.QWebView(OsmDownloaderBase)
        self.web_view.setProperty("url", QtCore.QUrl(_fromUtf8("about:blank")))
        self.web_view.setObjectName(_fromUtf8("web_view"))
        self.gridLayout_2.addWidget(self.web_view, 0, 0, 1, 1)
        self.feature_type_label = QtGui.QLabel(OsmDownloaderBase)
        self.feature_type_label.setObjectName(_fromUtf8("feature_type_label"))
        self.gridLayout_2.addWidget(self.feature_type_label, 1, 0, 1, 1)

        self.retranslateUi(OsmDownloaderBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), OsmDownloaderBase.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), OsmDownloaderBase.reject)
        QtCore.QMetaObject.connectSlotsByName(OsmDownloaderBase)

    def retranslateUi(self, OsmDownloaderBase):
        OsmDownloaderBase.setWindowTitle(_translate("OsmDownloaderBase", "OSM Downloader", None))
        self.feature_type.setItemText(0, _translate("OsmDownloaderBase", "All", None))
        self.feature_type.setItemText(1, _translate("OsmDownloaderBase", "Buildings", None))
        self.feature_type.setItemText(2, _translate("OsmDownloaderBase", "Roads", None))
        self.groupBox.setTitle(_translate("OsmDownloaderBase", "Bounding box", None))
        self.label_2.setText(_translate("OsmDownloaderBase", "Minimum latitude", None))
        self.label.setText(_translate("OsmDownloaderBase", "Minimum longitude", None))
        self.label_3.setText(_translate("OsmDownloaderBase", "Maximum longitude", None))
        self.label_4.setText(_translate("OsmDownloaderBase", "Maximum latitude", None))
        self.output_directory_label.setText(_translate("OsmDownloaderBase", "Output directory", None))
        self.directory_button.setText(_translate("OsmDownloaderBase", "...", None))
        self.feature_type_label.setText(_translate("OsmDownloaderBase", "Feature Type", None))

from PyQt4 import QtWebKit
