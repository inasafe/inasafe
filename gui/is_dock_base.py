# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'is_dock_base.ui'
#
# Created: Wed Mar 28 22:17:39 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ISDockBase(object):
    def setupUi(self, ISDockBase):
        ISDockBase.setObjectName(_fromUtf8("ISDockBase"))
        ISDockBase.resize(394, 547)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/inasafe/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ISDockBase.setWindowIcon(icon)
        ISDockBase.setWindowTitle(QtGui.QApplication.translate("ISDockBase", "InaSAFE", None, QtGui.QApplication.UnicodeUTF8))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setContentsMargins(3, 0, 0, 3)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.grpQuestion = QtGui.QGroupBox(self.dockWidgetContents)
        self.grpQuestion.setTitle(QtGui.QApplication.translate("ISDockBase", "Questions", None, QtGui.QApplication.UnicodeUTF8))
        self.grpQuestion.setObjectName(_fromUtf8("grpQuestion"))
        self.gridLayout_3 = QtGui.QGridLayout(self.grpQuestion)
        self.gridLayout_3.setContentsMargins(0, 6, 0, 0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_6 = QtGui.QLabel(self.grpQuestion)
        self.label_6.setText(QtGui.QApplication.translate("ISDockBase", "In the event of", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_3.addWidget(self.label_6, 0, 0, 1, 1)
        self.label_7 = QtGui.QLabel(self.grpQuestion)
        self.label_7.setText(QtGui.QApplication.translate("ISDockBase", "How many", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_3.addWidget(self.label_7, 2, 0, 1, 1)
        self.label_8 = QtGui.QLabel(self.grpQuestion)
        self.label_8.setText(QtGui.QApplication.translate("ISDockBase", "&Might", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_3.addWidget(self.label_8, 5, 0, 1, 1)
        self.cboFunction = QtGui.QComboBox(self.grpQuestion)
        self.cboFunction.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.cboFunction.setObjectName(_fromUtf8("cboFunction"))
        self.gridLayout_3.addWidget(self.cboFunction, 6, 0, 1, 1)
        self.cboExposure = QtGui.QComboBox(self.grpQuestion)
        self.cboExposure.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.cboExposure.setObjectName(_fromUtf8("cboExposure"))
        self.gridLayout_3.addWidget(self.cboExposure, 4, 0, 1, 1)
        self.cboHazard = QtGui.QComboBox(self.grpQuestion)
        self.cboHazard.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.cboHazard.setObjectName(_fromUtf8("cboHazard"))
        self.gridLayout_3.addWidget(self.cboHazard, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.grpQuestion, 0, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox_2.setTitle(QtGui.QApplication.translate("ISDockBase", "Results", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setContentsMargins(0, 3, 3, 3)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.wvResults = QtWebKit.QWebView(self.groupBox_2)
        self.wvResults.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.wvResults.setObjectName(_fromUtf8("wvResults"))
        self.verticalLayout.addWidget(self.wvResults)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_9 = QtGui.QLabel(self.groupBox_2)
        self.label_9.setMinimumSize(QtCore.QSize(64, 64))
        self.label_9.setMaximumSize(QtCore.QSize(64, 64))
        self.label_9.setText(_fromUtf8(""))
        self.label_9.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/inasafe/bnpb_logo_64.png")))
        self.label_9.setScaledContents(True)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.horizontalLayout_2.addWidget(self.label_9)
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setText(QtGui.QApplication.translate("ISDockBase", "Supported by AusAID and World Bank", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_2.addWidget(self.label_4)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pbnHelp = QtGui.QPushButton(self.dockWidgetContents)
        self.pbnHelp.setText(QtGui.QApplication.translate("ISDockBase", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.pbnHelp.setObjectName(_fromUtf8("pbnHelp"))
        self.horizontalLayout.addWidget(self.pbnHelp)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pbnPrint = QtGui.QPushButton(self.dockWidgetContents)
        self.pbnPrint.setText(QtGui.QApplication.translate("ISDockBase", "Print...", None, QtGui.QApplication.UnicodeUTF8))
        self.pbnPrint.setObjectName(_fromUtf8("pbnPrint"))
        self.horizontalLayout.addWidget(self.pbnPrint)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pbnRunStop = QtGui.QPushButton(self.dockWidgetContents)
        self.pbnRunStop.setText(QtGui.QApplication.translate("ISDockBase", "Run", None, QtGui.QApplication.UnicodeUTF8))
        self.pbnRunStop.setObjectName(_fromUtf8("pbnRunStop"))
        self.horizontalLayout.addWidget(self.pbnRunStop)
        self.gridLayout.addLayout(self.horizontalLayout, 4, 0, 1, 1)
        ISDockBase.setWidget(self.dockWidgetContents)
        self.label_6.setBuddy(self.cboHazard)
        self.label_7.setBuddy(self.cboExposure)
        self.label_8.setBuddy(self.cboFunction)

        self.retranslateUi(ISDockBase)
        QtCore.QMetaObject.connectSlotsByName(ISDockBase)
        ISDockBase.setTabOrder(self.cboHazard, self.cboExposure)
        ISDockBase.setTabOrder(self.cboExposure, self.cboFunction)
        ISDockBase.setTabOrder(self.cboFunction, self.wvResults)
        ISDockBase.setTabOrder(self.wvResults, self.pbnRunStop)
        ISDockBase.setTabOrder(self.pbnRunStop, self.pbnHelp)

    def retranslateUi(self, ISDockBase):
        pass

from PyQt4 import QtWebKit
import resources_rc
import resources_rc
