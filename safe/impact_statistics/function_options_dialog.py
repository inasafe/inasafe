# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Functions Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'oz@tanoshiistudio.com'
__revision__ = '$Format:%H$'
__date__ = '01/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import ast
from collections import OrderedDict
import logging
# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
# noinspection PyPackageRequirements
from PyQt4.QtCore import Qt
# noinspection PyPackageRequirements
from PyQt4.QtGui import (
    QGroupBox,
    QLineEdit,
    QDialog,
    QLabel,
    QCheckBox,
    QFormLayout,
    QGridLayout,
    QWidget,
    QScrollArea,
    QVBoxLayout)

from safe.utilities.i18n import tr
from safe.utilities.resources import get_ui_class
from safe.postprocessors.postprocessor_factory import (
    get_postprocessor_human_name)
from safe_extras.parameters.qt_widgets.parameter_container import (
    ParameterContainer)
from safe.common.resource_parameter import ResourceParameter
from safe.common.resource_parameter_widget import ResourceParameterWidget

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(text):
        return text

LOGGER = logging.getLogger('InaSAFE')
FORM_CLASS = get_ui_class('function_options_dialog_base.ui')


# FIXME (Tim and Ole): Change to ConfigurationDialog throughout
# Maybe also change filename and Base name accordingly.
class FunctionOptionsDialog(QtGui.QDialog, FORM_CLASS):
    """ConfigurableImpactFunctions Dialog for InaSAFE.
    """

    def __init__(self, parent=None):
        """Constructor for the dialog.

        This dialog will show the user the form for editing impact functions
        parameters if any.

        :param parent: Optional widget to use as parent
        """
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr('InaSAFE impact function configuration'))
        self.tabWidget.tabBar().setVisible(False)

        self._result = None
        self.values = OrderedDict()

    # noinspection PyCallingNonCallable,PyMethodMayBeStatic
    def bind(self, widget, property_name, function):
        """Return the widget.property converting the value using the function.

        :param widget: QWidget instance
        :type widget: QWidget

        :param property_name: The name of property inside QWidget instance
        :type property_name: str

        :param function: A function to convert the property value
        :type function: Callable

        :returns: The property value of widget
        """

        # NOTES (Ismail Sunni): I don't know why, but unittest and nosetest
        # gives different output for widget.property(property_name). So,
        # it's better to check the type of the widget.
        # for new_parameter in new_parameters:
        #     values[new_parameter.name] = new_parameter.value
        if type(widget) == QLineEdit:
            return lambda: function(widget.text())
        elif type(widget) == QCheckBox or type(widget) == QGroupBox:
            return lambda: function(widget.isChecked())
        else:
            return lambda: function(widget.property(property_name))

    def build_form(self, parameters):
        """Build a form from impact functions parameter.

        .. note:: see http://tinyurl.com/pyqt-differences

        :param parameters: Parameters to be edited
        """

        for key, value in parameters.items():
            if key == 'postprocessors':
                self.build_post_processor_form(value)
            elif key == 'minimum needs':
                self.build_minimum_needs_form(value)
            else:
                self.values[key] = self.build_widget(
                    self.configLayout, key, value)

    def build_minimum_needs_form(self, parameters):
        """Build minimum needs tab.

        :param parameters: A list containing element of form
        :type parameters: list
        """
        # create minimum needs tab
        tab = QWidget()
        form_layout = QGridLayout(tab)
        form_layout.setContentsMargins(0, 0, 0, 0)
        extra_parameters = [(ResourceParameter, ResourceParameterWidget)]
        parameter_container = ParameterContainer(parameters, extra_parameters)
        form_layout.addWidget(parameter_container)
        self.tabWidget.addTab(tab, self.tr('Minimum Needs'))
        self.tabWidget.tabBar().setVisible(True)
        self.values['minimum needs'] = parameter_container.get_parameters

    def build_post_processor_form(self, form_elements):
        """Build Post Processor Tab.

        :param form_elements: A Dictionary containing element of form.
        :type form_elements: dict
        """
        scroll_layout = QVBoxLayout()
        scroll_widget = QWidget()
        scroll_widget.setLayout(scroll_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.tabWidget.addTab(main_widget, self.tr('Postprocessors'))
        self.tabWidget.tabBar().setVisible(True)

        # create elements for the tab
        values = OrderedDict()
        for label, parameters in form_elements.items():
            parameter_container = ParameterContainer(parameters)
            scroll_layout.addWidget(parameter_container)
            input_values = parameter_container.get_parameters
            values[label] = input_values

        self.values['postprocessors'] = values

    def build_widget(self, form_layout, name, key_value):
        """Create a new form element dynamically based from key_value type.

        The element will be inserted to form_layout.

        :param form_layout: Mandatory a layout instance
        :type form_layout: QFormLayout

        :param name: Mandatory string referencing the key in the function
         configurable parameters dictionary.
        :type name: str

        :param key_value: Mandatory representing the value referenced by the
         key.
        :type key_value: object

        :returns: a function that return the value of widget

        :raises: None
        """
        # create label
        if isinstance(name, str):
            label = QLabel()
            label.setObjectName(_fromUtf8(name + "Label"))
            label_text = name.replace('_', ' ').capitalize()
            label.setText(tr(label_text))
            label.setToolTip(str(type(key_value)))
        else:
            label = name

        # create widget based on the type of key_value variable
        # if widget is a QLineEdit, value needs to be set
        # if widget is NOT a QLineEdit, property_name needs to be set
        value = None
        property_name = None

        # can be used for widgets that have their own text like QCheckBox
        hide_label = False

        if isinstance(key_value, list):
            def function(values_string):
                """
                :param values_string: This contains the list of values the user
                    added to the line edit for the parameter.
                :type values_string: basestring

                :returns: list of value types
                :rtype: list
                """
                value_type = type(key_value[0])
                return [value_type(y) for y in str(values_string).split(',')]
            widget = QLineEdit()
            value = ', '.join([str(x) for x in key_value])
            # NOTE: we assume that all element in list have same type
        elif isinstance(key_value, dict):
            def function(key_values_string):
                """
                :param key_values_string: This contains the dictionary that
                    the used defined on the line edit for this parameter.
                :type key_values_string: basestring

                :returns: a safe evaluation of the dict
                :rtype: dict
                """
                return ast.literal_eval(str(key_values_string))
            widget = QLineEdit()
            value = str(key_value)
        elif isinstance(key_value, bool):
            function = bool
            widget = QCheckBox()
            widget.setChecked(key_value)
            widget.setText(label.text())
            property_name = 'checked'
            hide_label = True
        else:
            function = type(key_value)
            widget = QLineEdit()
            value = str(key_value)
        if hide_label:
            form_layout.addRow(widget)
        else:
            form_layout.addRow(label, widget)

        if type(widget) is QLineEdit:
            widget.setText(value)
            property_name = 'text'

        return self.bind(widget, property_name, function)

    def set_dialog_info(self, function_id):
        """Show help text in dialog.

        :param function_id: The id of a function
        """
        text = self.tr(
            'Parameters for impact function "%s" that can be modified are:'
        ) % function_id
        label = self.lblFunctionDescription
        label.setText(text)

    def parse_input(self, input_dict):
        """Parse the input value of widget.

        :param input_dict: Dictionary that holds all values of element.
        :type input_dict: dict

        :returns: Dictionary that can be consumed for impact functions.
        :rtype: dict

        :raises:
            * ValueError - occurs when some input cannot be converted
                           to suitable type.
        """

        result = OrderedDict()
        for name, value in input_dict.items():
            if hasattr(value, '__call__'):
                result[name] = value()
            elif isinstance(value, dict):
                result[name] = self.parse_input(value)
            else:
                result[name] = value

        return result

    def accept(self):
        """Override the default accept function

        .. note:: see http://tinyurl.com/pyqt-differences # Broken url
        """

        try:
            self._result = self.parse_input(self.values)
            self.done(QDialog.Accepted)
        except (SyntaxError, ValueError) as ex:
            text = self.tr("Unexpected error: %s " % ex)
            self.lblErrorMessage.setText(text)

    def result(self):
        """Get the result."""
        return self._result
