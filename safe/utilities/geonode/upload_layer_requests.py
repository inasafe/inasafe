# -*- coding: utf-8 -*-

"""Upload a layer to Geonode using the web scrapping."""


import re
import os
import json
import requests
from requests.compat import urljoin
from os.path import splitext, isfile, split

from safe.common.exceptions import (
    GeoNodeLoginError, GeoNodeInstanceError, GeoNodeLayerUploadError)
from safe.utilities.i18n import tr
from safe.gis.vector.convert_geojson_to_shapefile import (
    convert_geojson_to_shapefile
)

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

login_url_prefix = 'account/login/'
upload_url_prefix = 'layers/upload'

# Extensions we are looking for
extension_siblings = {
    '.asc': {
        '.asc': 'application/octet-stream',
        '.prj': 'application/octet-stream',
        '.qml': 'application/octet-stream',
        '.sld': 'application/octet-stream',  # ?
        '.xml': 'text/xml',
    },
    '.tif': {
        '.tif': 'application/octet-stream',
        '.qml': 'application/octet-stream',
        '.xml': 'text/xml',
    },
    '.tiff': {
        '.tif': 'application/octet-stream',
        '.qml': 'application/octet-stream',
        '.xml': 'text/xml',
    },
    '.geojson': {
        '.geojson': 'application/vnd.geo+json',
        '.qml': 'application/octet-stream',
        '.sld': 'application/octet-stream',  # ?
        '.xml': 'text/xml',
    },
    '.shp': {
        '.dbf': 'application/x-dbase',
        '.prj': 'application/octet-stream',
        '.qml': 'application/octet-stream',
        '.shp': 'application/octet-stream',
        '.shx': 'application/octet-stream',
        '.sld': 'application/octet-stream',  # ?
        '.qpj': 'application/octet-stream',  # ?
        '.xml': 'text/xml',
    },
}


def siblings_files(path):
    """Return a list of sibling files available."""
    file_basename, extension = splitext(path)
    main_extension = extension.lower()
    files = {}
    if extension.lower() in list(extension_siblings.keys()):
        for text_extension in list(extension_siblings[main_extension].keys()):
            if isfile(file_basename + text_extension):
                files[file_basename + text_extension] = (
                    extension_siblings[main_extension][text_extension])

    if len(files) > 0:
        mime_base_file = extension_siblings[main_extension][main_extension]
    else:
        mime_base_file = None
    return files, mime_base_file


def pretty_print_post(req):
    """Helper to print a "prepared" query. Useful to debug a POST query.

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print(('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in list(req.headers.items())),
        req.body,
    )))


def login_user(server, login, password):
    """Get the login session.

    :param server: The Geonode server URL.
    :type server: basestring

    :param login: The login to use on Geonode.
    :type login: basestring

    :param password: The password to use on Geonode.
    :type password: basestring
    """
    login_url = urljoin(server, login_url_prefix)

    # Start the web session
    session = requests.session()
    result = session.get(login_url)

    # Check if the request ok
    if not result.ok:
        message = (tr(
            'Request failed to {geonode_url}, got status code {status_code} '
            'and reason {request_reason}').format(
                geonode_url=server,
                status_code=result.status_code,
                request_reason=result.reason))
        raise GeoNodeInstanceError(message)

    # Take the CSRF token
    login_form_regexp = (
        "<input type='hidden' name='csrfmiddlewaretoken' value='(.*)' />")
    expression_compiled = re.compile(login_form_regexp)
    match = expression_compiled.search(result.content)
    csrf_token = match.groups()[0]

    payload = {
        'username': login,
        'password': password,
        'csrfmiddlewaretoken': csrf_token,
    }

    # Make the login
    result = session.post(login_url, data=payload, headers=dict(
        referer=login_url))

    # Check the result url to check if the login success
    if result.url == login_url:
        message = tr('Failed to login to GeoNode at {geonode_url}').format(
            geonode_url=server)
        raise GeoNodeLoginError(message)

    return session


def upload(server, session, base_file, charset='UTF-8'):
    """Push a layer to a Geonode instance.

    :param server: The Geonode server URL.
    :type server: basestring

    :param base_file: The base file layer to upload such as a shp, geojson, ...
    :type base_file: basestring

    :param charset: The encoding to use. Default to UTF-8.
    :type charset: basestring
    """
    file_ext = os.path.splitext(base_file)[1]
    is_geojson = file_ext in ['.geojson', '.json']
    original_sibling_files, _ = siblings_files(base_file)
    if is_geojson:
        # base_file = os.path.splitext(base_file)[0]
        # create temp shapefile
        convert_geojson_to_shapefile(base_file)
        base_file = os.path.splitext(base_file)[0] + '.shp'

    upload_url = urljoin(server, upload_url_prefix)
    result = session.get(upload_url)

    # Get the upload CSRF token
    expression = re.compile('csrf_token(\s*)=(\s*)"([a-zA-Z0-9]*?)",')
    match = expression.search(result.content)
    csrf_token = match.groups()[2]

    # Start the data dict
    payload = {
        'charset': charset,
        'permissions': (
            '{"users":{"AnonymousUser":'
            '["view_resourcebase","download_resourcebase"]},"groups":{}}'
        )
    }

    headers = dict()
    headers['referer'] = upload_url
    headers['X-CSRFToken'] = csrf_token

    files, mime = siblings_files(base_file)
    if len(files) < 1:
        raise RuntimeError(tr('The base layer is not recognised.'))

    name_file = split(base_file)[1]
    multiple_files = [
        ('base_file', (name_file, open(base_file, 'rb'), mime)),
    ]
    for sibling, mime in list(files.items()):
        if sibling != base_file:
            name_param = splitext(sibling)[1][1:]
            name_file = split(sibling)[1]
            open_file = (name_file, open(sibling, 'rb'), mime)
            definition = ('{}_file'.format(name_param), open_file)
            multiple_files.append(definition)

    # For debug
    upload_request = requests.Request(
        'POST',
        upload_url,
        data=payload,
        files=multiple_files,
        headers=headers)

    prepared_request = session.prepare_request(upload_request)
    # For debug
    # pretty_print_post(prepared_request)
    result = session.send(prepared_request)

    # Clean up shapefile and its sibling friends
    if is_geojson:
        for filename in files.keys():
            if filename not in original_sibling_files:
                try:
                    os.remove(filename)
                except OSError:
                    pass

    if result.ok:
        result = json.loads(result.content)
        full_url = server + result['url']
        result['full_url'] = full_url
        return result
    else:
        message = (tr(
            'Failed to upload layer. Got HTTP Status Code {status_code} and '
            'the reason is {reason}').format(
                status_code=result.status_code, reason=result.reason))
        raise GeoNodeLayerUploadError(message)
