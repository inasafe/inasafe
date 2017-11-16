# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**metadata module.**

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
from safe.metadata35.provenance import Provenance


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
        title3 = 'Calculated fourth random impact'
        description3 = 'In this step we calculated a fourth random impact'
        data = {
            'start_time': '20140714_060955',
            'finish_time': '20140714_061255',
            'hazard_layer': 'path/to/hazard/layer',
            'exposure_layer': 'path/to/exposure/layer',
            'impact_function_id': 'IF_id',
            'impact_function_version': '2.1',
            'host_name': 'my_computer',
            'user': 'my_user',
            'qgis_version': '2.4',
            'gdal_version': '1.9.1',
            'qt_version': '4.5',
            'pyqt_version': '5.1',
            'os': 'ubuntu 12.04',
            'inasafe_version': '2.1',
            'exposure_pixel_size': '0.1',
            'hazard_pixel_size': '0.2',
            'impact_pixel_size': '0.1',
            'analysis_extent': [0, 1, 2, 2],
            'parameter': {}
        }
        provenance.append_step(title3, description3, data=data)

        self.assertEqual(provenance.count, 4)
        self.assertEqual(provenance.get(1).title, title1)
        self.assertEqual(provenance.last.title, title3)
        self.assertEqual(provenance.last.data(), data)
