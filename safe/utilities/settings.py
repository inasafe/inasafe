# coding=utf-8
"""Helper function for InaSAFE settings."""

import json
import logging

from PyQt4.QtCore import QSettings, QPyNullVariant

from safe.definitions import APPLICATION_NAME
from safe.definitions.default_settings import inasafe_default_settings

LOGGER = logging.getLogger("InaSAFE")
__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


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

    qsettings.setValue(key, value)


def general_setting(key, default=None, expected_type=None, qsettings=None):
    """Helper function to get a value from settings.

    :param key: Unique key for setting.
    :type key: basestring

    :param default: The default value in case of the key is not found or there
        is an error.
    :type default: basestring, None, boolean, int, float

    :param expected_type: The type of object expected.
    :type expected_type: type

    :param qsettings: A custom QSettings to use. If it's not defined, it will
        use the default one.
    :type qsettings: qgis.PyQt.QtCore.QSettings

    :returns: The value of the key in the setting.
    :rtype: object

    Note:
    The API for QSettings to get a value is different for PyQt and Qt C++.
    In PyQt we can specify the expected type.
    See: http://pyqt.sourceforge.net/Docs/PyQt4/qsettings.html#value
    """
    if qsettings is None:
        qsettings = QSettings()
    try:
        if isinstance(expected_type, type):
            return qsettings.value(key, default, type=expected_type)
        else:
            return qsettings.value(key, default)

    except TypeError as e:
        LOGGER.debug('exception %s' % e)
        LOGGER.debug('%s %s %s' % (key, default, expected_type))
        return qsettings.value(key, default)


def delete_general_setting(key, qsettings=None):
    """Delete setting from QSettings.

    :param key: unique key for setting.
    :type key: basestring

    :param qsettings: A custom QSettings to use. If it's not defined, it will
    use the default one.
    :type qsettings: qgis.PyQt.QtCore.QSettings
    """
    if not qsettings:
        qsettings = QSettings()

    qsettings.remove(key)


def set_setting(key, value, qsettings=None):
    """Set value to QSettings based on key in InaSAFE scope.

    :param key: Unique key for setting.
    :type key: basestring

    :param value: Value to be saved.
    :type value: QVariant

    :param qsettings: A custom QSettings to use. If it's not defined, it will
        use the default one.
    :type qsettings: qgis.PyQt.QtCore.QSettings
    """
    full_key = '%s/%s' % (APPLICATION_NAME, key)
    set_general_setting(full_key, value, qsettings)


def setting(key, default=None, expected_type=None, qsettings=None):
    """Helper function to get a value from settings under InaSAFE scope.

    :param key: Unique key for setting.
    :type key: basestring

    :param default: The default value in case of the key is not found or there
        is an error.
    :type default: basestring, None, boolean, int, float

    :param expected_type: The type of object expected.
    :type expected_type: type

    :param qsettings: A custom QSettings to use. If it's not defined, it will
        use the default one.
    :type qsettings: qgis.PyQt.QtCore.QSettings

    :returns: The value of the key in the setting.
    :rtype: object
    """
    if default is None:
        default = inasafe_default_settings.get(key, None)
    full_key = '%s/%s' % (APPLICATION_NAME, key)
    return general_setting(full_key, default, expected_type, qsettings)


def delete_setting(key, qsettings=None):
    """Delete setting from QSettings under InaSAFE scope.

    :param key: Unique key for setting.
    :type key: basestring

    :param qsettings: A custom QSettings to use. If it's not defined, it will
        use the default one.
    :type qsettings: qgis.PyQt.QtCore.QSettings
    """
    full_key = '%s/%s' % (APPLICATION_NAME, key)
    delete_general_setting(full_key, qsettings)


def export_setting(file_path, qsettings=None):
    """Export InaSAFE's setting to a file.

    :param file_path: The file to write the exported setting.
    :type file_path: basestring

    :param qsettings: A custom QSettings to use. If it's not defined, it will
        use the default one.
    :type qsettings: qgis.PyQt.QtCore.QSettings

    :returns: A dictionary of the exported settings.
    :rtype: dict
    """
    inasafe_settings = {}

    if not qsettings:
        qsettings = QSettings()

    qsettings.beginGroup('inasafe')
    all_keys = qsettings.allKeys()
    qsettings.endGroup()

    for key in all_keys:
        inasafe_settings[key] = setting(key, qsettings=qsettings)

    def custom_default(obj):
        if isinstance(obj, QPyNullVariant):
            return ''
        raise TypeError

    with open(file_path, 'w') as json_file:
        json.dump(
            inasafe_settings, json_file, indent=2, default=custom_default)

    return inasafe_settings


def import_setting(file_path, qsettings=None):
    """Import InaSAFE's setting from a file.

    :param file_path: The file to read the imported setting.
    :type file_path: basestring

    :param qsettings: A custom QSettings to use. If it's not defined, it will
        use the default one.
    :type qsettings: qgis.PyQt.QtCore.QSettings

    :returns: A dictionary of the imported settings.
    :rtype: dict
    """
    with open(file_path, 'r') as f:
        inasafe_settings = json.load(f)

    if not qsettings:
        qsettings = QSettings()

    # Clear the previous setting
    qsettings.beginGroup('inasafe')
    qsettings.remove('')
    qsettings.endGroup()

    for key, value in inasafe_settings.items():
        set_setting(key, value, qsettings=qsettings)

    return inasafe_settings
