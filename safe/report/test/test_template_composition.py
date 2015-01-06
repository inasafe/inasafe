# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Impact Merge Dialog Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__date__ = '06/01/2015'
__copyright__ = ('Copyright 2013, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest
import shutil
import logging


from safe.report.template_composition import TemplateComposition
from safe.utilities.resources import resources_path
from safe.test.utilities import get_qgis_app, temp_dir

LOGGER = logging.getLogger('InaSAFE')
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

INASAFE_TEMPLATE_PATH = resources_path(
    'qgis-composer-templates', 'inasafe-portrait-a4.qpt')


class TemplateCompositionTest(unittest.TestCase):
    """Test Impact Merge Dialog widget."""

    # noinspection PyPep8Naming
    def setUp(self):
        """Runs before each test."""
        pass

    # noinspection PyPep8Naming
    def tearDown(self):
        """Runs after each test."""
        pass

    def test_constructor(self):
        """Test constructor."""
        # If we give param renderer, composition instance must not be none
        renderer = CANVAS.mapRenderer()
        template_composition = TemplateComposition(renderer=renderer)
        message = 'The composition instance variable must not be none.'
        self.assertIsNotNone(template_composition.composition, message)

    def test_missing_elements(self):
        """Test if we can get missing elements correctly."""
        # Copy the inasafe template to temp dir
        template_path = os.path.join(
            temp_dir('test'), 'inasafe-portrait-a4.qpt')
        shutil.copy2(INASAFE_TEMPLATE_PATH, template_path)

        template_composition = TemplateComposition(template_path=template_path)
        # No missing elements here
        component_ids = ['safe-logo', 'north-arrow', 'organisation-logo',
                         'impact-map', 'impact-legend']
        template_composition.component_ids = component_ids
        message = 'There should be no missing elements, but it gets: %s' % (
            template_composition.missing_elements)
        expected_result = []
        self.assertEqual(
            template_composition.missing_elements, expected_result, message)

        # There are missing elements
        component_ids = ['safe-logo', 'north-arrow', 'organisation-logo',
                         'impact-map', 'impact-legend',
                         'i-added-element-id-here-nooo']
        template_composition.component_ids = component_ids
        message = 'There should be no missing elements, but it gets: %s' % (
            template_composition.missing_elements)
        expected_result = ['i-added-element-id-here-nooo']
        self.assertEqual(
            template_composition.missing_elements, expected_result, message)

        # Remove test dir
        shutil.rmtree(temp_dir('test'))

    def test_load_template(self):
        """Test we can load template correctly."""
        # Copy the inasafe template to temp dir
        template_path = os.path.join(
            temp_dir('test'), 'inasafe-portrait-a4.qpt')
        shutil.copy2(INASAFE_TEMPLATE_PATH, template_path)

        template_composition = TemplateComposition(
            template_path=template_path,
            renderer=CANVAS.mapRenderer())
        template_composition.load_template()

        # Check the element of the composition
        # In that template, there should be 'safe-logo' id
        component = template_composition.composition.getComposerItemById(
            'safe-logo')
        message = 'It must not be None, but it returns %s' % component
        self.assertIsNotNone(component, message)


if __name__ == '__main__':
    suite = unittest.makeSuite(TemplateCompositionTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
