# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Summary

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'qgis@borysjurgiel.pl'
__revision__ = '$Format:%H$'
__date__ = '16/03/2016'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import re

from safe.definitionsv4.constants import inasafe_keyword_version_key
from safe.definitionsv4.layer_purposes import (
    layer_purpose_exposure, layer_purpose_aggregation, layer_purpose_hazard)
from safe.definitionsv4.versions import inasafe_keyword_version
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwSummary(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Summary"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_kw_title
        return new_step

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
                    new_step = self.parent.step_fc_disjoint_layers

                elif parent_step in [self.parent.step_fc_agglayer_from_canvas,
                                     self.parent.
                                     step_fc_agglayer_from_browser]:
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
        return new_step

    def set_widgets(self):
        """Set widgets on the Keywords Summary tab."""

        current_keywords = self.parent.get_keywords()
        current_keywords[inasafe_keyword_version_key] = inasafe_keyword_version

        base_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            os.pardir,
            os.pardir,
            os.pardir,
            'resources'))
        header_path = os.path.join(base_dir, 'header.html')
        footer_path = os.path.join(base_dir, 'footer.html')
        header_file = file(header_path)
        footer_file = file(footer_path)
        header = header_file.read()
        footer = footer_file.read()
        header_file.close()
        footer_file.close()
        header = header.replace('PATH', base_dir)

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
            im_func = self.parent.step_fc_function.selected_function()
            if not self.parent.is_layer_compatible(
                    self.parent.layer, None, current_keywords):
                msg = self.tr(
                    'The selected keywords don\'t match requirements of the '
                    'selected impact function (%s). You can continue with '
                    'registering the layer, however, you\'ll need to choose '
                    'another layer for that function.') % im_func['name']
                body = '<br/><h5 class="problem">%s</h5> %s' % (msg, body)

        html = header + body + footer
        self.wvKwSummary.setHtml(html)
