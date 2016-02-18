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
__author__ = 'etienne@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '25/06/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import zipfile
import os
import logging
import tempfile

from PyQt4.QtNetwork import QNetworkReply
from PyQt4.QtGui import QDialog

from safe.utilities.i18n import tr
from safe.utilities.gis import qgis_version
from safe.utilities.file_downloader import FileDownloader
from safe.common.exceptions import DownloadError, CanceledImportDialogError
from safe.common.version import get_version

URL_OSM_PREFIX = 'http://osm.inasafe.org/'
URL_OSM_SUFFIX = '-shp'

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

    # preparing necessary data
    min_longitude = extent[0]
    min_latitude = extent[1]
    max_longitude = extent[2]
    max_latitude = extent[3]

    box = (
        '{min_longitude},{min_latitude},{max_longitude},'
        '{max_latitude}').format(
            min_longitude=min_longitude,
            min_latitude=min_latitude,
            max_longitude=max_longitude,
            max_latitude=max_latitude
    )

    url = URL_OSM_PREFIX + feature_type + URL_OSM_SUFFIX
    url = '{url}?bbox={box}&qgis_version={qgis}'.format(
        url=url, box=box, qgis=qgis_version())

    url += '&inasafe_version=%s' % get_version()

    if 'LANG' in os.environ:
        # Get the language only : eg 'en_US' -> 'en'
        env_lang = os.environ['LANG'].split('_')[0]
        url += '&lang=%s' % env_lang

    path = tempfile.mktemp('.shp.zip')

    # download and extract it
    fetch_zip(url, path, feature_type, progress_dialog)
    extract_zip(path, output_base_path)

    if progress_dialog:
        progress_dialog.done(QDialog.Accepted)


def fetch_zip(url, output_path, feature_type, progress_dialog=None):
    """Download zip containing shp file and write to output_path.

    .. versionadded:: 3.2

    :param url: URL of the zip bundle.
    :type url: str

    :param output_path: Path of output file,
    :type output_path: str

    :param feature_type: What kind of features should be downloaded.
        Currently 'buildings', 'building-points' or 'roads' are supported.
    :type feature_type: str

    :param progress_dialog: A progress dialog.
    :type progress_dialog: QProgressDialog

    :raises: ImportDialogError - when network error occurred
    """
    LOGGER.debug('Downloading file from URL: %s' % url)
    LOGGER.debug('Downloading to: %s' % output_path)

    if progress_dialog:
        progress_dialog.show()

        # Infinite progress bar when the server is fetching data.
        # The progress bar will be updated with the file size later.
        progress_dialog.setMaximum(0)
        progress_dialog.setMinimum(0)
        progress_dialog.setValue(0)

        # Get a pretty label from feature_type, but not translatable
        label_feature_type = feature_type.replace('-', ' ')

        label_text = tr('Fetching %s' % label_feature_type)
        progress_dialog.setLabelText(label_text)

    # Download Process
    downloader = FileDownloader(url, output_path, progress_dialog)
    try:
        result = downloader.download()
    except IOError as ex:
        raise IOError(ex)

    if result[0] is not True:
        _, error_message = result

        if result[0] == QNetworkReply.OperationCanceledError:
            raise CanceledImportDialogError(error_message)
        else:
            raise DownloadError(error_message)


def extract_zip(zip_path, destination_base_path):
    """Extract different extensions to the destination base path.

    Example : test.zip contains a.shp, a.dbf, a.prj
    and destination_base_path = '/tmp/CT-buildings
    Expected result :
        - /tmp/CT-buildings.shp
        - /tmp/CT-buildings.dbf
        - /tmp/CT-buildings.prj

    If two files in the zip with the same extension, only one will be
    copied.

    .. versionadded:: 3.2

    :param zip_path: The path of the .zip file
    :type zip_path: str

    :param destination_base_path: The destination base path where the shp
        will be written to.
    :type destination_base_path: str

    :raises: IOError - when not able to open path or output_dir does not
        exist.
    """
    handle = open(zip_path, 'rb')
    zip_file = zipfile.ZipFile(handle)
    for name in zip_file.namelist():
        extension = os.path.splitext(name)[1]
        output_final_path = u'%s%s' % (destination_base_path, extension)
        output_file = open(output_final_path, 'wb')
        output_file.write(zip_file.read(name))
        output_file.close()

    handle.close()
