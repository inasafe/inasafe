# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**metadata module.**

Contact: ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from safe.common.exceptions import InvalidProvenanceDataError

from safe.metadata35.provenance import IFProvenanceStep

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from unittest import TestCase


class TestImpactFunctionProvenanceStep(TestCase):
    good_data = {
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
        'actual_extent': [0, 1, 2, 2],
        'requested_extent': [0, 1, 2, 2],
        'actual_extent_crs': 'EPSG: 4326',
        'requested_extent_crs': 'EPSG: 4326',
        'parameter': {},
    }

    good_data_xml = (
        '<provenance_step '
        'timestamp="2015-08-13T20:20:48.178268">'
        '<title>TEST title</title>'
        '<description>TEST &amp;" \' &lt; &gt; description</description>'
        '<start_time>20140714_060955</start_time>'
        '<finish_time>20140714_061255</finish_time>'
        '<hazard_layer>path/to/hazard/layer</hazard_layer>'
        '<exposure_layer>path/to/exposure/layer</exposure_layer>'
        '<impact_function_id>IF_id</impact_function_id>'
        '<impact_function_version>2.1</impact_function_version>'
        '<host_name>my_computer</host_name>'
        '<user>my_user</user>'
        '<qgis_version>2.4</qgis_version>'
        '<gdal_version>1.9.1</gdal_version>'
        '<qt_version>4.5</qt_version>'
        '<pyqt_version>5.1</pyqt_version>'
        '<os>ubuntu 12.04</os>'
        '<inasafe_version>2.1</inasafe_version>'
        '<exposure_pixel_size>0.1</exposure_pixel_size>'
        '<hazard_pixel_size>0.2</hazard_pixel_size>'
        '<impact_pixel_size>0.1</impact_pixel_size>'
        '<actual_extent>[0, 1, 2, 2]</actual_extent>'
        '<requested_extent>[0, 1, 2, 2]</requested_extent>'
        '<actual_extent_crs>EPSG: 4326</actual_extent_crs>'
        '<requested_extent_crs>EPSG: 4326</requested_extent_crs>'
        '<parameter>{}</parameter>'
        '</provenance_step>'
    )

    def test_invalid_data(self):
        with self.assertRaises(InvalidProvenanceDataError):
            IFProvenanceStep('TEST title', 'TEST description', data={})

        partial_data = {
            'start_time': '20140714_060955',
            'finish_time': '20140714_061255',
            'hazard_layer': 'path/to/hazard/layer',
            'exposure_layer': 'path/to/exposure/layer',
            'impact_function_id': 'impact_function_id',
        }

        with self.assertRaises(InvalidProvenanceDataError):
            IFProvenanceStep(
                'TEST title',
                'TEST description',
                data=partial_data)

        IFProvenanceStep('TEST title', 'TEST description', data=self.good_data)

    def test_xml(self):
        step = IFProvenanceStep(
            'TEST title',
            'TEST &" \' < > description',
            data=self.good_data,
            timestamp='2015-08-13T20:20:48.178268')
        self.assertEqual(self.good_data_xml, step.xml)
