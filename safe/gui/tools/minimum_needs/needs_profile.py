# coding=utf-8
"""
This is the concrete Minimum Needs class that contains the logic to load
the minimum needs to and from the QSettings.
"""


__author__ = 'Christian Christelis <christian@kartoza.com>'
__date__ = '05/10/2014'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
from shutil import copy, rmtree

from qgis.PyQt.QtCore import QSettings
from qgis.core import QgsApplication

from parameters.text_parameter import TextParameter
from safe.common.minimum_needs import MinimumNeeds
from safe.common.parameters.resource_parameter import ResourceParameter
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path


def add_needs_parameters(parameters):
    """Add minimum needs to an impact functions parameters.

    :param parameters: A dictionary of impact function parameters.
    :type parameters: dict

    :returns: A dictionary of parameters with minimum needs appended.
    :rtype: dict
    """
    minimum_needs = NeedsProfile()
    parameters['minimum needs'] = minimum_needs.get_needs_parameters()
    return parameters


def get_needs_provenance(parameters):
    """Get the provenance of minimum needs.

    :param parameters: A dictionary of impact function parameters.
    :type parameters: dict

    :returns: A parameter of provenance
    :rtype: TextParameter
    """
    if 'minimum needs' not in parameters:
        return None
    needs = parameters['minimum needs']
    provenance = [p for p in needs if p.name == tr('Provenance')]
    if provenance:
        return provenance[0]
    return None


def get_needs_provenance_value(parameters):
    """Get the value of provenance.

    :param parameters: A dictionary of impact function parameters.
    :type parameters: dict

    :returns: A string value of provenance
    :rtype: str
    """
    provenance_param = get_needs_provenance(parameters)
    if provenance_param:
        return provenance_param.value
    return None


def filter_needs_parameters(parameter_list):
    """Get all minimum needs parameters.

    :param parameter_list: A list of parameters
    :type parameter_list: list

    :return: A list of ResourceParameter
    :rtype: list
    """
    return [n for n in parameter_list if isinstance(n, ResourceParameter)]


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
        self.locale = self.settings.value('locale/userLocale')
        self.load()

    def load(self):
        """Load the minimum needs.

        If the minimum needs defined in QSettings use it, if not, get the
        most relevant available minimum needs (based on QGIS locale). The
        last thing to do is to just use the default minimum needs.
        """
        self.minimum_needs = self.settings.value('MinimumNeeds')

        if not self.minimum_needs or self.minimum_needs == '':
            # Load the most relevant minimum needs
            # If more than one profile exists, just use defaults so
            # the user doesn't get confused.
            profiles = self.get_profiles()
            if len(profiles) == 1:
                profile = self.get_profiles()[0]
                self.load_profile(profile)
            else:
                self.minimum_needs = self._defaults()

    def load_profile(self, profile):
        """Load a specific profile into the current minimum needs.

        :param profile: The profile's name
        :type profile: basestring, str
        """
        profile_path = os.path.join(
            self.root_directory, 'minimum_needs', profile + '.json')
        self.read_from_file(profile_path)

    def save_profile(self, profile):
        """Save the current minimum needs into a new profile.

        :param profile: The profile's name
        :type profile: basestring, str
        """
        profile = profile.replace('.json', '')
        profile_path = os.path.join(
            self.root_directory,
            'minimum_needs',
            profile + '.json'
        )
        self.write_to_file(profile_path)

    def save(self):
        """Save the minimum needs to the QSettings object.
        """
        # This needs to be imported here to avoid an inappropriate loading
        # sequence
        if not self.minimum_needs['resources']:
            return

        self.settings.setValue('MinimumNeeds', self.minimum_needs)

    def get_profiles(self, overwrite=False):
        """Get all the minimum needs profiles.

        :returns: The minimum needs by name.
        :rtype: list
        """
        def sort_by_locale(unsorted_profiles, locale):
            """Sort the profiles by language settings.

            The profiles that are in the same language as the QGIS' locale
            will be sorted out first.

            :param unsorted_profiles: The user profiles profiles
            :type unsorted_profiles: list

            :param locale: The language settings string
            :type locale: str

            :returns: Ordered profiles
            :rtype: list
            """
            if locale is None:
                return unsorted_profiles

            locale = '_%s' % locale[:2]
            profiles_our_locale = []
            profiles_remaining = []
            for profile_name in unsorted_profiles:
                if locale in profile_name:
                    profiles_our_locale.append(profile_name)
                else:
                    profiles_remaining.append(profile_name)

            return profiles_our_locale + profiles_remaining

        # We ignore empty root_directory to avoid load min needs profile
        # to test directory when test is running.
        if not self.root_directory:
            profiles = []
            return profiles

        else:
            locale_minimum_needs_dir = os.path.join(
                self.root_directory, 'minimum_needs')
            path_name = resources_path('minimum_needs')
            if not os.path.exists(locale_minimum_needs_dir):
                os.makedirs(locale_minimum_needs_dir)
            # load default min needs profile
            for file_name in os.listdir(path_name):
                source_file = os.path.join(path_name, file_name)
                destination_file = os.path.join(
                    locale_minimum_needs_dir, file_name)
                if not os.path.exists(destination_file) or overwrite:
                    copy(source_file, destination_file)
            # move old min needs profile under user profile to inasafe
            # subdirectory
            self.move_old_profile(locale_minimum_needs_dir)
            profiles = [
                profile[:-5] for profile in
                os.listdir(locale_minimum_needs_dir) if
                profile[-5:] == '.json']
            profiles = sort_by_locale(profiles, self.locale)
            return profiles

    def precision_of(self, number_as_text):
        """The number of digits after the decimal will be counted and used
        as returned as the precision.

        :param number_as_text: A textual representation of the number whose
            precision we wish to determine.
        :type number_as_text: basestring

        :returns: The precision of the passed in textual
         representation of a number.
        :rtype: int
        """
        precision = number_as_text.split('.')[1]
        return len(precision)

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
            # choose highest precision between resource's parameters
            # start with default of 1
            precisions = [1]
            precision_influence = [
                'Maximum allowed', 'Minimum allowed', 'Default']
            for element in precision_influence:
                resource_element = str(resource[element])
                if resource[element] is not None and '.' in resource_element:
                    precisions.append(self.precision_of(resource_element))

            parameter.precision = max(precisions)
            parameters.append(parameter)

        prov_parameter = TextParameter()
        prov_parameter.name = tr('Provenance')
        prov_parameter.description = tr('The provenance of minimum needs')
        prov_parameter.help_text = tr('The provenance of minimum needs')
        try:
            prov_parameter.value = self.provenance
        except TypeError:
            prov_parameter.value = ''
        parameters.append(prov_parameter)

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
        """Map the root directory to user profile/inasafe so the minimum needs
           profile will be placed there (user profile/inasafe/minimum_needs).

        :returns: root directory
        :rtype: QString
        """
        if not QgsApplication.qgisSettingsDirPath() or (
                QgsApplication.qgisSettingsDirPath() == ''):
            self._root_directory = None
        else:
            # noinspection PyArgumentList
            self._root_directory = os.path.join(
                QgsApplication.qgisSettingsDirPath(),
                'inasafe')

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
            os.path.join(
                self.root_directory, 'minimum_needs', profile + '.json')
        )

    def move_old_profile(self, locale_minimum_needs_dir):
        """Move old minimum needs profile under user profile/minimum_needs.
           This function is to get rid the old min needs profile came
           from InaSAFE < 4.0.

        :param locale_minimum_needs_dir: User local minimum needs profile path.
        :type locale_minimum_needs_dir: str
        """
        old_profile_path = os.path.join(
            QgsApplication.qgisSettingsDirPath(), 'minimum_needs')

        if os.path.exists(old_profile_path):
            for filename in os.listdir(old_profile_path):
                source_file = os.path.join(old_profile_path, filename)
                destination_file = os.path.join(
                    locale_minimum_needs_dir, filename)
                if not os.path.exists(destination_file):
                    copy(source_file, destination_file)
                if os.path.exists(destination_file):
                    os.remove(source_file)
            # remove old profile path
            rmtree(old_profile_path)
