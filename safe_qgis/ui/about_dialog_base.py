# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about_dialog_base.ui'
#
# Created: Fri Feb 28 11:06:03 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_AboutDialogBase(object):
    def setupUi(self, AboutDialogBase):
        AboutDialogBase.setObjectName(_fromUtf8("AboutDialogBase"))
        AboutDialogBase.resize(683, 492)
        self.gridLayout_6 = QtGui.QGridLayout(AboutDialogBase)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.tab_widget = QtGui.QTabWidget(AboutDialogBase)
        self.tab_widget.setObjectName(_fromUtf8("tab_widget"))
        self.about_tab = QtGui.QWidget()
        self.about_tab.setObjectName(_fromUtf8("about_tab"))
        self.gridLayout = QtGui.QGridLayout(self.about_tab)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.about_text = QtGui.QTextEdit(self.about_tab)
        self.about_text.setReadOnly(True)
        self.about_text.setObjectName(_fromUtf8("about_text"))
        self.gridLayout.addWidget(self.about_text, 0, 0, 1, 1)
        self.tab_widget.addTab(self.about_tab, _fromUtf8(""))
        self.getting_started_tab = QtGui.QWidget()
        self.getting_started_tab.setObjectName(_fromUtf8("getting_started_tab"))
        self.gridLayout_2 = QtGui.QGridLayout(self.getting_started_tab)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.getting_started_text = QtGui.QTextEdit(self.getting_started_tab)
        self.getting_started_text.setReadOnly(True)
        self.getting_started_text.setObjectName(_fromUtf8("getting_started_text"))
        self.gridLayout_2.addWidget(self.getting_started_text, 0, 0, 1, 1)
        self.tab_widget.addTab(self.getting_started_tab, _fromUtf8(""))
        self.limitations_tab = QtGui.QWidget()
        self.limitations_tab.setObjectName(_fromUtf8("limitations_tab"))
        self.gridLayout_3 = QtGui.QGridLayout(self.limitations_tab)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.limitations_text = QtGui.QTextEdit(self.limitations_tab)
        self.limitations_text.setReadOnly(True)
        self.limitations_text.setObjectName(_fromUtf8("limitations_text"))
        self.gridLayout_3.addWidget(self.limitations_text, 0, 0, 1, 1)
        self.tab_widget.addTab(self.limitations_tab, _fromUtf8(""))
        self.disclaimer_tab = QtGui.QWidget()
        self.disclaimer_tab.setObjectName(_fromUtf8("disclaimer_tab"))
        self.gridLayout_4 = QtGui.QGridLayout(self.disclaimer_tab)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.disclaimer_text = QtGui.QTextEdit(self.disclaimer_tab)
        self.disclaimer_text.setReadOnly(True)
        self.disclaimer_text.setObjectName(_fromUtf8("disclaimer_text"))
        self.gridLayout_4.addWidget(self.disclaimer_text, 0, 0, 1, 1)
        self.tab_widget.addTab(self.disclaimer_tab, _fromUtf8(""))
        self.supporters_tab = QtGui.QWidget()
        self.supporters_tab.setObjectName(_fromUtf8("supporters_tab"))
        self.gridLayout_5 = QtGui.QGridLayout(self.supporters_tab)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.supporters_text = QtGui.QTextBrowser(self.supporters_tab)
        self.supporters_text.setOpenExternalLinks(True)
        self.supporters_text.setObjectName(_fromUtf8("supporters_text"))
        self.gridLayout_5.addWidget(self.supporters_text, 0, 0, 1, 1)
        self.tab_widget.addTab(self.supporters_tab, _fromUtf8(""))
        self.gridLayout_6.addWidget(self.tab_widget, 0, 0, 1, 3)
        self.label = QtGui.QLabel(AboutDialogBase)
        self.label.setMaximumSize(QtCore.QSize(600, 100))
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/inasafe/supporters.png")))
        self.label.setScaledContents(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_6.addWidget(self.label, 1, 1, 2, 1)
        spacerItem = QtGui.QSpacerItem(11, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem, 1, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(24, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem1, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(AboutDialogBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_6.addWidget(self.buttonBox, 3, 0, 1, 3)

        self.retranslateUi(AboutDialogBase)
        self.tab_widget.setCurrentIndex(4)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AboutDialogBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AboutDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(AboutDialogBase)

    def retranslateUi(self, AboutDialogBase):
        AboutDialogBase.setWindowTitle(QtGui.QApplication.translate("AboutDialogBase", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.about_text.setHtml(QtGui.QApplication.translate("AboutDialogBase", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">InaSAFE is free software that produces realistic natural hazard impact scenarios for better planning, preparedness and response activities. It provides a simple but rigorous way to combine data from scientists, local governments and communities to provide insights into the likely impacts of future disaster events.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Cantarell\'; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">InaSAFE was conceived and initially developed by the Indonesia\'s National Disaster Management Agency (BNPB) and the Australian Government, through the Australia-Indonesia Facility for Disaster Reduction and the World Bank - Global Facility for Disaster Reduction and Recovery (World Bank-GFDRR).</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.about_tab), QtGui.QApplication.translate("AboutDialogBase", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.getting_started_text.setHtml(QtGui.QApplication.translate("AboutDialogBase", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">These are the minimum steps you need to follow in order to use InaSAFE:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Cantarell\'; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">1. Add at least one hazard layer (e.g. earthquake MMI) to QGIS.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">2. Add at least one exposure layer (e.g. structures) to QGIS.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">3. Make sure you have defined keywords for your hazard and exposure layers. You can do this using the keywords icon in the InaSAFE toolbar.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">4. Click on the Run button in the InaSAFE panel.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.getting_started_tab), QtGui.QApplication.translate("AboutDialogBase", "Getting Started", None, QtGui.QApplication.UnicodeUTF8))
        self.limitations_text.setHtml(QtGui.QApplication.translate("AboutDialogBase", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">1. InaSAFE is not a hazard modelling tool.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">2. Polygon area analysis (such as land use) is not yet supported.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">3. Population density data (raster) must be provided in WGS84 geographic coordinates.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">4. Population by administration boundary is not yet supported.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">5. InaSAFE is a Free and Open Source Software (FOSS) project, published under the GPL V3 license. As such you may freely download, share and (if you like) modify the software.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.limitations_tab), QtGui.QApplication.translate("AboutDialogBase", "Limitations", None, QtGui.QApplication.UnicodeUTF8))
        self.disclaimer_text.setHtml(QtGui.QApplication.translate("AboutDialogBase", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">InaSAFE has been jointly developed by Indonesian Government-BNPB, Australian Government-AIFDR and the World Bank-GFDRR. These agencies and the individual software developers of InaSAFE take no responsibility for the correctness of outputs from InaSAFE or decisions derived as a consequence.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.disclaimer_tab), QtGui.QApplication.translate("AboutDialogBase", "Disclaimer", None, QtGui.QApplication.UnicodeUTF8))
        self.supporters_text.setHtml(QtGui.QApplication.translate("AboutDialogBase", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://aifdr.org\"><span style=\" font-family:\'Cantarell\'; font-size:11pt; text-decoration: underline; color:#0000ff;\">Australia-Indonesia Facility for Disaster Reduction</span></a></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://www.gfdrr.org/\"><span style=\" font-family:\'Cantarell\'; font-size:11pt; text-decoration: underline; color:#0000ff;\">World Bank - Global Facility for Disaster Reductions and Recovery</span></a></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://hot.openstreetmap.org/\"><span style=\" font-family:\'Cantarell\'; font-size:11pt; text-decoration: underline; color:#0000ff;\">Humanitarian OpenStreetMap Team</span></a></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://linfiniti.com\"><span style=\" font-family:\'Cantarell\'; font-size:11pt; text-decoration: underline; color:#0000ff;\">Linfiniti Consulting CC.</span></a></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://essc.org.ph/\"><span style=\" font-family:\'Cantarell\'; font-size:11pt; text-decoration: underline; color:#0000ff;\">Environmental Science for Social Change (Philippines)</span></a></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.supporters_tab), QtGui.QApplication.translate("AboutDialogBase", "Supporters", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
