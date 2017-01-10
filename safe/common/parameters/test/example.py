# coding=utf-8
"""Example usage of custom parameters."""

import sys
from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from PyQt4.QtGui import (
    QApplication, QWidget, QGridLayout, QPushButton, QMessageBox)

from safe_extras.parameters.qt_widgets.parameter_container import (
    ParameterContainer)

from safe.common.parameters.default_value_parameter import (
    DefaultValueParameter)
from safe.common.parameters.default_value_parameter_widget import (
    DefaultValueParameterWidget)


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def main():
    app = QApplication([])

    default_value_parameter = DefaultValueParameter()
    default_value_parameter.name = 'Default value parameter'
    default_value_parameter.help_text = 'Help text'
    default_value_parameter.description = 'Description'
    default_value_parameter.default_labels = [
        'Setting', 'Do not use', 'Custom']
    default_value_parameter.default_values = [0, 1, None]

    parameters = [
        default_value_parameter
    ]

    extra_parameters = [
        (DefaultValueParameter, DefaultValueParameterWidget)
    ]

    parameter_container = ParameterContainer(
        parameters, extra_parameters=extra_parameters)
    parameter_container.setup_ui()

    widget = QWidget()
    layout = QGridLayout()
    layout.addWidget(parameter_container)
    # layout.addWidget(button)
    # layout.addWidget(parameter_container2)
    # layout.addWidget(parameter_container3)
    # layout.addWidget(validate_button)

    widget.setLayout(layout)
    widget.setGeometry(0, 0, 500, 500)

    widget.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
