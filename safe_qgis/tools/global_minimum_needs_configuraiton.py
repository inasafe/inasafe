# coding=utf-8
"""
Impact Layer Merge Dialog.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'Christian Christelis christian@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '27/10/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


import sys

from PyQt4.QtGui import QApplication, QWidget, QGridLayout
from third_party.parameters.float_parameter import FloatParameter
from third_party.parameters.integer_parameter import IntegerParameter
from third_party.parameters.qt_widgets.parameter_container import (
    ParameterContainer)
from third_party.parameters.string_parameter import StringParameter

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
        self.parameter_container = None
        self.resourceListWidget.setDragDropMode(
            self.resourceListWidget.InternalMove)
        self.removeButton.clicked.connect(self.remove_resource)
        self.addButton.clicked.connect(self.add_new_resource)
        self.editButton.clicked.connect(self.edit_resource)
        self.discardButton.clicked.connect(self.discard_changes)
        self.acceptButton.clicked.connect(self.accept_changes)

        self.populate_resource_list()
        self.load_profiles()
        # self.add_resource()
        self.setting_up_resource_parameters()
        # self.mark_current_profile_as_saved()

    def populate_resource_list(self):
        self.add_resource({
            'Readable sentence': 'We need water measured in {{ Unit }}!',
            'Unit': 'liter'})

    def add_resource(self, resource):
        sentence = resource['Readable sentence'].split('{{')
        updated_sentence = sentence[0].rstrip()
        for part in sentence[1:]:
            replace, keep = part.split('}}')
            replace = replace.strip()
            updated_sentence = "%s %s%s" % (
                updated_sentence,
                resource[replace],
                keep
            )
        item = QtGui.QListWidgetItem(updated_sentence)
        item.resource_full = resource
        self.resourceListWidget.addItem(item)

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

    def add_new_resource(self):
        self.setting_up_resource_parameters()
        self.stackedWidget.setCurrentIndex(1)

    def edit_resource(self):
        self.setting_up_resource_parameters()
        # self.populate resource
        self.stackedWidget.setCurrentIndex(1)

    def resource_dismiss(self):
        self.stackedWidget.setCurrentIndex(0)

    def resource_accept(self):

        self.stackedWidget.setCurrentIndex(0)

    def setting_up_resource_parameters(self):
        name_parameter = StringParameter('UUID-1')
        name_parameter.name = 'Resource name'
        name_parameter.help_text = (
            'Name of the resource that will be provided '
            'as part of minimum needs. '
            'e.g. Rice, Water etc.')
        name_parameter.description = (
            'A <b>resource</b> is something that you provide to displaced '
            'persons in the event of a disaster. The resource will be made '
            'available at IDP camps and may need to be stockpiled by '
            'contingency planners in their preparations for a disaster.')
        name_parameter.is_required = True
        name_parameter.value = ''

        description_parameter = StringParameter('UUID-2')
        description_parameter.name = 'Resource description'
        description_parameter.help_text = (
            'Description of the resource that will be provided as part of '
            'minimum needs.')
        description_parameter.description = (
            'This gives a detailed description of what the resource is and ')
        description_parameter.is_required = True
        description_parameter.value = ''

        unit_parameter = StringParameter('UUID-3')
        unit_parameter.name = 'Unit'
        unit_parameter.help_text = (
            'Single unit for the resources spelled out. e.g. litre, '
            'kilogram etc.')
        unit_parameter.description = (
            'A <b>unit</b> is the basic measurement unit used for computing '
            'the allowance per individual. For example when planning water '
            'rations the unit would be single litre.')
        unit_parameter.is_required = True
        unit_parameter.value = ''

        units_parameter = StringParameter('UUID-4')
        units_parameter.name = 'Units'
        units_parameter.help_text = (
            'Multiple units for the resources spelled out. e.g. litres, '
            'kilogram etc.')
        units_parameter.description = (
            '<b>Units</b> are the basic measurement used for computing the '
            'allowance per individual. For example when planning water rations '
            'the units would be litres.')
        units_parameter.is_required = True
        units_parameter.value = ''

        unit_abbreviation_parameter = StringParameter('UUID-5')
        unit_abbreviation_parameter.name = 'Unit abbreviation'
        unit_abbreviation_parameter.help_text = (
            'Abbreviations of unit for the resources. e.g. l, kg etc.')
        unit_abbreviation_parameter.description = (
            "A <b>unti abbreviation</b> is the basic measurement unit's "
            "shortened. For example when planning water rations "
            "the units would be l.")
        unit_abbreviation_parameter.is_required = True
        unit_abbreviation_parameter.value = ''

        minimum_parameter = FloatParameter('UUID-6')
        minimum_parameter.name = 'Minimum allowed'
        minimum_parameter.is_required = True
        minimum_parameter.precision = 2
        minimum_parameter.minimum_allowed_value = -99999.0
        minimum_parameter.maximum_allowed_value = 99999.0
        minimum_parameter.help_text = (
            'The minimum allowable quantity per person. ')
        minimum_parameter.description = (
            'The <b>minimum</b> is the minimum allowed quantity of the '
            'resource per person. For example you may dictate that the water '
            'ration per person per day should never be allowed to be less than '
            '0.5l. This is enforced when tweaking a minimum needs set before '
            'an impact evaluation')
        minimum_parameter.value = 0.00

        maximum_parameter = FloatParameter('UUID-7')
        maximum_parameter.name = 'Maximum allowed'
        maximum_parameter.is_required = True
        maximum_parameter.precision = 2
        maximum_parameter.minimum_allowed_value = -99999.0
        maximum_parameter.maximum_allowed_value = 99999.0
        maximum_parameter.help_text = (
            'The maximum allowable quantity per person. ')
        maximum_parameter.description = (
            'The <b>maximum</b> is the maximum allowed quantity of the '
            'resource per person. For example you may dictate that the water '
            'ration per person per day should never be allowed to be more than '
            '50l. This is enforced when tweaking a minimum needs set before '
            'an impact evaluation.')
        maximum_parameter.value = 100.0

        default_parameter = FloatParameter('UUID-8')
        default_parameter.name = 'Default'
        default_parameter.is_required = True
        default_parameter.precision = 2
        default_parameter.minimum_allowed_value = -99999.0
        default_parameter.default_allowed_value = 99999.0
        default_parameter.help_text = (
            'The default allowable quantity per person. ')
        default_parameter.description = (
            "The <b>default</b> is the default allowed quantity of the "
            "resource per person. For example you may indicate that the water "
            "ration per person per day should be 25l.")
        default_parameter.value = 10.0

        frequency_parameter = StringParameter('UUID-9')
        frequency_parameter.name = 'Frequency'
        frequency_parameter.help_text = (
            "The frequency that this resource needs to be provided to a "
            "displaced person. e.g. weekly, daily, once etc.")
        frequency_parameter.description = (
            "The <b>frequency</b> informs the aid worker how regularly this "
            "resource needs to be provided to the displaced person.")
        frequency_parameter.is_required = True
        frequency_parameter.value = 'weekly'

        sentence_parameter = StringParameter('UUID-10')
        sentence_parameter.name = 'Readable sentence'
        sentence_parameter.help_text = (
            'A readable presentation of the resource.')
        sentence_parameter.description = (
            "A <b>readable sentence</b> is a presentation of the resource "
            "that displays all pertinent information. If you are unsure then "
            "use the default. Properties should be included using double "
            "curly brackets '{{' '}}'. Including the resource name would be "
            "achieved by including e.g. {{ Resource name }}")
        sentence_parameter.is_required = True
        sentence_parameter.value = (
            "A displaced person should be provided with "
            "{{ Default }} {{ Unit }}\{{ Units }}{{ Unit  }} of "
            "{{ Resource name }}. Though no less than {{ Minimum allowed }} "
            "and no more than {{ Maximum allowed }}. This should be provided "
            "{{ Frequency }}.")

        parameters = [
            name_parameter,
            description_parameter,
            unit_parameter,
            units_parameter,
            unit_abbreviation_parameter,
            default_parameter,
            minimum_parameter,
            maximum_parameter,
            frequency_parameter,
            sentence_parameter
        ]
        self.parameter_container = ParameterContainer(parameters)

        layout = QGridLayout()
        layout.addWidget(self.parameter_container)
        self.resourceGroupBox.setLayout(layout)

    def remove_resource(self):
        self.mark_current_profile_as_pending()
        for item in self.resourceListWidget.selectedItems():
            self.resourceListWidget.takeItem(self.resourceListWidget.row(item))

    def discard_changes(self):
        self.stackedWidget.setCurrentIndex(0)

    def accept_changes(self):
        from pydev import pydevd  # pylint: disable=F0401

        pydevd.settrace(
            'localhost', port=5678, stdoutToServer=True,
            stderrToServer=True)
        resource = {}
        layout = self.resourceGroupBox.layout()
        print layout
        print dir(layout.widget)
        new_parameters = layout.widget().get_parameters()
        for parameter in new_parameters:
            print parameter.name, parameter.value, parameter._value
            resource[parameter.name] = parameter.value
        self.add_resource(resource)
        self.stackedWidget.setCurrentIndex(0)
