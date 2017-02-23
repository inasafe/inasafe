# coding=utf-8
"""
Save Scenario Dialog.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '25/02/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import logging
from ConfigParser import ConfigParser

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from PyQt4 import QtGui
# noinspection PyPackageRequirements
from PyQt4.QtCore import QSettings
# noinspection PyPackageRequirements
from PyQt4.QtGui import QDialog, QFileDialog
from safe.utilities.gis import extent_to_array, viewport_geo_array
from safe.utilities.keyword_io import KeywordIO


LOGGER = logging.getLogger('InaSAFE')


class SaveScenarioDialog(QDialog):
    """Tools for saving an active scenario on the dock."""

    def __init__(self, iface, dock):
        """Constructor for the class."""
        QDialog.__init__(self)
        # Class Member
        self.iface = iface
        self.dock = dock
        self.output_directory = None
        self.exposure_layer = None
        self.hazard_layer = None
        self.aggregation_layer = None
        self.keyword_io = KeywordIO()

        # Calling some init methods
        self.restore_state()

    def restore_state(self):
        """ Read last state of GUI from configuration file."""
        settings = QSettings()
        try:
            last_save_directory = settings.value(
                'inasafe/lastSourceDir', '.', type=str)
        except TypeError:
            last_save_directory = ''
        self.output_directory = last_save_directory

    def save_state(self):
        """ Store current state of GUI to configuration file """
        settings = QSettings()
        settings.setValue('inasafe/lastSourceDir', self.output_directory)

    def validate_input(self):
        """Validate the input before saving a scenario.

        Those validations are:
        1. self.exposure_layer must be not None
        2. self.hazard_layer must be not None
        3. self.function_id is not an empty string or None
        """
        self.exposure_layer = self.dock.get_exposure_layer()
        self.hazard_layer = self.dock.get_hazard_layer()
        self.aggregation_layer = self.dock.get_aggregation_layer()

        is_valid = True
        warning_message = None
        if self.exposure_layer is None:
            warning_message = self.tr(
                'Exposure layer is not found, can not save scenario. Please '
                'add exposure layer to do so.')
            is_valid = False

        if self.hazard_layer is None:
            warning_message = self.tr(
                'Hazard layer is not found, can not save scenario. Please add '
                'hazard layer to do so.')
            is_valid = False

        return is_valid, warning_message

    def save_scenario(self, scenario_file_path=None):
        """Save current scenario to a text file.

        You can use the saved scenario with the batch runner.

        :param scenario_file_path: A path to the scenario file.
        :type scenario_file_path: str
        """
        # Validate Input
        warning_title = self.tr('InaSAFE Save Scenario Warning')
        is_valid, warning_message = self.validate_input()
        if not is_valid:
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QtGui.QMessageBox.warning(self, warning_title, warning_message)
            return

        # Make extent to look like:
        # 109.829170982, -8.13333290561, 111.005344795, -7.49226294379

        # Added in 2.2 to support user defined analysis extents
        if self.dock.extent.user_extent is not None \
                and self.dock.extent.crs is not None:
            # In V4.0, user_extent is QgsGeometry.
            user_extent = self.dock.extent.user_extent.boundingBox()
            extent = extent_to_array(user_extent, self.dock.extent.crs)
        else:
            extent = viewport_geo_array(self.iface.mapCanvas())
        extent_string = ', '.join(('%f' % x) for x in extent)

        exposure_path = self.exposure_layer.publicSource()
        hazard_path = self.hazard_layer.publicSource()
        title = self.keyword_io.read_keywords(self.hazard_layer, 'title')
        title = self.tr(title)
        default_filename = title.replace(
            ' ', '_').replace('(', '').replace(')', '')

        # Popup a dialog to request the filename if scenario_file_path = None
        dialog_title = self.tr('Save Scenario')
        if scenario_file_path is None:
            # noinspection PyCallByClass,PyTypeChecker
            scenario_file_path = QFileDialog.getSaveFileName(
                self,
                dialog_title,
                os.path.join(self.output_directory, default_filename + '.txt'),
                "Text files (*.txt)")
        if scenario_file_path is None or scenario_file_path == '':
            return
        self.output_directory = os.path.dirname(scenario_file_path)

        #  Write to file
        parser = ConfigParser()
        parser.add_section(title)
        # Relative path is not recognized by the batch runner, so we use
        # absolute path.
        parser.set(title, 'exposure', exposure_path)
        parser.set(title, 'hazard', hazard_path)

        parser.set(title, 'extent', extent_string)
        if self.dock.extent.crs is None:
            parser.set(title, 'extent_crs', 'EPSG:4326')
        else:
            parser.set(
                title,
                'extent_crs',
                self.dock.extent.crs.authid())
        if self.aggregation_layer is not None:
            aggregation_path = self.aggregation_layer.publicSource()
            relative_aggregation_path = self.relative_path(
                scenario_file_path, aggregation_path)
            parser.set(title, 'aggregation', relative_aggregation_path)

        try:
            parser.write(open(scenario_file_path, 'a'))
        except IOError:
            # noinspection PyTypeChecker,PyCallByClass,PyArgumentList
            QtGui.QMessageBox.warning(
                self,
                self.tr('InaSAFE'),
                self.tr('Failed to save scenario to ' + scenario_file_path))

        # Save State
        self.save_state()

    @staticmethod
    def relative_path(reference_path, input_path):
        """Get the relative path to input_path from reference_path.

        :param reference_path: The reference path
        :type reference_path: str

        :param input_path: The input path
        :type input_path: str
        """
        start_path = os.path.dirname(reference_path)
        try:
            relative_path = os.path.relpath(input_path, start_path)
        except ValueError, e:
            # LOGGER.info(e.message)
            relative_path = input_path
        return relative_path
