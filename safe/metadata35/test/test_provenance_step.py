# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Exception Classes.**

Custom exception classes for the IS application.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '12/10/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from datetime import datetime
from unittest import TestCase

from safe.metadata35.provenance import ProvenanceStep


class TestProvenanceStep(TestCase):

    def test_step(self):
        title = 'Calculated some random impact'
        description = 'Calculated some random impact'
        provenance_step = ProvenanceStep(title, description)

        # check that we get the correct step message
        self.assertIs(provenance_step.title, title)

        # check that the timestamp is correct
        delta_seconds = (datetime.now() - provenance_step.time).total_seconds()
        self.assertLessEqual(delta_seconds, 0.1)
