# coding=utf-8
"""Helper function for InaSAFE settings."""

from qgis.PyQt.QtCore import QSettings
from safe.definitionsv4 import GLOBAL, zero_default_value
from safe.definitionsv4.utilities import definition
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

APPLICATION_NAME = 'inasafe'


def setting(key, default=None, expected_type=None, qsettings=None):
    """Helper function to get a value from settings.

    :param key: Unique key for setting.
    :type key: basestring

    :param default: The default value in case of the key is not found or there
        is an error.
    :type default: basestring, None, boolean, int, float

    :param expected_type: The type of object expected.
    :type expected_type: basestring, None, boolean, int, float

    :param qsettings: A custom QSettings to use. If it's not defined, it will
        use the default one.
    :type qsettings: qgis.PyQt.QtCore.QSettings
    """
    if not qsettings:
        qsettings = QSettings()

    key = '%s/%s' % (APPLICATION_NAME, key)

    if default and expected_type:
        if not isinstance(default, expected_type):
            raise Exception(
                tr('The default value do not match the expected type.'))

    try:
        if default:
            value = qsettings.value(key, default)
        else:
            value = qsettings.value(key)
    except TypeError:
        # Catch error : unable to convert a QVariant to a QMetaType.
        return default

    else:
        if default is not None and \
                expected_type and not isinstance(value, expected_type):
            value = expected_type(value)

        return value


def set_setting(key, value, qsettings=None):
    """Set value to QSettings based on key.

    :param key: Unique key for setting.
    :type key: basestring

    :param value: Value to be saved.
    :type value: QVariant

    :param qsettings: A custom QSettings to use. If it's not defined, it will
        use the default one.
    :type qsettings: qgis.PyQt.QtCore.QSettings
    """
    if not qsettings:
        qsettings = QSettings()

    key = '%s/%s' % (APPLICATION_NAME, key)
    qsettings.setValue(key, value)


def set_inasafe_default_value_qsetting(
        qsetting, category, inasafe_field_key, value):
    """Helper method to set inasafe default value to qsetting.

    :param qsetting: QSettings
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

    :param qsetting: QSetting
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
