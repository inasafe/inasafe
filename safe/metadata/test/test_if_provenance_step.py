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

from safe.metadata.provenance import IFProvenanceStep

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
        'analysis_extent': [0, 1, 2, 2],
        'parameter': {},
    }

    good_data_xml = ('<provenance_step '
                     'timestamp="2015-08-13T20:20:48.178268">\n'
                     '<title>TEST title</title>\n'
                     '<description>TEST description</description>\n'
                     '<start_time>20140714_060955</start_time>\n'
                     '<finish_time>20140714_061255</finish_time>\n'
                     '<hazard_layer>path/to/hazard/layer</hazard_layer>\n'
                     '<exposure_layer>path/to/exposure/layer'
                     '</exposure_layer>\n'
                     '<impact_function_id>IF_id</impact_function_id>\n'
                     '<impact_function_version>2.1</impact_function_version>\n'
                     '<host_name>my_computer</host_name>\n'
                     '<user>my_user</user>\n'
                     '<qgis_version>2.4</qgis_version>\n'
                     '<gdal_version>1.9.1</gdal_version>\n'
                     '<qt_version>4.5</qt_version>\n'
                     '<pyqt_version>5.1</pyqt_version>\n'
                     '<os>ubuntu 12.04</os>\n'
                     '<inasafe_version>2.1</inasafe_version>\n'
                     '<exposure_pixel_size>0.1</exposure_pixel_size>\n'
                     '<hazard_pixel_size>0.2</hazard_pixel_size>\n'
                     '<impact_pixel_size>0.1</impact_pixel_size>\n'
                     '<analysis_extent>[0, 1, 2, 2]</analysis_extent>\n'
                     '<parameter>{}</parameter>\n'
                     '</provenance_step>\n')

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
                'TEST title', 'TEST description', data=partial_data)

        IFProvenanceStep('TEST title', 'TEST description', data=self.good_data)

    def test_xml(self):
        step = IFProvenanceStep(
            'TEST title',
            'TEST description',
            data=self.good_data,
            timestamp='2015-08-13T20:20:48.178268')
        self.assertEquals(self.good_data_xml, step.xml)
