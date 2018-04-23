# coding=utf-8

"""Geonode uploader."""


from requests.compat import urljoin

from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsMapLayerRegistry

from safe.gui.gui_utilities import layer_from_combo
from safe.utilities.geonode.upload_layer_requests import (
    extension_siblings, login_user, upload)
from safe.utilities.gis import qgis_version, layer_icon
from safe.utilities.i18n import tr
from safe.utilities.qgis_utilities import (
    display_warning_message_box, display_success_message_bar)
from safe.utilities.qt import disable_busy_cursor, enable_busy_cursor
from safe.utilities.resources import get_ui_class, resources_path
from safe.utilities.settings import set_setting, setting

__copyright__ = 'Copyright 2018, The InaSAFE Project'
__license__ = 'GPL version 3'
__email__ = 'info@inasafe.org'
__revision__ = '$Format:%H$'


FORM_CLASS = get_ui_class('geonode_uploader.ui')
GEONODE_USER = 'geonode_user'
GEONODE_PASSWORD = 'geonode_password'
GEONODE_URL = 'geonode_url'


class GeonodeUploaderDialog(QDialog, FORM_CLASS):

    """Geonode uploader dialog."""

    def __init__(self, parent=None):
        """Constructor for import dialog.

        :param parent: Optional widget to use as parent.
        :type parent: QWidget
        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        icon = resources_path('img', 'icons', 'geonode.png')
        self.setWindowIcon(QIcon(icon))

        self.header.setText(tr(
            'In this dialog, you can upload a layer to a Geonode instance. '
            'If you want to upload the style, you need to save it as default '
            'in the layer properties. '
            'This tool might not work if you are behind a proxy. '
            'If you save your credentials, it will be stored in plain text in '
            'your QGIS settings. '
            'The layer must be file based, only these extensions are '
            'supported: {}.').format(', '.join(list(extension_siblings.keys()))))

        # Fix for issue 1699 - cancel button does nothing
        cancel_button = self.button_box.button(QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(self.reject)
        # Fix ends
        self.ok_button = self.button_box.button(QDialogButtonBox.Ok)
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)

        reset_defaults = self.button_box.button(
            QDialogButtonBox.RestoreDefaults)
        reset_defaults.clicked.connect(self.reset_defaults)

        self.fill_layer_combo()

        # Connect
        self.layers.currentIndexChanged.connect(self.check_ok_button)
        self.login.textChanged.connect(self.check_ok_button)
        self.password.textChanged.connect(self.check_ok_button)
        self.url.textChanged.connect(self.check_ok_button)

        self.save_login.setChecked(False)
        self.save_password.setChecked(False)
        self.save_url.setChecked(False)

        # Pre fill the form
        login = setting(GEONODE_USER, '', str)
        if login:
            self.login.setText(login)
            self.save_login.setChecked(True)

        password = setting(GEONODE_PASSWORD, '', str)
        if password:
            self.password.setText(password)
            self.save_password.setChecked(True)

        url = setting(GEONODE_URL, '', str)
        if url:
            self.url.setText(url)
            self.save_url.setChecked(True)

        self.check_ok_button()

    def reset_defaults(self):
        """Reset login and password in QgsSettings."""
        self.save_login.setChecked(False)
        self.save_password.setChecked(False)
        self.save_url.setChecked(False)

        set_setting(GEONODE_USER, '')
        set_setting(GEONODE_PASSWORD, '')
        set_setting(GEONODE_URL, '')

        self.login.setText('')
        self.password.setText('')
        self.url.setText('')

    def fill_layer_combo(self):
        """Fill layer combobox."""
        project = QgsProject.instance()
        # MapLayers returns a QMap<QString id, QgsMapLayer layer>
        layers = list(project.mapLayers().values())

        extensions = tuple(extension_siblings.keys())
        for layer in layers:
            if layer.source().lower().endswith(extensions):
                icon = layer_icon(layer)
                self.layers.addItem(icon, layer.name(), layer.id())

    def check_ok_button(self):
        """Helper to enable or not the OK button."""
        login = self.login.text()
        password = self.password.text()
        url = self.url.text()
        if self.layers.count() >= 1 and login and password and url:
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)

    def accept(self):
        """Upload the layer to Geonode."""
        enable_busy_cursor()
        self.button_box.setEnabled(False)
        layer = layer_from_combo(self.layers)

        login = self.login.text()
        if self.save_login.isChecked():
            set_setting(GEONODE_USER, login)
        else:
            set_setting(GEONODE_USER, '')

        password = self.password.text()
        if self.save_password.isChecked():
            set_setting(GEONODE_PASSWORD, password)
        else:
            set_setting(GEONODE_PASSWORD, '')

        url = self.url.text()
        if self.save_url.isChecked():
            set_setting(GEONODE_URL, url)
        else:
            set_setting(GEONODE_URL, '')

        geonode_session = login_user(url, login, password)

        result = upload(url, geonode_session, layer.source())
        self.button_box.setEnabled(True)
        disable_busy_cursor()

        if result['success']:
            self.done(QDialog.Accepted)
            layer_url = urljoin(url, result['url'])
            # Link is not working in QGIS 2.
            # It's gonna work in QGIS 3.
            if qgis_version() >= 29900:
                external_link = '<a href=\"{url}\">{url}</a>'.format(
                    url=layer_url)
            else:
                external_link = layer_url

            display_success_message_bar(
                tr('Uploading done'),
                tr('Successfully uploaded to {external_link}').format(
                    external_link=external_link)
            )
        else:
            display_warning_message_box(
                self,
                tr('Error while uploading the layer.'),
                str(result)
            )
