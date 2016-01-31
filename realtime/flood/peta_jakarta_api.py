# coding=utf-8
import logging

import requests

from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'

__date__ = '11/23/15'


LOGGER = logging.getLogger(realtime_logger_name())


class PetaJakartaAPI(object):

    @classmethod
    def get_aggregate_report(cls, duration, level):
        rest_point = 'https://petajakarta.org/banjir/data/api/v2/' \
                     'aggregates/live'
        params = {
            'hours': duration,
            'level': level,
            'format': 'geojson'
        }
        r = requests.get(rest_point, params=params)
        if not r.status_code == requests.codes.ok:
            LOGGER.error("Can't access API")
            return
        return r.text

