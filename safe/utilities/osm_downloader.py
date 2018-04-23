# coding=utf-8
"""OSM Downloader tool."""

import logging
import os
import tempfile
import zipfile

from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtNetwork import QNetworkReply

from safe.common.exceptions import DownloadError, CanceledImportDialogError
from safe.common.version import get_version
from safe.definitions.osm_downloader import PRODUCTION_SERVER, URL_OSM_SUFFIX
from safe.utilities.file_downloader import FileDownloader
from safe.utilities.gis import qgis_version
from safe.utilities.i18n import tr, locale

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


def download(
        feature_type,
        output_base_path,
        extent,
        progress_dialog=None,
        server_url=None):
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

    :param server_url: The server URL to use.
    :type: basestring

    :raises: ImportDialogError, CanceledImportDialogError
    """
    if not server_url:
        server_url = PRODUCTION_SERVER

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

    url = (
        '{url_osm_prefix}'
        '{feature_type}'
        '{url_osm_suffix}?'
        'bbox={box}&'
        'qgis_version={qgis}&'
        'lang={lang}&'
        'inasafe_version={inasafe_version}'.format(
            url_osm_prefix=server_url,
            feature_type=feature_type,
            url_osm_suffix=URL_OSM_SUFFIX,
            box=box,
            qgis=qgis_version(),
            lang=locale(),
            inasafe_version=get_version()))

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
        output_final_path = '%s%s' % (destination_base_path, extension)
        output_file = open(output_final_path, 'wb')
        output_file.write(zip_file.read(name))
        output_file.close()

    handle.close()
