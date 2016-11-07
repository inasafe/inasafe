# coding=utf-8
"""
Module as a wrapper for QgsComposition.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '21/03/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# noinspection PyUnresolvedReferences
from qgis.core import QgsComposition
try:
    from qgis.core import QgsMapSettings  # pylint: disable=unused-import
except ImportError:
    from qgis.core import QgsMapRenderer  # pylint: disable=unused-import
from PyQt4 import QtCore, QtXml

from safe.utilities.i18n import tr
from safe.common.exceptions import TemplateLoadingError


class TemplateComposition(object):
    """Class for handling composition using specific template.

    .. versionadded: 3.0
    """
    def __init__(self, template_path=None, map_settings=None):
        """Class constructor."""
        # The path to the template
        self._template_path = template_path
        # The map settings for composition
        self._map_settings = map_settings
        # Needed elements on the template
        self._component_ids = []
        # Missing elements on the template
        self._missing_elements = []
        # Template Map Substitution
        self._substitution = {}
        # The composition
        self._composition = None

        # Call the setter to set other things needed
        if template_path is not None:
            self.template_path = template_path

        # Call the setter to set other things needed
        if map_settings is not None:
            self.map_settings = map_settings

    @property
    def template_path(self):
        """Getter for template_path instance variable."""
        return self._template_path

    @template_path.setter
    def template_path(self, template_path):
        """Setter for template_path instance variable.

        :param template_path: Template path.
        :type template_path: str
        """
        self._template_path = template_path

    @property
    def map_settings(self):
        """Getter for map_settings instance variable."""
        return self._map_settings

    @map_settings.setter
    def map_settings(self, map_settings):
        """Setter for map settings instance variable.

        :param map_settings: The map settings for QgsComposition.
        :type map_settings: QgsMapSettings
        """
        self._map_settings = map_settings
        # noinspection PyCallingNonCallable
        self._composition = QgsComposition(map_settings)

    @property
    def component_ids(self):
        """Getter component ids that should exist on the template."""
        return self._component_ids

    @component_ids.setter
    def component_ids(self, component_ids):
        """Setter component ids that should exist on the template.

        :param component_ids: List of component ids of the template.
        :type component_ids: list
        """
        self._component_ids = component_ids
        # Set missing_elements every time we set component_ids
        missing_elements = []
        template_file = QtCore.QFile(self.template_path)
        template_file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
        template_content = template_file.readAll()
        for component_id in self.component_ids:
            if component_id not in template_content:
                missing_elements.append(component_id)
        self._missing_elements = missing_elements

    @property
    def missing_elements(self):
        """Getter for missing elements on the template

        :returns: Sub list of component_ids missing from composition.
        :rtype: list
        """
        return self._missing_elements

    @property
    def substitution(self):
        """Getter for template substitution when loading it to composition.
        """
        return self._substitution

    @substitution.setter
    def substitution(self, substitution):
        """Set substitution for the template.

        :param substitution: the substitution for the template.
        :type substitution: dict
        """
        self._substitution = substitution

    @property
    def composition(self):
        """Getter for composition.
        """
        return self._composition

    def load_template(self):
        """Load the template to composition.

        To load template properly, you need to set the template and the
        map settings first (and template_substitution if you want to), e.g:
            template_composition = TemplateComposition(
                                    template_path='/template/path',
                                    map_settings=some_map_settings)
            substitution_map = {
                'impact-title': title,
                'date': date,
                'time': time,
                'safe-version': version,
                'disclaimer': self.disclaimer
            }
            template_composition.template_substitution = substitution_map
            template_composition.load_template()

            or

            template_composition = TemplateComposition()
            template_composition.template_path = '/template/path'
            template_composition.map_settings = some_map_settings
            template_composition.load_template()


        :raises: LoadingTemplateError
        """
        template_file = QtCore.QFile(self.template_path)
        template_file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
        template_content = template_file.readAll()
        template_file.close()

        # Create a dom document containing template content
        document = QtXml.QDomDocument()
        document.setContent(template_content)

        # Load template
        load_status = self.composition.loadFromTemplate(
            document, self.substitution)
        if not load_status:
            raise TemplateLoadingError(
                tr('Error loading template: %s') % self.template_path)
