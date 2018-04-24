# coding=utf-8
"""InaSAFE Wizard Step Keyword Summary."""

import re

from safe import messaging as m
from safe.definitions.constants import inasafe_keyword_version_key
from safe.definitions.layer_purposes import (
    layer_purpose_exposure, layer_purpose_aggregation, layer_purpose_hazard)
from safe.definitions.versions import inasafe_keyword_version
from safe.gui.tools.wizard.utilities import layers_intersect
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwSummary(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Keyword Summary."""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.parent.parent_step:
            # Come back from KW to the parent IFCW thread.
            parent_step = self.parent.parent_step
            if self.parent.is_layer_compatible(self.parent.layer):
                # If the layer is compatible,
                # go to the next step (issue #2347)
                if parent_step in [self.parent.step_fc_hazlayer_from_canvas,
                                   self.parent.step_fc_hazlayer_from_browser]:
                    new_step = self.parent.step_fc_explayer_origin

                elif parent_step in [self.parent.step_fc_explayer_from_canvas,
                                     self.parent.
                                     step_fc_explayer_from_browser]:
                    if layers_intersect(
                            self.parent.hazard_layer,
                            self.parent.exposure_layer):
                        new_step = self.parent.step_fc_agglayer_origin
                    else:
                        new_step = self.parent.step_fc_disjoint_layers

                elif parent_step in [self.parent.step_fc_agglayer_from_canvas,
                                     self.parent.
                                     step_fc_agglayer_from_browser]:
                    if layers_intersect(self.parent.exposure_layer,
                                        self.parent.aggregation_layer):
                        new_step = self.parent.step_fc_summary
                    else:
                        new_step = self.parent.step_fc_agglayer_disjoint
                else:
                    raise Exception('No such step')
            else:
                # If the layer is incompatible, stay on the parent step.
                # However, if the step is xxxLayerFromCanvas and there are
                # no compatible layers, the list will be empty,
                # so go one step back.
                haz = layer_purpose_hazard['key']
                exp = layer_purpose_exposure['key']
                agg = layer_purpose_aggregation['key']
                if (parent_step == self.parent.step_fc_hazlayer_from_canvas and
                        not self.parent.get_compatible_canvas_layers(haz)):
                    new_step = self.parent.step_fc_hazlayer_origin
                elif (parent_step ==
                      self.parent.step_fc_explayer_from_canvas and
                      not self.parent.get_compatible_canvas_layers(exp)):
                    new_step = self.parent.step_fc_explayer_origin
                elif (parent_step ==
                      self.parent.step_fc_agglayer_from_canvas and
                      not self.parent.get_compatible_canvas_layers(agg)):
                    new_step = self.parent.step_fc_agglayer_origin
                else:
                    new_step = parent_step
            self.parent.parent_step = None
            self.parent.is_selected_layer_keywordless = False
            self.parent.set_mode_label_to_ifcw()
        else:
            # Wizard complete
            new_step = None
        # Reset the step history
        self.parent.keyword_steps = []
        return new_step

    def set_widgets(self):
        """Set widgets on the Keywords Summary tab."""

        current_keywords = self.parent.get_keywords()
        current_keywords[inasafe_keyword_version_key] = inasafe_keyword_version

        header_path = resources_path('header.html')
        footer_path = resources_path('footer.html')
        header_file = open(header_path)
        footer_file = open(footer_path)
        header = header_file.read()
        footer = footer_file.read()
        header_file.close()
        footer_file.close()
        header = header.replace('PATH', resources_path())

        # TODO: Clone the dict inside keyword_io.to_message rather then here.
        #       It pops the dict elements damaging the function parameter
        body = self.parent.keyword_io.to_message(dict(current_keywords)).\
            to_html()
        # remove the branding div
        body = re.sub(
            r'^.*div class="branding".*$', '', body, flags=re.MULTILINE)

        if self.parent.parent_step:
            # It's the KW mode embedded in IFCW mode,
            # so check if the layer is compatible
            if not self.parent.is_layer_compatible(
                    self.parent.layer, None, current_keywords):
                msg = self.tr(
                    'The selected keywords don\'t match requirements of the '
                    'selected combination for the impact function. You can '
                    'continue with registering the layer, however, you\'ll '
                    'need to choose another layer for that function.')
                body = '<br/><h5 class="problem">%s</h5> %s' % (msg, body)

        html = header + body + footer
        self.wvKwSummary.setHtml(html)

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Keyword Summary Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will be able to '
            'review all the keywords that have been set for this layer'
        ).format(step_name=self.step_name)))
        return message
