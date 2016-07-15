# coding=utf-8
import logging
import os
from zipfile import ZipFile

import requests

from realtime.exceptions import RESTRequestFailedError
from realtime.ash.ash_event import AshEvent
from realtime.push_rest import (
    InaSAFEDjangoREST)
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
        LOGGER.info('Insufficient information to push shake map to '
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

        # Create a zipped impact layer
        impact_zip_path = os.path.join(ash_event.report_path, 'impact.zip')

        with ZipFile(impact_zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(ash_event.working_dir):
                for f in files:
                    _, ext = os.path.splitext(f)
                    if ('impact' in f and
                            not f == 'impact.zip' and
                            not ext == '.pdf'):
                        filename = os.path.join(root, f)
                        zipf.write(filename, arcname=f)

        # build the data request:
        dateformat = '%Y-%m-%d %H:%M:%S %z'
        timestring = '%Y%m%d%H%M%S%z'
        ash_data = {
            'volcano_name': ash_event.volcano_name,
            'time': ash_event.time.strftime(dateformat),
        }
        ash_data_file = {
            'impact_files': open(impact_zip_path),
            'map_report': open(ash_event.map_report_path),
        }

        # modify headers
        headers = {
            'X-CSRFTOKEN': inasafe_django.csrf_token,
        }

        # check does the shake event already exists?
        response = session.ash(
            ash_data['volcano_name'],
            ash_event.time.strftime(timestring)).GET()
        if response.status_code == requests.codes.ok:
            # event exists, we should update using PUT Url
            response = session.ash(
                ash_data['volcano_name'],
                ash_event.time.strftime(timestring)).PUT(
                data=ash_data,
                files=ash_data_file,
                headers=headers)
        elif response.status_code == requests.codes.not_found:
            # event does not exists, create using POST url
            response = session.ash.POST(
                data=ash_data,
                files=ash_data_file,
                headers=headers)

        if not (response.status_code == requests.codes.ok or
                response.status_code == requests.codes.created):
            # raise exceptions
            error = RESTRequestFailedError(
                url=response.url,
                status_code=response.status_code,
                data=ash_data)
            if fail_silent:
                LOGGER.warning(error.message)
            else:
                raise error

        # post the report
        # build report data
        event_report_files = {
            'map_report': open(ash_event.map_report_path),
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
        if response.status_code == requests.codes.ok:
            # event exists, we should update using PUT Url
            response = session(
                'ash-report',
                ash_data['volcano_name'],
                ash_event.time.strftime(timestring)).PUT(
                data=ash_data,
                files=event_report_files,
                headers=headers)
        elif response.status_code == requests.codes.not_found:
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
