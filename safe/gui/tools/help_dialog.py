# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **About Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""
__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '28/09/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from PyQt4 import QtGui

from safe.common.version import get_version
from safe.utilities.resources import get_ui_class, html_footer, html_header
from safe.gui.tools.help.dock_help import dock_help

FORM_CLASS = get_ui_class('help_dialog_base.ui')


class HelpDialog(QtGui.QDialog, FORM_CLASS):
    """About dialog for the InaSAFE plugin."""

    def __init__(self, parent=None):
        """Constructor for the dialog.

        :param parent: Parent widget of this dialog
        :type parent: QWidget
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr('InaSAFE %s Help' % get_version()))
        self.parent = parent

        header = html_header()
        footer = html_footer()

        string = header

        message = dock_help()

        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)
