# coding=utf-8

"""Test Markdown."""

import unittest

from qgis.core import QgsCoordinateReferenceSystem

from safe.impact_function.impact_function import ImpactFunction
from safe.test.qgis_app import qgis_app
from safe.test.utilities import load_test_vector_layer
from safe.utilities.github_ticket import markdown

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

qgis_app()


class GitHubTicketTest(unittest.TestCase):
    """Test GitHub ticket creation."""

    def test_markdown(self):
        """Test we can create markdown if we have an exception."""
        text = None  # NOQA
        try:
            raise AttributeError
        except AttributeError as e:
            text = markdown(e)
        self.assertIsNotNone(text)
        self.assertTrue('* InaSAFE' in text)

        # Let's try with a Impact Function
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_vector_layer('exposure', 'roads.shp')

        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.crs = QgsCoordinateReferenceSystem(4326)

        # Monkey patch an exception instead of the normal `prepare()`
        def prepare():
            raise AttributeError
        impact_function.prepare = prepare

        try:
            impact_function.prepare()
        except AttributeError as e:
            text = markdown(e, impact_function)
        self.assertIsNotNone(text)
        self.assertTrue('* Debug' in text)
        print text
