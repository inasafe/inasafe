# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'extent_selector_base.ui'
#
# Created: Thu Oct 23 16:21:04 2014
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
        ExtentSelectorBase.resize(443, 275)
        self.gridLayout_3 = QtGui.QGridLayout(ExtentSelectorBase)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label = QtGui.QLabel(ExtentSelectorBase)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.activate_button = QtGui.QPushButton(ExtentSelectorBase)
        self.activate_button.setObjectName(_fromUtf8("activate_button"))
        self.gridLayout_3.addWidget(self.activate_button, 1, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(ExtentSelectorBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_2.addWidget(self.label_6, 1, 0, 1, 1)
        self.y_maximum = QtGui.QLineEdit(self.groupBox)
        self.y_maximum.setObjectName(_fromUtf8("y_maximum"))
        self.gridLayout_2.addWidget(self.y_maximum, 3, 1, 1, 1)
        self.x_maximum = QtGui.QLineEdit(self.groupBox)
        self.x_maximum.setObjectName(_fromUtf8("x_maximum"))
        self.gridLayout_2.addWidget(self.x_maximum, 2, 2, 1, 1)
        self.y_minimum = QtGui.QLineEdit(self.groupBox)
        self.y_minimum.setObjectName(_fromUtf8("y_minimum"))
        self.gridLayout_2.addWidget(self.y_minimum, 1, 1, 1, 1)
        self.x_minimum = QtGui.QLineEdit(self.groupBox)
        self.x_minimum.setObjectName(_fromUtf8("x_minimum"))
        self.gridLayout_2.addWidget(self.x_minimum, 2, 0, 1, 1)
        self.label_7 = QtGui.QLabel(self.groupBox)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_2.addWidget(self.label_7, 0, 1, 1, 1)
        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_2.addWidget(self.label_8, 1, 2, 1, 1)
        self.label_9 = QtGui.QLabel(self.groupBox)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_2.addWidget(self.label_9, 4, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 2, 0, 1, 1)

        self.retranslateUi(ExtentSelectorBase)
        QtCore.QMetaObject.connectSlotsByName(ExtentSelectorBase)

    def retranslateUi(self, ExtentSelectorBase):
        self.label.setText(_translate("ExtentSelectorBase", "Select the extent by dragging a rectangle  on canvas or change the extent coordinates", None))
        self.activate_button.setText(_translate("ExtentSelectorBase", "Re-Enable", None))
        self.groupBox.setTitle(_translate("ExtentSelectorBase", "Bounding box", None))
        self.label_6.setText(_translate("ExtentSelectorBase", "West", None))
        self.label_7.setText(_translate("ExtentSelectorBase", "North", None))
        self.label_8.setText(_translate("ExtentSelectorBase", "East", None))
        self.label_9.setText(_translate("ExtentSelectorBase", "South", None))

