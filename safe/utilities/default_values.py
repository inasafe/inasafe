# coding=utf-8

"""Helpers to get/set default values."""

from safe.definitions import GLOBAL, zero_default_value
from safe.definitions.utilities import definition

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def set_inasafe_default_value_qsetting(
        qsetting, category, inasafe_field_key, value):
    """Helper method to set inasafe default value to qsetting.

    :param qsetting: QSettings.
    :type qsetting: QSettings

    :param category: Category of the default value. It can be global or
        recent. Global means the global setting for default value. Recent
        means the last set custom for default value from the user.
    :type category: str

    :param inasafe_field_key: Key for the field.
    :type inasafe_field_key: str

    :param value: Value of the inasafe_default_value.
    :type value: float, int
    """
    key = 'inasafe/default_value/%s/%s' % (category, inasafe_field_key)
    qsetting.setValue(key, value)


def get_inasafe_default_value_qsetting(
        qsetting, category, inasafe_field_key):
    """Helper method to get the inasafe default value from qsetting.

    :param qsetting: QSetting.
    :type qsetting: QSetting

    :param category: Category of the default value. It can be global or
        recent. Global means the global setting for default value. Recent
        means the last set custom for default value from the user.
    :type category: str

    :param inasafe_field_key: Key for the field.
    :type inasafe_field_key: str

    :returns: Value of the inasafe_default_value.
    :rtype: float
    """
    key = 'inasafe/default_value/%s/%s' % (category, inasafe_field_key)
    default_value = qsetting.value(key)
    if default_value is None:
        if category == GLOBAL:
            # If empty for global setting, use default one.
            inasafe_field = definition(inasafe_field_key)
            default_value = inasafe_field.get('default_value', {})
            return default_value.get('default_value', zero_default_value)

        return zero_default_value
    try:
        return float(default_value)
    except ValueError:
        return zero_default_value
