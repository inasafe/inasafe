# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**InaSAFE Post Processors Definitions**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from utilities.i18n import tr
from safe.definitionsv4.fields import (
    female_ratio_field,
    population_count_field,
    women_count_field,
    youth_ratio_field,
    youth_count_field,
    adult_ratio_field,
    adult_count_field,
    elderly_ratio_field,
    elderly_count_field
)

__author__ = 'ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '22/09/16'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

post_processor_gender = {
    'key': 'post_processor_gender',
    'name': tr('Gender Post Processor'),
    'description': tr(
        'Post processor to calculate the number of affected woman'),
    'input': {
        'population': {
            'field': population_count_field,
            # We can add something later, like mandatory requirement, another
            #  source of input (e.g. parameter)
        },
        'gender_ratio': {
            'field': female_ratio_field,
        }
    },
    'output': {
        'women': {
            'field': women_count_field,
            'formula': 'population * gender_ratio'
        }
    }
}
post_processor_youth = {
    'key': 'post_processor_youth',
    'name': tr('Youth Post Processor'),
    'description': tr(
        'Post processor to calculate the number of affected youth people'),
    'input': {
        'population': {
            'field': population_count_field,
            # We can add something later, like mandatory requirement, another
            #  source of input (e.g. parameter)
        },
        'youth_ratio': {
            'field': youth_ratio_field,
        }
    },
    'output': {
        'youth': {
            'field': youth_count_field,
            'formula': 'population * youth_ratio'
        }
    }
}
post_processor_adult = {
    'key': 'post_processor_adult',
    'name': tr('Adult Post Processor'),
    'description': tr(
        'Post processor to calculate the number of affected adult people'),
    'input': {
        'population': {
            'field': population_count_field,
            # We can add something later, like mandatory requirement, another
            #  source of input (e.g. parameter)
        },
        'adult_ratio': {
            'field': adult_ratio_field,
        }
    },
    'output': {
        'adult': {
            'field': adult_count_field,
            'formula': 'population * adult_ratio'
        }
    }
}
post_processor_elderly = {
    'key': 'post_processor_elderly',
    'name': tr('Elderly Post Processor'),
    'description': tr(
        'Post processor to calculate the number of affected elderly people'),
    'input': {
        'population': {
            'field': population_count_field,
            # We can add something later, like mandatory requirement, another
            #  source of input (e.g. parameter)
        },
        'elderly_ratio': {
            'field': elderly_ratio_field,
        }
    },
    'output': {
        'elderly': {
            'field': elderly_count_field,
            'formula': 'population * elderly_ratio'
        }
    }
}

post_processors = [
    post_processor_gender,
    post_processor_youth,
    post_processor_adult
]
