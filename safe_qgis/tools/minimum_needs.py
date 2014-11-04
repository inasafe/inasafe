# coding=utf-8
"""This is the concrete Minimum Needs class that contains the logic to load
the minimum needs to and from the QSettings"""

__author__ = 'Christian Christelis <christian@kartoza.com>'
__date__ = '05/10/2014'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')

from PyQt4.QtCore import QSettings, QFile, QDir
from qgis.core import QgsApplication
from safe.common.minimum_needs import MinimumNeeds
import json


class QMinimumNeeds(MinimumNeeds):
    """The concrete MinimumNeeds class to be used in a QGis environment.

    In the case where we assume QGis we use the QSettings object to store the
    minimum needs.

    .. versionadded:: 2.2.
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
                QFile('%s/minimum_needs/%s.json' % (
                    QgsApplication.qgisSettingsDirPath(), profiles)))
        if self.minimum_needs is None:
            self.minimum_needs = self._defaults()

    def load_profile(self, profile):
        """Load a specific profile into the current minimum needs.

        :param profile: The profile's name
        :type profile: basestring, str
        """
        self.read_from_file(
            QFile('%s/minimum_needs/%s.json' % (
                QgsApplication.qgisSettingsDirPath(), profile)))

    def save_profile(self, profile):
        """Save the current minimum needs into a new profile.

        :param profile: The profile's name
        :type profile: basestring, str
        """
        self.write_to_file(
            QFile('%s/minimum_needs/%s.json' % (
                QgsApplication.qgisSettingsDirPath(), profile)))

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
        for (_, plugin) in get_plugins().items():
            if not hasattr(plugin, 'parameters'):
                continue
            if 'minimum needs' in plugin.parameters:
                plugin.parameters['minimum needs'] = self.get_minimum_needs()

    def get_profiles(self):
        """Get all the minimum needs profiles.

        :returns: The minimum needs by name.
        :rtype: list
        """
        local_minimum_needs_dir = QDir(
            '%s/minimum_needs/' % QgsApplication.qgisSettingsDirPath())
        plugins_minimum_needs_dir = QDir(
            '%s/python/plugins/inasafe/files/minimum_needs/' %
            QgsApplication.qgisSettingsDirPath())
        if not local_minimum_needs_dir.exists():
            if not plugins_minimum_needs_dir.exists():
                # This is specifically to get Travis working.
                return [self._defaults()['profile']]
            QDir(QgsApplication.qgisSettingsDirPath()).mkdir('minimum_needs')
            for file_name in plugins_minimum_needs_dir.entryList():
                source_file = QFile(
                    '%s/python/plugins/inasafe/files/minimum_needs/%s' %
                    (QgsApplication.qgisSettingsDirPath(), file_name))
                source_file.copy(
                    '%s/minimum_needs/%s' %
                    (QgsApplication.qgisSettingsDirPath(), file_name))
        profiles = [
            profile.rstrip('.json') for profile in
            local_minimum_needs_dir.entryList() if
            profile[-5:] == '.json']
        return profiles

    def read_from_file(self, qfile):
        """Read from an existing json file.

        :param qfile: The object to be read from.
        :type qfile: QFile

        :returns: Success status. -1 for unsuccessful 0 for success
        :rtype: int
        """
        if not qfile.exists():
            return -1
        qfile.open(QFile.ReadOnly)
        needs_json = qfile.readAll()
        try:
            minimum_needs = json.loads(needs_json)
        except (TypeError, ValueError):
            minimum_needs = None

        if not minimum_needs:
            return -1

        return self.update_minimum_needs(minimum_needs)

    def write_to_file(self, qfile):
        """Write minimum needs as json to a file.

        :param qfile: The file to be written to.
        :type qfile: QFile
        """
        if not qfile.exists():
            return -1
        qfile.open(QFile.WriteOnly)
        needs_json = json.dumps(self.minimum_needs)
        qfile.write(needs_json)
