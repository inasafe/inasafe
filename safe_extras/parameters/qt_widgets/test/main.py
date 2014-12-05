# coding=utf-8
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'main'
__date__ = '8/19/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

import sys

from PyQt4.QtGui import (QApplication, QWidget, QGridLayout)
from metadata import unit_feet_depth, unit_metres_depth
from boolean_parameter import BooleanParameter
from float_parameter import FloatParameter
from integer_parameter import IntegerParameter
from qt_widgets.parameter_container import ParameterContainer
from string_parameter import StringParameter
from unit import Unit


def main():
    """Main function"""
    app = QApplication([])

    unit_feet = Unit('130790')
    unit_feet.load_dictionary(unit_feet_depth)

    unit_metres = Unit('900713')
    unit_metres.load_dictionary(unit_metres_depth)

    string_parameter = StringParameter('28082014')
    string_parameter.name = 'Province Name'
    string_parameter.help_text = 'Name of province.'
    string_parameter.description = (
        'A <b>test _description</b> that is very long so that you need to read '
        'it for one minute and you will be tired after read this description. '
        'You are the best user so far. Even better if you read this '
        'description loudly so that all of your friends will be able to hear '
        'you')
    string_parameter.is_required = True
    string_parameter.value = 'Daerah Istimewa Yogyakarta'

    boolean_parameter = BooleanParameter('1231231')
    boolean_parameter.name = 'Post processor'
    boolean_parameter.help_text = 'This is post processor parameter.'
    boolean_parameter.description = (
        'A <b>test _description</b> that is very long so that you need to read '
        'it for one minute and you will be tired after read this description. '
        'You are the best user so far. Even better if you read this '
        'description loudly so that all of your friends will be able to hear '
        'you')
    boolean_parameter.is_required = True
    boolean_parameter.value = True

    float_parameter = FloatParameter()
    float_parameter.name = 'Flood Depth'
    float_parameter.is_required = True
    float_parameter.precision = 3
    float_parameter.minimum_allowed_value = 1.0
    float_parameter.maximum_allowed_value = 2.0
    float_parameter.help_text = 'The depth of flood.'
    float_parameter.description = (
        'A <b>test _description</b> that is very long so that you need to read '
        'it for one minute and you will be tired after read this description. '
        'You are the best user so far. Even better if you read this '
        'description loudly so that all of your friends will be able to hear '
        'you')
    float_parameter.unit = unit_feet
    float_parameter.allowed_units = [unit_metres, unit_feet]
    float_parameter.value = 1.12

    integer_parameter = IntegerParameter()
    integer_parameter.name = 'Paper'
    integer_parameter.is_required = True
    integer_parameter.minimum_allowed_value = 1
    integer_parameter.maximum_allowed_value = 5
    integer_parameter.help_text = 'Number of paper'
    integer_parameter.description = (
        'A <b>test _description</b> that is very long so that you need to read '
        'it for one minute and you will be tired after read this description. '
        'You are the best user so far. Even better if you read this '
        'description loudly so that all of your friends will be able to hear '
        'you')
    integer_parameter.unit = unit_feet
    integer_parameter.allowed_units = [unit_feet]
    integer_parameter.value = 3

    parameters = [
        string_parameter,
        integer_parameter,
        boolean_parameter,
        float_parameter,
        float_parameter,
        boolean_parameter,
        integer_parameter]
    parameter_container = ParameterContainer(parameters)

    widget = QWidget()
    layout = QGridLayout()
    layout.addWidget(parameter_container)
    widget.setLayout(layout)
    widget.setGeometry(0, 0, 500, 500)

    widget.show()

    new_parameters = parameter_container.get_parameters()
    for new_parameter in new_parameters:
        print new_parameter.name, new_parameter.value

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
