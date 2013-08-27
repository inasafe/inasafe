# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'batch_dialog_base.ui'
#
# Created: Mon Aug 26 11:54:08 2013
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

class Ui_BatchDialogBase(object):
    def setupUi(self, BatchDialogBase):
        BatchDialogBase.setObjectName(_fromUtf8("BatchDialogBase"))
        BatchDialogBase.resize(430, 599)
        self.gridLayout_3 = QtGui.QGridLayout(BatchDialogBase)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.groupBox = QtGui.QGroupBox(BatchDialogBase)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.source_directory = QtGui.QLineEdit(self.groupBox)
        self.source_directory.setObjectName(_fromUtf8("source_directory"))
        self.horizontalLayout.addWidget(self.source_directory)
        self.source_directory_chooser = QtGui.QToolButton(self.groupBox)
        self.source_directory_chooser.setObjectName(_fromUtf8("source_directory_chooser"))
        self.horizontalLayout.addWidget(self.source_directory_chooser)
        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(BatchDialogBase)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.table = QtGui.QTableWidget(self.groupBox_2)
        self.table.setObjectName(_fromUtf8("table"))
        self.table.setColumnCount(2)
        self.table.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        self.gridLayout.addWidget(self.table, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(BatchDialogBase)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.scenario_directory_radio = QtGui.QRadioButton(self.groupBox_3)
        self.scenario_directory_radio.setChecked(True)
        self.scenario_directory_radio.setObjectName(_fromUtf8("scenario_directory_radio"))
        self.gridLayout_2.addWidget(self.scenario_directory_radio, 0, 0, 1, 1)
        self.custom_directory_radio = QtGui.QRadioButton(self.groupBox_3)
        self.custom_directory_radio.setObjectName(_fromUtf8("custom_directory_radio"))
        self.gridLayout_2.addWidget(self.custom_directory_radio, 1, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.output_directory = QtGui.QLineEdit(self.groupBox_3)
        self.output_directory.setObjectName(_fromUtf8("output_directory"))
        self.horizontalLayout_2.addWidget(self.output_directory)
        self.output_directory_chooser = QtGui.QToolButton(self.groupBox_3)
        self.output_directory_chooser.setObjectName(_fromUtf8("output_directory_chooser"))
        self.horizontalLayout_2.addWidget(self.output_directory_chooser)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_3, 2, 0, 1, 1)
        self.button_box = QtGui.QDialogButtonBox(BatchDialogBase)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Help)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        self.gridLayout_3.addWidget(self.button_box, 3, 0, 1, 1)

        self.retranslateUi(BatchDialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), BatchDialogBase.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), BatchDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(BatchDialogBase)

    def retranslateUi(self, BatchDialogBase):
        BatchDialogBase.setWindowTitle(_translate("BatchDialogBase", "Batch Runner", None))
        self.groupBox.setTitle(_translate("BatchDialogBase", "Scenario directory", None))
        self.source_directory_chooser.setText(_translate("BatchDialogBase", "...", None))
        self.groupBox_2.setTitle(_translate("BatchDialogBase", "Result table", None))
        item = self.table.horizontalHeaderItem(0)
        item.setText(_translate("BatchDialogBase", "Task", None))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("BatchDialogBase", "Status", None))
        self.groupBox_3.setTitle(_translate("BatchDialogBase", "Output destination", None))
        self.scenario_directory_radio.setText(_translate("BatchDialogBase", "Use scenario directory", None))
        self.custom_directory_radio.setText(_translate("BatchDialogBase", "Choose custom output directory", None))
        self.output_directory_chooser.setText(_translate("BatchDialogBase", "...", None))

