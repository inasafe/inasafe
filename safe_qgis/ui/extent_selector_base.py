# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'extent_selector_base.ui'
#
# Created: Mon Oct 27 08:18:35 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_ExtentSelectorBase(object):
    def setupUi(self, ExtentSelectorBase):
        ExtentSelectorBase.setObjectName(_fromUtf8("ExtentSelectorBase"))
        ExtentSelectorBase.resize(626, 45)
        font = QtGui.QFont()
        font.setPointSize(9)
        ExtentSelectorBase.setFont(font)
        self.horizontalLayout = QtGui.QHBoxLayout(ExtentSelectorBase)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.x_minimum = QtGui.QDoubleSpinBox(ExtentSelectorBase)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.x_minimum.setFont(font)
        self.x_minimum.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.x_minimum.setDecimals(7)
        self.x_minimum.setMinimum(-999999999.0)
        self.x_minimum.setMaximum(999999999.0)
        self.x_minimum.setObjectName(_fromUtf8("x_minimum"))
        self.horizontalLayout.addWidget(self.x_minimum)
        self.y_minimum = QtGui.QDoubleSpinBox(ExtentSelectorBase)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.y_minimum.setFont(font)
        self.y_minimum.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.y_minimum.setDecimals(7)
        self.y_minimum.setMinimum(-999999999.0)
        self.y_minimum.setMaximum(999999999.0)
        self.y_minimum.setObjectName(_fromUtf8("y_minimum"))
        self.horizontalLayout.addWidget(self.y_minimum)
        self.x_maximum = QtGui.QDoubleSpinBox(ExtentSelectorBase)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.x_maximum.setFont(font)
        self.x_maximum.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.x_maximum.setDecimals(7)
        self.x_maximum.setMinimum(-999999999.0)
        self.x_maximum.setMaximum(999999999.0)
        self.x_maximum.setObjectName(_fromUtf8("x_maximum"))
        self.horizontalLayout.addWidget(self.x_maximum)
        self.y_maximum = QtGui.QDoubleSpinBox(ExtentSelectorBase)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.y_maximum.setFont(font)
        self.y_maximum.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.y_maximum.setDecimals(7)
        self.y_maximum.setMinimum(-999999999.0)
        self.y_maximum.setMaximum(999999999.0)
        self.y_maximum.setObjectName(_fromUtf8("y_maximum"))
        self.horizontalLayout.addWidget(self.y_maximum)
        self.toolButton = QtGui.QToolButton(ExtentSelectorBase)
        self.toolButton.setObjectName(_fromUtf8("toolButton"))
        self.horizontalLayout.addWidget(self.toolButton)
        self.toolButton_2 = QtGui.QToolButton(ExtentSelectorBase)
        self.toolButton_2.setObjectName(_fromUtf8("toolButton_2"))
        self.horizontalLayout.addWidget(self.toolButton_2)
        self.toolButton_3 = QtGui.QToolButton(ExtentSelectorBase)
        self.toolButton_3.setObjectName(_fromUtf8("toolButton_3"))
        self.horizontalLayout.addWidget(self.toolButton_3)

        self.retranslateUi(ExtentSelectorBase)
        QtCore.QMetaObject.connectSlotsByName(ExtentSelectorBase)

    def retranslateUi(self, ExtentSelectorBase):
        self.x_minimum.setPrefix(_translate("ExtentSelectorBase", "East: ", None))
        self.y_minimum.setPrefix(_translate("ExtentSelectorBase", "North: ", None))
        self.x_maximum.setPrefix(_translate("ExtentSelectorBase", "West: ", None))
        self.y_maximum.setPrefix(_translate("ExtentSelectorBase", "South: ", None))
        self.toolButton.setText(_translate("ExtentSelectorBase", "...", None))
        self.toolButton_2.setText(_translate("ExtentSelectorBase", "...", None))
        self.toolButton_3.setText(_translate("ExtentSelectorBase", "...", None))

