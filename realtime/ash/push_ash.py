# coding=utf-8
import logging

import requests

from realtime.ash.ash_event import AshEvent
from realtime.exceptions import RESTRequestFailedError
from realtime.push_rest import InaSAFEDjangoREST
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '7/13/16'

LOGGER = logging.getLogger(realtime_logger_name())


def push_ash_event_to_rest(ash_event, fail_silent=True):
    """Push ash event to inasafe-django

    :param ash_event: The Ash Event
    :type ash_event: AshEvent
    :param fail_silent:
    :return:
    """
    if not ash_event.impact_exists:
        LOGGER.info('No impact exists. Will not push anything')
        return

    inasafe_django = InaSAFEDjangoREST()
    # check credentials exists in os.environ
    if not inasafe_django.is_configured():
        LOGGER.info('Insufficient information to push ash event to '
                    'Django Realtime')
        LOGGER.info('Please set environment for INASAFE_REALTIME_REST_URL, '
                    'INASAFE_REALTIME_REST_LOGIN_URL, '
                    'INASAFE_REALTIME_REST_USER, and '
                    'INASAFE_REALTIME_REST_PASSWORD')
        return

    # set headers and cookie
    # begin communicating with server
    LOGGER.info('----------------------------------')
    LOGGER.info('Push data to REST server: %s', inasafe_django.base_url())
    try:
        session = inasafe_django.rest

        # build the data request:
        dateformat = '%Y-%m-%d %H:%M:%S %z'
        timestring = '%Y%m%d%H%M%S%z'
        ash_data = {
            'volcano_name': ash_event.volcano_name,
            'event_time': ash_event.time.strftime(dateformat),
            'language': ash_event.locale,
        }
        ash_data_file = {
            'impact_files': (
                '%s-impact.zip' % ash_event.event_id,
                open(ash_event.impact_zip_path)),
        }

        # modify headers
        headers = {
            'X-CSRFTOKEN': inasafe_django.csrf_token,
        }

        # post impact results
        # Update using PUT url
        response = session.ash(
            ash_data['volcano_name'],
            ash_event.time.strftime(timestring)).PUT(
            files=ash_data_file,
            headers=headers)

        if not (response.status_code == requests.codes.ok or
                response.status_code == requests.codes.created):
            error = RESTRequestFailedError(
                url=response.url,
                status_code=response.status_code,
                files=ash_data_file)

            if fail_silent:
                LOGGER.warning(error.message)
            else:
                raise error

        # post the report
        # build report data
        event_report_files = {
            'report_map': open(ash_event.map_report_path),
        }
        # check report exists

        # build headers and cookies
        headers = {
            'X-CSRFTOKEN': inasafe_django.csrf_token,
        }
        response = session(
            'ash-report',
            ash_data['volcano_name'],
            ash_event.time.strftime(timestring)).GET()
        report_exists = False
        if response.status_code == requests.codes.ok:
            result = response.json()
            if result and 'count' in result and result['count'] > 0:
                report_exists = True
        elif response.status_code == requests.codes.not_found:
            report_exists = False

        if report_exists:
            # event exists, we should update using PUT Url
            response = session(
                'ash-report',
                ash_data['volcano_name'],
                ash_event.time.strftime(timestring),
                ash_event.locale).PUT(
                data=ash_data,
                files=event_report_files,
                headers=headers)
        else:
            # event doesn't exists, we should update using POST url
            response = session(
                'ash-report',
                ash_data['volcano_name'],
                ash_event.time.strftime(timestring)).POST(
                data=ash_data,
                files=event_report_files,
                headers=headers)

        if not (response.status_code == requests.codes.ok or
                response.status_code == requests.codes.created):
            error = RESTRequestFailedError(
                url=response.url,
                status_code=response.status_code,
                data=ash_data,
                files=event_report_files)

            if fail_silent:
                LOGGER.warning(error.message)
            else:
                raise error
        return True
    # pylint: disable=broad-except
    except Exception as exc:
        if fail_silent:
            LOGGER.warning(exc)
        else:
            raise exc
