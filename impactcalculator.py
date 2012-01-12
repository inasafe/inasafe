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


class ImpactCalculator:
    '''A class to compute an impact scenario.'''

    def __init__(self, iface):
        """ Save reference to the QGIS interface
        """
        self.layers = None
        self.hazard_layers = None
        self.exposure_layers = None

    def make_ascii(self, x):
        '''Convert QgsString to ASCII'''

        x = unicode(x)
        x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore')
        return x

    def run(self):
        ''' Main function for hazard impact calculation '''
        '''
        hazard_index = dlg.ui.comboBox.currentIndex()
        hazard_layer = self.hazard_layers[hazard_index]
        # Get the layer by index from the previous stored list

        exposure_index = dlg.ui.comboBox_2.currentIndex()
        exposure_layer = self.exposure_layers[exposure_index]
        # Get the layer by index from the previous stored list


        # Get the layer source filenames
        hazard_filename = hazard_layer.source()
        exposure_filename = exposure_layer.source()

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
