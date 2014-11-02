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

from PyQt4.QtGui import QWidget, QGridLayout
from third_party.parameters.float_parameter import FloatParameter
from third_party.parameters.qt_widgets.parameter_container import (
    ParameterContainer)
from third_party.parameters.string_parameter import StringParameter

from PyQt4.QtGui import QDialog, QFileDialog

from safe_qgis.ui.minimum_needs_configuration import Ui_minimumNeeds
from safe_qgis.safe_interface import (
    styles)
from PyQt4 import QtGui
from safe_qgis.tools.minimum_needs import QMinimumNeeds
from os.path import expanduser, basename

INFO_STYLE = styles.INFO_STYLE


#noinspection PyArgumentList
# noinspection PyProtectedMember
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
        self.resourceListWidget.setDragDropMode(
            self.resourceListWidget.InternalMove)
        self.removeButton.clicked.connect(self.remove_resource)
        self.addButton.clicked.connect(self.add_new_resource)
        self.editButton.clicked.connect(self.edit_resource)
        self.discardButton.clicked.connect(self.discard_changes)
        self.acceptButton.clicked.connect(self.accept_changes)
        self.exportButton.clicked.connect(self.export_minimum_needs)
        self.importButton.clicked.connect(self.import_minimum_needs)
        self.minimum_needs = QMinimumNeeds()
        self.edit_item = None

        self.saveButton.clicked.connect(self.save_minimum_needs)
        self.saveAsButton.clicked.connect(self.save_minimum_needs_as)
        self.newButton.clicked.connect(self.new_profile)

        self.load_profiles()
        self.clear_resource_list()
        self.populate_resource_list()
        self.set_up_resource_parameters()

        self.profileComboBox.activated.connect(
            self.select_profile)

    def populate_resource_list(self):
        """Populate the list resource list.
        """
        minimum_needs = self.minimum_needs.get_full_needs()
        for full_resource in minimum_needs["resources"]:
            self.add_resource(full_resource)
        self.provenanceLineEdit.setText(minimum_needs["provenance"])

    def clear_resource_list(self):
        """Clear the resource list.
        """
        self.resourceListWidget.clear()

    @staticmethod
    def _format_sentence(sentence, resource):
        """Populate the placeholders in the sentence.

        :param sentence: The sentence with placeholder keywords.
        :type sentence: basestring, str

        :param resource: The resource to be placed into the sentence.
        :type resource: dict

        :returns: The formatted sentence.
        :rtype: basestring
        """
        sentence = sentence.split('{{')
        updated_sentence = sentence[0].rstrip()
        for part in sentence[1:]:
            replace, keep = part.split('}}')
            replace = replace.strip()
            updated_sentence = "%s %s%s" % (
                updated_sentence,
                resource[replace],
                keep
            )
        return updated_sentence

    def add_resource(self, resource):
        """Add a resource to the minimum needs table.

        :param resource: The resource to be added
        :type resource: dict
        """
        updated_sentence = self._format_sentence(
            resource['Readable sentence'], resource)
        if self.edit_item:
            item = self.edit_item
            item.setText(updated_sentence)
            self.edit_item = None
        else:
            item = QtGui.QListWidgetItem(updated_sentence)
        item.resource_full = resource
        self.resourceListWidget.addItem(item)

    def load_profiles(self):
        """Load the profiles into the dropdown list.
        """
        for profile in self.minimum_needs.get_profiles():
            self.profileComboBox.addItem(profile)
        minimum_needs = self.minimum_needs.get_full_needs()
        self.profileComboBox.setCurrentIndex(
            self.profileComboBox.findText(minimum_needs['profile']))

    def select_profile(self, index):
        """Select a given profile by index. (handler)
        :param index: The selected item's index
        :type index: int
        """
        new_profile = self.profileComboBox.itemText(index)
        self.resourceListWidget.clear()
        self.minimum_needs.load_profile(new_profile)
        self.clear_resource_list()
        self.populate_resource_list()
        self.minimum_needs.save()

    def mark_current_profile_as_pending(self):
        """Mark the current profile as pending by colouring the text red.
        """
        index = self.profileComboBox.currentIndex()
        item = self.profileComboBox.model().item(index)
        item.setForeground(QtGui.QColor('red'))

    def mark_current_profile_as_saved(self):
        """Mark the current profile as saved by colouring the text black.
        """
        index = self.profileComboBox.currentIndex()
        item = self.profileComboBox.model().item(index)
        item.setForeground(QtGui.QColor('black'))

    def add_new_resource(self):
        """Handle add new resource requests.
        """
        parameters_widget = [
            self.resourceGroupBox.layout().itemAt(i) for i in
            range(self.resourceGroupBox.layout().count())][0].widget()
        parameter_widgets = [
            parameters_widget.vertical_layout.itemAt(i).widget() for i in
            range(parameters_widget.vertical_layout.count())]
        parameter_widgets[0]._line_edit_input.setText('')
        parameter_widgets[1]._line_edit_input.setText('')
        parameter_widgets[2]._line_edit_input.setText('')
        parameter_widgets[3]._line_edit_input.setText('')
        parameter_widgets[4]._line_edit_input.setText('')
        parameter_widgets[5]._input.setValue(10)
        parameter_widgets[6]._input.setValue(0)
        parameter_widgets[7]._input.setValue(100)
        parameter_widgets[8]._line_edit_input.setText('weekly')
        parameter_widgets[9]._line_edit_input.setText(
            "A displaced person should be provided with "
            "{{ Default }} {{ Unit }}/{{ Units }}/{{ Unit abbreviation }} of "
            "{{ Resource name }}. Though no less than {{ Minimum allowed }} "
            "and no more than {{ Maximum allowed }}. This should be provided "
            "{{ Frequency }}.")
        self.stackedWidget.setCurrentIndex(1)

    def edit_resource(self):
        """Handle edit resource requests.
        """
        self.mark_current_profile_as_pending()
        resource = None
        for item in self.resourceListWidget.selectedItems()[:1]:
            resource = item.resource_full
            self.edit_item = item
        if not resource:
            return
        parameters_widget = [
            self.resourceGroupBox.layout().itemAt(i) for i in
            range(self.resourceGroupBox.layout().count())][0].widget()
        parameter_widgets = [
            parameters_widget.vertical_layout.itemAt(i).widget() for i in
            range(parameters_widget.vertical_layout.count())]
        parameter_widgets[0]._line_edit_input.setText(
            resource['Resource name'])
        parameter_widgets[1]._line_edit_input.setText(
            resource['Resource description'])
        parameter_widgets[2]._line_edit_input.setText(resource['Unit'])
        parameter_widgets[3]._line_edit_input.setText(resource['Units'])
        parameter_widgets[4]._line_edit_input.setText(
            resource['Unit abbreviation'])
        parameter_widgets[5]._input.setValue(float(resource['Default']))
        parameter_widgets[6]._input.setValue(float(
            resource['Minimum allowed']))
        parameter_widgets[7]._input.setValue(float(
            resource['Maximum allowed']))
        parameter_widgets[8]._line_edit_input.setText(resource['Frequency'])
        parameter_widgets[9]._line_edit_input.setText(
            resource['Readable sentence'])
        self.stackedWidget.setCurrentIndex(1)

    def set_up_resource_parameters(self):
        """Set up the resource parameter for the add/edit view.
        """
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
            'allowance per individual. For example when planning water '
            'rations the units would be litres.')
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
            'ration per person per day should never be allowed to be less '
            'than 0.5l. This is enforced when tweaking a minimum needs set '
            'before an impact evaluation')
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
            'ration per person per day should never be allowed to be more '
            'than 50l. This is enforced when tweaking a minimum needs set '
            'before an impact evaluation.')
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
            "{{ Default }} {{ Unit }}/{{ Units }}/{{ Unit abbreviation }} of "
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
        parameter_container = ParameterContainer(parameters)

        layout = QGridLayout()
        layout.addWidget(parameter_container)
        self.resourceGroupBox.setLayout(layout)

    def remove_resource(self):
        """Remove the currently selected resource.
        """
        self.mark_current_profile_as_pending()
        for item in self.resourceListWidget.selectedItems():
            self.resourceListWidget.takeItem(self.resourceListWidget.row(item))

    def discard_changes(self):
        """Discard the changes to the resource add/edit.
        """
        self.edit_item = None
        self.stackedWidget.setCurrentIndex(0)

    def accept_changes(self):
        """Accept the add/edit of the current resource.
        """
        # --
        # Hackorama to get this working outside the method that the
        # parameters where defined in.
        parameters_widget = [
            self.resourceGroupBox.layout().itemAt(i) for i in
            range(self.resourceGroupBox.layout().count())][0]
        parameters = parameters_widget.widget().get_parameters()
        # --
        resource = {}
        for parameter in parameters:
            resource[parameter.name] = parameter.value
        self.add_resource(resource)
        self.stackedWidget.setCurrentIndex(0)

    def import_minimum_needs(self):
        """ Import minimum needs from an existing json file.
        The minimum needs are loaded from a file into the table. This state
        is only saved if the form is accepted.
        """
        # noinspection PyCallByClass,PyTypeChecker
        file_name = QtGui.QFileDialog.getOpenFileName(
            self,
            self.tr('Import minimum needs'),
            '',
            self.tr('JSON files (*.json *.JSON)'))
        if file_name == '' or file_name is None:
            return -1

        if self.minimum_needs.read_from_file(file_name) == -1:
            return -1

        self.populate_minimum_needs_table()
        return 0

    def export_minimum_needs(self):
        """ Export minimum needs to a json file.
        This method will save the current state of the minimum needs setup.
        Then open a dialog allowing the user to browse to the desired
        destination loction and allow the user to save the needs as a json
        file.
        """
        # self.save_minimum_needs()  # save current state before continuing
        file_name_dialog = QFileDialog(self)
        file_name_dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        file_name_dialog.setNameFilter(self.tr('JSON files (*.json *.JSON)'))
        file_name_dialog.setDefaultSuffix('json')
        file_name = None
        if file_name_dialog.exec_():
            file_name = file_name_dialog.selectedFiles()[0]
        if file_name != '' and file_name is not None:
            self.minimum_needs.write_to_file(file_name)

    def save_minimum_needs(self):
        """ Save the current state of the minimum needs widget.
        The minimum needs widget current state is saved to the QSettings via
        the appropriate QMinimumNeeds class' method.
        """
        minimum_needs = {'resources': []}
        for index in xrange(self.resourceListWidget.count()):
            item = self.resourceListWidget.item(index)
            minimum_needs['resources'].append(item.resource_full)
        minimum_needs['provenance'] = self.provenanceLineEdit.text()
        minimum_needs['profile'] = self.profileComboBox.itemText(
            self.profileComboBox.currentIndex()
        )
        self.minimum_needs.update_minimum_needs(minimum_needs)
        self.minimum_needs.save()
        self.minimum_needs.save_profile(minimum_needs['profile'])
        self.mark_current_profile_as_saved()

    def save_minimum_needs_as(self):
        """Save the minimum needs under a new profile name.
        """
        # noinspection PyCallByClass,PyTypeChecker
        file_name = QFileDialog.getSaveFileName(
            self,
            self.tr('Export minimum needs'),
            expanduser('~/.qgis2/minimum_needs'),
            self.tr('JSON files (*.json *.JSON)'),
            options=QtGui.QFileDialog.DirectoryOnly)
        if not file_name:
            return
        file_name = basename(file_name)
        minimum_needs = {'resources': []}
        self.mark_current_profile_as_saved()
        for index in xrange(self.resourceListWidget.count()):
            item = self.resourceListWidget.item(index)
            minimum_needs['resources'].append(item.resource_full)
        minimum_needs['provenance'] = self.provenanceLineEdit.text()
        minimum_needs['profile'] = file_name
        self.minimum_needs.update_minimum_needs(minimum_needs)
        self.minimum_needs.save()
        self.minimum_needs.save_profile(file_name)
        if self.profileComboBox.findText(file_name) == -1:
            self.profileComboBox.addItem(file_name)
        self.profileComboBox.setCurrentIndex(
            self.profileComboBox.findText(file_name))

    def new_profile(self):
        """Create a new profile by name.
        """
        # noinspection PyCallByClass,PyTypeChecker
        file_name = QFileDialog.getSaveFileName(
            self,
            self.tr('Export minimum needs'),
            expanduser('~/.qgis2/minimum_needs'),
            self.tr('JSON files (*.json *.JSON)'),
            options=QtGui.QFileDialog.DontUseNativeDialog)
        if not file_name:
            return
        file_name = basename(file_name)
        minimum_needs = {
            'resources': [], 'provenance': '', 'profile': file_name}
        self.minimum_needs.update_minimum_needs(minimum_needs)
        self.minimum_needs.save_profile(file_name)
        if self.profileComboBox.findText(file_name) == -1:
            self.profileComboBox.addItem(file_name)
        self.profileComboBox.setCurrentIndex(
            self.profileComboBox.findText(file_name))
