# coding=utf-8
import json
import logging
import os
from zipfile import ZipFile

import requests

from realtime.exceptions import RESTRequestFailedError
from realtime.flood.flood_event import FloodEvent
from realtime.push_rest import (
    InaSAFEDjangoREST)
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '12/01/15'

LOGGER = logging.getLogger(realtime_logger_name())


def push_flood_event_to_rest(flood_event, fail_silent=True):
    """Pushing flood event to REST server.

    :param flood_event: The flood event to push
    :type flood_event: FloodEvent

    :param fail_silent: If set True, will still continue whan the push process
        failed. Default vaule to True. If False, this method will raise
        exception.
    :type fail_silent:

    :return: Return True if successfully pushed data
    :rtype: bool
    """
    if not flood_event.impact_exists:
        LOGGER.info('No impact exists. Will not push anything')
        return

    inasafe_django = InaSAFEDjangoREST()
    # check credentials exists in os.environ
    if not inasafe_django.is_configured():
        LOGGER.info('Insufficient information to push flood event to '
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
        flood_data = {
            'event_id': flood_event.report_id,
            'data_source': flood_event.flood_data_source,
            'time': flood_event.time,
            'interval': flood_event.duration,
            'source': flood_event.source,
            'region': flood_event.region
        }
        flood_data_file = {
            'hazard_layer': (
                '%s-hazard.zip' % flood_event.report_id,
                open(flood_event.hazard_zip_path)),
            'impact_layer': (
                '%s-impact.zip' % flood_event.report_id,
                open(flood_event.impact_zip_path))
        }

        # modify headers
        headers = {
            'X-CSRFTOKEN': inasafe_django.csrf_token,
        }

        # check does the flood event already exists?
        response = session.flood(
            flood_data['event_id']).GET()
        if response.status_code == requests.codes.ok:
            # event exists, we should update using PUT Url
            response = session.flood(
                flood_data['event_id']).PUT(
                data=flood_data,
                files=flood_data_file,
                headers=headers)
        elif response.status_code == requests.codes.not_found:
            # event does not exists, create using POST url
            response = session.flood.POST(
                data=flood_data,
                files=flood_data_file,
                headers=headers)

        if not (response.status_code == requests.codes.ok or
                response.status_code == requests.codes.created):
            # raise exceptions
            error = RESTRequestFailedError(
                url=response.url,
                status_code=response.status_code,
                data=flood_data)
            if fail_silent:
                LOGGER.warning(error.message)
            else:
                raise error

        # post the report
        # build report data
        map_report_path = flood_event.map_report_path
        table_report_path = flood_event.table_report_path

        event_report_dict = {
            'event_id': flood_event.report_id,
            'language': flood_event.locale
        }
        event_report_files = {
            'impact_map': (
                '%s-map.pdf' % flood_event.report_id,
                open(map_report_path)),
            # 'impact_report': open(table_report_path)
        }
        # check report exists

        # build headers and cookies
        headers = {
            'X-CSRFTOKEN': inasafe_django.csrf_token,
        }
        response = session(
            'flood-report',
            event_report_dict['event_id'],
            event_report_dict['language']).GET()
        if response.status_code == requests.codes.ok:
            # event exists, we should update using PUT Url
            response = session(
                'flood-report',
                event_report_dict['event_id'],
                event_report_dict['language']).PUT(
                data=event_report_dict,
                files=event_report_files,
                headers=headers)
        elif response.status_code == requests.codes.not_found:
            # event doesn't exists, we should update using POST url
            response = session(
                'flood-report',
                event_report_dict['event_id']).POST(
                    data=event_report_dict,
                    files=event_report_files,
                    headers=headers)

        if not (response.status_code == requests.codes.ok or
                response.status_code == requests.codes.created):
            error = RESTRequestFailedError(
                url=response.url,
                status_code=response.status_code,
                data=event_report_dict,
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
