# coding=utf-8
"""InaSAFE Wizard Step Classifications."""
from builtins import range

# noinspection PyPackageRequirements
from qgis.PyQt import QtCore
from qgis.PyQt.QtWidgets import QListWidgetItem

from safe import messaging as m
from safe.common.exceptions import InvalidWizardStep
from safe.definitions.layer_modes import (
    layer_mode_classified, layer_mode_continuous)
from safe.definitions.layer_purposes import (
    layer_purpose_hazard, layer_purpose_exposure)
from safe.definitions.utilities import definition, get_classifications
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_strings import classification_question
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwClassification(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Classifications."""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_classification())

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        layer_mode = self.parent.step_kw_layermode.selected_layermode()
        if layer_mode == layer_mode_classified:
            new_step = self.parent.step_kw_classify
        elif layer_mode == layer_mode_continuous:
            new_step = self.parent.step_kw_threshold
        else:
            message = tr('Layer mode should be continuous or classified')
            raise InvalidWizardStep(message)
        return new_step

    def classifications_for_layer(self):
        """Return a list of valid classifications for a layer.

        :returns: A list where each value represents a valid classification.
        :rtype: list
        """
        subcategory_key = self.parent.step_kw_subcategory.\
            selected_subcategory()['key']
        layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        if layer_purpose in [layer_purpose_hazard, layer_purpose_exposure]:
            classifications = []
            selected_unit = self.parent.step_kw_unit.selected_unit()
            for classification in get_classifications(subcategory_key):
                if selected_unit is None:
                    # we are using classified data, so let's allow all
                    # classifications
                    classifications.append(classification)
                elif 'multiple_units' not in classification:
                    # this classification is not multiple unit aware, so let's
                    # allow it
                    classifications.append(classification)
                elif selected_unit in classification['multiple_units']:
                    # we are using continuous data, and this classification
                    # supports the chosen unit so we allow it
                    classifications.append(classification)
            return classifications
        else:
            # There are no classifications for non exposure and hazard
            # defined yet
            return []

    def on_lstClassifications_itemSelectionChanged(self):
        """Update classification description label and unlock the Next button.

        .. note:: This is an automatic Qt slot
           executed when the field selection changes.
        """
        self.clear_further_steps()
        classification = self.selected_classification()
        # Exit if no selection
        if not classification:
            return
        # Set description label
        self.lblDescribeClassification.setText(classification["description"])
        # Enable the next button
        self.parent.pbnNext.setEnabled(True)

    def selected_classification(self):
        """Obtain the classification selected by user.

        :returns: Metadata of the selected classification.
        :rtype: dict, None
        """
        item = self.lstClassifications.currentItem()
        try:
            return definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def clear_further_steps(self):
        """Clear all further steps in order to properly calculate the prev step
        """
        self.parent.step_kw_classify.treeClasses.clear()

    def set_widgets(self):
        """Set widgets on the Classification tab."""
        self.clear_further_steps()
        purpose = self.parent.step_kw_purpose.selected_purpose()['name']
        subcategory = self.parent.step_kw_subcategory.\
            selected_subcategory()['name']
        self.lstClassifications.clear()
        self.lblDescribeClassification.setText('')
        self.lblSelectClassification.setText(
            classification_question % (subcategory, purpose))
        classifications = self.classifications_for_layer()
        for classification in classifications:
            if not isinstance(classification, dict):
                classification = definition(classification)
            item = QListWidgetItem(
                classification['name'],
                self.lstClassifications)
            item.setData(QtCore.Qt.UserRole, classification['key'])
            self.lstClassifications.addItem(item)

        # Set values based on existing keywords (if already assigned)
        classification_keyword = self.parent.get_existing_keyword(
            'classification')
        if classification_keyword:
            classifications = []
            for index in range(self.lstClassifications.count()):
                item = self.lstClassifications.item(index)
                classifications.append(item.data(QtCore.Qt.UserRole))
            if classification_keyword in classifications:
                self.lstClassifications.setCurrentRow(
                    classifications.index(classification_keyword))

        self.auto_select_one_item(self.lstClassifications)

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Classification Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will be able to set the '
            'classification of the layer that is being assigned in this '
            'wizard.'
        ).format(step_name=self.step_name)))
        return message
