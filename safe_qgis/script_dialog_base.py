# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'script_dialog_base.ui'
#
# Created: Tue Feb 26 16:37:15 2013
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ScriptDialogBase(object):
    def setupUi(self, ScriptDialogBase):
        ScriptDialogBase.setObjectName(_fromUtf8("ScriptDialogBase"))
        ScriptDialogBase.resize(515, 661)
        self.gridLayout = QtGui.QGridLayout(ScriptDialogBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.leSourceDir = QtGui.QLineEdit(ScriptDialogBase)
        self.leSourceDir.setEnabled(False)
        self.leSourceDir.setObjectName(_fromUtf8("leSourceDir"))
        self.horizontalLayout_4.addWidget(self.leSourceDir)
        self.tbSourceDir = QtGui.QToolButton(ScriptDialogBase)
        self.tbSourceDir.setObjectName(_fromUtf8("tbSourceDir"))
        self.horizontalLayout_4.addWidget(self.tbSourceDir)
        self.gridLayout.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)
        self.tblScript = QtGui.QTableWidget(ScriptDialogBase)
        self.tblScript.setAlternatingRowColors(False)
        self.tblScript.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblScript.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblScript.setCornerButtonEnabled(False)
        self.tblScript.setObjectName(_fromUtf8("tblScript"))
        self.tblScript.setColumnCount(2)
        self.tblScript.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tblScript.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tblScript.setHorizontalHeaderItem(1, item)
        self.tblScript.horizontalHeader().setDefaultSectionSize(100)
        self.gridLayout.addWidget(self.tblScript, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnRunSelected = QtGui.QPushButton(ScriptDialogBase)
        self.btnRunSelected.setObjectName(_fromUtf8("btnRunSelected"))
        self.horizontalLayout.addWidget(self.btnRunSelected)
        self.pbnRunAll = QtGui.QPushButton(ScriptDialogBase)
        self.pbnRunAll.setObjectName(_fromUtf8("pbnRunAll"))
        self.horizontalLayout.addWidget(self.pbnRunAll)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        self.pbnAdvanced = QtGui.QPushButton(ScriptDialogBase)
        self.pbnAdvanced.setCheckable(True)
        self.pbnAdvanced.setChecked(False)
        self.pbnAdvanced.setObjectName(_fromUtf8("pbnAdvanced"))
        self.gridLayout.addWidget(self.pbnAdvanced, 3, 0, 1, 1)
        self.gboOptions = QtGui.QGroupBox(ScriptDialogBase)
        self.gboOptions.setCheckable(False)
        self.gboOptions.setObjectName(_fromUtf8("gboOptions"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gboOptions)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label = QtGui.QLabel(self.gboOptions)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.sboCount = QtGui.QSpinBox(self.gboOptions)
        self.sboCount.setSuffix(_fromUtf8(""))
        self.sboCount.setPrefix(_fromUtf8(""))
        self.sboCount.setMinimum(1)
        self.sboCount.setObjectName(_fromUtf8("sboCount"))
        self.horizontalLayout_2.addWidget(self.sboCount)
        self.label_2 = QtGui.QLabel(self.gboOptions)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.leBaseDataDir = QtGui.QLineEdit(self.gboOptions)
        self.leBaseDataDir.setObjectName(_fromUtf8("leBaseDataDir"))
        self.horizontalLayout_3.addWidget(self.leBaseDataDir)
        self.tbBaseDataDir = QtGui.QToolButton(self.gboOptions)
        self.tbBaseDataDir.setObjectName(_fromUtf8("tbBaseDataDir"))
        self.horizontalLayout_3.addWidget(self.tbBaseDataDir)
        self.gridLayout_2.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.gboOptions, 4, 0, 1, 1)

        self.retranslateUi(ScriptDialogBase)
        QtCore.QMetaObject.connectSlotsByName(ScriptDialogBase)

    def retranslateUi(self, ScriptDialogBase):
        ScriptDialogBase.setWindowTitle(QtGui.QApplication.translate("ScriptDialogBase", "InaSAFE Batch Runner", None, QtGui.QApplication.UnicodeUTF8))
        self.tbSourceDir.setText(QtGui.QApplication.translate("ScriptDialogBase", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.tblScript.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("ScriptDialogBase", "Task", None, QtGui.QApplication.UnicodeUTF8))
        self.tblScript.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("ScriptDialogBase", "Status", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRunSelected.setText(QtGui.QApplication.translate("ScriptDialogBase", "Run Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.pbnRunAll.setText(QtGui.QApplication.translate("ScriptDialogBase", "Run All", None, QtGui.QApplication.UnicodeUTF8))
        self.pbnAdvanced.setText(QtGui.QApplication.translate("ScriptDialogBase", "Show advanced options", None, QtGui.QApplication.UnicodeUTF8))
        self.gboOptions.setTitle(QtGui.QApplication.translate("ScriptDialogBase", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ScriptDialogBase", "Run selected script ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ScriptDialogBase", "times", None, QtGui.QApplication.UnicodeUTF8))
        self.tbBaseDataDir.setText(QtGui.QApplication.translate("ScriptDialogBase", "...", None, QtGui.QApplication.UnicodeUTF8))

