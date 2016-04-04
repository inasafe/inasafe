# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Import Dialog.**
Contact : etienne@kartoza.com
.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'oscar mbita (mgwetam@gmail.com)'
__date__ = '8/02/2016'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import logging
import tempfile
import requests

# from PyQt4.QtGui import QDialog, QMessageBox


LOGGER = logging.getLogger('InaSAFE')

def download(feature_type, output_base_path, extent, progress_dialog=None):
    """Download shapefiles from Kartoza server.
    .. versionadded:: 3.2
    :param feature_type: What kind of features should be downloaded.
        Currently 'buildings', 'building-points' or 'roads' are supported.
    :type feature_type: str
    :param output_base_path: The base path of the shape file.
    :type output_base_path: str
    :param extent: A list in the form [xmin, ymin, xmax, ymax] where all
    coordinates provided are in Geographic / EPSG:4326.
    :type extent: list
    :param progress_dialog: A progress dialog.
    :type progress_dialog: QProgressDialog
    :raises: ImportDialogError, CanceledImportDialogError
    """

    # preparing coordinates of the Area to be dragged
    min_longitude = extent[0]
    min_latitude = extent[1]
    max_longitude = extent[2]
    max_latitude = extent[3]

    min_long_max_lat = [min_longitude, max_latitude]
    max_long_max_lat = [max_longitude, max_latitude]
    max_long_min_lat = [max_longitude, min_latitude]
    min_long_min_lat = [min_longitude, min_latitude]

    coordinates = '[[' + str(min_long_max_lat) + ',' + \
                  str(max_long_max_lat) + ',' + \
                  str(max_long_min_lat) + ',' + \
                  str(min_long_min_lat) + ',' + \
                  str(min_long_max_lat) + ']]'

    data = {'coordinates': coordinates}

    # python requests to fetch json data from Api
    url = 'https://worldpop-api-server.herokuapp.com/api'
    response = requests.post(url, data)
    response.content
    population_data = response.content

    # msgBox = QMessageBox()
    # msgBox.setText(population_data)

    path = tempfile.mktemp('.geojson')
    file_path = output_base_path + '.geojson'

    with open(file_path, 'w+') as outfile:
        outfile.write(population_data)
