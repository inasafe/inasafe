# coding=utf-8
"""Example usage of group select parameter."""

import sys
from collections import OrderedDict
from functools import partial

from safe.test.qgis_app import qgis_app

from PyQt4.QtGui import QWidget, QGridLayout, QPushButton, QMessageBox

from parameters.qt_widgets.parameter_container import (
    ParameterContainer)
from parameters.group_parameter import GroupParameter
from safe.common.parameters.group_select_parameter import (
    GroupSelectParameter)
from safe.common.parameters.group_select_parameter_widget import (
    GroupSelectParameterWidget)
from safe.definitions.constants import (
    DO_NOT_REPORT,
    CUSTOM_VALUE,
    GLOBAL_DEFAULT,
    FIELDS,
    STATIC,
    SINGLE_DYNAMIC,
    MULTIPLE_DYNAMIC)


__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def main():
    """Main function to run the example."""
    app, iface = qgis_app()

    options = OrderedDict([
        (DO_NOT_REPORT,
         {
             'label': 'Do not report',
             'value': None,
             'type': STATIC,
             'constraint': {}
         }),
        (GLOBAL_DEFAULT,
         {
             'label': 'Global default',
             'value': 0.5,
             'type': STATIC,
             'constraint': {}
         }),
        (CUSTOM_VALUE,
         {
             'label': 'Custom',
             'value': 0.7,  # Taken from keywords / recent value
             'type': SINGLE_DYNAMIC,
             'constraint':
                 {
                     'min': 0,
                     'max': 1
                 }
         }),
        (FIELDS,
         {
             'label': 'Ratio fields',
             'value': ['field A', 'field B', 'field C'],  # Taken from keywords
             'type': MULTIPLE_DYNAMIC,
             'constraint': {}
         })
    ])

    default_value_parameter = GroupSelectParameter()
    default_value_parameter.name = 'Group Select parameter'
    default_value_parameter.help_text = 'Help text'
    default_value_parameter.description = 'Description'
    default_value_parameter.options = options
    default_value_parameter.selected = 'ratio fields'

    parameters = [
        default_value_parameter
    ]

    extra_parameters = [
        (GroupSelectParameter, GroupSelectParameterWidget)
    ]

    parameter_container = ParameterContainer(
        parameters, extra_parameters=extra_parameters)
    parameter_container.setup_ui()

    widget = QWidget()
    layout = QGridLayout()
    layout.addWidget(parameter_container)

    def show_error_message(parent, exception):
        """Generate error message to handle parameter errors

        :param parent: The widget as a parent of message box
        :type parent: QWidget
        :param exception: python Exception or Error
        :type exception: Exception
        """
        box = QMessageBox()
        box.critical(parent, 'Error occured', exception.message)

    def show_parameter(the_parameter_container):
        """Print the value of parameter.

        :param the_parameter_container: A parameter container
        :type the_parameter_container: ParameterContainer
        """
        def show_parameter_value(a_parameter):
            if isinstance(a_parameter, GroupParameter):
                for param in a_parameter.value:
                    show_parameter_value(param)
            else:
                print a_parameter.guid, a_parameter.name, a_parameter.value

        try:
            the_parameters = the_parameter_container.get_parameters()
            if the_parameters:
                for parameter in the_parameters:
                    show_parameter_value(parameter)
        except Exception as inst:
            show_error_message(parameter_container, inst)

    print_button = QPushButton('Print Result')
    # noinspection PyUnresolvedReferences
    print_button.clicked.connect(
        partial(show_parameter, the_parameter_container=parameter_container))

    layout.addWidget(print_button)

    widget.setLayout(layout)
    widget.setGeometry(0, 0, 500, 500)

    widget.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
