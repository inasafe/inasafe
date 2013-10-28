# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Options Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '26/10/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature
from safe_qgis.ui.impact_report_dialog_base import Ui_ImpactReportDialogBase
from safe_qgis.utilities.help import show_context_help


class ImpactReportDialog(QtGui.QDialog, Ui_ImpactReportDialogBase):
    """Impact report dialog for the InaSAFE plugin."""

    def __init__(self, iface, dock=None, parent=None):
        """Constructor for the dialog.

        :param iface: A Quantum GIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param parent: Parent widget of this dialog
        :type parent: QWidget

        :param dock: Optional dock widget instance that we can notify of
            changes to the keywords.
        :type dock: Dock
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        self.dock = dock

        button = self.buttonBox.button(QtGui.QDialogButtonBox.Help)
        button.clicked.connect(self.show_help)

        # Load templates from resources...
        templates_dir = QtCore.QDir(':/plugins/inasafe')
        templates_dir.setFilter(QtCore.QDir.Files | QtCore.QDir.NoSymLinks |
                                QtCore.QDir.NoDotAndDotDot)
        templates_dir.setNameFilters(['*.qpt', '*.QPT'])
        report_files = templates_dir.entryList()
        for f in report_files:
            self.template_combo.addItem(QtCore.QFileInfo(f).baseName(),
                                        ':/plugins/inasafe/' + f)
        #  ...and user directory
        settings = QtCore.QSettings()
        path = settings.value('inasafe/reportTemplatePath', '', type=str)
        if path != '':
            templates_dir = QtCore.QDir(path)
            templates_dir.setFilter(QtCore.QDir.Files |
                                    QtCore.QDir.NoSymLinks |
                                    QtCore.QDir.NoDotAndDotDot)
            templates_dir.setNameFilters(['*.qpt', '*.QPT'])
            report_files = templates_dir.entryList()
            for f in report_files:
                self.template_combo.addItem(QtCore.QFileInfo(f).baseName(),
                                            path + '/' + f)

        self.restore_state()

    def restore_state(self):
        """Reinstate the options based on the user's stored session info.
        """
        settings = QtCore.QSettings()

        flag = bool(settings.value(
            'inasafe/analysisExtentFlag', True, type=bool))
        self.analysis_extent_radio.setChecked(flag)
        self.current_extent_radio.setChecked(not flag)

        flag = bool(settings.value(
            'inasafe/showComposerFlag', True, type=bool))
        self.show_composer_radio.setChecked(flag)
        self.create_pdf_radio.setChecked(not flag)

        path = settings.value('inasafe/lastTemplate', '', type=str)
        self.template_combo.setCurrentIndex(
            self.template_combo.findData(path))
        path = settings.value('inasafe/lastCustomTemplate', '', type=str)
        self.template_path.setText(path)

    def save_state(self):
        """Store the options into the user's stored session info.
        """
        settings = QtCore.QSettings()
        settings.setValue(
            'inasafe/analysisExtentFlag',
            self.analysis_extent_radio.isChecked())
        settings.setValue(
            'inasafe/showComposerFlag',
            self.show_composer_radio.isChecked())
        settings.setValue(
            'inasafe/lastTemplate',
            self.template_combo.itemData(self.template_combo.currentIndex()))
        settings.setValue(
            'inasafe/lastCustomTemplate', self.template_path.text())

    def show_help(self):
        """Show context help for the impact report dialog."""
        show_context_help('impact_report')

    def accept(self):
        """Method invoked when OK button is clicked."""
        self.save_state()
        self.close()

    @pyqtSignature('')  # prevents actions being handled twice
    def on_template_chooser_clicked(self):
        """Auto-connect slot activated when report file tool button is clicked.
        """
        # noinspection PyCallByClass,PyTypeChecker
        file_name = QtGui.QFileDialog.getOpenFileName(
            self,
            self.tr('Select report'),
            '',
            self.tr('QGIS composer templates (*.qpt *.QPT)'))
        self.template_path.setText(file_name)
