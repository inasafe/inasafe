# coding=utf-8
"""This is the concrete Minimum Needs class that contains the logic to load
the minimum needs to and from the QSettings"""

__author__ = 'Christian Christelis <christian@kartoza.com>'
__date__ = '05/10/2014'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')

from PyQt4.QtCore import QSettings
from safe.common.minimum_needs import MinimumNeeds
import os
from os.path import expanduser, exists
import shutil


class QMinimumNeeds(MinimumNeeds):
    """The concrete MinimumNeeds class to be used in a QGis environment.

    In the case where we assume QGis we use the QSettings object to store the
    minimum needs.
    """

    def __init__(self, testing=False):
        self.settings = QSettings()
        if testing:
            self.settings = QSettings('Test Settings')
        self.load()

    def load(self):
        """Load the minimum needs from the QSettings object.
        """
        minimum_needs = self.settings.value('minimum_needs')
        if minimum_needs is None:
            profiles = self.get_profiles()
            minimum_needs = self.read_from_file(
                expanduser('~/.qgis2/minimum_needs/%s.json' % profiles))
        self.minimum_needs = minimum_needs

    def load_profile(self, profile):
        self.read_from_file(
            expanduser('~/.qgis2/minimum_needs/%s.json' % profile))

    def save_profile(self, profile):
        self.write_to_file(
            expanduser('~/.qgis2/minimum_needs/%s.json' % profile))

    def save(self):
        """Save the minimum needs to the QSettings object.
        """
        # This needs to be imported here to avoid an inappropriate loading
        # sequence
        from safe.impact_functions.core import get_plugins
        self.settings.setValue('minimum_needs', self.minimum_needs)
        ## Monkey patch all the impact functions
        for (name, plugin) in get_plugins().items():
            if not hasattr(plugin, 'parameters'):
                continue
            if 'minimum needs' in plugin.parameters:
                plugin.parameters['minimum needs'] = self.get_minimum_needs()

    def get_profiles(self):
        if not exists(expanduser('~/.qgis2/minimum_needs/')):
            shutil.copytree(
                expanduser(
                    '~/.qgis2/python/plugins/inasafe/files/minimum_needs/'),
                expanduser('~/.qgis2/minimum_needs'))
        profiles = [
            profile.rstrip('.json') for profile in
            os.listdir(expanduser('~/.qgis2/minimum_needs/')) if
            profile[-5:] == '.json']
        return profiles

