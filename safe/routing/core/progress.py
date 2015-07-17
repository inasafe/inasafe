# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid / DFAT -
**New Metadata for SAFE.**

Contact : etienne@kartoza.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'etienne'

import logging

from processing.gui.SilentProgress import SilentProgress
from processing.core.GeoAlgorithmExecutionException import \
    GeoAlgorithmExecutionException

# The LOGGER is initialised in utilities.py by init
LOGGER = logging.getLogger('InaSAFE')


class Progress(SilentProgress):
    """Custom progress for using Processing."""

    def __init__(self, progress_bar=None, progress_text=None):
        """Constructor.

        :param progress_bar: A progress bar.
        :type progress_bar: QProgressBar

        :param progress_text: A progress text.
        :type progress_text: QLabel
        """
        # SilentProgress doesn't have an __init__ before QGIS 2.10.
        self.progress_bar = progress_bar
        self.progress_text = progress_text

    def error(self, message):
        """Raise an exception if there is an error.

        :param message: The error message.
        :type message: str

        :raise GeoAlgorithmExecutionException
        """
        raise GeoAlgorithmExecutionException(message)

    def setText(self, text):
        """Inform the user about the progress with a text.

        :param text: The text to show.
        :type text: str
        """
        self.progress_text.setText(text)

    def setPercentage(self, value):
        """Inform the user about the progress with a percentage.

        :param value: The percentage.
        :type value: int
        """
        self.progress_bar.setValue(value)

    def setInfo(self, text):
        """Show general information.

        :param text: The information.
        :type text: str
        """
        self.progress_text.setText(text)

    def setDebugInfo(self, info):
        """Log debug.

        :param info: The information.
        :type info: str
        """
        LOGGER.debug(info)

    def setConsoleInfo(self, info):
        """Log some console information.

        :param info: The information.
        :type info: str
        """
        LOGGER.info(info)

    def setCommand(self, cmd):
        pass

    def close(self):
        pass
