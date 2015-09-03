# coding=utf-8
import json
import logging
import os
import requests
import re

from realtime.utilities import realtime_logger_name
from realtime.exceptions import RESTRequestFailedError

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/07/15'

LOGGER = logging.getLogger(realtime_logger_name())


# Get Realtime Rest URL from the os environment
INASAFE_REALTIME_REST_URL = None

if 'INASAFE_REALTIME_REST_URL' in os.environ:
    INASAFE_REALTIME_REST_URL = os.environ['INASAFE_REALTIME_REST_URL']

INASAFE_REALTIME_SHAKEMAP_HOOK_URL = None

if 'INASAFE_REALTIME_SHAKEMAP_HOOK_URL' in os.environ:
    INASAFE_REALTIME_SHAKEMAP_HOOK_URL = os.environ[
        'INASAFE_REALTIME_SHAKEMAP_HOOK_URL']

INASAFE_REALTIME_REST_USER = None
if 'INASAFE_REALTIME_REST_USER' in os.environ:
    INASAFE_REALTIME_REST_USER = os.environ['INASAFE_REALTIME_REST_USER']

INASAFE_REALTIME_REST_PASSWORD = None
if 'INASAFE_REALTIME_REST_PASSWORD' in os.environ:
    INASAFE_REALTIME_REST_PASSWORD = \
        os.environ['INASAFE_REALTIME_REST_PASSWORD']

INASAFE_REALTIME_REST_LOGIN_URL = None
if 'INASAFE_REALTIME_REST_LOGIN_URL' in os.environ:
    INASAFE_REALTIME_REST_LOGIN_URL = \
        os.environ['INASAFE_REALTIME_REST_LOGIN_URL']

INASAFE_REALTIME_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S %Z'
if 'INASAFE_REALTIME_DATETIME_FORMAT' in os.environ:
    INASAFE_REALTIME_DATETIME_FORMAT = \
        os.environ['INASAFE_REALTIME_DATETIME_FORMAT']

INASAFE_REALTIME_REST_URLPATTERN = {
    'login': INASAFE_REALTIME_REST_LOGIN_URL,
    'earthquake': INASAFE_REALTIME_REST_URL + 'earthquake/',
    'earthquake-detail': INASAFE_REALTIME_REST_URL + 'earthquake/<shake_id>',
    'earthquake-report': INASAFE_REALTIME_REST_URL + 'earthquake-report/',
    'earthquake-report-detail': (
        INASAFE_REALTIME_REST_URL + 'earthquake-report/<shake_id>/<locale>')
}


def generate_earthquake_list_url():
    """Generate url for earthquake list

    :return: url
    """
    return INASAFE_REALTIME_REST_URLPATTERN['earthquake']


def generate_earthquake_detail_url(shake_id):
    """Generate url for earthquake detail

    :param shake_id: the shake id of the event
    :type shake_id str:
    :return: url
    """
    return INASAFE_REALTIME_REST_URLPATTERN['earthquake-detail'].replace(
        '<shake_id>', shake_id)


def generate_earthquake_report_list_url():
    """Generate url for earthquake report list

    :return: url
    """
    return INASAFE_REALTIME_REST_URLPATTERN['earthquake-report']


def generate_earthquake_report_detail_url(shake_id, locale):
    """Generate url for earthquake report detail

    :param shake_id: the shake id of the event
    :param locale: the locale used for the report
    :return: url
    """
    return INASAFE_REALTIME_REST_URLPATTERN[
        'earthquake-report-detail'].replace(
            '<shake_id>', shake_id).replace(
                '<locale>', locale)


def get_realtime_session():
    """Get session of logged in user in Realtime django app

    :return: session requests object
    """
    session = requests.session()
    r = session.get(INASAFE_REALTIME_REST_LOGIN_URL)
    csrf_token = r.cookies.get('csrftoken')
    login_data = {
        'username': INASAFE_REALTIME_REST_USER,
        'password': INASAFE_REALTIME_REST_PASSWORD,
        'csrfmiddlewaretoken': csrf_token,
        'next': INASAFE_REALTIME_REST_URL
    }
    session.post(INASAFE_REALTIME_REST_LOGIN_URL, data=login_data)
    return session


def is_realtime_rest_configured():
    """Determine if realtime REST is configured.

    :return: True if Realtime REST credentials is provided in os.environ
    """
    return (INASAFE_REALTIME_REST_URL and
            INASAFE_REALTIME_REST_LOGIN_URL and
            INASAFE_REALTIME_REST_USER and
            INASAFE_REALTIME_REST_PASSWORD)


def notify_realtime_rest(timestamp):
    """Notify realtime rest that someone is logged in to realtime.

    This can indicate someone is pushing raw shakemap files

    :param timestamp: python datetime object indicating shakemap timestamp
    :type timestamp: datetime.datetime
    """
    session = get_realtime_session()
    data = {
        'timestamp': timestamp.strftime(INASAFE_REALTIME_DATETIME_FORMAT)
    }
    session.post(INASAFE_REALTIME_SHAKEMAP_HOOK_URL, data=json.dumps(data))
    # We will not handle post error, since we don't need it.
    # It just simply fails


def push_shake_event_to_rest(shake_event, fail_silent=True):
    """Pushing shake event Grid.xml description files to REST server.

    :param shake_event: The shake event to push
    :type shake_event: ShakeEvent
    """
    # check credentials exists in os.environ
    if not is_realtime_rest_configured():
        LOGGER.info('Insufficient information to push shake map to '
                    'Django Realtime')
        LOGGER.info('Please set environment for INASAFE_REALTIME_REST_URL, '
                    'INASAFE_REALTIME_REST_LOGIN_URL, '
                    'INASAFE_REALTIME_REST_USER, and '
                    'INASAFE_REALTIME_REST_PASSWORD')
        return

    event_dict = shake_event.event_dict()
    earthquake_list_url = generate_earthquake_list_url()
    earthquake_detail_url = generate_earthquake_detail_url(
        shake_event.event_id)

    # set headers and cookie
    # begin communicating with server
    LOGGER.info('----------------------------------')
    LOGGER.info('Push data to REST server: %s', INASAFE_REALTIME_REST_URL)
    try:
        session = get_realtime_session()
        cookies = session.get(earthquake_list_url,
                              params={'format': 'api'}).cookies
        session.headers['X-CSRFTOKEN'] = cookies.get('csrftoken')
        session.headers['Content-Type'] = 'application/json'

        # build the data request:
        earthquake_data = {
            'shake_id': shake_event.event_id,
            'magnitude': float(event_dict.get('mmi')),
            'depth': float(event_dict.get('depth-value')),
            'time': str(shake_event.shake_grid.time),
            'location': {
                'type': 'Point',
                'coordinates': [
                    shake_event.shake_grid.longitude,
                    shake_event.shake_grid.latitude
                ]
            },
            'location_description': event_dict.get('place-name')
        }
        # check does the shake event already exists?
        response = session.get(earthquake_detail_url)
        if response.status_code == requests.codes.ok:
            # event exists, we should update using PUT Url
            response = session.put(earthquake_detail_url,
                                   data=json.dumps(earthquake_data))
        elif response.status_code == requests.codes.not_found:
            # event does not exists, create using POST url
            response = session.post(earthquake_list_url,
                                    data=json.dumps(earthquake_data))

        if not (response.status_code == requests.codes.ok or
                response.status_code == requests.codes.created):
            # raise exceptions
            error = RESTRequestFailedError(
                url=response.url,
                status_code=response.status_code,
                data=json.dumps(earthquake_data))
            if fail_silent:
                LOGGER.error(error.message)
            else:
                raise error

        # post the report
        # build report data
        path_files = shake_event.generate_result_path_dict()
        event_report_dict = {
            'shake_id': shake_event.event_id,
            'language': shake_event.locale
        }
        event_report_files = {
            'report_pdf': open(path_files.get('pdf')),
            'report_image': open(path_files.get('image')),
            'report_thumbnail': open(path_files.get('thumbnail'))
        }
        # check report exists
        earthquake_report_detail_url = generate_earthquake_report_detail_url(
            shake_event.event_id, shake_event.locale)
        earthquake_report_list_url = generate_earthquake_report_list_url()

        # build headers and cookies
        session = get_realtime_session()
        response = session.get(earthquake_report_list_url,
                               params={'format': 'api'})
        cookies = response.cookies
        csrftoken = cookies.get('csrftoken')
        session.headers['X-CSRFToken'] = csrftoken
        response = session.get(earthquake_report_detail_url)
        if response.status_code == requests.codes.ok:
            # event exists, we should update using PUT Url
            response = session.put(
                earthquake_report_detail_url,
                data=event_report_dict,
                files=event_report_files)
        elif response.status_code == requests.codes.not_found:
            # event doesn't exists, we should update using POST url
            response = session.post(
                earthquake_report_list_url,
                data=event_report_dict,
                files=event_report_files)

        if not (response.status_code == requests.codes.ok or
                response.status_code == requests.codes.created):
            error = RESTRequestFailedError(
                url=response.url,
                status_code=response.status_code,
                data=event_report_dict,
                files=event_report_files)

            if fail_silent:
                LOGGER.error(error.message)
            else:
                raise error
    except Exception as exc:
        if not fail_silent:
            LOGGER.error(exc.message)
        else:
            raise exc
