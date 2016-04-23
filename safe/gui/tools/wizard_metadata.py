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

road_class_mapping = [
    {
        'key': 'motorway',
        'name': tr('Motorway'),
        'description': tr('A road to solve the traffic and have a fare.'),
        'string_defaults': ['Motorway']
    },
    {
        'key': 'primary',
        'name': tr('Primary'),
        'description': tr('A road that service the main transportation with a '
                          'long distance travel characteristic and high '
                          'average velocity.'),
        'string_defaults': ['Primary']
    },
    {
        'key': 'secondary',
        'name': tr('Secondary'),
        'description': tr('A road that service the transportation with a '
                          'medium distance travel characteristic and medium '
                          'average velocity.'),
        'string_defaults': ['Secondary']
    },
    {
        'key': 'local',
        'name': tr('Local'),
        'description': tr('A road that service the transportation with short '
                          'distance travel and low average velocity.'),
        'string_defaults': ['Local']
    },
    {
        'key': 'other',
        'name': tr('Other'),
        'description': tr('A road that service the transportation with short '
                          'travel and low average velocity.'),
        'string_defaults': ['Other']
    },
    {
        'key': 'path',
        'name': tr('Path'),
        'description': tr('A road to walk on foot aim.'),
        'string_defaults': ['Path', 'Track']
    }
]

structure_class_mapping = [
    {
        'key': 'education',
        'name': tr('Education'),
        'description': tr('An object that has a service in education sector.'),
        'string_defaults': [
            'Kindergarten', 'College', 'School', 'University'
        ]
    },
    {
        'key': 'health',
        'name': tr('Health'),
        'description': tr(
            'An object that has a service and facility in health sector.'),
        'string_defaults': [
            'Clinic', 'Doctor', 'Hospital', 'Dentist', 'Pharmacy'
        ]
    },
    {
        'key': 'transportation',
        'name': tr('Transportation'),
        'description': tr(
            'An object that has a service and facility in public '
            'transportation.'),
        'string_defaults': [
            'bus stop', 'bus station', 'station', 'ferry terminal',
            'aerodrome', 'airport', 'terminal']
    },
    {
        'key': 'place of worship',
        'name': tr('Place of Worship'),
        'description': tr(
            'An object that used to pray or related to religion activity.'),
        'string_defaults': [
            'Place of Worship - Islam',
            'Place of Worship - Buddhist',
            'Place of Worship - Christian',
            'Place of Worship - Hindu',
            'Place of Worship'
        ]
    },
    {
        'key': 'government',
        'name': tr('Government'),
        'description': tr(
            'A building that used to doing government activity in public '
            'service or the other government activity.'),
        'string_defaults': ['Government']
    },
    {
        'key': 'economy',
        'name': tr('Economy'),
        'description': tr(
            'A building that used to trade / buy and sell activity or an '
            'object that has an economy activity.'),
        'string_defaults': [
            'Supermarket', 'shop', 'market', 'tailor', 'warehouse', 'works',
            'convenience', 'seafood', 'atm', 'mall', 'clothes', 'shoes'
        ]
    },
    {
        'key': 'recreation and entertainment',
        'name': tr('Recreation and Entertainment'),
        'description': tr(
            'An Object that provide an entertainment or recreation '
            'facilities.'),
        'string_defaults': [
            'amusement arcade', 'cinema', 'zoo', 'museum', 'theatre'
        ]
    },
    {
        'key': 'sport',
        'name': tr('Sport'),
        'description': tr(
            'An object that has a sport facility and people can use it.'),
        'string_defaults': ['stadium', 'sport centre', 'pitch']
    },
    {
        'key': 'public facility',
        'name': tr('Public Facility'),
        'description': tr(
            'An object that provide a service or facility to public like '
            'toilet, library, convention hall, etc.'),
        'string_defaults': ['library', 'toiler', 'convention hall', 'prison']
    },
    {
        'key': 'accommodation',
        'name': tr('Accommodation'),
        'description': tr(
            'An object that provide an accommodation / lodging or food '
            'services.'),
        'string_defaults': ['restaurant', 'cafe', 'fast food', 'hotel']
    },
    {
        'key': 'other',
        'name': tr('Other'),
        'description': tr(
            'An object that be found in Indonesia, and frequently mapped.'),
        'string_defaults': ['Animal Boarding', 'Water Well', 'Lighthouse']
    }
]
