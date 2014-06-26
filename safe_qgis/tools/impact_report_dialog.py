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

        # additional buttons
        self.button_save_pdf = QtGui.QPushButton(self.tr('Open PDF'))
        self.button_save_pdf.setObjectName('button_save_pdf')
        self.button_save_pdf.setToolTip(self.tr(
            'Write report to PDF and open it in default viewer'))
        self.buttonBox.addButton(
            self.button_save_pdf, QtGui.QDialogButtonBox.ActionRole)

        self.button_open_composer = QtGui.QPushButton(self.tr('Open composer'))
        self.button_open_composer.setObjectName('button_open_composer')
        self.button_open_composer.setToolTip(
            self.tr('Prepare report and open it in QGIS composer'))
        self.buttonBox.addButton(
            self.button_open_composer,
            QtGui.QDialogButtonBox.ActionRole)

        self.button_save_pdf.clicked.connect(self.accept)
        self.button_open_composer.clicked.connect(self.accept)

        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        self.dock = dock

        self.create_pdf = False

        self.default_template_radio.toggled.connect(
            self.toggle_template_selectors)

        button = self.buttonBox.button(QtGui.QDialogButtonBox.Help)
        button.clicked.connect(self.show_help)

        # Load templates from resources...
        templates_dir = QtCore.QDir(':/plugins/inasafe')
        templates_dir.setFilter(
            QtCore.QDir.Files |
            QtCore.QDir.NoSymLinks |
            QtCore.QDir.NoDotAndDotDot)
        templates_dir.setNameFilters(['*.qpt', '*.QPT'])
        report_files = templates_dir.entryList()
        for f in report_files:
            self.template_combo.addItem(
                QtCore.QFileInfo(f).baseName(), ':/plugins/inasafe/' + f)
        #  ...and user directory
        settings = QtCore.QSettings()
        path = settings.value('inasafe/reportTemplatePath', '', type=str)
        if path != '':
            templates_dir = QtCore.QDir(path)
            templates_dir.setFilter(
                QtCore.QDir.Files |
                QtCore.QDir.NoSymLinks |
                QtCore.QDir.NoDotAndDotDot)
            templates_dir.setNameFilters(['*.qpt', '*.QPT'])
            report_files = templates_dir.entryList()
            for f in report_files:
                self.template_combo.addItem(
                    QtCore.QFileInfo(f).baseName(), path + '/' + f)

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
            'inasafe/useDefaultTemplates', True, type=bool))
        self.default_template_radio.setChecked(flag)
        self.custom_template_radio.setChecked(not flag)

        try:
            path = settings.value(
                'inasafe/lastTemplate',
                ':/plugins/inasafe/inasafe-portrait-a4.qpt',
                type=str)
            self.template_combo.setCurrentIndex(
                self.template_combo.findData(path))
        except TypeError:
            self.template_combo.setCurrentIndex(2)

        try:
            path = settings.value('inasafe/lastCustomTemplate', '', type=str)
        except TypeError:
            path = ''
        self.template_path.setText(path)

    def save_state(self):
        """Store the options into the user's stored session info.
        """
        settings = QtCore.QSettings()
        settings.setValue(
            'inasafe/analysisExtentFlag',
            self.analysis_extent_radio.isChecked())
        settings.setValue(
            'inasafe/useDefaultTemplates',
            self.default_template_radio.isChecked())
        settings.setValue(
            'inasafe/lastTemplate',
            self.template_combo.itemData(self.template_combo.currentIndex()))
        settings.setValue(
            'inasafe/lastCustomTemplate', self.template_path.text())

    def show_help(self):
        """Show context help for the impact report dialog."""
        show_context_help('reports')

    def accept(self):
        """Method invoked when OK button is clicked."""
        self.save_state()
        sender_name = self.sender().objectName()
        if sender_name == 'button_save_pdf':
            self.create_pdf = True
        else:
            self.create_pdf = False
        QtGui.QDialog.accept(self)

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

    def toggle_template_selectors(self, checked):
        if checked:
            self.template_combo.setEnabled(True)
            self.template_path.setEnabled(False)
            self.template_chooser.setEnabled(False)
        else:
            self.template_combo.setEnabled(False)
            self.template_path.setEnabled(True)
            self.template_chooser.setEnabled(True)
