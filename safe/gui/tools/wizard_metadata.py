# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid **GUI InaSAFE Wizard Metadata.**

 ** NOTE This file meant for temporary storing metadata to be later moved
         to proper places.


Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'qgis@borysjurgiel.pl'
__revision__ = '$Format:%H$'
__date__ = '12/04/2016'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from safe.utilities.i18n import tr

road_class_mapping = [{
    'key': 'Motorway / highway',
    'name': tr('Motorway / highway'),
    'description': tr('Motorway / highway'),
    'string_defaults': ['Motorway or highway']
}, {
    'key': 'Motorway link',
    'name': tr('Motorway link'),
    'description': tr('Motorway link'),
    'string_defaults': ['Motorway link']
}, {
    'key': 'Primary road',
    'name': tr('Primary road'),
    'description': tr('Primary road'),
    'string_defaults': ['Primary road']
}, {
    'key': 'Primary link',
    'name': tr('Primary link'),
    'description': tr('Primary link'),
    'string_defaults': ['Primary link']
}, {
    'key': 'Tertiary',
    'name': tr('Tertiary'),
    'description': tr('Tertiary'),
    'string_defaults': ['Tertiary']
}, {
    'key': 'Tertiary link',
    'name': tr('Tertiary link'),
    'description': tr('Tertiary link'),
    'string_defaults': ['Tertiary link']
}, {
    'key': 'Secondary',
    'name': tr('Secondary'),
    'description': tr('Secondary'),
    'string_defaults': ['Secondary']
}, {
    'key': 'Secondary link',
    'name': tr('Secondary link'),
    'description': tr('Secondary link'),
    'string_defaults': ['Secondary link']
}, {
    'key': 'Road, residential, living street, etc.',
    'name': tr('Road, residential, living street, etc.'),
    'description': tr('Road, residential, living street, etc.'),
    'string_defaults': ['Road, residential, living street, etc.']
}, {
    'key': 'Track',
    'name': tr('Track'),
    'description': tr('Track'),
    'string_defaults': ['Track']
}, {
    'key': 'Cycleway, footpath, etc.',
    'name': tr('Cycleway, footpath, etc.'),
    'description': tr('Cycleway, footpath, etc.'),
    'string_defaults': ['Cycleway, footpath, etc.']
}, {
    'key': 'Other',
    'name': tr('Other'),
    'description': tr('Other'),
    'string_defaults': []
}]


structure_class_mapping = [{
    'key': 'Medical',
    'name': tr('Medical'),
    'description': tr('Medical'),
    'string_defaults': ['Clinic/Doctor', 'Hospital']
}, {
    'key': 'Schools',
    'name': tr('Schools'),
    'description': tr('Schools'),
    'string_defaults': ['School', 'University/College']
}, {
    'key': 'Places of worship',
    'name': tr('Places of worship'),
    'description': tr('Places of worship'),
    'string_defaults': ['Place of Worship - Unitarian',
                        'Place of Worship - Islam',
                        'Place of Worship - Buddhist',
                        'Place of Worship']
}, {
    'key': 'Residential',
    'name': tr('Residential'),
    'description': tr('Residential'),
    'string_defaults': ['Residential']
}, {
    'key': 'Government',
    'name': tr('Government'),
    'description': tr('Government'),
    'string_defaults': ['Government']
}, {
    'key': 'Public Building',
    'name': tr('Public Building'),
    'description': tr('Public Building'),
    'string_defaults': ['Public Building']
}, {
    'key': 'Fire Station',
    'name': tr('Fire Station'),
    'description': tr('Fire Station'),
    'string_defaults': ['Fire Station']
}, {
    'key': 'Police Station',
    'name': tr('Police Station'),
    'description': tr('Police Station'),
    'string_defaults': ['Police Station']
}, {
    'key': 'Supermarket',
    'name': tr('Supermarket'),
    'description': tr('Supermarket'),
    'string_defaults': ['Supermarket']
}, {
    'key': 'Commercial',
    'name': tr('Commercial'),
    'description': tr('Commercial'),
    'string_defaults': ['Commercial']
}, {
    'key': 'Industrial',
    'name': tr('Industrial'),
    'description': tr('Industrial'),
    'string_defaults': ['Industrial']
}, {
    'key': 'Utility',
    'name': tr('Utility'),
    'description': tr('Utility'),
    'string_defaults': ['Utility']
}, {
    'key': 'Sports Facility',
    'name': tr('Sports Facility'),
    'description': tr('Sports Facility'),
    'string_defaults': ['Sports Facility']
}, {
    'key': 'Other',
    'name': tr('Other'),
    'description': tr('Other'),
    'string_defaults': []
}]
