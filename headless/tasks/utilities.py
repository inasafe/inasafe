# coding=utf-8
import os
import tempfile
import urlparse
from zipfile import ZipFile

import requests
import shutil

from safe.utilities.styling import set_vector_categorized_style, \
    set_vector_graduated_style, setRasterStyle

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/27/16'


def download_file(url):
    parsed_uri = urlparse.urlparse(url)
    if parsed_uri.scheme == 'http' or parsed_uri.scheme == 'https':
        tmpfile = tempfile.mktemp()
        # NOTE the stream=True parameter
        # Assign User-Agent to emulate browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) '
                          'Gecko/20071127 Firefox/2.0.0.11'
        }
        r = requests.get(url, headers=headers, stream=True)
        with open(tmpfile, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return tmpfile
    elif parsed_uri.scheme == 'file' or not parsed_uri.scheme:
        tmpfile = tempfile.mktemp()
        shutil.copy(parsed_uri.path, tmpfile)
        return tmpfile


def download_layer(url):
    """Download a layer specified by url to a directory

    :param url: The url or file path of the zip file
    :type url: str

    :return: The file path of extracted layer
    :rtype: str
    """
    # download archive file
    filename = download_file(url)
    base_name, _ = os.path.splitext(filename)
    dir_name = os.path.dirname(filename)
    layer_base_name = None
    with ZipFile(filename) as zipf:
        name_list = zipf.namelist()
        zipf.extractall(path=dir_name)
        layer_extensions = ['.shp', '.tif', '.asc']
        layer_ext = None
        for name in name_list:
            for ext in layer_extensions:
                if name.endswith(ext):
                    layer_ext = ext
                    layer_base_name = name
                    break
            if layer_ext:
                break

    return os.path.join(dir_name, layer_base_name)


def archive_layer(layer_name):
    """Archiving a layer with all dependent files to .zip

    :param layer_name: the layer name to archive
    :type layer_name: str

    :return: path to archive file
    :rtype: str

    """
    dirname, basename = os.path.split(layer_name)
    rootname, ext = os.path.splitext(basename)
    zip_basename = '%s.zip' % rootname

    zip_path = os.path.join(dirname, zip_basename)

    with ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(dirname):
            for f in files:
                _, ext = os.path.splitext(f)
                if rootname in f and not f == zip_basename:
                    filename = os.path.join(root, f)
                    zipf.write(filename, arcname=f)

    return zip_path


def generate_styles(safe_impact_layer, qgis_impact_layer):
    # Get requested style for impact layer of either kind
    style = safe_impact_layer.get_style_info()
    style_type = safe_impact_layer.get_style_type()

    # Determine styling for QGIS layer
    if safe_impact_layer.is_vector:
        if not style:
            # Set default style if possible
            pass
        elif style_type == 'categorizedSymbol':
            set_vector_categorized_style(qgis_impact_layer, style)
        elif style_type == 'graduatedSymbol':
            set_vector_graduated_style(qgis_impact_layer, style)

    elif safe_impact_layer.is_raster:
        if not style:
            qgis_impact_layer.setDrawingStyle("SingleBandPseudoColor")
        else:
            setRasterStyle(qgis_impact_layer, style)
