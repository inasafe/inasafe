# coding=utf-8

"""Tests for definitions help.
"""

import unittest
import logging
from safe.utilities.i18n import tr
from safe.gui.tools.help import definitions_help
from safe.test.utilities import get_control_text

LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestDefinitionsHelp(unittest.TestCase):
    """Test Defintions Help Generation
    """
    test_subdefinition1 = {
        'key': 'test_subdefinition1',
        'name': tr('Super Nice SubDefinition1'),
        'description': tr(
            'Some nice kind of description 1.'),
        'citations': [
            {
                'text': None,
                'link': None
            }
        ],
        'types': [
        ]
    }
    test_subdefinition2 = {
        'key': 'test_subdefinition2',
        'name': tr('Super Nice SubDefinition2'),
        'description': tr(
            'Some nice kind of description 2.'),
        'citations': [
            {
                'text': None,
                'link': None
            }
        ],
        'types': [
        ]
    }
    test_definition = {
        'key': 'test_definition',
        'name': tr('Super Nice Definition'),
        'description': tr(
            'Some nice kind of description.'),
        'citations': [
            {
                'text': None,
                'link': None
            }
        ],
        'types': [
            test_subdefinition1,
            test_subdefinition2
        ]
    }

    # noinspection PyPep8Naming
    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_definitions_help(self):
        """Test definitions help generation."""
        help_text = definitions_help.definitions_help().to_text()
        expected_result = get_control_text(
            'test-definition-help-response.txt')

        for line in expected_result:
            line = line.replace('\n', '')
            self.assertIn(line, help_text)

    def test_definition_to_message(self):
        """Test definitions to message renderer."""
        help_text = definitions_help.definition_to_message(
            self.test_definition).to_text()
        expected_result = get_control_text(
            'test-definition-to-message-response.txt')

        for line in expected_result:
            line = line.replace('\n', '')
            self.assertIn(line, help_text)

if __name__ == '__main__':
    suite = unittest.makeSuite(TestDefinitionsHelp, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
