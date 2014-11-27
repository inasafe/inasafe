# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'extent_selector_base.ui'
#
# Created: Thu Nov 13 14:29:43 2014
#      by: PyQt4 UI code generator 4.11.2
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
        ExtentSelectorBase.resize(440, 389)
        font = QtGui.QFont()
        font.setPointSize(9)
        ExtentSelectorBase.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/inasafe/icon.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ExtentSelectorBase.setWindowIcon(icon)
        self.gridLayout_2 = QtGui.QGridLayout(ExtentSelectorBase)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.web_view = QtWebKit.QWebView(ExtentSelectorBase)
        self.web_view.setProperty("url", QtCore.QUrl(_fromUtf8("about:blank")))
        self.web_view.setObjectName(_fromUtf8("web_view"))
        self.gridLayout_2.addWidget(self.web_view, 0, 0, 1, 1)
        self.group_box = QtGui.QGroupBox(ExtentSelectorBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.group_box.sizePolicy().hasHeightForWidth())
        self.group_box.setSizePolicy(sizePolicy)
        self.group_box.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.group_box.setFlat(True)
        self.group_box.setObjectName(_fromUtf8("group_box"))
        self.gridLayout = QtGui.QGridLayout(self.group_box)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.y_maximum = QtGui.QDoubleSpinBox(self.group_box)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.y_maximum.setFont(font)
        self.y_maximum.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.y_maximum.setDecimals(7)
        self.y_maximum.setMinimum(-999999999.0)
        self.y_maximum.setMaximum(999999999.0)
        self.y_maximum.setObjectName(_fromUtf8("y_maximum"))
        self.gridLayout.addWidget(self.y_maximum, 0, 1, 1, 1)
        self.x_minimum = QtGui.QDoubleSpinBox(self.group_box)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.x_minimum.setFont(font)
        self.x_minimum.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.x_minimum.setDecimals(7)
        self.x_minimum.setMinimum(-999999999.0)
        self.x_minimum.setMaximum(999999999.0)
        self.x_minimum.setObjectName(_fromUtf8("x_minimum"))
        self.gridLayout.addWidget(self.x_minimum, 1, 0, 1, 1)
        self.capture_button = QtGui.QPushButton(self.group_box)
        self.capture_button.setObjectName(_fromUtf8("capture_button"))
        self.gridLayout.addWidget(self.capture_button, 1, 1, 1, 1)
        self.x_maximum = QtGui.QDoubleSpinBox(self.group_box)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.x_maximum.setFont(font)
        self.x_maximum.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.x_maximum.setDecimals(7)
        self.x_maximum.setMinimum(-999999999.0)
        self.x_maximum.setMaximum(999999999.0)
        self.x_maximum.setObjectName(_fromUtf8("x_maximum"))
        self.gridLayout.addWidget(self.x_maximum, 1, 2, 1, 1)
        self.y_minimum = QtGui.QDoubleSpinBox(self.group_box)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.y_minimum.setFont(font)
        self.y_minimum.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.y_minimum.setDecimals(7)
        self.y_minimum.setMinimum(-999999999.0)
        self.y_minimum.setMaximum(999999999.0)
        self.y_minimum.setObjectName(_fromUtf8("y_minimum"))
        self.gridLayout.addWidget(self.y_minimum, 2, 1, 1, 1)
        self.gridLayout_2.addWidget(self.group_box, 1, 0, 1, 1)
        self.button_box = QtGui.QDialogButtonBox(ExtentSelectorBase)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Reset)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        self.gridLayout_2.addWidget(self.button_box, 2, 0, 1, 1)

        self.retranslateUi(ExtentSelectorBase)
        QtCore.QMetaObject.connectSlotsByName(ExtentSelectorBase)
        ExtentSelectorBase.setTabOrder(self.x_minimum, self.y_maximum)
        ExtentSelectorBase.setTabOrder(self.y_maximum, self.x_maximum)
        ExtentSelectorBase.setTabOrder(self.x_maximum, self.y_minimum)
        ExtentSelectorBase.setTabOrder(self.y_minimum, self.capture_button)
        ExtentSelectorBase.setTabOrder(self.capture_button, self.button_box)

    def retranslateUi(self, ExtentSelectorBase):
        ExtentSelectorBase.setWindowTitle(_translate("ExtentSelectorBase", "InaSAFE Analysis Area", None))
        self.group_box.setTitle(_translate("ExtentSelectorBase", "Bounding box", None))
        self.y_maximum.setPrefix(_translate("ExtentSelectorBase", "North: ", None))
        self.x_minimum.setPrefix(_translate("ExtentSelectorBase", "East: ", None))
        self.capture_button.setText(_translate("ExtentSelectorBase", "Select on map", None))
        self.x_maximum.setPrefix(_translate("ExtentSelectorBase", "West: ", None))
        self.y_minimum.setPrefix(_translate("ExtentSelectorBase", "South: ", None))

from PyQt4 import QtWebKit
import resources_rc
