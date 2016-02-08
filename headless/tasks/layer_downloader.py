# coding=utf-8
import os
import urllib
from zipfile import ZipFile

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/27/16'


def download_layer(url):
    """Download a layer specified by url to a directory"""
    # download archive file
    filename, _ = urllib.urlretrieve(url)
    base_name, _ = os.path.splitext(filename)
    dir_name = os.path.dirname(filename)
    with ZipFile(filename) as zipf:
        name_list = zipf.namelist()
        place = zipf.extractall(path=dir_name)
        layer_extensions = ['.shp', '.tif', '.asc']
        layer_ext = None
        for name in name_list:
            for ext in layer_extensions:
                if name.endswith(ext):
                    layer_ext = ext
                    break
            if layer_ext:
                break

    return base_name + layer_ext
