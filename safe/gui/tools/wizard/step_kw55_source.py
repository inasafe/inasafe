# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Source

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

# noinspection PyPackageRequirements
from PyQt4.QtCore import QDateTime

from safe.definitionsv4.layer_purposes import layer_purpose_aggregation
from safe.definitionsv4.layer_modes import layer_mode_classified
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.utilities.unicode import get_unicode


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwSource(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Source"""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizad Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)

        source_tooltip = self.tr(
            'Please record who is the custodian of this layer i.e. '
            'OpenStreetMap')
        self.lblSource.setToolTip(source_tooltip)
        self.leSource.setToolTip(source_tooltip)

        date_tooltip = self.tr(
            'When was this data collected or downloaded i.e. 1-May-2014')
        self.lblDate.setToolTip(date_tooltip)
        self.dtSource_date.setToolTip(date_tooltip)

        scale_tooltip = self.tr('What is the scale of this layer?')
        self.lblScale.setToolTip(scale_tooltip)
        self.leSource_scale.setToolTip(scale_tooltip)

        url_tooltip = self.tr(
            'Does the custodians have their own website '
            'i.e. www.openstreetmap.org')
        self.lblURL.setToolTip(url_tooltip)
        self.leSource_url.setToolTip(url_tooltip)

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
        if self.parent.step_kw_purpose.selected_purpose()\
                == layer_purpose_aggregation:
            new_step = self.parent.step_kw_aggregation
        elif self.parent.step_kw_extrakeywords.\
                additional_keywords_for_the_layer():
            new_step = self.parent.step_kw_extrakeywords
        # otherwise behave like it was step_kw_extrakeywords
        elif self.parent.step_kw_layermode.\
                selected_layermode() == layer_mode_classified:
            if self.parent.step_kw_classification.selected_classification() \
                    or self.parent.step_kw_classify.\
                    postprocessor_classification_for_layer():
                new_step = self.parent.step_kw_classify
            elif self.parent.step_kw_field.selected_field():
                new_step = self.parent.step_kw_field
            else:
                new_step = self.parent.step_kw_layermode
        else:
            if self.parent.step_kw_resample.\
                    selected_allowresampling() is not None:
                new_step = self.parent.step_kw_resample
            else:
                new_step = self.parent.step_kw_unit
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_kw_title
        return new_step

    # noinspection PyPep8Naming
    def on_ckbSource_date_toggled(self, state):
        """This is an automatic Qt slot executed when the checkbox is toggled

        :param state: the new state
        :type state: boolean
        """
        self.dtSource_date.setEnabled(state)

    def set_widgets(self):
        """Set widgets on the Source tab."""
        # Just set values based on existing keywords
        source = self.parent.get_existing_keyword('source')
        if source or source == 0:
            self.leSource.setText(get_unicode(source))
        else:
            self.leSource.clear()

        source_scale = self.parent.get_existing_keyword('scale')
        if source_scale or source_scale == 0:
            self.leSource_scale.setText(get_unicode(source_scale))
        else:
            self.leSource_scale.clear()

        source_date = self.parent.get_existing_keyword('date')
        if source_date:
            self.ckbSource_date.setChecked(True)
            self.dtSource_date.setDateTime(
                QDateTime.fromString(get_unicode(source_date),
                                     'yyyy-MM-dd HH:mm:ss'))
        else:
            self.ckbSource_date.setChecked(False)
            self.dtSource_date.clear()

        source_url = self.parent.get_existing_keyword('url')
        try:
            source_url = source_url.toString()
        except AttributeError:
            pass

        if source_url or source_url == 0:
            self.leSource_url.setText(get_unicode(source_url))
        else:
            self.leSource_url.clear()

        source_license = self.parent.get_existing_keyword('license')
        if source_license or source_license == 0:
            self.leSource_license.setText(get_unicode(source_license))
        else:
            self.leSource_license.clear()
