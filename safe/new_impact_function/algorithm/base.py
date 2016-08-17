# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Algorithm.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from processing.core.Processing import Processing


__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'base'
__date__ = '8/16/16'
__copyright__ = 'imajimatika@gmail.com'



class BaseAlgorithm(object):

    def __init__(self, **kwargs):
        """Initialize"""

        # From kwargs
        self.hazard = kwargs.get('hazard')
        self.exposure = kwargs.get('exposure')
        self.aggregation = kwargs.get('aggregation')
        self.extent = kwargs.get('extent')
        self.hazard_field = kwargs.get('hazard_field')
        self.aggregation_field = kwargs.get('aggregation_field')
        self.original_hazard_field = kwargs.get('original_hazard_field')
        self.original_aggregation_field = kwargs.get(
            'original_aggregation_field')

        # Processing
        self.processing = Processing
        self.processing.initialize()

    def run(self):
        """Run the algorithm

        :returns: Vector layer.
        :rtype: QgsVectorLayer
        """
        return self.exposure

    def run_processing_algorithm(self, algorithm_name, *args):
        """Adapt from processing.runalg with our own Processing.

        :param algorithm_name: The name of the algorithm.
        :type algorithm_name: str
        :param args: list of arguments
        :type args: list

        :returns: The output of the algorithm.
        :rtype: dict
        """
        algorithm = self.processing.runAlgorithm(algorithm_name, None, *args)
        if algorithm is not None:
            return algorithm.getOutputValuesAsDictionary()