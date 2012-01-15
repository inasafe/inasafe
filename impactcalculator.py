'''
Disaster risk assessment tool developed by AusAid - **impactcalculator.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

'''

__author__ = 'tim@linfiniti.com, ole.moller.nielsen@gmail.com'
__version__ = '0.0.1'
__date__ = '11/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


import unicodedata
from riabexceptions import InsufficientParametersException


class ImpactCalculator:
    '''A class to compute an impact scenario.'''

    def __init__(self):
        '''Constructor for the impact calculator.'''
        self._hazard_layer = None
        self._exposure_layer = None

    def getHazardLayer(self):
        '''Accessor: hazard layer.'''
        return self.__hazard_layer

    def getExposureLayer(self):
        '''Accessor: exposure layer.'''
        return self.__exposure_layer

    def setHazardLayer(self, value):
        '''Mutator: hazard layer.'''
        self.__hazard_layer = value

    def setExposureLayer(self, value):
        '''Mutator: exposure layer.'''
        self.__exposure_layer = value

    def delHazardLayer(self):
        '''Delete: hazard layer.'''
        del self.__hazard_layer

    def delExposureLayer(self):
        '''Delete: exposure layer.'''
        del self.__exposure_layer

    _hazard_layer = property(getHazardLayer, setHazardLayer,
        delHazardLayer, '''Hazard layer property  (e.g. a flood depth
        raster).''')

    _exposure_layer = property(getExposureLayer, setExposureLayer,
        delExposureLayer, '''Exposure layer property (e.g. buildings or
        features that will be affected).''')

    def make_ascii(self, x):
        '''Convert QgsString to ASCII'''
        x = unicode(x)
        x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore')
        return x

    def run(self):
        ''' Main function for hazard impact calculation.
        Requires three parameters to be set before execution
        can take place:

        * Hazard layer - a path to a raster,
        * Exposure layer - a path to a vector points layer.
        * Function - a function that defines how the Hazard assessment
          will be computed.

        Args:
           None.
        Returns:
           A two tuple containing:

           * a raster output layer's path
           * a string (probably in html markup) containing reporting
             information summarising the analysis result

        Raises:
           InsufficientParametersException if not all parameters are
           set.
        '''
        if not self._hazard_layer:
            msg = 'Error: Hazard layer not set.'
            raise InsufficientParametersException(msg)

        if not self._exposure_layer:
            msg = 'Error: Exposure layer not set.'
            raise InsufficientParametersException(msg)

        '''
        print 'Hazard:', hazard_filename
        print 'Exposure:', exposure_filename


        hazard_filename = make_ascii(hazard_filename)
        exposure_filename = make_ascii(exposure_filename)


        # Code from Risiko
        from impact.engine.core import calculate_impact
        from impact.storage.io import read_layer

        from impact.storage.io import write_vector_data
        from impact.storage.io import write_raster_data
        from impact.plugins import get_plugins

        plugin_name = 'Flood Building Impact Function'

        # Get layers using API
        H = read_layer(hazard_filename)
        E = read_layer(exposure_filename)

        plugin_list = get_plugins(plugin_name)

        IF = plugin_list[0][plugin_name]

        print 'H', H
        print 'E', E

        # Call impact calculation engine
        impact_filename = calculate_impact(layers=[H, E],
                                           impact_fcn=IF)


        print 'Result', impact_filename '''
        pass
