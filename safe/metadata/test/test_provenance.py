# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **metadata module.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from unittest import TestCase
from safe.metadata.provenance.provenance import Provenance


class TestProvenance(TestCase):

    def test_append_step(self):
        provenance = Provenance()
        title0 = 'Calculated first random impact'
        description0 = 'In this step we calculated a first random impact'
        provenance.append_step(title0, description0)
        title1 = 'Calculated second random impact'
        description1 = 'In this step we calculated a second random impact'
        provenance.append_step(title1, description1)
        title2 = 'Calculated third random impact'
        description2 = 'In this step we calculated a third random impact'
        provenance.append_step(title2, description2)

        self.assertEqual(provenance.count, 3)
        self.assertEqual(provenance.get(1).title, title1)
        self.assertEqual(provenance.last.title, title2)
