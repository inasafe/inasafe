# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'safe_qgis/ui/impact_report_dialog_base.ui'
#
# Created: Thu Nov 28 10:51:35 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImpactReportDialogBase(object):
    def setupUi(self, ImpactReportDialogBase):
        ImpactReportDialogBase.setObjectName(_fromUtf8("ImpactReportDialogBase"))
        ImpactReportDialogBase.resize(400, 213)
        self.verticalLayout = QtGui.QVBoxLayout(ImpactReportDialogBase)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(ImpactReportDialogBase)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.analysis_extent_radio = QtGui.QRadioButton(self.groupBox)
        self.analysis_extent_radio.setChecked(True)
        self.analysis_extent_radio.setObjectName(_fromUtf8("analysis_extent_radio"))
        self.horizontalLayout.addWidget(self.analysis_extent_radio)
        self.current_extent_radio = QtGui.QRadioButton(self.groupBox)
        self.current_extent_radio.setObjectName(_fromUtf8("current_extent_radio"))
        self.horizontalLayout.addWidget(self.current_extent_radio)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(ImpactReportDialogBase)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.template_path = QtGui.QLineEdit(self.groupBox_2)
        self.template_path.setEnabled(False)
        self.template_path.setObjectName(_fromUtf8("template_path"))
        self.gridLayout.addWidget(self.template_path, 1, 1, 1, 1)
        self.default_template_radio = QtGui.QRadioButton(self.groupBox_2)
        self.default_template_radio.setText(_fromUtf8(""))
        self.default_template_radio.setChecked(True)
        self.default_template_radio.setObjectName(_fromUtf8("default_template_radio"))
        self.gridLayout.addWidget(self.default_template_radio, 0, 0, 1, 1)
        self.template_chooser = QtGui.QToolButton(self.groupBox_2)
        self.template_chooser.setEnabled(False)
        self.template_chooser.setObjectName(_fromUtf8("template_chooser"))
        self.gridLayout.addWidget(self.template_chooser, 1, 2, 1, 1)
        self.template_combo = QtGui.QComboBox(self.groupBox_2)
        self.template_combo.setObjectName(_fromUtf8("template_combo"))
        self.gridLayout.addWidget(self.template_combo, 0, 1, 1, 2)
        self.custom_template_radio = QtGui.QRadioButton(self.groupBox_2)
        self.custom_template_radio.setText(_fromUtf8(""))
        self.custom_template_radio.setObjectName(_fromUtf8("custom_template_radio"))
        self.gridLayout.addWidget(self.custom_template_radio, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.buttonBox = QtGui.QDialogButtonBox(ImpactReportDialogBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ImpactReportDialogBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ImpactReportDialogBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ImpactReportDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(ImpactReportDialogBase)

    def retranslateUi(self, ImpactReportDialogBase):
        ImpactReportDialogBase.setWindowTitle(QtGui.QApplication.translate("ImpactReportDialogBase", "Impact report", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ImpactReportDialogBase", "Area to print", None, QtGui.QApplication.UnicodeUTF8))
        self.analysis_extent_radio.setText(QtGui.QApplication.translate("ImpactReportDialogBase", "Analysis extent", None, QtGui.QApplication.UnicodeUTF8))
        self.current_extent_radio.setText(QtGui.QApplication.translate("ImpactReportDialogBase", "Current extent", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("ImpactReportDialogBase", "Template to use", None, QtGui.QApplication.UnicodeUTF8))
        self.template_chooser.setText(QtGui.QApplication.translate("ImpactReportDialogBase", "...", None, QtGui.QApplication.UnicodeUTF8))
