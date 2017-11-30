# coding=utf-8
"""Example usage of group select parameter."""

import sys
from collections import OrderedDict

from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from PyQt4.QtGui import QApplication, QWidget, QGridLayout  # NOQA

from parameters.qt_widgets.parameter_container import (
    ParameterContainer)  # NOQA

from safe.common.parameters.group_select_parameter import (
    GroupSelectParameter)  # NOQA
from safe.common.parameters.group_select_parameter_widget import (
    GroupSelectParameterWidget)  # NOQA
from safe.definitions.constants import (
    DO_NOT_REPORT,
    CUSTOM_VALUE,
    GLOBAL_DEFAULT,
    FIELDS,
    STATIC,
    SINGLE_DYNAMIC,
    MULTIPLE_DYNAMIC)  # NOQA

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def main():
    """Main function to run the example."""
    app = QApplication([])

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

    widget.setLayout(layout)
    widget.setGeometry(0, 0, 500, 500)

    widget.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
