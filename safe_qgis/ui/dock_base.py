# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dock_base.ui'
#
# Created: Fri Feb 21 11:13:27 2014
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_DockBase(object):
    def setupUi(self, DockBase):
        DockBase.setObjectName(_fromUtf8("DockBase"))
        DockBase.resize(393, 547)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/inasafe/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DockBase.setWindowIcon(icon)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.pbnShowQuestion = QtGui.QPushButton(self.dockWidgetContents)
        self.pbnShowQuestion.setObjectName(_fromUtf8("pbnShowQuestion"))
        self.gridLayout.addWidget(self.pbnShowQuestion, 0, 0, 1, 1)
        self.grpQuestion = QtGui.QGroupBox(self.dockWidgetContents)
        self.grpQuestion.setObjectName(_fromUtf8("grpQuestion"))
        self.gridLayout_3 = QtGui.QGridLayout(self.grpQuestion)
        self.gridLayout_3.setContentsMargins(0, 6, 0, 0)
        self.gridLayout_3.setVerticalSpacing(1)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_8 = QtGui.QLabel(self.grpQuestion)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_3.addWidget(self.label_8, 4, 0, 1, 1)
        self.cboHazard = QtGui.QComboBox(self.grpQuestion)
        self.cboHazard.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.cboHazard.setObjectName(_fromUtf8("cboHazard"))
        self.gridLayout_3.addWidget(self.cboHazard, 0, 0, 1, 2)
        self.label_2 = QtGui.QLabel(self.grpQuestion)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_3.addWidget(self.label_2, 6, 0, 1, 1)
        self.cboAggregation = QtGui.QComboBox(self.grpQuestion)
        self.cboAggregation.setObjectName(_fromUtf8("cboAggregation"))
        self.gridLayout_3.addWidget(self.cboAggregation, 7, 0, 1, 2)
        self.label_7 = QtGui.QLabel(self.grpQuestion)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_3.addWidget(self.label_7, 1, 0, 1, 1)
        self.cboExposure = QtGui.QComboBox(self.grpQuestion)
        self.cboExposure.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.cboExposure.setObjectName(_fromUtf8("cboExposure"))
        self.gridLayout_3.addWidget(self.cboExposure, 3, 0, 1, 2)
        self.cboFunction = QtGui.QComboBox(self.grpQuestion)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cboFunction.sizePolicy().hasHeightForWidth())
        self.cboFunction.setSizePolicy(sizePolicy)
        self.cboFunction.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.cboFunction.setObjectName(_fromUtf8("cboFunction"))
        self.gridLayout_3.addWidget(self.cboFunction, 5, 0, 1, 1)
        self.toolFunctionOptions = QtGui.QPushButton(self.grpQuestion)
        self.toolFunctionOptions.setObjectName(_fromUtf8("toolFunctionOptions"))
        self.gridLayout_3.addWidget(self.toolFunctionOptions, 5, 1, 1, 1)
        self.gridLayout.addWidget(self.grpQuestion, 1, 0, 1, 1)
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setContentsMargins(3, -1, -1, -1)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.wvResults = MessageViewer(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.wvResults.sizePolicy().hasHeightForWidth())
        self.wvResults.setSizePolicy(sizePolicy)
        self.wvResults.setMinimumSize(QtCore.QSize(0, 50))
        self.wvResults.setProperty("url", QtCore.QUrl(_fromUtf8("about:blank")))
        self.wvResults.setObjectName(_fromUtf8("wvResults"))
        self.verticalLayout_4.addWidget(self.wvResults)
        self.org_logo_placeholder = QtGui.QHBoxLayout()
        self.org_logo_placeholder.setObjectName(_fromUtf8("org_logo_placeholder"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.org_logo_placeholder.addItem(spacerItem)
        self.org_logo = QtGui.QLabel(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.org_logo.sizePolicy().hasHeightForWidth())
        self.org_logo.setSizePolicy(sizePolicy)
        self.org_logo.setMaximumSize(QtCore.QSize(0, 64))
        self.org_logo.setText(_fromUtf8(""))
        self.org_logo.setScaledContents(True)
        self.org_logo.setAlignment(QtCore.Qt.AlignCenter)
        self.org_logo.setObjectName(_fromUtf8("org_logo"))
        self.org_logo_placeholder.addWidget(self.org_logo)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.org_logo_placeholder.addItem(spacerItem1)
        self.verticalLayout_4.addLayout(self.org_logo_placeholder)
        self.gridLayout.addLayout(self.verticalLayout_4, 2, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pbnHelp = QtGui.QPushButton(self.dockWidgetContents)
        self.pbnHelp.setObjectName(_fromUtf8("pbnHelp"))
        self.horizontalLayout.addWidget(self.pbnHelp)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.pbnPrint = QtGui.QPushButton(self.dockWidgetContents)
        self.pbnPrint.setObjectName(_fromUtf8("pbnPrint"))
        self.horizontalLayout.addWidget(self.pbnPrint)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.pbnRunStop = QtGui.QPushButton(self.dockWidgetContents)
        self.pbnRunStop.setObjectName(_fromUtf8("pbnRunStop"))
        self.horizontalLayout.addWidget(self.pbnRunStop)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 1)
        DockBase.setWidget(self.dockWidgetContents)
        self.label_8.setBuddy(self.cboFunction)
        self.label_7.setBuddy(self.cboExposure)

        self.retranslateUi(DockBase)
        QtCore.QObject.connect(self.pbnShowQuestion, QtCore.SIGNAL(_fromUtf8("clicked()")), self.pbnShowQuestion.hide)
        QtCore.QObject.connect(self.pbnShowQuestion, QtCore.SIGNAL(_fromUtf8("clicked()")), self.grpQuestion.show)
        QtCore.QMetaObject.connectSlotsByName(DockBase)
        DockBase.setTabOrder(self.cboHazard, self.cboExposure)
        DockBase.setTabOrder(self.cboExposure, self.cboFunction)
        DockBase.setTabOrder(self.cboFunction, self.pbnRunStop)
        DockBase.setTabOrder(self.pbnRunStop, self.pbnHelp)

    def retranslateUi(self, DockBase):
        DockBase.setWindowTitle(_translate("DockBase", "InaSAFE", None))
        self.pbnShowQuestion.setText(_translate("DockBase", "Show question form", None))
        self.grpQuestion.setTitle(_translate("DockBase", "Question: In the event of", None))
        self.label_8.setText(_translate("DockBase", "&Might", None))
        self.label_2.setText(_translate("DockBase", "Aggregate results by", None))
        self.label_7.setText(_translate("DockBase", "How many", None))
        self.toolFunctionOptions.setText(_translate("DockBase", "Options ...", None))
        self.pbnHelp.setText(_translate("DockBase", "Help", None))
        self.pbnPrint.setText(_translate("DockBase", "Print ...", None))
        self.pbnRunStop.setText(_translate("DockBase", "Run", None))

from ..widgets.message_viewer import MessageViewer
import resources_rc
