# coding=utf-8
"""Example usage of group select parameter.."""

import sys
from collections import OrderedDict
from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from PyQt4.QtGui import QApplication, QWidget, QGridLayout

from safe_extras.parameters.qt_widgets.parameter_container import (
    ParameterContainer)

from safe.common.parameters.group_select_parameter import (
    GroupSelectParameter)
from safe.common.parameters.group_select_parameter_widget import (
    GroupSelectParameterWidget)

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def main():
    """Main function to run the example."""
    app = QApplication([])

    options = OrderedDict([
        ('do not use',
         {
             'label': 'Do not use',
             'value': None,
             'type': 'static',
             'constraint': {}
         }),
        ('global default',
         {
             'label': 'Global default',
             'value': 0.5,
             'type': 'static',
             'constraint': {}
         }),
        ('custom value',
         {
             'label': 'Custom',
             'value': 0.7,  # Taken from keywords / recent value
             'type': 'single dynamic',
             'constraint':
                 {
                     'min': 0,
                     'max': 1
                 }
         }),
        ('ratio fields',
         {
             'label': 'Ratio fields',
             'value': ['field A', 'field B', 'field C'],  # Taken from keywords
             'type': 'multiple dynamic',
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
