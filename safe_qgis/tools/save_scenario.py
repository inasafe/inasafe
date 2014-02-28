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

from PyQt4 import QtGui
from PyQt4.QtCore import QSettings
from PyQt4.QtGui import QFileDialog

from safe_qgis.utilities.utilities import viewport_geo_array
from safe_qgis.safe_interface import safeTr

LOGGER = logging.getLogger('InaSAFE')


class SaveScenarioDialog(object):
    """Tools for saving an active scenario on the dock."""

    def __init__(self):
        """Constructor for the dialog."""

    def save_current_scenario(self, scenario_file_path=None):
        """Save current scenario to a text file.

        You can use the saved scenario with the batch runner.

        :param scenario_file_path: A path to the scenario file.
        :type scenario_file_path: str

        """
        warning_title = self.tr('InaSAFE Save Scenario Warning')
        # get data layer
        # get absolute path of exposure & hazard layer, or the contents
        exposure_layer = self.get_exposure_layer()
        hazard_layer = self.get_hazard_layer()
        aggregation_layer = self.get_aggregation_layer()
        function_id = self.get_function_id(self.cboFunction.currentIndex())
        extent = viewport_geo_array(self.iface.mapCanvas())
        # make it look like this:
        # 109.829170982, -8.13333290561, 111.005344795, -7.49226294379
        extent_string = ', '.join(('%f' % x) for x in extent)

        # Checking f exposure and hazard layer is not None
        if exposure_layer is None:
            warning_message = self.tr(
                'Exposure layer is not found, can not save scenario. Please '
                'add exposure layer to do so.')
            # noinspection PyCallByClass,PyTypeChecker
            QtGui.QMessageBox.warning(self, warning_title, warning_message)
            return
        if hazard_layer is None:
            warning_message = self.tr(
                'Hazard layer is not found, can not save scenario. Please add '
                'hazard layer to do so.')
            # noinspection PyCallByClass,PyTypeChecker
            QtGui.QMessageBox.warning(self, warning_title, warning_message)
            return

        # Checking if function id is not None
        if function_id == '' or function_id is None:
            warning_message = self.tr(
                'The impact function is empty, can not save scenario')
            # noinspection PyCallByClass,PyTypeChecker
            QtGui.QMessageBox.question(self, warning_title, warning_message)
            return

        exposure_path = str(exposure_layer.publicSource())
        hazard_path = str(hazard_layer.publicSource())

        title = self.keyword_io.read_keywords(hazard_layer, 'title')
        title = safeTr(title)

        title_dialog = self.tr('Save Scenario')
        # get last dir from setting
        settings = QSettings()
        last_save_dir = settings.value('inasafe/lastSourceDir', '.', type=str)
        default_name = title.replace(
            ' ', '_').replace('(', '').replace(')', '')
        if scenario_file_path is None:
            # noinspection PyCallByClass,PyTypeChecker
            file_name = str(QFileDialog.getSaveFileName(
                self, title_dialog,
                os.path.join(last_save_dir, default_name + '.txt'),
                "Text files (*.txt)"))
        else:
            file_name = scenario_file_path

        relative_exposure_path, relative_hazard_path = \
            self.scenario_layer_paths(
                exposure_path, hazard_path, file_name)
        #  write to file
        parser = ConfigParser()
        parser.add_section(title)
        parser.set(title, 'exposure', relative_exposure_path)
        parser.set(title, 'hazard', relative_hazard_path)
        parser.set(title, 'function', function_id)
        parser.set(title, 'extent', extent_string)

        if aggregation_layer is not None:
            aggregation_path = str(aggregation_layer.publicSource())
            try:
                relative_aggregation_path = os.path.relpath(
                    aggregation_path, os.path.dirname(file_name))
            except ValueError, e:
                LOGGER.info(e.message)
                relative_aggregation_path = aggregation_path
            parser.set(title, 'aggregation', relative_aggregation_path)

        if file_name is None or file_name == '':
            return

        try:
            parser.write(open(file_name, 'a'))
            # Save directory settings
            last_save_dir = os.path.dirname(file_name)
            settings.setValue('inasafe/lastSourceDir', last_save_dir)
        except IOError:
            # noinspection PyTypeChecker,PyCallByClass
            QtGui.QMessageBox.warning(
                self, self.tr('InaSAFE'),
                self.tr('Failed to save scenario to ' + file_name))

    @staticmethod
    def scenario_layer_paths(exposure_path, hazard_path, scenario_path):
        """Calculate the paths for hazard and exposure relative to scenario.

        :param exposure_path: Public path for exposure.
        :type exposure_path: str

        :param hazard_path: Public path for hazard.
        :type hazard_path: str

        :param scenario_path: Path to scenario file.
        :type scenario_path: str

        :return: Tuple of relative paths for exposure and hazard.
        :rtype: (str, str)
        """
        start_path = os.path.dirname(scenario_path)
        try:
            relative_exposure_path = os.path.relpath(
                exposure_path, start_path)
        except ValueError, e:
            LOGGER.info(e.message)
            relative_exposure_path = exposure_path
        try:
            relative_hazard_path = os.path.relpath(hazard_path, start_path)
        except ValueError, e:
            LOGGER.info(e.message)
            relative_hazard_path = hazard_path

        return relative_exposure_path, relative_hazard_path
