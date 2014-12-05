# coding=utf-8
"""This is the concrete Minimum Needs class that contains the logic to load
the minimum needs to and from the QSettings"""

__author__ = 'Christian Christelis <christian@kartoza.com>'
__date__ = '05/10/2014'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')

# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611  # force sip2 api

from shutil import copy
from os.path import exists, dirname
from os import listdir, environ, makedirs

# noinspection PyPackageRequirements
from PyQt4.QtCore import QSettings
# noinspection PyUnresolvedReferences
# pylint: disable=W0611
from qgis.core import QgsApplication

from safe_extras.parameters.resource_parameter import ResourceParameter
from safe.common.minimum_needs import MinimumNeeds


class NeedsProfile(MinimumNeeds):
    """The concrete MinimumNeeds class to be used in a QGIS environment.

    In the case where we assume QGIS we use the QSettings object to store the
    minimum needs.

    .. versionadded:: 2.2.
    """

    def __init__(self):
        self.settings = QSettings()
        self.minimum_needs = None
        self._root_directory = None
        self.locale = environ['LANG']
        self.load()

    def load(self):
        """Load the minimum needs from the QSettings object.
        """
        minimum_needs = None
        try:
            minimum_needs = self.settings.value('MinimumNeeds', type=dict)
            if not minimum_needs and minimum_needs != u'':
                profiles = self.get_profiles()
                self.read_from_file(
                    '%s/minimum_needs/%s.json' % (
                        self.root_directory, profiles))
        except TypeError:
            minimum_needs = self._defaults()

        if not minimum_needs and minimum_needs != u'':
            minimum_needs = self._defaults()

        self.minimum_needs = minimum_needs

    def load_profile(self, profile):
        """Load a specific profile into the current minimum needs.

        :param profile: The profile's name
        :type profile: basestring, str
        """
        self.read_from_file(
            '%s/minimum_needs/%s.json' % (self.root_directory, profile))

    def save_profile(self, profile):
        """Save the current minimum needs into a new profile.

        :param profile: The profile's name
        :type profile: basestring, str
        """
        profile = profile.replace('.json', '')
        self.write_to_file(
            '%s/minimum_needs/%s.json' % (self.root_directory, profile))

    def save(self):
        """Save the minimum needs to the QSettings object.
        """
        # This needs to be imported here to avoid an inappropriate loading
        # sequence
        if not self.minimum_needs['resources']:
            return
        from safe.impact_functions.core import get_plugins
        self.settings.setValue('MinimumNeeds', self.minimum_needs)
        # Monkey patch all the impact functions
        for (_, plugin) in get_plugins().items():
            if not hasattr(plugin, 'parameters'):
                continue
            if 'minimum needs' in plugin.parameters:
                plugin.parameters['minimum needs'] = (
                    self.get_needs_parameters())
                plugin.parameters['provenance'] = self.provenance

    def get_profiles(self):
        """Get all the minimum needs profiles.

        :returns: The minimum needs by name.
        :rtype: list
        """
        def sort_by_locale(unsorted_profiles, locale):
            """Sort the profiles by language settings

            :param unsorted_profiles: The user profiles profiles
            :type unsorted_profiles: list

            :param locale: The language settings string
            :type locale: str

            :returns: Ordered profiles
            :rtype: list
            """
            locale = '_%s' % locale[:2]
            profiles_our_locale = []
            profiles_remaining = []
            for profile_name in unsorted_profiles:
                if locale in profile_name:
                    profiles_our_locale.append(profile_name)
                else:
                    profiles_remaining.append(profile_name)

            return profiles_our_locale + profiles_remaining

        locale_minimum_needs_dir = '%s/minimum_needs/' % self.root_directory
        path_name = "%s/../../../files/minimum_needs" % dirname(__file__)
        if not exists(locale_minimum_needs_dir):
            makedirs(locale_minimum_needs_dir)
        for file_name in listdir(path_name):
            source_file = '%s/%s' % (path_name, file_name)
            destination_file = (
                '%s/%s' % (locale_minimum_needs_dir, file_name))
            if not exists(destination_file):
                copy(
                    source_file,
                    destination_file)
        profiles = [
            profile[:-5] for profile in
            listdir(locale_minimum_needs_dir) if
            profile[-5:] == '.json']
        profiles = sort_by_locale(profiles, self.locale)
        return profiles

    def get_needs_parameters(self):
        """Get the minimum needs resources in parameter format

        :returns: The minimum needs resources wrapped in parameters.
        :rtype: list
        """
        parameters = []
        for resource in self.minimum_needs['resources']:
            parameter = ResourceParameter()
            parameter.name = resource['Resource name']
            parameter.help_text = resource['Resource description']
            # Adding in the frequency property. This is not in the
            # FloatParameter by default, so maybe we should subclass.
            parameter.frequency = resource['Frequency']
            parameter.description = self.format_sentence(
                resource['Readable sentence'],
                resource)
            parameter.minimum_allowed_value = float(
                resource['Minimum allowed'])
            parameter.maximum_allowed_value = float(
                resource['Maximum allowed'])
            parameter.unit.name = resource['Unit']
            parameter.unit.plural = resource['Units']
            parameter.unit.abbreviation = resource['Unit abbreviation']
            parameter.value = float(resource['Default'])
            parameters.append(parameter)
        return parameters

    @property
    def provenance(self):
        """The provenance that is provided with the loaded profile.


        :returns: The provenance.
        :rtype: str
        """
        return self.minimum_needs['provenance']

    @property
    def root_directory(self):
        """Get the home root directory

        :returns: root directory
        :rtype: QString
        """
        if self._root_directory is None or self._root_directory == '':
            try:
                # noinspection PyArgumentList
                self._root_directory = QgsApplication.qgisSettingsDirPath()
            except NameError:
                # This only happens when running only one test on its own
                self._root_directory = None
            if self._root_directory is None or self._root_directory == '':
                self._root_directory = "%s/.qgis2" % (environ['HOME'])
        return self._root_directory

    @staticmethod
    def format_sentence(sentence, resource):
        """Populate the placeholders in the sentence.

        :param sentence: The sentence with placeholder keywords.
        :type sentence: basestring, str

        :param resource: The resource to be placed into the sentence.
        :type resource: dict

        :returns: The formatted sentence.
        :rtype: basestring
        """
        sentence = sentence.split('{{')
        updated_sentence = sentence[0].rstrip()
        for part in sentence[1:]:
            replace, keep = part.split('}}')
            replace = replace.strip()
            updated_sentence = "%s %s%s" % (
                updated_sentence,
                resource[replace],
                keep
            )
        return updated_sentence

    def remove_profile(self, profile):
        """Remove a profile.

        :param profile: The profile to be removed.
        :type profile: basestring, str
        """
        self.remove_file(
            '%s/minimum_needs/%s.json' % (self.root_directory, profile)
        )
