# coding=utf-8
"""Example usage of field mapping widget."""

import sys

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import get_qgis_app, load_test_vector_layer

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from PyQt4.QtGui import QApplication, QWidget, QGridLayout  # NOQA

from safe.gui.widgets.field_mapping_tab import FieldMappingTab  # NOQA
from safe.definitions.field_groups import age_ratio_group  # NOQA

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def main():
    """Main function to run the example."""
    layer = load_test_vector_layer(
        'aggregation', 'district_osm_jakarta.geojson', clone=True)

    app = QApplication([])

    field_mapping = FieldMappingTab(age_ratio_group, PARENT, IFACE)
    field_mapping.set_layer(layer)

    widget = QWidget()
    layout = QGridLayout()
    layout.addWidget(field_mapping)

    widget.setLayout(layout)

    widget.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
