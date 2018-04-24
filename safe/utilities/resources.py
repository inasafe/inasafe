# coding=utf-8
"""This module contains utilities for locating application resources (img etc).
"""

import codecs
import os

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA pylint: disable=unused-import
from qgis.PyQt import QtCore, uic

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def html_footer():
    """Get a standard html footer for wrapping content in.

    :returns: A header containing a web page closing content in html - up to
        and including the body close tag.
    :rtype: str
    """
    file_path = resources_path('footer.html')
    with open(file_path) as header_file:
        content = header_file.read()
    return content


def html_header():
    """Get a standard html header for wrapping content in.

    :returns: A header containing a web page preamble in html - up to and
        including the body open tag.
    :rtype: str
    """
    file_path = resources_path('header.html')

    with codecs.open(file_path, 'r', encoding='utf8') as header_file:
        content = header_file.read()
        content = content.replace('PATH', resources_path())
    return content


def html_help_header():
    """Get a standard help html header for wrapping content in.

    This one differs from the normal html header in that it will
    include style rules to number headings.

    ..versionadded:: 4.0

    :returns: A header containing a web page preamble in html - up to and
        including the body open tag.
    :rtype: str
    """
    file_path = resources_path('header-help.html')

    with codecs.open(file_path, 'r', encoding='utf8') as header_file:
        content = header_file.read()
        content = content.replace('PATH', resources_path())
    return content


def resources_path(*args):
    """Get the path to our resources folder.

    .. versionadded:: 3.0

    Note that in version 3.0 we removed the use of Qt Resource files in
    favour of directly accessing on-disk resources.

    :param args List of path elements e.g. ['img', 'logos', 'image.png']
    :type args: str

    :return: Absolute path to the resources folder.
    :rtype: str
    """
    path = os.path.dirname(__file__)
    path = os.path.abspath(
        os.path.join(path, os.path.pardir, 'resources'))
    for item in args:
        path = os.path.abspath(os.path.join(path, item))

    return path


def resource_url(path):
    """Get the a local filesystem url to a given resource.

    .. versionadded:: 3.0

    Note that in version 3.0 we removed the use of Qt Resource files in
    favour of directly accessing on-disk resources.

    :param path: Path to resource e.g. /home/timlinux/foo/bar.png
    :type path: str

    :return: A valid file url e.g. file:///home/timlinux/foo/bar.png
    :rtype: str
    """
    url = QtCore.QUrl.fromLocalFile(path)
    return str(url.toString())


def get_ui_class(ui_file):
    """Get UI Python class from .ui file.

       Can be filename.ui or subdirectory/filename.ui

    :param ui_file: The file of the ui in safe.gui.ui
    :type ui_file: str
    """
    os.path.sep.join(ui_file.split('/'))
    ui_file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            'gui',
            'ui',
            ui_file
        )
    )
    return uic.loadUiType(ui_file_path)[0]
