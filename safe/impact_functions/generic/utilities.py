# coding=utf-8
from safe.utilities.i18n import tr

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '11/06/15'


def increasing_validator(parameters=None):
    """Custom validator to use with Group Parameter.

    Validator to make sure the threshold or input value of hazard classes
    is monotonically increasing
    :param parameters: the list of parameters to check FloatParameter
    :type parameters: list[FloatParameter]
    """
    previous = None
    valid = True
    for p in parameters:
        if previous and p.value <= previous:
            valid = False
            break
        elif not previous:
            previous = p.value

    if not valid:
        message = tr(
            'Each threshold should be greater than the previous '
            'threshold')
        raise ValueError(message)
