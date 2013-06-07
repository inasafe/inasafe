# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'import_dialog_base.ui'
#
# Created: Fri Jun  7 09:18:55 2013
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

class Ui_ImportDialogBase(object):
    def setupUi(self, ImportDialogBase):
        ImportDialogBase.setObjectName(_fromUtf8("ImportDialogBase"))
        ImportDialogBase.resize(683, 502)
        self.gridLayout = QtGui.QGridLayout(ImportDialogBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gbxMap = QtGui.QGroupBox(ImportDialogBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gbxMap.sizePolicy().hasHeightForWidth())
        self.gbxMap.setSizePolicy(sizePolicy)
        self.gbxMap.setMinimumSize(QtCore.QSize(400, 300))
        self.gbxMap.setObjectName(_fromUtf8("gbxMap"))
        self.map = QtGui.QWidget(self.gbxMap)
        self.map.setGeometry(QtCore.QRect(10, 20, 381, 261))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.map.sizePolicy().hasHeightForWidth())
        self.map.setSizePolicy(sizePolicy)
        self.map.setObjectName(_fromUtf8("map"))
        self.gridLayout.addWidget(self.gbxMap, 0, 0, 1, 2)
        self.groupBox = QtGui.QGroupBox(ImportDialogBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(256, 300))
        self.groupBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.minLongitude = QtGui.QLineEdit(self.groupBox)
        self.minLongitude.setObjectName(_fromUtf8("minLongitude"))
        self.verticalLayout.addWidget(self.minLongitude)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.minLatitude = QtGui.QLineEdit(self.groupBox)
        self.minLatitude.setObjectName(_fromUtf8("minLatitude"))
        self.verticalLayout.addWidget(self.minLatitude)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.maxLongitude = QtGui.QLineEdit(self.groupBox)
        self.maxLongitude.setObjectName(_fromUtf8("maxLongitude"))
        self.verticalLayout.addWidget(self.maxLongitude)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.maxLatitude = QtGui.QLineEdit(self.groupBox)
        self.maxLatitude.setObjectName(_fromUtf8("maxLatitude"))
        self.verticalLayout.addWidget(self.maxLatitude)
        self.gridLayout.addWidget(self.groupBox, 0, 2, 1, 1)
        self.gbxOptions = QtGui.QGroupBox(ImportDialogBase)
        self.gbxOptions.setObjectName(_fromUtf8("gbxOptions"))
        self.formLayout = QtGui.QFormLayout(self.gbxOptions)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.regionLabel = QtGui.QLabel(self.gbxOptions)
        self.regionLabel.setObjectName(_fromUtf8("regionLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.regionLabel)
        self.cbxRegion = QtGui.QComboBox(self.gbxOptions)
        self.cbxRegion.setObjectName(_fromUtf8("cbxRegion"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.cbxRegion)
        self.presetLabel = QtGui.QLabel(self.gbxOptions)
        self.presetLabel.setObjectName(_fromUtf8("presetLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.presetLabel)
        self.cbxPreset = QtGui.QComboBox(self.gbxOptions)
        self.cbxPreset.setObjectName(_fromUtf8("cbxPreset"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.cbxPreset)
        self.outputDirectoryLabel = QtGui.QLabel(self.gbxOptions)
        self.outputDirectoryLabel.setObjectName(_fromUtf8("outputDirectoryLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.outputDirectoryLabel)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.outDir = QtGui.QLineEdit(self.gbxOptions)
        self.outDir.setText(_fromUtf8(""))
        self.outDir.setObjectName(_fromUtf8("outDir"))
        self.horizontalLayout.addWidget(self.outDir)
        self.pBtnDir = QtGui.QToolButton(self.gbxOptions)
        self.pBtnDir.setObjectName(_fromUtf8("pBtnDir"))
        self.horizontalLayout.addWidget(self.pBtnDir)
        self.formLayout.setLayout(2, QtGui.QFormLayout.FieldRole, self.horizontalLayout)
        self.gridLayout.addWidget(self.gbxOptions, 1, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ImportDialogBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 3)

        self.retranslateUi(ImportDialogBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ImportDialogBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ImportDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(ImportDialogBase)

    def retranslateUi(self, ImportDialogBase):
        ImportDialogBase.setWindowTitle(_translate("ImportDialogBase", "Dialog", None))
        self.gbxMap.setTitle(_translate("ImportDialogBase", "Map", None))
        self.groupBox.setTitle(_translate("ImportDialogBase", "Bounding box", None))
        self.label.setText(_translate("ImportDialogBase", "Minimum Longitude", None))
        self.label_2.setText(_translate("ImportDialogBase", "Minimum latitude", None))
        self.label_3.setText(_translate("ImportDialogBase", "Maximum longitude", None))
        self.label_4.setText(_translate("ImportDialogBase", "Maximum latitude", None))
        self.gbxOptions.setTitle(_translate("ImportDialogBase", "Options", None))
        self.regionLabel.setText(_translate("ImportDialogBase", "Region", None))
        self.presetLabel.setText(_translate("ImportDialogBase", "Preset", None))
        self.outputDirectoryLabel.setText(_translate("ImportDialogBase", "Output Directory", None))
        self.pBtnDir.setText(_translate("ImportDialogBase", "...", None))

