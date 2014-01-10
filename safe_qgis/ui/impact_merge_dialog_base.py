# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'impact_merge_dialog_base.ui'
#
# Created: Fri Jan 10 09:37:54 2014
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
        ImpactMergeDialogBase.resize(542, 608)
        self.gridLayout = QtGui.QGridLayout(ImpactMergeDialogBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.second_layer_label = QtGui.QLabel(ImpactMergeDialogBase)
        self.second_layer_label.setObjectName(_fromUtf8("second_layer_label"))
        self.gridLayout.addWidget(self.second_layer_label, 4, 0, 1, 1)
        self.aggregation_layer_label = QtGui.QLabel(ImpactMergeDialogBase)
        self.aggregation_layer_label.setObjectName(_fromUtf8("aggregation_layer_label"))
        self.gridLayout.addWidget(self.aggregation_layer_label, 6, 0, 1, 1)
        self.second_layer = QtGui.QComboBox(ImpactMergeDialogBase)
        self.second_layer.setObjectName(_fromUtf8("second_layer"))
        self.gridLayout.addWidget(self.second_layer, 5, 0, 1, 1)
        self.aggregation_layer = QtGui.QComboBox(ImpactMergeDialogBase)
        self.aggregation_layer.setObjectName(_fromUtf8("aggregation_layer"))
        self.gridLayout.addWidget(self.aggregation_layer, 7, 0, 1, 1)
        self.output_directory_label = QtGui.QLabel(ImpactMergeDialogBase)
        self.output_directory_label.setObjectName(_fromUtf8("output_directory_label"))
        self.gridLayout.addWidget(self.output_directory_label, 8, 0, 1, 1)
        self.button_box = QtGui.QDialogButtonBox(ImpactMergeDialogBase)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        self.gridLayout.addWidget(self.button_box, 10, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.output_directory = QtGui.QLineEdit(ImpactMergeDialogBase)
        self.output_directory.setText(_fromUtf8(""))
        self.output_directory.setObjectName(_fromUtf8("output_directory"))
        self.horizontalLayout.addWidget(self.output_directory)
        self.directory_chooser = QtGui.QToolButton(ImpactMergeDialogBase)
        self.directory_chooser.setObjectName(_fromUtf8("directory_chooser"))
        self.horizontalLayout.addWidget(self.directory_chooser)
        self.gridLayout.addLayout(self.horizontalLayout, 9, 0, 1, 1)
        self.first_layer = QtGui.QComboBox(ImpactMergeDialogBase)
        self.first_layer.setObjectName(_fromUtf8("first_layer"))
        self.gridLayout.addWidget(self.first_layer, 3, 0, 1, 1)
        self.web_view = QtWebKit.QWebView(ImpactMergeDialogBase)
        self.web_view.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.web_view.setObjectName(_fromUtf8("web_view"))
        self.gridLayout.addWidget(self.web_view, 0, 0, 1, 1)
        self.first_layer_label = QtGui.QLabel(ImpactMergeDialogBase)
        self.first_layer_label.setObjectName(_fromUtf8("first_layer_label"))
        self.gridLayout.addWidget(self.first_layer_label, 2, 0, 1, 1)
        self.second_layer_label.setBuddy(self.second_layer)
        self.aggregation_layer_label.setBuddy(self.aggregation_layer)
        self.output_directory_label.setBuddy(self.output_directory)
        self.first_layer_label.setBuddy(self.first_layer)

        self.retranslateUi(ImpactMergeDialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), ImpactMergeDialogBase.reject)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), ImpactMergeDialogBase.accept)
        QtCore.QMetaObject.connectSlotsByName(ImpactMergeDialogBase)
        ImpactMergeDialogBase.setTabOrder(self.web_view, self.first_layer)
        ImpactMergeDialogBase.setTabOrder(self.first_layer, self.second_layer)
        ImpactMergeDialogBase.setTabOrder(self.second_layer, self.aggregation_layer)
        ImpactMergeDialogBase.setTabOrder(self.aggregation_layer, self.output_directory)
        ImpactMergeDialogBase.setTabOrder(self.output_directory, self.directory_chooser)
        ImpactMergeDialogBase.setTabOrder(self.directory_chooser, self.button_box)

    def retranslateUi(self, ImpactMergeDialogBase):
        ImpactMergeDialogBase.setWindowTitle(QtGui.QApplication.translate("ImpactMergeDialogBase", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.second_layer_label.setText(QtGui.QApplication.translate("ImpactMergeDialogBase", "&Second impact layer", None, QtGui.QApplication.UnicodeUTF8))
        self.aggregation_layer_label.setText(QtGui.QApplication.translate("ImpactMergeDialogBase", "&Aggregation Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.output_directory_label.setText(QtGui.QApplication.translate("ImpactMergeDialogBase", "&Output directory", None, QtGui.QApplication.UnicodeUTF8))
        self.directory_chooser.setText(QtGui.QApplication.translate("ImpactMergeDialogBase", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.first_layer_label.setText(QtGui.QApplication.translate("ImpactMergeDialogBase", "&First impact layer", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import QtWebKit
