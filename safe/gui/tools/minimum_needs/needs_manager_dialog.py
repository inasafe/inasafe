# coding=utf-8
"""Need Manager Dialog."""


import os
from os.path import expanduser, basename

from qgis.PyQt import QtGui, QtWidgets
from qgis.PyQt.QtCore import pyqtSlot
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QGridLayout, QPushButton, QDialogButtonBox, QMessageBox
from qgis.PyQt.QtGui import QIcon
# This import must come first to force sip2 api
# noinspection PyUnresolvedReferences
from qgis.core import Qgis  # NOQA pylint: disable=unused-import
from qgis.core import QgsApplication

from parameters.float_parameter import FloatParameter
from parameters.parameter_exceptions import (
    ValueOutOfBounds,
    InvalidMaximumError,
    InvalidMinimumError)
from parameters.qt_widgets.parameter_container import (
    ParameterContainer)
from parameters.string_parameter import StringParameter
from parameters.text_parameter import TextParameter
from safe.common.parameters.resource_parameter import ResourceParameter
from safe.gui.tools.help.needs_manager_help import needs_manager_helps
from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.resources import (
    resources_path, get_ui_class, html_footer, html_header)

__copyright__ = "Copyright 2014, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
FORM_CLASS = get_ui_class('needs_manager_dialog_base.ui')


class NeedsManagerDialog(QDialog, FORM_CLASS):
    """Dialog class for the InaSAFE global minimum needs configuration.

    .. versionadded:: 2.2.
    """

    def __init__(self, parent=None, dock=None):
        """Constructor for the minimum needs dialog.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget

        :param dock: Dock widget instance that we can notify of changes.
        :type dock: Dock
        """
        QtWidgets.QDialog.__init__(self, parent)
        # List of parameters with the translated name.
        self.resource_parameters = {
            'Resource name': tr('Resource name'),
            'Resource description': tr('Resource description'),
            'Unit': tr('Unit'),
            'Units': tr('Units'),
            'Unit abbreviation': tr('Unit abbreviation'),
            'Minimum allowed': tr('Minimum allowed'),
            'Maximum allowed': tr('Maximum allowed'),
            'Default': tr('Default'),
            'Frequency': tr('Frequency'),
            'Readable sentence': tr('Readable sentence')
        }

        self.setupUi(self)
        icon = resources_path('img', 'icons', 'show-minimum-needs.svg')
        self.setWindowIcon(QtGui.QIcon(icon))
        self.dock = dock
        # These are in the little button bar at the bottom
        # 'Remove resource' button
        # noinspection PyUnresolvedReferences
        self.remove_resource_button.clicked.connect(self.remove_resource)
        self.remove_resource_button.setIcon(
            QIcon(os.path.join(
                resources_path(), 'img', 'icons', 'remove.svg')))

        # Add resource
        # noinspection PyUnresolvedReferences
        self.add_resource_button.clicked.connect(self.add_new_resource)
        self.add_resource_button.setIcon(
            QIcon(os.path.join(
                resources_path(), 'img', 'icons', 'add.svg')))
        # Edit resource
        # noinspection PyUnresolvedReferences
        self.edit_resource_button.clicked.connect(self.edit_resource)
        self.edit_resource_button.setIcon(
            QIcon(os.path.join(
                resources_path(), 'img', 'icons', 'edit.svg')))

        # Discard changes to a resource
        self.discard_changes_button = QPushButton(self.tr('Discard changes'))
        self.button_box.addButton(
            self.discard_changes_button, QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        self.discard_changes_button.clicked.connect(self.discard_changes)

        # Restore defaults profiles
        self.restore_defaults_button = QPushButton(self.tr('Restore defaults'))
        self.button_box.addButton(
            self.restore_defaults_button, QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        self.restore_defaults_button.clicked.connect(self.restore_defaults)

        # Save changes to a resource
        self.save_resource_button = QPushButton(self.tr('Save resource'))
        self.button_box.addButton(
            self.save_resource_button, QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        self.save_resource_button.clicked.connect(self.save_resource)

        # Export profile button
        self.export_profile_button = QPushButton(self.tr('Export ...'))
        self.button_box.addButton(
            self.export_profile_button, QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        self.export_profile_button.clicked.connect(self.export_profile)

        # Import profile button
        self.import_profile_button = QPushButton(self.tr('Import ...'))
        self.button_box.addButton(
            self.import_profile_button, QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        self.import_profile_button.clicked.connect(self.import_profile)

        # New profile button
        self.new_profile_button = QPushButton(self.tr('New'))
        self.button_box.addButton(
            self.new_profile_button, QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        self.new_profile_button.clicked.connect(self.new_profile)

        # Save profile button
        self.save_profile_button = QPushButton(self.tr('Save'))
        self.button_box.addButton(
            self.save_profile_button, QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        self.save_profile_button.clicked.connect(self.save_profile)

        # 'Save as' profile button
        self.save_profile_as_button = QPushButton(self.tr('Save as'))
        self.button_box.addButton(
            self.save_profile_as_button, QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        self.save_profile_as_button.clicked.connect(
            self.save_profile_as)

        # Set up things for context help
        self.help_button = self.button_box.button(QtWidgets.QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)

        self.minimum_needs = NeedsProfile()
        self.edit_item = None

        # Remove profile button
        # noinspection PyUnresolvedReferences
        self.remove_profile_button.clicked.connect(self.remove_profile)

        # These are all buttons that will get hidden on context change
        # to the profile editing view
        self.profile_editing_buttons = list()
        self.profile_editing_buttons.append(self.remove_resource_button)
        self.profile_editing_buttons.append(self.add_resource_button)
        self.profile_editing_buttons.append(self.edit_resource_button)
        self.profile_editing_buttons.append(self.export_profile_button)
        self.profile_editing_buttons.append(self.import_profile_button)
        self.profile_editing_buttons.append(self.new_profile_button)
        self.profile_editing_buttons.append(self.save_profile_button)
        self.profile_editing_buttons.append(self.save_profile_as_button)
        # We also keep a list of all widgets to disable in context of resource
        # editing (not hidden, just disabled)
        self.profile_editing_widgets = self.profile_editing_buttons
        self.profile_editing_widgets.append(self.remove_profile_button)
        self.profile_editing_widgets.append(self.profile_combo)
        # These are all buttons that will get hidden on context change
        # to the resource editing view
        self.resource_editing_buttons = list()
        self.resource_editing_buttons.append(self.discard_changes_button)
        self.resource_editing_buttons.append(self.save_resource_button)
        for item in self.resource_editing_buttons:
            item.hide()

        self.load_profiles()
        # Next 2 lines fixes issues #1388 #1389 #1390 #1391
        if self.profile_combo.count() > 0:
            self.select_profile(0)

        # initial sync profile_combo and resource list
        self.clear_resource_list()
        self.populate_resource_list()
        self.set_up_resource_parameters()
        # Only do this afterward load_profiles to avoid the resource list
        # being updated
        # noinspection PyUnresolvedReferences
        self.profile_combo.activated.connect(self.select_profile)
        # noinspection PyUnresolvedReferences
        self.stacked_widget.currentChanged.connect(self.page_changed)
        self.select_profile(self.profile_combo.currentIndex())

    def reject(self):
        """Overload the base dialog reject event so we can handle state change.

        If the user is in resource editing mode, clicking close button,
        window [x] or pressing escape should switch context back to the
        profile view, not close the whole window.

        See https://github.com/AIFDR/inasafe/issues/1387
        """
        if self.stacked_widget.currentWidget() == self.resource_edit_page:
            self.edit_item = None
            self.switch_context(self.profile_edit_page)
        else:
            super(NeedsManagerDialog, self).reject()

    def populate_resource_list(self):
        """Populate the list resource list.
        """
        minimum_needs = self.minimum_needs.get_full_needs()
        for full_resource in minimum_needs["resources"]:
            self.add_resource(full_resource)
        self.provenance.setText(minimum_needs["provenance"])

    def clear_resource_list(self):
        """Clear the resource list.
        """
        self.resources_list.clear()

    def add_resource(self, resource):
        """Add a resource to the minimum needs table.

        :param resource: The resource to be added
        :type resource: dict
        """
        updated_sentence = NeedsProfile.format_sentence(
            resource['Readable sentence'], resource)
        if self.edit_item:
            item = self.edit_item
            item.setText(updated_sentence)
            self.edit_item = None
        else:
            item = QtWidgets.QListWidgetItem(updated_sentence)
        item.resource_full = resource
        self.resources_list.addItem(item)

    def restore_defaults(self):
        """Restore defaults profiles."""
        title = tr('Restore defaults')
        msg = tr(
            'Restoring defaults will overwrite your changes on profiles '
            'provided by InaSAFE. Do you want to continue ?')
        # noinspection PyCallByClass
        reply = QMessageBox.question(
            self, title, msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.profile_combo.clear()
            self.load_profiles(True)
            # Next 2 lines fixes issues #1388 #1389 #1390 #1391
            if self.profile_combo.count() > 0:
                self.select_profile(0)

    def load_profiles(self, overwrite=False):
        """Load the profiles into the dropdown list.

        :param overwrite: If we overwrite existing profiles from the plugin.
        :type overwrite: bool
        """
        for profile in self.minimum_needs.get_profiles(overwrite):
            self.profile_combo.addItem(profile)
        minimum_needs = self.minimum_needs.get_full_needs()
        self.profile_combo.setCurrentIndex(
            self.profile_combo.findText(minimum_needs['profile']))

    def select_profile(self, index):
        """Select a given profile by index.

        Slot for when profile is selected.

        :param index: The selected item's index
        :type index: int
        """
        new_profile = self.profile_combo.itemText(index)
        self.resources_list.clear()
        self.minimum_needs.load_profile(new_profile)
        self.clear_resource_list()
        self.populate_resource_list()
        self.minimum_needs.save()

    def select_profile_by_name(self, profile_name):
        """Select a given profile by profile name

        :param profile_name: The profile name
        :type profile_name: str
        """
        self.select_profile(self.profile_combo.findText(profile_name))

    def mark_current_profile_as_pending(self):
        """Mark the current profile as pending by colouring the text red.
        """
        index = self.profile_combo.currentIndex()
        item = self.profile_combo.model().item(index)
        item.setForeground(QtGui.QColor('red'))

    def mark_current_profile_as_saved(self):
        """Mark the current profile as saved by colouring the text black.
        """
        index = self.profile_combo.currentIndex()
        item = self.profile_combo.model().item(index)
        item.setForeground(QtGui.QColor('black'))

    def add_new_resource(self):
        """Handle add new resource requests.
        """
        parameters_widget = [
            self.parameters_scrollarea.layout().itemAt(i) for i in
            range(self.parameters_scrollarea.layout().count())][0].widget()
        parameter_widgets = [
            parameters_widget.vertical_layout.itemAt(i).widget() for i in
            range(parameters_widget.vertical_layout.count())]
        parameter_widgets[0].set_text('')
        parameter_widgets[1].set_text('')
        parameter_widgets[2].set_text('')
        parameter_widgets[3].set_text('')
        parameter_widgets[4].set_text('')
        parameter_widgets[5].set_value(10)
        parameter_widgets[6].set_value(0)
        parameter_widgets[7].set_value(100)
        parameter_widgets[8].set_text(tr('weekly'))
        parameter_widgets[9].set_text(tr(
            'A displaced person should be provided with '
            '%(default value)s %(unit)s/%(units)s/%(unit abbreviation)s of '
            '%(resource name)s. Though no less than %(minimum allowed)s '
            'and no more than %(maximum allowed)s. This should be provided '
            '%(frequency)s.' % {
                'default value': '{{ Default }}',
                'unit': '{{ Unit }}',
                'units': '{{ Units }}',
                'unit abbreviation': '{{ Unit abbreviation }}',
                'resource name': '{{ Resource name }}',
                'minimum allowed': '{{ Minimum allowed }}',
                'maximum allowed': '{{ Maximum allowed }}',
                'frequency': '{{ Frequency }}'
            }))
        self.stacked_widget.setCurrentWidget(self.resource_edit_page)
        # hide the close button
        self.button_box.button(QDialogButtonBox.Close).setHidden(True)

    def edit_resource(self):
        """Handle edit resource requests.
        """
        self.mark_current_profile_as_pending()
        resource = None
        for item in self.resources_list.selectedItems()[:1]:
            resource = item.resource_full
            self.edit_item = item
        if not resource:
            return
        parameters_widget = [
            self.parameters_scrollarea.layout().itemAt(i) for i in
            range(self.parameters_scrollarea.layout().count())][0].widget()
        parameter_widgets = [
            parameters_widget.vertical_layout.itemAt(i).widget() for i in
            range(parameters_widget.vertical_layout.count())]
        parameter_widgets[0].set_text(resource['Resource name'])
        parameter_widgets[1].set_text(resource['Resource description'])
        parameter_widgets[2].set_text(resource['Unit'])
        parameter_widgets[3].set_text(resource['Units'])
        parameter_widgets[4].set_text(resource['Unit abbreviation'])
        parameter_widgets[5].set_value(float(resource['Default']))
        parameter_widgets[6].set_value(float(resource['Minimum allowed']))
        parameter_widgets[7].set_value(float(resource['Maximum allowed']))
        parameter_widgets[8].set_text(resource['Frequency'])
        parameter_widgets[9].set_text(resource['Readable sentence'])
        self.switch_context(self.resource_edit_page)

    def set_up_resource_parameters(self):
        """Set up the resource parameter for the add/edit view.
        """
        name_parameter = StringParameter('UUID-1')
        name_parameter.name = self.resource_parameters['Resource name']
        name_parameter.help_text = tr(
            'Name of the resource that will be provided '
            'as part of minimum needs. '
            'e.g. Rice, Water etc.')
        name_parameter.description = tr(
            'A <b>resource</b> is something that you provide to displaced '
            'persons in the event of a disaster. The resource will be made '
            'available at IDP camps and may need to be stockpiled by '
            'contingency planners in their preparations for a disaster.')
        name_parameter.is_required = True
        name_parameter.value = ''

        description_parameter = StringParameter('UUID-2')
        description_parameter.name = self.resource_parameters[
            'Resource description']
        description_parameter.help_text = tr(
            'Description of the resource that will be provided as part of '
            'minimum needs.')
        description_parameter.description = tr(
            'This gives a detailed description of what the resource is and ')
        description_parameter.is_required = True
        description_parameter.value = ''

        unit_parameter = StringParameter('UUID-3')
        unit_parameter.name = self.resource_parameters['Unit']
        unit_parameter.help_text = tr(
            'Single unit for the resources spelled out. e.g. litre, '
            'kilogram etc.')
        unit_parameter.description = tr(
            'A <b>unit</b> is the basic measurement unit used for computing '
            'the allowance per individual. For example when planning water '
            'rations the unit would be single litre.')
        unit_parameter.is_required = True
        unit_parameter.value = ''

        units_parameter = StringParameter('UUID-4')
        units_parameter.name = self.resource_parameters['Units']
        units_parameter.help_text = tr(
            'Multiple units for the resources spelled out. e.g. litres, '
            'kilogram etc.')
        units_parameter.description = tr(
            '<b>Units</b> are the basic measurement used for computing the '
            'allowance per individual. For example when planning water '
            'rations the units would be litres.')
        units_parameter.is_required = True
        units_parameter.value = ''

        unit_abbreviation_parameter = StringParameter('UUID-5')
        unit_abbreviation_parameter.name = \
            self.resource_parameters['Unit abbreviation']
        unit_abbreviation_parameter.help_text = tr(
            'Abbreviations of unit for the resources. e.g. l, kg etc.')
        unit_abbreviation_parameter.description = tr(
            "A <b>unit abbreviation</b> is the basic measurement unit's "
            "shortened. For example when planning water rations "
            "the units would be l.")
        unit_abbreviation_parameter.is_required = True
        unit_abbreviation_parameter.value = ''

        minimum_parameter = FloatParameter('UUID-6')
        minimum_parameter.name = self.resource_parameters['Minimum allowed']
        minimum_parameter.is_required = True
        minimum_parameter.precision = 6
        minimum_parameter.minimum_allowed_value = 0.0
        minimum_parameter.maximum_allowed_value = 99999.0
        minimum_parameter.help_text = tr(
            'The minimum allowable quantity per person. ')
        minimum_parameter.description = tr(
            'The <b>minimum</b> is the minimum allowed quantity of the '
            'resource per person. For example you may dictate that the water '
            'ration per person per day should never be allowed to be less '
            'than 0.5l. This is enforced when tweaking a minimum needs set '
            'before an impact evaluation')
        minimum_parameter.value = 0.00

        maximum_parameter = FloatParameter('UUID-7')
        maximum_parameter.name = self.resource_parameters['Maximum allowed']
        maximum_parameter.is_required = True
        maximum_parameter.precision = 6
        maximum_parameter.minimum_allowed_value = 0.0
        maximum_parameter.maximum_allowed_value = 99999.0
        maximum_parameter.help_text = tr(
            'The maximum allowable quantity per person. ')
        maximum_parameter.description = tr(
            'The <b>maximum</b> is the maximum allowed quantity of the '
            'resource per person. For example you may dictate that the water '
            'ration per person per day should never be allowed to be more '
            'than 67l. This is enforced when tweaking a maximum needs set '
            'before an impact evaluation.')
        maximum_parameter.value = 100.0

        default_parameter = FloatParameter('UUID-8')
        default_parameter.name = self.resource_parameters['Default']
        default_parameter.is_required = True
        default_parameter.precision = 6
        default_parameter.minimum_allowed_value = 0.0
        default_parameter.maximum_allowed_value = 99999.0
        default_parameter.help_text = tr(
            'The default allowable quantity per person. ')
        default_parameter.description = tr(
            "The <b>default</b> is the default allowed quantity of the "
            "resource per person. For example you may indicate that the water "
            "ration per person weekly should be 67l.")
        default_parameter.value = 10.0

        frequency_parameter = StringParameter('UUID-9')
        frequency_parameter.name = self.resource_parameters['Frequency']
        frequency_parameter.help_text = tr(
            "The frequency that this resource needs to be provided to a "
            "displaced person. e.g. weekly, daily, once etc.")
        frequency_parameter.description = tr(
            "The <b>frequency</b> informs the aid worker how regularly this "
            "resource needs to be provided to the displaced person.")
        frequency_parameter.is_required = True
        frequency_parameter.value = tr('weekly')

        sentence_parameter = TextParameter('UUID-10')
        sentence_parameter.name = self.resource_parameters['Readable sentence']
        sentence_parameter.help_text = tr(
            'A readable presentation of the resource.')
        sentence_parameter.description = tr(
            "A <b>readable sentence</b> is a presentation of the resource "
            "that displays all pertinent information. If you are unsure then "
            "use the default. Properties should be included using double "
            "curly brackets '{{' '}}'. Including the resource name would be "
            "achieved by including e.g. {{ Resource name }}")
        sentence_parameter.is_required = True
        sentence_parameter.value = tr(
            'A displaced person should be provided with '
            '%(default value)s %(unit)s/%(units)s/%(unit abbreviation)s of '
            '%(resource name)s. Though no less than %(minimum allowed)s '
            'and no more than %(maximum allowed)s. This should be provided '
            '%(frequency)s.' % {
                'default value': '{{ Default }}',
                'unit': '{{ Unit }}',
                'units': '{{ Units }}',
                'unit abbreviation': '{{ Unit abbreviation }}',
                'resource name': '{{ Resource name }}',
                'minimum allowed': '{{ Minimum allowed }}',
                'maximum allowed': '{{ Maximum allowed }}',
                'frequency': '{{ Frequency }}'
            })

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
        parameter_container.setup_ui()

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(parameter_container)
        self.parameters_scrollarea.setLayout(layout)

    def remove_resource(self):
        """Remove the currently selected resource.
        """
        self.mark_current_profile_as_pending()
        for item in self.resources_list.selectedItems():
            self.resources_list.takeItem(self.resources_list.row(item))

    def discard_changes(self):
        """Discard the changes to the resource add/edit.
        """
        self.edit_item = None
        self.switch_context(self.profile_edit_page)

    def save_resource(self):
        """Accept the add/edit of the current resource.
        """
        # --
        # Hackorama to get this working outside the method that the
        # parameters where defined in.
        parameters_widget = [
            self.parameters_scrollarea.layout().itemAt(i) for i in
            range(self.parameters_scrollarea.layout().count())][0]
        parameters = parameters_widget.widget().get_parameters()

        # To store parameters, we need the english version.
        translated_to_english = dict(
            (y, x) for x, y in list(self.resource_parameters.items()))
        resource = {}
        for parameter in parameters:
            resource[translated_to_english[parameter.name]] = parameter.value

        # verify the parameters are ok - create a throw-away resource param
        try:
            parameter = ResourceParameter()
            parameter.name = resource['Resource name']
            parameter.help_text = resource['Resource description']
            # Adding in the frequency property. This is not in the
            # FloatParameter by default, so maybe we should subclass.
            parameter.frequency = resource['Frequency']
            parameter.description = NeedsProfile.format_sentence(
                resource['Readable sentence'],
                resource)
            parameter.minimum_allowed_value = float(
                resource['Minimum allowed'])
            parameter.maximum_allowed_value = float(
                resource['Maximum allowed'])
            parameter.unit.name = resource['Unit']
            parameter.unit.plural = resource['Units']
            parameter.unit.abbreviation = resource['Unit abbreviation']
            parameter.value = float(resource['Default'])
        except ValueOutOfBounds as e:
            warning = self.tr(
                'Problem - default value is invalid') + '\n' + str(e)
            # noinspection PyTypeChecker,PyArgumentList
            QMessageBox.warning(None, 'InaSAFE', warning)
            return
        except InvalidMaximumError as e:
            warning = self.tr(
                'Problem - maximum value is invalid') + '\n' + str(e)
            # noinspection PyTypeChecker,PyArgumentList
            QMessageBox.warning(None, 'InaSAFE', warning)
            return
        except InvalidMinimumError as e:
            warning = self.tr(
                'Problem - minimum value is invalid') + '\n' + str(e)
            # noinspection PyTypeChecker,PyArgumentList
            QMessageBox.warning(None, 'InaSAFE', warning)
            return
        # end of test for parameter validity

        self.add_resource(resource)
        self.switch_context(self.profile_edit_page)

    def import_profile(self):
        """ Import minimum needs from an existing json file.

        The minimum needs are loaded from a file into the table. This state
        is only saved if the form is accepted.
        """
        # noinspection PyCallByClass,PyTypeChecker
        file_name_dialog = QFileDialog(self)
        file_name_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_name_dialog.setNameFilter(self.tr('JSON files (*.json *.JSON)'))
        file_name_dialog.setDefaultSuffix('json')
        path_name = resources_path('minimum_needs')
        file_name_dialog.setDirectory(path_name)
        if file_name_dialog.exec_():
            file_name = file_name_dialog.selectedFiles()[0]
        else:
            return -1

        if self.minimum_needs.read_from_file(file_name) == -1:
            return -1

        self.clear_resource_list()
        self.populate_resource_list()
        self.switch_context(self.profile_edit_page)

    def export_profile(self):
        """ Export minimum needs to a json file.

        This method will save the current state of the minimum needs setup.
        Then open a dialog allowing the user to browse to the desired
        destination location and allow the user to save the needs as a json
        file.
        """
        file_name_dialog = QFileDialog(self)
        file_name_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_name_dialog.setNameFilter(self.tr('JSON files (*.json *.JSON)'))
        file_name_dialog.setDefaultSuffix('json')
        file_name = None
        if file_name_dialog.exec_():
            file_name = file_name_dialog.selectedFiles()[0]
        if file_name != '' and file_name is not None:
            self.minimum_needs.write_to_file(file_name)

    def save_profile(self):
        """ Save the current state of the minimum needs widget.

        The minimum needs widget current state is saved to the QSettings via
        the appropriate QMinimumNeeds class' method.
        """
        minimum_needs = {'resources': []}
        for index in range(self.resources_list.count()):
            item = self.resources_list.item(index)
            minimum_needs['resources'].append(item.resource_full)
        minimum_needs['provenance'] = self.provenance.text()
        minimum_needs['profile'] = self.profile_combo.itemText(
            self.profile_combo.currentIndex()
        )
        self.minimum_needs.update_minimum_needs(minimum_needs)
        self.minimum_needs.save()
        self.minimum_needs.save_profile(minimum_needs['profile'])
        self.mark_current_profile_as_saved()

    def save_profile_as(self):
        """Save the minimum needs under a new profile name.
        """
        # noinspection PyCallByClass,PyTypeChecker
        file_name_dialog = QFileDialog(self)
        file_name_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_name_dialog.setNameFilter(self.tr('JSON files (*.json *.JSON)'))
        file_name_dialog.setDefaultSuffix('json')
        dir = os.path.join(QgsApplication.qgisSettingsDirPath(), 'inasafe', 'minimum_needs')
        file_name_dialog.setDirectory(expanduser(dir))
        if file_name_dialog.exec_():
            file_name = file_name_dialog.selectedFiles()[0]
        else:
            return
        file_name = basename(file_name)
        file_name = file_name.replace('.json', '')
        minimum_needs = {'resources': []}
        self.mark_current_profile_as_saved()
        for index in range(self.resources_list.count()):
            item = self.resources_list.item(index)
            minimum_needs['resources'].append(item.resource_full)
        minimum_needs['provenance'] = self.provenance.text()
        minimum_needs['profile'] = file_name
        self.minimum_needs.update_minimum_needs(minimum_needs)
        self.minimum_needs.save()
        self.minimum_needs.save_profile(file_name)
        if self.profile_combo.findText(file_name) == -1:
            self.profile_combo.addItem(file_name)
        self.profile_combo.setCurrentIndex(
            self.profile_combo.findText(file_name))

    def new_profile(self):
        """Create a new profile by name.
        """
        # noinspection PyCallByClass,PyTypeChecker
        dir = os.path.join(QgsApplication.qgisSettingsDirPath(), 'inasafe', 'minimum_needs')
        file_name, __ = QFileDialog.getSaveFileName(
            self,
            self.tr('Create a minimum needs profile'),
            expanduser(dir),
            self.tr('JSON files (*.json *.JSON)'),
            options=QFileDialog.DontUseNativeDialog)
        if not file_name:
            return
        file_name = basename(file_name)
        if self.profile_combo.findText(file_name) == -1:
            minimum_needs = {
                'resources': [], 'provenance': '', 'profile': file_name}
            self.minimum_needs.update_minimum_needs(minimum_needs)
            self.minimum_needs.save_profile(file_name)
            self.profile_combo.addItem(file_name)
            self.clear_resource_list()
            self.profile_combo.setCurrentIndex(
                self.profile_combo.findText(file_name))
        else:
            self.profile_combo.setCurrentIndex(
                self.profile_combo.findText(file_name))
            self.select_profile_by_name(file_name)

    def page_changed(self, index):
        """Slot for when tab changes in the stacked widget changes.

        :param index: Index of the now active tab.
        :type index: int
        """
        if index == 0:  # profile edit page
            for item in self.resource_editing_buttons:
                item.hide()
            for item in self.profile_editing_widgets:
                item.setEnabled(True)
            for item in self.profile_editing_buttons:
                item.show()
        else:  # resource_edit_page
            for item in self.resource_editing_buttons:
                item.show()
            for item in self.profile_editing_widgets:
                item.setEnabled(False)
            for item in self.profile_editing_buttons:
                item.hide()

    def switch_context(self, page):
        """Switch context tabs by tab widget name.

        :param page: The page should be focussed.
        :type page: QWidget
        """
        # noinspection PyUnresolvedReferences
        if page.objectName() == 'profile_edit_page':
            self.stacked_widget.setCurrentIndex(0)
            self.button_box.button(QDialogButtonBox.Close).setHidden(False)
        else:  # resource_edit_page
            self.stacked_widget.setCurrentIndex(1)
            # hide the close button
            self.button_box.button(QDialogButtonBox.Close).setHidden(True)

    def remove_profile(self):
        """Remove the current profile.

        Make sure the user is sure.
        """
        profile_name = self.profile_combo.currentText()
        # noinspection PyTypeChecker
        button_selected = QMessageBox.warning(
            None,
            'Remove Profile',
            self.tr('Remove %s.') % profile_name,
            QMessageBox.Ok,
            QMessageBox.Cancel
        )
        if button_selected == QMessageBox.Ok:
            self.profile_combo.removeItem(
                self.profile_combo.currentIndex()
            )
            self.minimum_needs.remove_profile(profile_name)
            self.select_profile(self.profile_combo.currentIndex())

    @pyqtSlot(bool)  # prevents actions being handled twice
    def help_toggled(self, flag):
        """Show or hide the help tab in the stacked widget.

        .. versionadded: 3.2.1

        :param flag: Flag indicating whether help should be shown or hidden.
        :type flag: bool
        """
        if flag:
            self.help_button.setText(self.tr('Hide Help'))
            self.show_help()
        else:
            self.help_button.setText(self.tr('Show Help'))
            self.hide_help()

    def hide_help(self):
        """Hide the usage info from the user.

        .. versionadded: 3.2.1
        """
        self.main_stacked_widget.setCurrentIndex(1)

    def show_help(self):
        """Show usage info to the user."""
        # Read the header and footer html snippets
        self.main_stacked_widget.setCurrentIndex(0)
        header = html_header()
        footer = html_footer()

        string = header

        message = needs_manager_helps()

        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)
