import re
import os
from sqlite3 import OperationalError

# noinspection PyPackageRequirements
from PyQt4 import QtCore, QtGui
# noinspection PyPackageRequirements
from PyQt4.QtGui import QWidget, QListWidgetItem

from qgis.core import QgsCoordinateTransform

from safe.common.exceptions import (
    HashNotFoundError,
    NoKeywordsFoundError,
    KeywordNotFoundError,
    InvalidParameterError,
    UnsupportedProviderError)
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.resources import get_ui_class


def get_wizard_step_ui_class(py_file_name):
    return get_ui_class(os.path.join(
        'wizard', re.sub(r"pyc?$", "ui", os.path.basename(py_file_name))))


class WizardStep(QWidget):
    """A docstring."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        FOOOOOOOO Show the grid converter dialog.

        :param parent: parent - widget to use as parent.
        :type parent: QWidget

        """
        #TODO Docstring
        QWidget.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        self.keyword_io = KeywordIO()
        self.impact_function_manager = ImpactFunctionManager()


    # noinspection PyUnresolvedReferences,PyMethodMayBeStatic
    def auto_select_one_item(self, list_widget):
        """Select item in the list in list_widget if it's the only item.

        :param list_widget: The list widget that want to be checked.
        :type list_widget: QListWidget
        """
        if list_widget.count() == 1 and list_widget.currentRow() == -1:
            list_widget.setCurrentRow(0)

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
           no reason to block the Next button.

           This method must be implemented in derived classes.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return False

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

           This method must be implemented in derived classes.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        raise NotImplementedError("The current step class doesn't implement \
            the get_previous_step method")

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

           This method must be implemented in derived classes.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        raise NotImplementedError("The current step class doesn't implement \
            the get_next_step method")

    def set_widgets(self):
        """Set all widgets on the tab.

           This method must be implemented in derived classes.
        """
        raise NotImplementedError("The current step class doesn't implement \
            the set_widgets method")

    def layers_intersect(self, layer_a, layer_b):
        """Check if extents of two layers intersect.

           A helper function

        :param layer_a: One of the two layers to test overlapping
        :type layer_a: QgsMapLayer

        :param layer_b: The second of the two layers to test overlapping
        :type layer_b: QgsMapLayer

        :returns: true if the layers intersect, false if they are disjoint
        :rtype: boolean
        """
        extent_a = layer_a.extent()
        extent_b = layer_b.extent()
        if layer_a.crs() != layer_b.crs():
            coord_transform = QgsCoordinateTransform(
                layer_a.crs(), layer_b.crs())
            extent_b = (coord_transform.transform(
                extent_b, QgsCoordinateTransform.ReverseTransform))
        return extent_a.intersects(extent_b)

    def get_compatible_layers_from_canvas(self, category):
        """Collect compatible layers from map canvas.

        .. note:: Returns layers with keywords and layermode matching
           the category and compatible with the selected impact function.
           Also returns layers without keywords with layermode
           compatible with the selected impact function.

        :param category: The category to filter for.
        :type category: string

        :returns: Metadata of found layers.
        :rtype: list of dicts
        """

        # Collect compatible layers
        layers = []
        for layer in self.parent.iface.mapCanvas().layers():
            try:
                keywords = self.keyword_io.read_keywords(layer)
                if ('layer_purpose' not in keywords and
                        'impact_summary' not in keywords):
                    keywords = None
            except (HashNotFoundError,
                    OperationalError,
                    NoKeywordsFoundError,
                    KeywordNotFoundError,
                    InvalidParameterError,
                    UnsupportedProviderError):
                keywords = None

            if self.parent.is_layer_compatible(layer, category, keywords):
                layers += [
                    {'id': layer.id(),
                     'name': layer.name(),
                     'keywords': keywords}]

        # Move layers without keywords to the end
        l1 = [l for l in layers if l['keywords']]
        l2 = [l for l in layers if not l['keywords']]
        layers = l1 + l2

        return layers

    def list_compatible_layers_from_canvas(self, category, list_widget):
        """Fill given list widget with compatible layers.

        .. note:: Uses get_compatible_layers_from_canvas() to filter layers

        :param category: The category to filter for.
        :type category: string

        :param list_widget: The list widget to be filled with layers.
        :type list_widget: QListWidget


        :returns: Metadata of found layers.
        :rtype: list of dicts
        """

        italic_font = QtGui.QFont()
        italic_font.setItalic(True)

        # Add compatible layers
        list_widget.clear()
        for layer in self.get_compatible_layers_from_canvas(category):
            item = QListWidgetItem(layer['name'], list_widget)
            item.setData(QtCore.Qt.UserRole, layer['id'])
            if not layer['keywords']:
                item.setFont(italic_font)
            list_widget.addItem(item)
