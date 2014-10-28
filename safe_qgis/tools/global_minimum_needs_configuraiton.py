# coding=utf-8
"""
Impact Layer Merge Dialog.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '06/05/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
from collections import OrderedDict
from xml.dom import minidom

#noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore, QtXml
#noinspection PyPackageRequirements
from PyQt4.QtCore import QSettings, pyqtSignature, QUrl
#noinspection PyPackageRequirements
from PyQt4.QtGui import QDialog, QMessageBox, QFileDialog, QDesktopServices
from qgis.core import (
    QgsMapLayerRegistry,
    QgsMapRenderer,
    QgsComposition,
    QgsRectangle,
    QgsAtlasComposition)

from safe_qgis.ui.minimum_needs_configuration import Ui_minimumNeeds
from safe_qgis.exceptions import (
    InvalidLayerError,
    EmptyDirectoryError,
    FileNotFoundError,
    CanceledImportDialogError,
    NoKeywordsFoundError,
    KeywordNotFoundError,
    InvalidParameterError,
    ReportCreationError,
    UnsupportedProviderError)
from safe_qgis.safe_interface import (
    messaging as m,
    styles,
    temp_dir)
from safe_qgis.utilities.defaults import disclaimer
from safe_qgis.utilities.utilities import (
    html_header,
    html_footer,
    html_to_file,
    add_ordered_combo_item)
from safe_qgis.utilities.help import show_context_help
from safe_qgis.utilities.keyword_io import KeywordIO
from PyQt4 import QtCore, QtGui

INFO_STYLE = styles.INFO_STYLE


#noinspection PyArgumentList
class GlobalMinimumNdeedsDialog(QDialog, Ui_minimumNeeds):
    """Tools for merging 2 impact layer based on different exposure."""

    """Dialog class for the InaSAFE global minimum needs configuration.
    """

    def __init__(self, parent=None):
        """Constructor for the minimum needs dialog.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr(
            'InaSAFE Global Minimum Needs Configuration'))
        # self.resourcesListView.
        # help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        # help_button.clicked.connect(self.show_help)
        self.resourceListWidget.setDragDropMode(
            self.resourceListWidget.InternalMove)

        self.populate_resource_list()
        self.load_profiles()
        self.mark_current_profile_as_pending()
        # self.mark_current_profile_as_saved()

    def populate_resource_list(self):
        item = QtGui.QListWidgetItem('20 liters bath water per day')
        self.resourceListWidget.addItem(item)
        self.resourceListWidget.addItem('100 kg of rice per week')
        self.resourceListWidget.addItem('1 potato per week')
        for x in range(50):
            self.resourceListWidget.addItem('%s random per week' % x)

    def load_profiles(self):
        self.profileComboBox.addItem('This is the default profile')
        self.profileComboBox.addItem('A way out wacky profile')

    def change_profile(self):
        self.resourceListWidget.clear()
        self.populate_resource_list()

    def mark_current_profile_as_pending(self):
        index = self.profileComboBox.currentIndex()
        item = self.profileComboBox.model().item(index)
        item.setForeground(QtGui.QColor('red'))

    def mark_current_profile_as_saved(self):
        index = self.profileComboBox.currentIndex()
        item = self.profileComboBox.model().item(index)
        item.setForeground(QtGui.QColor('black'))

    def add_resource(self):
        pass

    def edit_resource(self):
        pass

    def remove_resource(self):
        pass
