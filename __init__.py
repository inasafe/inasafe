'''
/***************************************************************************
 Riab
                                 A QGIS plugin
 Disaster risk assessment tool developed by AusAid
                             -------------------
        begin                : 2012-01-09
        copyright            : (C) 2012 by Australia Indonesia Facility for
                                           Disaster Reduction
        email                : ole.moller.nielsen@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
'''


def name():
    return 'Risk in a box'


def description():
    return 'Disaster risk assessment tool developed by AusAid'


def version():
    return 'Version 0.1'


def icon():
    return 'icon.png'


def qgisMinimumVersion():
    return '1.7'


def classFactory(iface):
    '''Load Riab class from file Riab'''

    from riab import Riab
    return Riab(iface)
