# coding=utf-8
"""Tests for resources utilities."""
import os

# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
import unittest
from safe.utilities.resources import (
    html_header, html_footer, resources_path, resource_url)


class TestResources(unittest.TestCase):

    def test_html_footer(self):
        """Test that we can get the html footer.

        .. versionadded:: 3.0
        """
        footer = html_footer()
        self.assertTrue('/html' in footer, footer)

    def test_html_header(self):
        """Test that we can get the html header.

        .. versionadded:: 3.0
        """
        header = html_header()
        self.assertTrue(
            'bootstrap' in header,
            'bootstrap not in ' + header)

    def test_resources_path(self):
        """Test we can get the path to the resources dir nicely.

        .. versionadded:: 3.0
        """
        css_path = resources_path('css', 'bootstrap.css')
        self.assertTrue(
            os.path.exists(css_path),
            css_path + ' does not exist')

    def test_resources_url(self):
        """Test we can get the path as a local url nicely.

        .. versionadded:: 3.0
        """
        url = resource_url(
            resources_path(
                'img', 'logos', 'inasafe-logo.png'))
        self.assertTrue(
            'file://' in url,
            url + ' is not valid')


if __name__ == '__main__':
    unittest.main()
