# coding=utf-8
"""Helper function for InaSAFE settings."""

from PyQt4.QtCore import QSettings
from safe.utilities.i18n import tr
from safe.definitions.default_settings import inasafe_default_settings

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
    if default is None:
        default = inasafe_default_settings.get(key, None)
    full_key = '%s/%s' % (APPLICATION_NAME, key)
    return general_setting(full_key, default, expected_type, qsettings)


def general_setting(key, default=None, expected_type=None, qsettings=None):
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
        if value in ['true', 'True', 'false', 'False']:
            expected_type = bool
        if default is not None and \
                expected_type and not isinstance(value, expected_type):
            # If expected value is boolean, make sure it will return boolean.
            if expected_type == bool and value in ['true', 'True']:
                value = True
            elif expected_type == bool:
                value = False
            else:
                value = expected_type(value)

        return value


def set_general_setting(key, value, qsettings=None):
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


def delete_setting(key):
    """ Delete setting from QSettings.

    :param key: unique key for setting.
    :type key: basestring
    """
    settings = QSettings()
    settings.remove('%s/%s' % (APPLICATION_NAME, key))
