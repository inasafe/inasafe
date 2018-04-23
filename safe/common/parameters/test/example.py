# coding=utf-8
"""Example usage of custom parameters."""

import sys

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from qgis.PyQt.QtWidgets import QApplication, QWidget, QGridLayout  # NOQA

from parameters.qt_widgets.parameter_container import (
    ParameterContainer)  # NOQA

from safe.common.parameters.default_value_parameter import (
    DefaultValueParameter)  # NOQA
from safe.common.parameters.default_value_parameter_widget import (
    DefaultValueParameterWidget)  # NOQA


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def main():
    """Main function to run the example."""
    app = QApplication([])

    default_value_parameter = DefaultValueParameter()
    default_value_parameter.name = 'Value parameter'
    default_value_parameter.help_text = 'Help text'
    default_value_parameter.description = 'Description'
    default_value_parameter.labels = [
        'Setting', 'Do not report', 'Custom']
    default_value_parameter.options = [0, 1, None]

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

    widget.setLayout(layout)
    widget.setGeometry(0, 0, 500, 500)

    widget.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
