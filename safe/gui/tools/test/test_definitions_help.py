# coding=utf-8

"""Tests for definitions help."""

import unittest
import logging
from safe.gui.tools.help import definitions_help
import safe.messaging as m
from safe.test.utilities import get_control_text

LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestDefinitionsHelp(unittest.TestCase):

    """Test Definitions Help Generation."""

    test_subdefinition1 = {
        'key': 'test_subdefinition1',
        'name': 'Super Nice SubDefinition1',
        'description': 'Some nice kind of description 1.',
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
        'name': 'Super Nice SubDefinition2',
        'description': 'Some nice kind of description 2.',
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
        'name': 'Super Nice Definition',
        'description': 'Some nice kind of description.',
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
        message = m.Message()
        table_of_contents = m.Message()
        definitions_help.definition_to_message(
            self.test_definition,
            message=message,
            table_of_contents=table_of_contents
        )
        help_text = message.to_text()
        expected_result = get_control_text(
            'test-definition-to-message-response.txt')

        for line in expected_result:
            line = line.replace('\n', '')
            self.assertIn(line, help_text)


if __name__ == '__main__':
    suite = unittest.makeSuite(TestDefinitionsHelp, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
