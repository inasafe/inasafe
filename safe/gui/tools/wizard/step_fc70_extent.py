# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Function Centric Wizard Step: Extent

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

from safe.common.exceptions import InsufficientOverlapError
from safe.utilities.analysis_handler import AnalysisHandler

from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step import WizardStep


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcExtent(WizardStep, FORM_CLASS):
    """Function Centric Wizard Step: Extent"""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizad Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)
        self.swExtent = None
        self.extent_dialog = None

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
        if self.parent.step_fc_agglayer_origin.rbAggLayerFromCanvas.isChecked():
            new_step = self.parent.step_fc_agglayer_from_canvas
        elif self.parent.step_fc_agglayer_origin.rbAggLayerFromBrowser.\
                isChecked():
            new_step = self.parent.step_fc_agglayer_from_browser
        else:
            new_step = self.parent.step_fc_agglayer_origin
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.validate_extent():
            new_step = self.parent.step_fc_params
        else:
            new_step = self.parent.step_fc_extent_disjoint
        return new_step

    def validate_extent(self):
        """Check if the selected extent intersects source data.

        :returns: true if extent intersects both layers, false if is disjoint
        :rtype: boolean
        """
        _analysis_handler = AnalysisHandler(self.parent)
        _analysis_handler.setup_analysis()
        try:
            impact_function = _analysis_handler.impact_function
            clip_parameters = impact_function.clip_parameters
            # pylint: disable=unused-variable
            adjusted_geo_extent = clip_parameters['adjusted_geo_extent']
            # pylint: enable=unused-variable
        except (AttributeError, InsufficientOverlapError):
            _analysis_handler = None
            return False

        _analysis_handler = None
        return True

    # noinspection PyPep8Naming
    def on_rbExtentUser_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.parent.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_rbExtentLayer_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.parent.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_rbExtentScreen_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.parent.pbnNext.setEnabled(True)

    def start_capture_coordinates(self):
        """Enter the coordinate capture mode"""
        self.parent.hide()

    def stop_capture_coordinates(self):
        """Exit the coordinate capture mode"""
        self.extent_dialog._populate_coordinates()
        self.extent_dialog.canvas.setMapTool(
            self.extent_dialog.previous_map_tool)
        self.parent.show()

    def write_extent(self):
        """ After the extent selection,
            save the extent and disconnect signals
        """
        self.extent_dialog.accept()
        self.extent_dialog.clear_extent.disconnect(
            self.parent.dock.extent.clear_user_analysis_extent)
        self.extent_dialog.extent_defined.disconnect(
            self.parent.dock.define_user_analysis_extent)
        self.extent_dialog.capture_button.clicked.disconnect(
            self.start_capture_coordinates)
        self.extent_dialog.tool.rectangle_created.disconnect(
            self.stop_capture_coordinates)

    def set_widgets(self):
        """Set widgets on the Extent tab"""
        # import here only so that it is AFTER i18n set up
        from safe.gui.tools.extent_selector_dialog import ExtentSelectorDialog
        self.extent_dialog = ExtentSelectorDialog(
            self.parent.iface,
            self.parent.iface.mainWindow(),
            extent=self.parent.dock.extent.user_extent,
            crs=self.parent.dock.extent.user_extent_crs)
        self.extent_dialog.tool.rectangle_created.disconnect(
            self.extent_dialog.stop_capture)
        self.extent_dialog.clear_extent.connect(
            self.parent.dock.extent.clear_user_analysis_extent)
        self.extent_dialog.extent_defined.connect(
            self.parent.dock.define_user_analysis_extent)
        self.extent_dialog.capture_button.clicked.connect(
            self.start_capture_coordinates)
        self.extent_dialog.tool.rectangle_created.connect(
            self.stop_capture_coordinates)

        self.extent_dialog.label.setText(self.tr(
            'Please specify extent of your analysis:'))

        if self.swExtent:
            self.swExtent.hide()

        self.swExtent = self.extent_dialog.main_stacked_widget
        self.layoutAnalysisExtent.addWidget(self.swExtent)
