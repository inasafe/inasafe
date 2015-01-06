# coding=utf-8
"""
Module to handle report using QgsComposition with template.

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

from qgis.core import QgsComposition, QgsMapRenderer
from PyQt4 import QtCore, QtXml

from safe.utilities.i18n import tr
from safe.common.exceptions import LoadingTemplateError


class TemplateComposition(object):
    """Class for handling composition using specific template.

    ..versionadded: 3.0
    """
    def __init__(self, template_path=None, renderer=None):
        """Class constructor."""
        # The path to the template
        self._template_path = template_path
        # The renderer for the map element in composition
        self._renderer = renderer
        # Needed elements on the template
        self._component_ids = []
        # Missing elements on the template
        self._missing_elements = []
        # Template Map Substitution
        self._template_substitution = {}
        # The composition
        self._composition = None

        # Call the setter to set other things needed
        if template_path is not None:
            self.template_path = template_path

        # Call the setter to set other things needed
        if renderer is not None:
            self.renderer = renderer

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
    def renderer(self):
        """Getter for renderer instance variable."""
        return self._renderer

    @renderer.setter
    def renderer(self, renderer):
        """Setter for renderer instance variable.

        :param renderer: The renderer for map element on QgsComposition.
        :type renderer: QgsMapRenderer
        """
        self._renderer = renderer
        # noinspection PyCallingNonCallable
        self._composition = QgsComposition(renderer)

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
    def template_substitution(self):
        """Getter for template substitution when loading it to composition.
        """
        return self._template_substitution

    @template_substitution.setter
    def template_substitution(self, template_substitution):
        """Set substitution for the template.

        :param template_substitution: the substitution for the template.
        :type template_substitution: dict
        """
        self._template_substitution = template_substitution

    @property
    def composition(self):
        """Getter for composition.
        """
        return self._composition

    def load_template(self):
        """Load the template to composition.

        To load template properly, you need to set the template and the
        renderer first (and template_substitution if you want to), e.g:
            template_composition = TemplateComposition(
                                    template_path='/template/path',
                                    renderer=some_renderer)
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
            template_composition.renderer = some_renderer
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
            document, self.template_substitution)
        if not load_status:
            raise LoadingTemplateError(
                tr('Error loading template: %s') % self.template_path)
