# coding=utf-8
"""InaSAFE Wizard Step Layer Purpose Type."""


from qgis.PyQt import QtCore
from qgis.PyQt.QtWidgets import QListWidgetItem
from qgis.PyQt.QtGui import QPixmap

from safe import messaging as m
from safe.definitions.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard)
from safe.definitions.utilities import (
    hazards_for_layer,
    definition,
    exposures_for_layer)
from safe.gui.tools.wizard.utilities import get_question_text, get_image_path
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.utilities.gis import is_raster_layer
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwSubcategory(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Layer Purpose Type."""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_subcategory())

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.parent.step_kw_purpose.\
                selected_purpose() == layer_purpose_hazard:
            new_step = self.parent.step_kw_hazard_category
        else:
            if is_raster_layer(self.parent.layer):
                new_step = self.parent.step_kw_band_selector
            else:
                new_step = self.parent.step_kw_layermode
        return new_step

    def subcategories_for_layer(self):
        """Return a list of valid subcategories for a layer.
           Subcategory is hazard type or exposure type.

        :returns: A list where each value represents a valid subcategory.
        :rtype: list
        """
        purpose = self.parent.step_kw_purpose.selected_purpose()
        layer_geometry_key = self.parent.get_layer_geometry_key()
        if purpose == layer_purpose_hazard:
            return hazards_for_layer(layer_geometry_key)
        elif purpose == layer_purpose_exposure:
            return exposures_for_layer(layer_geometry_key)

    # noinspection PyPep8Naming
    def on_lstSubcategories_itemSelectionChanged(self):
        """Update subcategory description label.

        .. note:: This is an automatic Qt slot
           executed when the subcategory selection changes.
        """
        self.clear_further_steps()
        # Set widgets
        subcategory = self.selected_subcategory()
        # Exit if no selection
        if not subcategory:
            return
        # Set description label
        self.lblDescribeSubcategory.setText(subcategory['description'])

        icon_path = get_image_path(subcategory)

        self.lblIconSubcategory.setPixmap(QPixmap(icon_path))
        # Enable the next button
        self.parent.pbnNext.setEnabled(True)

    def selected_subcategory(self):
        """Obtain the subcategory selected by user.

        :returns: Metadata of the selected subcategory.
        :rtype: dict, None
        """
        item = self.lstSubcategories.currentItem()
        try:
            return definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def clear_further_steps(self):
        """Clear all further steps in order to properly calculate the prev step
        """
        self.parent.step_kw_hazard_category.lstHazardCategories.clear()
        self.parent.step_kw_layermode.lstLayerModes.clear()
        self.parent.step_kw_unit.lstUnits.clear()
        self.parent.step_kw_field.lstFields.clear()
        self.parent.step_kw_classification.lstClassifications.clear()

    def set_widgets(self):
        """Set widgets on the Subcategory tab."""
        self.clear_further_steps()
        # Set widgets
        purpose = self.parent.step_kw_purpose.selected_purpose()
        self.lstSubcategories.clear()
        self.lblDescribeSubcategory.setText('')
        self.lblIconSubcategory.setPixmap(QPixmap())
        self.lblSelectSubcategory.setText(
            get_question_text('%s_question' % purpose['key']))
        for i in self.subcategories_for_layer():
            # noinspection PyTypeChecker
            item = QListWidgetItem(i['name'], self.lstSubcategories)
            # noinspection PyTypeChecker
            item.setData(QtCore.Qt.UserRole, i['key'])
            self.lstSubcategories.addItem(item)

        # Check if layer keywords are already assigned
        key = self.parent.step_kw_purpose.selected_purpose()['key']
        keyword = self.parent.get_existing_keyword(key)

        # Overwrite the keyword if it's KW mode embedded in IFCW mode
        if self.parent.parent_step:
            keyword = self.parent.get_parent_mode_constraints()[1]['key']

        # Set values based on existing keywords or parent mode
        if keyword:
            subcategories = []
            for index in range(self.lstSubcategories.count()):
                item = self.lstSubcategories.item(index)
                subcategories.append(item.data(QtCore.Qt.UserRole))
            if keyword in subcategories:
                self.lstSubcategories.setCurrentRow(
                    subcategories.index(keyword))

        self.auto_select_one_item(self.lstSubcategories)

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Layer Purpose Type Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will be able to set the '
            'type of your layer based on the purpose that you have set in the '
            'previous step (if you choose hazard or exposure purpose). In '
            'this step, there is list of exposure / hazard type that you can '
            'select to specify your layer purpose type.'
        ).format(step_name=self.step_name)))
        return message
