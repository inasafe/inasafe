# coding=utf-8

"""GUI utilities for the dock and the multi Exposure Tool."""
from past.builtins import cmp


from qgis.PyQt.QtCore import Qt
from qgis.core import QgsMapLayerRegistry

from safe.utilities.i18n import tr


def layer_from_combo(combo):
    """Get the QgsMapLayer currently selected in a combo.

    Obtain QgsMapLayer id from the userrole of the QtCombo and return it as a
    QgsMapLayer.

    :returns: The currently selected map layer a combo.
    :rtype: QgsMapLayer
    """
    index = combo.currentIndex()
    if index < 0:
        return None

    layer_id = combo.itemData(index, Qt.UserRole)
    layer = QgsProject.instance().mapLayer(layer_id)
    return layer


def add_ordered_combo_item(
        combo, text, data=None, count_selected_features=None, icon=None):
    """Add a combo item ensuring that all items are listed alphabetically.

    Although QComboBox allows you to set an InsertAlphabetically enum
    this only has effect when a user interactively adds combo items to
    an editable combo. This we have this little function to ensure that
    combos are always sorted alphabetically.

    :param combo: Combo box receiving the new item.
    :type combo: QComboBox

    :param text: Display text for the combo.
    :type text: str

    :param data: Optional UserRole data to be associated with the item.
    :type data: QVariant, str

    :param count_selected_features: A count to display if the layer has some
    selected features. Default to None, nothing will be displayed.
    :type count_selected_features: None, int

    :param icon: Icon to display in the combobox.
    :type icon: QIcon
    """
    if count_selected_features is not None:
        text += ' (' + tr('{count} selected features').format(
            count=count_selected_features) + ')'
    size = combo.count()
    for combo_index in range(0, size):
        item_text = combo.itemText(combo_index)
        # see if text alphabetically precedes item_text
        if cmp(text.lower(), item_text.lower()) < 0:
            if icon:
                combo.insertItem(combo_index, icon, text, data)
            else:
                combo.insertItem(combo_index, text, data)
            return

    # otherwise just add it to the end
    if icon:
        combo.insertItem(size, icon, text, data)
    else:
        combo.insertItem(size, text, data)
