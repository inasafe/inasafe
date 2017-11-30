# coding=utf-8
"""Function Option Dialog (deprecated?)"""

import logging
from collections import OrderedDict

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature, pyqtSlot
from PyQt4.QtGui import (
    QGroupBox,
    QLineEdit,
    QLabel,
    QDialog,
    QCheckBox,
    QWidget,
    QScrollArea,
    QVBoxLayout)
from parameters.parameter_exceptions import CollectionLengthError
from parameters.qt_widgets.parameter_container import ParameterContainer

from safe.common.parameters.resource_parameter import ResourceParameter
from safe.common.parameters.resource_parameter_widget import (
    ResourceParameterWidget)
from safe.gui.tools.help.function_options_help import function_options_help
from safe.utilities.i18n import tr
from safe.utilities.resources import html_footer, html_header, get_ui_class

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

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

        # Set up things for context help
        self.help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)

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
        if isinstance(widget, QLineEdit):
            return lambda: function(widget.text())
        elif isinstance(widget, QCheckBox) or isinstance(widget, QGroupBox):
            return lambda: function(widget.isChecked())
        else:
            return lambda: function(widget.property(property_name))

    def build_form(self, parameters):
        """Build a form from impact functions parameter.

        .. note:: see http://tinyurl.com/pyqt-differences

        :param parameters: Parameters to be edited
        """
        scroll_layout = QVBoxLayout()
        scroll_widget = QWidget()
        scroll_widget.setLayout(scroll_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)
        self.configLayout.addWidget(scroll)

        for key, value in parameters.items():
            if key == 'postprocessors':
                self.build_post_processor_form(value)
            elif key == 'minimum needs':
                self.build_minimum_needs_form(value)
            else:
                self.build_widget(scroll_layout, key, value)

        if scroll_layout.count() == 0:
            # Rizky: in case empty impact function, let's show some messages
            label = QLabel()
            message = tr('This impact function does not have any options to '
                         'configure')
            label.setText(message)
            scroll_layout.addWidget(label)

        scroll_layout.addStretch()

    def build_minimum_needs_form(self, parameters):
        """Build minimum needs tab.

        :param parameters: A list containing element of form
        :type parameters: list
        """
        # create minimum needs tab
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

        extra_parameters = [(ResourceParameter, ResourceParameterWidget)]
        parameter_container = ParameterContainer(
            parameters=parameters, extra_parameters=extra_parameters)
        parameter_container.setup_ui()
        scroll_layout.addWidget(parameter_container)
        self.tabWidget.addTab(main_widget, self.tr('Minimum Needs'))
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
            parameter_container.setup_ui(must_scroll=False)
            scroll_layout.addWidget(parameter_container)
            input_values = parameter_container.get_parameters
            values[label] = input_values

        self.values['postprocessors'] = values
        scroll_layout.addStretch()

    def build_widget(self, form_layout, name, parameter_value):
        """Create a new form element dynamically based from key_value type.

        The Parameter Container will be inserted to form_layout.

        :param form_layout: Mandatory a layout instance
        :type form_layout: QFormLayout

        :param name: Mandatory string referencing the key in the function
         configurable parameters dictionary.
        :type name: str

        :param parameter_value: Mandatory representing the value referenced
        by the key.
        :type parameter_value: object, list

        :returns: a function that return the value of widget

        :raises: None
        """
        input_values = None
        if parameter_value is not None:
            # create and add widget to the dialog box
            # default tab's layout
            parameter_container = ParameterContainer(parameter_value)
            parameter_container.setup_ui(must_scroll=False)
            for w in [w.widget() for w in
                      parameter_container.get_parameter_widgets()]:
                # Rizky : assign error handler for
                # InputListParameterWidget
                w.add_row_error_handler = self.explain_errors
            form_layout.addWidget(parameter_container)
            # bind parameter
            input_values = parameter_container.get_parameters
            self.values[name] = input_values
        else:
            LOGGER.debug('build_widget : parameter is None')
            LOGGER.debug(parameter_value)
        return input_values

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
        except (SyntaxError, ValueError, TypeError,
                CollectionLengthError) as ex:
            self.explain_errors(ex)

    def explain_errors(self, exception):
        text = self.tr("Unexpected error: %s " % exception)
        self.lblErrorMessage.setText(text)

    def result(self):
        """Get the result."""
        return self._result

    @pyqtSlot()
    @pyqtSignature('bool')  # prevents actions being handled twice
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

        message = function_options_help()

        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)
