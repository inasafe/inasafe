# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file
# 'aggregation_attribute_dialog_base.ui'
#
# Created: Mon Sep 24 13:36:23 2012
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Ui_AggregationAttributeDialogBase(object):
    def setupUi(self, AggregationAttributeDialogBase):
        AggregationAttributeDialogBase.setObjectName(
            _fromUtf8("AggregationAttributeDialogBase"))
        AggregationAttributeDialogBase.resize(425, 101)
        self.verticalLayout = QtGui.QVBoxLayout(AggregationAttributeDialogBase)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(AggregationAttributeDialogBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.cboAggregationAttributes = QtGui.QComboBox(
            AggregationAttributeDialogBase)
        self.cboAggregationAttributes.setObjectName(
            _fromUtf8("cboAggregationAttributes"))
        self.verticalLayout.addWidget(self.cboAggregationAttributes)
        self.buttonBox = QtGui.QDialogButtonBox(AggregationAttributeDialogBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AggregationAttributeDialogBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(
            _fromUtf8("accepted()")), AggregationAttributeDialogBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(
            _fromUtf8("rejected()")), AggregationAttributeDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(AggregationAttributeDialogBase)

    def retranslateUi(self, AggregationAttributeDialogBase):
        AggregationAttributeDialogBase.setWindowTitle(
            QtGui.QApplication.translate("AggregationAttributeDialogBase",
                "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate(
            "AggregationAttributeDialogBase",
            "Which attribute do you want to use as aggregation attribute?",
            None, QtGui.QApplication.UnicodeUTF8))
