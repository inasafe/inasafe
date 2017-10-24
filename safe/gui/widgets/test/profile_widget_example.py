# coding=utf-8
"""Example usage of Profile Widget."""

import sys

from safe.test.utilities import get_qgis_app, load_test_vector_layer

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from PyQt4.QtGui import QApplication, QWidget, QGridLayout  # NOQA

from safe.gui.widgets.profile_widget import ProfileWidget  # NOQA
from safe.definitions.utilities import generate_default_profile

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def main():
    """Main function to run the example."""
    app = QApplication([])

    default_profile = generate_default_profile()
    profile_widget = ProfileWidget(parent=PARENT, data=default_profile)

    widget = QWidget()
    layout = QGridLayout()
    layout.addWidget(profile_widget)

    widget.setLayout(layout)

    widget.setFixedHeight(500)
    widget.setFixedWidth(500)
    widget.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
