# coding=utf-8
"""About Dialog."""

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA
from qgis.PyQt import QtGui, QtWidgets

from safe.common.version import get_version
from safe.definitions.messages import limitations, disclaimer
from safe.utilities.resources import resources_path, get_ui_class

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_ui_class('about_dialog_base.ui')


class AboutDialog(QtWidgets.QDialog, FORM_CLASS):

    """About dialog for the InaSAFE plugin."""

    def __init__(self, parent=None):
        """Constructor for the dialog.

        :param parent: Parent widget of this dialog
        :type parent: QWidget
        """

        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr('About InaSAFE %s' % get_version()))
        self.parent = parent

        icon = resources_path('img', 'icons', 'icon.png')
        self.setWindowIcon(QtGui.QIcon(icon))

        # Set Limitations Text
        limitations_text = ''
        for index, limitation in enumerate(limitations()):
            limitations_text += '%s. %s \n' % (index + 1, limitation)
        self.limitations_text.setFontPointSize(11)
        self.limitations_text.setText(limitations_text)

        # Set Disclaimer Text
        self.disclaimer_text.setFontPointSize(11)
        self.disclaimer_text.setText(disclaimer())

        # Set Attributions text
        image_credits_text = ''
        for index, limitation in enumerate(self.attributions()):
            image_credits_text += '%s. %s \n' % (index + 1, limitation)
        self.image_credits_text.setFontPointSize(11)
        self.image_credits_text.setText(image_credits_text)

        supporters_path = resources_path('img', 'logos', 'supporters.png')
        pixmap = QtGui.QPixmap(supporters_path)
        self.supporters_label.setPixmap(pixmap)

    def attributions(self):
        """List of attributions for icons etc."""
        attributes_list = list()
        attributes_list.append(self.tr(
            'Edit by Hugo Garduño from The Noun Project'))
        attributes_list.append(self.tr(
            '"Add icon" designed by Michael Zenaty from the Noun Project'))
        attributes_list.append(self.tr(
            '"Remove icon" designed by Dalpat Prajapati from the Noun '
            'Project'))
        attributes_list.append(self.tr('Humanitarian icons source: OCHA'))
        attributes_list.append(self.tr(
            '"Sign post" by Tara Swart from the Noun Project'))
        return attributes_list
