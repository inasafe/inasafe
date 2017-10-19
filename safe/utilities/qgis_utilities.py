# coding=utf-8

"""QGIS utilities for InaSAFE."""

from PyQt4.QtGui import QMessageBox, QPushButton
from qgis.core import QGis, QgsProject, QgsMapLayerRegistry, QgsLayerTreeLayer
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def add_above_layer(new_layer, *existing_layers):
    """Add a layer (e.g. impact layer) above another layer in the legend.

    .. versionadded:: 3.2

    .. note:: This method works in QGIS 2.4 and better only. In
        earlier versions it will just add the layer to the top of the
        layer stack.

    .. seealso:: issue #2322

    :param existing_layers: Layers which the new layer
        should be added above.
    :type existing_layers: QgsMapLayer

    :param new_layer: The new layer being added. An assumption is made
        that the newly added layer is not already loaded in the legend
        or the map registry.
    :type new_layer: QgsMapLayer

    """
    # Some existing layers might be None, ie the aggregation layer #2948.
    existing_layers = [l for l in existing_layers if l is not None]
    if not len(existing_layers) or new_layer is None:
        return

    registry = QgsMapLayerRegistry.instance()

    if QGis.QGIS_VERSION_INT < 20400:
        # True flag adds layer directly to legend
        registry.addMapLayer(existing_layers, True)
        return

    # False flag prevents layer being added to legend
    registry.addMapLayer(new_layer, False)
    minimum_index = len(QgsProject.instance().layerTreeRoot().children())
    for layer in existing_layers:
        index = layer_legend_index(layer)
        if index < minimum_index:
            minimum_index = index
    root = QgsProject.instance().layerTreeRoot()
    root.insertLayer(minimum_index, new_layer)


def layer_legend_index(layer):
    """Find out where in the legend layer stack a layer is.

    .. note:: This function requires QGIS 2.4 or greater to work. In older
        versions it will simply return 0.

    .. version_added:: 3.2

    :param layer: A map layer currently loaded in the legend.
    :type layer: QgsMapLayer

    :returns: An integer representing the z-order of the given layer in
        the legend tree. If the layer cannot be found, or the QGIS version
        is < 2.4 it will return 0.
    :rtype: int
    """
    if QGis.QGIS_VERSION_INT < 20400:
        return 0

    root = QgsProject.instance().layerTreeRoot()
    layer_id = layer.id()
    current_index = 0
    nodes = root.children()
    for node in nodes:
        # check if the node is a layer as opposed to a group
        if isinstance(node, QgsLayerTreeLayer):
            if layer_id == node.layerId():
                return current_index
        current_index += 1
    return current_index


def display_information_message_box(
        parent=None, title=None, message=None):
    """
    Display an information message box.

    :param title: The title of the message box.
    :type title: str

    :param message: The message inside the message box.
    :type message: str
    """
    QMessageBox.information(parent, title, message)


def display_information_message_bar(
        title=None,
        message=None,
        more_details=None,
        button_text=tr('Show details ...'),
        duration=8):
    """
    Display an information message bar.

    :param iface: The QGIS IFace instance. Note that we cannot
        use qgis.utils.iface since it is not available in our
        test environment.
    :type iface: QgisInterface

    :param title: The title of the message bar.
    :type title: str

    :param message: The message inside the message bar.
    :type message: str

    :param more_details: The message inside the 'Show details' button.
    :type more_details: str

    :param button_text: The text of the button if 'more_details' is not empty.
    :type button_text: str

    :param duration: The duration for the display, default is 8 seconds.
    :type duration: int
    """
    iface.messageBar().clearWidgets()
    widget = iface.messageBar().createMessage(title, message)

    if more_details:
        button = QPushButton(widget)
        button.setText(button_text)
        button.pressed.connect(
            lambda: display_information_message_box(
                title=title, message=more_details))
        widget.layout().addWidget(button)

    iface.messageBar().pushWidget(widget, QgsMessageBar.INFO, duration)


def display_success_message_bar(
        title=None,
        message=None,
        more_details=None,
        button_text=tr('Show details ...'),
        duration=8):
    """
    Display a success message bar.

    :param iface: The QGIS IFace instance. Note that we cannot
        use qgis.utils.iface since it is not available in our
        test environment.
    :type iface: QgisInterface

    :param title: The title of the message bar.
    :type title: str

    :param message: The message inside the message bar.
    :type message: str

    :param more_details: The message inside the 'Show details' button.
    :type more_details: str

    :param button_text: The text of the button if 'more_details' is not empty.
    :type button_text: str

    :param duration: The duration for the display, default is 8 seconds.
    :type duration: int
    """

    iface.messageBar().clearWidgets()
    widget = iface.messageBar().createMessage(title, message)

    if more_details:
        button = QPushButton(widget)
        button.setText(button_text)
        button.pressed.connect(
            lambda: display_information_message_box(
                title=title, message=more_details))
        widget.layout().addWidget(button)

    if QGis.QGIS_VERSION_INT >= 20700:
        iface.messageBar().pushWidget(widget, QgsMessageBar.SUCCESS, duration)
    else:
        iface.messageBar().pushWidget(widget, QgsMessageBar.INFO, duration)


def display_warning_message_box(parent=None, title=None, message=None):
    """
    Display a warning message box.

    :param title: The title of the message box.
    :type title: str

    :param message: The message inside the message box.
    :type message: str
    """
    QMessageBox.warning(parent, title, message)


def display_warning_message_bar(
        title=None,
        message=None,
        more_details=None,
        button_text=tr('Show details ...'),
        duration=8):
    """
    Display a warning message bar.

    :param title: The title of the message bar.
    :type title: str

    :param message: The message inside the message bar.
    :type message: str

    :param more_details: The message inside the 'Show details' button.
    :type more_details: str

    :param button_text: The text of the button if 'more_details' is not empty.
    :type button_text: str

    :param duration: The duration for the display, default is 8 seconds.
    :type duration: int
    """

    iface.messageBar().clearWidgets()
    widget = iface.messageBar().createMessage(title, message)

    if more_details:
        button = QPushButton(widget)
        button.setText(button_text)
        button.pressed.connect(
            lambda: display_warning_message_box(
                title=title, message=more_details))
        widget.layout().addWidget(button)

    iface.messageBar().pushWidget(widget, QgsMessageBar.WARNING, duration)


def display_critical_message_box(parent=None, title=None, message=None):
    """
    Display a critical message box.

    :param title: The title of the message box.
    :type title: str

    :param message: The message inside the message box.
    :type message: str
    """
    QMessageBox.critical(parent, title, message)


def display_critical_message_bar(
        title=None,
        message=None,
        more_details=None,
        button_text=tr('Show details ...'),
        duration=8):
    """
    Display a critical message bar.

    :param title: The title of the message bar.
    :type title: str

    :param message: The message inside the message bar.
    :type message: str

    :param more_details: The message inside the 'Show details' button.
    :type more_details: str

    :param button_text: The text of the button if 'more_details' is not empty.
    :type button_text: str

    :param duration: The duration for the display, default is 8 seconds.
    :type duration: int
    """

    iface.messageBar().clearWidgets()
    widget = iface.messageBar().createMessage(title, message)

    if more_details:
        button = QPushButton(widget)
        button.setText(button_text)
        button.pressed.connect(
            lambda: display_critical_message_box(
                title=title, message=more_details))
        widget.layout().addWidget(button)

    iface.messageBar().pushWidget(widget, QgsMessageBar.CRITICAL, duration)
