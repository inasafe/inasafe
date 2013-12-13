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
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QGroupBox, QLineEdit, QDialog, QLabel, QCheckBox,
                         QFormLayout, QWidget)
from third_party.odict import OrderedDict

from safe_qgis.ui.function_options_dialog_base import (
    Ui_FunctionOptionsDialogBase)
from safe_qgis.safe_interface import safeTr, get_postprocessor_human_name

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


# FIXME (Tim and Ole): Change to ConfigurationDialog throughout
# Maybe also change filename and Base name accordingly.
class FunctionOptionsDialog(QtGui.QDialog,
                            Ui_FunctionOptionsDialogBase):
    """ConfigurableImpactFunctions Dialog for InaSAFE.
    """

    def __init__(self, theParent=None):
        """Constructor for the dialog.

        This dialog will show the user the form for editing impact functions
        parameters if any.

        :param theParent: Optional widget to use as parent
        """
        QtGui.QDialog.__init__(self, theParent)
        self.setupUi(self)
        self.setWindowTitle(self.tr('InaSAFE impact function configuration'))
        self.tabWidget.tabBar().setVisible(False)

        self._result = None
        self.values = OrderedDict()

    def bind(self, theObject, theProperty, theType):
        """Create a function that return the QWidget property of object and
        convert the value to type.

        :param theObject: QWidget instance
        :param theProperty: The name of property inside QWidget instance
        :param theType: A function to convert the property value

        :returns: The property value of theObject
        """
        return lambda: theType(theObject.property(theProperty))

    def build_form(self, theParams):
        """we build a form from impact functions parameter

        .. note:: see http://tinyurl.com/pyqt-differences

        :param theParams: Parameters to be edited
        """

        for key, value in theParams.items():
            if key == 'postprocessors':
                self.build_post_processor_form(value)
            elif key == 'minimum needs':
                self.build_minimum_needs_form(value)
            else:
                self.values[key] = self.build_widget(
                    self.configLayout,
                    key,
                    value)

    def build_minimum_needs_form(self, parameters):
        """Build minimum needs tab

        :param parameters: A Dictionary containing element of form
        """
        # create minimum needs tab
        tab = QWidget()
        form_layout = QFormLayout(tab)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        self.tabWidget.addTab(tab, self.tr('Minimum Needs'))
        self.tabWidget.tabBar().setVisible(True)

        widget = QWidget()
        layout = QFormLayout(widget)
        widget.setLayout(layout)

        values = OrderedDict()
        for myLabel, value in parameters.items():
            values[myLabel] = self.build_widget(
                layout, myLabel, value)

        form_layout.addRow(widget, None)
        self.values['minimum needs'] = values

    def build_post_processor_form(self, parameters):
        """Build Post Processor Tab

        :param  parameters: A Dictionary containing element of form
        """

        # create postprocessors tab
        tab = QWidget()
        form_layout = QFormLayout(tab)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        self.tabWidget.addTab(tab, self.tr('Postprocessors'))
        self.tabWidget.tabBar().setVisible(True)

        # create element for the tab
        values = OrderedDict()
        for myLabel, options in parameters.items():
            input_values = OrderedDict()

            # NOTE (gigih) : 'params' is assumed as dictionary
            if 'params' in options:
                group_box = QGroupBox()
                group_box.setCheckable(True)
                group_box.setTitle(get_postprocessor_human_name(myLabel))

                # NOTE (gigih): is 'on' always exist??
                group_box.setChecked(options.get('on'))
                input_values['on'] = self.bind(group_box, 'checked', bool)

                layout = QFormLayout(group_box)
                group_box.setLayout(layout)

                # create widget element from 'params'
                input_values['params'] = OrderedDict()
                for key, value in options['params'].items():
                    input_values['params'][key] = self.build_widget(
                        layout, key, value)

                form_layout.addRow(group_box, None)

            elif 'on' in options:
                checkbox = QCheckBox()
                checkbox.setText(get_postprocessor_human_name(myLabel))
                checkbox.setChecked(options['on'])

                input_values['on'] = self.bind(checkbox, 'checked', bool)
                form_layout.addRow(checkbox, None)
            else:
                raise NotImplementedError('This case is not handled for now')

            values[myLabel] = input_values

        self.values['postprocessors'] = values

    def build_widget(self, theFormLayout, theName, theValue):
        """Create a new form element dynamically based from theValue type.
        The element will be inserted to theFormLayout.

        :param theFormLayout: Mandatory a layout instance
        :type theFormLayout: QFormLayout

        :param theName: Mandatory string referencing the key in the function
         configurable parameters dictionary.
        :type theName: str

        :param theValue: Mandatory representing the value referenced by the
         key.
        :type theValue: object

        :returns: a function that return the value of widget

        :raises: None
        """

        # create label
        if isinstance(theName, str):
            label = QLabel()
            label.setObjectName(_fromUtf8(theName + "Label"))
            label_text = theName.replace('_', ' ').capitalize()
            label.setText(safeTr(label_text))
            label.setToolTip(str(type(theValue)))
        else:
            label = theName

        # create widget based on the type of theValue variable
        if isinstance(theValue, list):
            widget = QLineEdit()
            value = ', '.join([str(x) for x in theValue])
            # NOTE: we assume that all element in list have same type
            value_type = type(theValue[0])
            function = lambda x: [value_type(y) for y in str(x).split(',')]
        elif isinstance(theValue, dict):
            widget = QLineEdit()
            value = str(theValue)
            function = lambda x: ast.literal_eval(str(x))
        else:
            widget = QLineEdit()
            value = str(theValue)
            function = type(theValue)

        widget.setText(value)
        theFormLayout.addRow(label, widget)

        return self.bind(widget, 'text', function)

    def set_dialog_info(self, function_id):
        """Show help text in dialog.

        :param function_id:
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

        .. note:: see http://tinyurl.com/pyqt-differences
        """

        try:
            self._result = self.parse_input(self.values)
            self.done(QDialog.Accepted)
        except (SyntaxError, ValueError) as myEx:
            text = self.tr("Unexpected error: %s " % myEx)
            self.lblErrorMessage.setText(text)

    def result(self):
        """Get the result.

        :return:
        :rtype:
        """
        return self._result
