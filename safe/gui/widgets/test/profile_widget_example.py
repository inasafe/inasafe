# coding=utf-8
"""Example usage of Profile Widget."""

import sys
import qgis  # NOQA

from PyQt4.QtGui import QWidget, QGridLayout, QPushButton

from functools import partial
from safe.definitions.utilities import generate_default_profile
from safe.gui.widgets.profile_widget import ProfileWidget
from safe.test.qgis_app import qgis_app

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


# noinspection PyUnresolvedReferences
def main():
    """Main function to run the example."""
    def print_values(the_profile_widget):
        data = the_profile_widget.data
        from pprint import pprint
        pprint(data)

    def clear_widget(the_profile_widget):
        the_profile_widget.clear()

    def restore_data(the_profile_widget):
        the_profile_widget.clear()
        the_profile_widget.data = generate_default_profile()

    app, iface = qgis_app()

    default_profile = generate_default_profile()
    profile_widget = ProfileWidget(data=default_profile)

    get_result_button = QPushButton('Get result...')
    get_result_button.clicked.connect(
        partial(print_values, profile_widget))

    clear_button = QPushButton('Clear widget...')
    clear_button.clicked.connect(
        partial(clear_widget, profile_widget))

    restore_button = QPushButton('Restore data...')
    restore_button.clicked.connect(
        partial(restore_data, profile_widget))

    widget = QWidget()
    layout = QGridLayout()
    layout.addWidget(profile_widget)
    layout.addWidget(restore_button)
    layout.addWidget(get_result_button)
    layout.addWidget(clear_button)

    widget.setLayout(layout)

    widget.setFixedHeight(600)
    widget.setFixedWidth(800)
    widget.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
