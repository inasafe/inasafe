# coding=utf-8
"""This module contains utilities for locating application resources (img etc).
"""
import os
from PyQt4 import QtCore


def html_footer():
    """Get a standard html footer for wrapping content in.

    :returns: A header containing a web page closing content in html - up to
        and including the body close tag.
    :rtype: str
    """
    file_path = os.path.join(resources_path(), 'footer.html')
    with file(file_path) as header_file:
        content = header_file.read()
    return content


def html_header():
    """Get a standard html header for wrapping content in.

    :returns: A header containing a web page preamble in html - up to and
        including the body open tag.
    :rtype: str
    """
    file_path = os.path.join(resources_path(), 'header.html')
    with file(file_path) as header_file:
        content = header_file.read()
        content = content.replace('PATH', resources_path())
    return content


def resources_path(*args):
    """Get the path to our resources folder.

    .. versionadded:: 3.0

    Note that in version 3.0 we removed the use of Qt Resource files in
    favour of directly accessing on-disk resources.

    :param args List of path elements e.g. ['img', 'logos', 'image.png']
    :type args: list

    :return: Absolute path to the resources folder.
    :rtype: str
    """
    path = os.path.dirname(__file__)
    path = os.path.abspath(
        os.path.join(path, os.path.pardir, os.path.pardir, 'resources'))
    for item in args:
        path = os.path.abspath(os.path.join(path, item))
    url = QtCore.QUrl(path)
    path = url.toLocalFile()
    return str(path)
