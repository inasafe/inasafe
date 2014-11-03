# coding=utf-8

"""Simple example of using parameters to define a parameter - how meta!"""

__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'main'
__date__ = '8/19/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

import sys

from PyQt4.QtGui import QApplication, QWidget, QGridLayout
from float_parameter import FloatParameter
from integer_parameter import IntegerParameter
from qt_widgets.parameter_container import ParameterContainer
from string_parameter import StringParameter


def main():
    """Main function"""
    app = QApplication([])

    name_parameter = StringParameter('UUID-1')
    name_parameter.name = 'Resource name'
    name_parameter.help_text = (
        'Name of the resource that will be provided as part of minimum needs.'
        'e.g. Tea, Water etc.')
    name_parameter.description = (
        'A <b>resource</b> is something that you provide to displaced persons '
        'in the event of a disaster. The resource will be made available '
        'at IDP camps and may need to be stockpiled by contingency planners '
        'in their preparations for a disaster.')
    name_parameter.is_required = True
    name_parameter.value = ''

    description_parameter = StringParameter('UUID-1')
    description_parameter.name = 'Resource description'
    description_parameter.help_text = (
        'Description of the resource that will be provided as part of minimum '
        'needs. e.g. Tea, Water etc.')
    description_parameter.description = (
        'Description of the resource that will be provided as part of minimum '
        'needs. e.g. Tea, Water etc.')
    description_parameter.is_required = True
    description_parameter.value = ''

    unit_parameter = StringParameter('UUID-2')
    unit_parameter.name = 'Units'
    unit_parameter.help_text = (
        'Unit for the resources. e.g. litres, kg etc.')
    unit_parameter.description = (
        'A <b>unit</b> the basic measurement unit used for computing the '
        'allowance per individual. For example when planning water rations '
        'the units would be litres.')
    unit_parameter.is_required = True
    unit_parameter.value = ''

    minimum_parameter = FloatParameter('UUID-3')
    minimum_parameter.name = 'Minimum allowed'
    minimum_parameter.is_required = True
    minimum_parameter.precision = 3
    minimum_parameter.minimum_allowed_value = -99999.0
    minimum_parameter.maximum_allowed_value = 99999.0
    minimum_parameter.help_text = 'The minimum allowable quantity per person. '
    minimum_parameter.description = (
        'The <b>minimum</b> is the minimum allowed quantity of the resource '
        'per person. For example you may dictate that the water ration per '
        'person per day should never be allowed to be less than 0.5l.')
    minimum_parameter.value = 1.0

    maximum_parameter = FloatParameter('UUID-3')
    maximum_parameter.name = 'Minimum allowed'
    maximum_parameter.is_required = True
    maximum_parameter.precision = 3
    maximum_parameter.minimum_allowed_value = -99999.0
    maximum_parameter.maximum_allowed_value = 99999.0
    maximum_parameter.help_text = 'The maximum allowable quantity per person. '
    maximum_parameter.description = (
        'The <b>maximum</b> is the maximum allowed quantity of the resource '
        'per person. For example you may dictate that the water ration per '
        'person per day should never be allowed to be more than 50l.')
    maximum_parameter.value = 1.0

    maximum_parameter = FloatParameter('UUID-4')
    maximum_parameter.name = 'Minimum allowed'
    maximum_parameter.is_required = True
    maximum_parameter.precision = 3
    maximum_parameter.minimum_allowed_value = -99999.0
    maximum_parameter.maximum_allowed_value = 99999.0
    maximum_parameter.help_text = 'The maximum allowable quantity per person. '
    maximum_parameter.description = (
        'The <b>maximum</b> is the maximum allowed quantity of the resource '
        'per person. For example you may dictate that the water ration per '
        'person per day should never be allowed to be more than 50l.')
    maximum_parameter.value = 1.0

    default_parameter = FloatParameter('UUID-5')
    default_parameter.name = 'Default'
    default_parameter.is_required = True
    default_parameter.precision = 3
    default_parameter.minimum_allowed_value = -99999.0
    default_parameter.default_allowed_value = 99999.0
    default_parameter.help_text = 'The default allowable quantity per person. '
    default_parameter.description = (
        'The <b>default</b> is the default allowed quantity of the resource '
        'per person. For example you may indicate that the water ration per '
        'person per day should be 25l.')
    default_parameter.value = 1.0

    parameters = [
        name_parameter,
        description_parameter,
        unit_parameter,
        minimum_parameter,
        maximum_parameter,
        default_parameter]
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
