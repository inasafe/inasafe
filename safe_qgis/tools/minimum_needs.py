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

    def __init__(self):
        self.settings = QSettings()
        self.minimum_needs = None
        self.load()

    def load(self):
        """Load the minimum needs from the QSettings object.
        """
        minimum_needs = self.settings.value('Minimum Needs')
        if minimum_needs is None:
            profiles = self.get_profiles()[0]
            self.read_from_file(
                expanduser('~/.qgis2/minimum_needs/%s.json' % profiles))
        if self.minimum_needs is None:
            self.minimum_needs = self._defaults()

    def load_profile(self, profile):
        """Load a specific profile into the current minimum needs.

        :param profile: The profile's name
        :type profile: basestring, str
        """
        self.read_from_file(
            expanduser('~/.qgis2/minimum_needs/%s.json' % profile))

    def save_profile(self, profile):
        """Save the current minimum needs into a new profile.

        :param profile: The profile's name
        :type profile: basestring, str
        """
        self.write_to_file(
            expanduser('~/.qgis2/minimum_needs/%s.json' % profile))

    def save(self):
        """Save the minimum needs to the QSettings object.
        """
        # This needs to be imported here to avoid an inappropriate loading
        # sequence
        if not self.minimum_needs['resources']:
            return
        from safe.impact_functions.core import get_plugins
        self.settings.setValue('Minimum Needs', self.minimum_needs)
        ## Monkey patch all the impact functions
        for (name, plugin) in get_plugins().items():
            if not hasattr(plugin, 'parameters'):
                continue
            if 'minimum needs' in plugin.parameters:
                plugin.parameters['minimum needs'] = self.get_minimum_needs()

    @staticmethod
    def get_profiles():
        """Get all the minimum needs profiles.

        :returns: The minimum needs by name.
        :rtype: list
        """
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
