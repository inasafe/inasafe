# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'impact_merge_dialog_base.ui'
#
# Created: Thu Feb 20 13:24:44 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImpactMergeDialogBase(object):
    def setupUi(self, ImpactMergeDialogBase):
        ImpactMergeDialogBase.setObjectName(_fromUtf8("ImpactMergeDialogBase"))
        ImpactMergeDialogBase.resize(513, 650)
        self.verticalLayout = QtGui.QVBoxLayout(ImpactMergeDialogBase)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.web_view = QtWebKit.QWebView(ImpactMergeDialogBase)
        self.web_view.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.web_view.setObjectName(_fromUtf8("web_view"))
        self.verticalLayout.addWidget(self.web_view)
        self.first_layer_label = QtGui.QLabel(ImpactMergeDialogBase)
        self.first_layer_label.setObjectName(_fromUtf8("first_layer_label"))
        self.verticalLayout.addWidget(self.first_layer_label)
        self.first_layer = QtGui.QComboBox(ImpactMergeDialogBase)
        self.first_layer.setObjectName(_fromUtf8("first_layer"))
        self.verticalLayout.addWidget(self.first_layer)
        self.second_layer_label = QtGui.QLabel(ImpactMergeDialogBase)
        self.second_layer_label.setObjectName(_fromUtf8("second_layer_label"))
        self.verticalLayout.addWidget(self.second_layer_label)
        self.second_layer = QtGui.QComboBox(ImpactMergeDialogBase)
        self.second_layer.setObjectName(_fromUtf8("second_layer"))
        self.verticalLayout.addWidget(self.second_layer)
        self.aggregation_layer_label = QtGui.QLabel(ImpactMergeDialogBase)
        self.aggregation_layer_label.setObjectName(_fromUtf8("aggregation_layer_label"))
        self.verticalLayout.addWidget(self.aggregation_layer_label)
        self.aggregation_layer = QtGui.QComboBox(ImpactMergeDialogBase)
        self.aggregation_layer.setObjectName(_fromUtf8("aggregation_layer"))
        self.verticalLayout.addWidget(self.aggregation_layer)
        self.output_directory_label = QtGui.QLabel(ImpactMergeDialogBase)
        self.output_directory_label.setObjectName(_fromUtf8("output_directory_label"))
        self.verticalLayout.addWidget(self.output_directory_label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.output_directory = QtGui.QLineEdit(ImpactMergeDialogBase)
        self.output_directory.setText(_fromUtf8(""))
        self.output_directory.setObjectName(_fromUtf8("output_directory"))
        self.horizontalLayout.addWidget(self.output_directory)
        self.directory_chooser = QtGui.QToolButton(ImpactMergeDialogBase)
        self.directory_chooser.setObjectName(_fromUtf8("directory_chooser"))
        self.horizontalLayout.addWidget(self.directory_chooser)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.report_template_checkbox = QtGui.QCheckBox(ImpactMergeDialogBase)
        self.report_template_checkbox.setObjectName(_fromUtf8("report_template_checkbox"))
        self.verticalLayout.addWidget(self.report_template_checkbox)
        self.splitter = QtGui.QSplitter(ImpactMergeDialogBase)
        self.splitter.setEnabled(False)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.report_template_le = QtGui.QLineEdit(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.report_template_le.sizePolicy().hasHeightForWidth())
        self.report_template_le.setSizePolicy(sizePolicy)
        self.report_template_le.setText(_fromUtf8(""))
        self.report_template_le.setObjectName(_fromUtf8("report_template_le"))
        self.report_template_chooser = QtGui.QToolButton(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.report_template_chooser.sizePolicy().hasHeightForWidth())
        self.report_template_chooser.setSizePolicy(sizePolicy)
        self.report_template_chooser.setObjectName(_fromUtf8("report_template_chooser"))
        self.verticalLayout.addWidget(self.splitter)
        self.button_box = QtGui.QDialogButtonBox(ImpactMergeDialogBase)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        self.verticalLayout.addWidget(self.button_box)
        self.first_layer_label.setBuddy(self.first_layer)
        self.second_layer_label.setBuddy(self.second_layer)
        self.aggregation_layer_label.setBuddy(self.aggregation_layer)
        self.output_directory_label.setBuddy(self.output_directory)

        self.retranslateUi(ImpactMergeDialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), ImpactMergeDialogBase.reject)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), ImpactMergeDialogBase.accept)
        QtCore.QObject.connect(self.report_template_checkbox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.splitter.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ImpactMergeDialogBase)
        ImpactMergeDialogBase.setTabOrder(self.web_view, self.first_layer)
        ImpactMergeDialogBase.setTabOrder(self.first_layer, self.second_layer)
        ImpactMergeDialogBase.setTabOrder(self.second_layer, self.aggregation_layer)
        ImpactMergeDialogBase.setTabOrder(self.aggregation_layer, self.output_directory)
        ImpactMergeDialogBase.setTabOrder(self.output_directory, self.directory_chooser)
        ImpactMergeDialogBase.setTabOrder(self.directory_chooser, self.button_box)

    def retranslateUi(self, ImpactMergeDialogBase):
        ImpactMergeDialogBase.setWindowTitle(QtGui.QApplication.translate("ImpactMergeDialogBase", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.first_layer_label.setText(QtGui.QApplication.translate("ImpactMergeDialogBase", "&First impact layer", None, QtGui.QApplication.UnicodeUTF8))
        self.second_layer_label.setText(QtGui.QApplication.translate("ImpactMergeDialogBase", "&Second impact layer", None, QtGui.QApplication.UnicodeUTF8))
        self.aggregation_layer_label.setText(QtGui.QApplication.translate("ImpactMergeDialogBase", "&Aggregation Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.output_directory_label.setText(QtGui.QApplication.translate("ImpactMergeDialogBase", "&Output directory", None, QtGui.QApplication.UnicodeUTF8))
        self.directory_chooser.setText(QtGui.QApplication.translate("ImpactMergeDialogBase", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.report_template_checkbox.setText(QtGui.QApplication.translate("ImpactMergeDialogBase", "&Use customized report template", None, QtGui.QApplication.UnicodeUTF8))
        self.report_template_chooser.setText(QtGui.QApplication.translate("ImpactMergeDialogBase", "...", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import QtWebKit
