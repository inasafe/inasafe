# coding=utf-8
import logging
import os

from hammock import Hammock

from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/1/15'

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

INASAFE_REALTIME_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
if 'INASAFE_REALTIME_DATETIME_FORMAT' in os.environ:
    INASAFE_REALTIME_DATETIME_FORMAT = \
        os.environ['INASAFE_REALTIME_DATETIME_FORMAT']

INASAFE_REALTIME_REST_URLPATTERN = {
    'login': INASAFE_REALTIME_REST_LOGIN_URL,
}


class InaSAFEDjangoREST(object):

    def __init__(self):
        self.base_rest = Hammock(INASAFE_REALTIME_REST_URL, append_slash=True)
        self.session_login()

    def base_url(self):
        return str(self.base_rest)

    def session_login(self):
        """Session login to Realtime InaSAFE Django
        """
        r = self.base_rest.auth.login.GET()
        csrf_token = r.cookies.get('csrftoken')
        login_data = {
            'username': INASAFE_REALTIME_REST_USER,
            'password': INASAFE_REALTIME_REST_PASSWORD,
            'csrfmiddlewaretoken': csrf_token,
            'next': INASAFE_REALTIME_REST_URL
        }
        self.base_rest.auth.login.POST(data=login_data)

    @property
    def rest(self):
        return self.base_rest

    @classmethod
    def is_configured(cls):
        """Determine if realtime REST is configured.

        :return: True if Realtime REST credentials is provided in os.environ
        """
        return (INASAFE_REALTIME_REST_URL and
                INASAFE_REALTIME_REST_USER and
                INASAFE_REALTIME_REST_PASSWORD)

    @property
    def cookies(self):
        r = self.base_rest.auth.login.GET()
        return r.cookies

    @property
    def csrf_token(self):
        return self.cookies.get('csrftoken')

    @property
    def is_logged_in(self):
        headers = {
            'X-CSRFTOKEN': self.csrf_token
        }
        r = self.base_rest.is_logged_in.GET(headers=headers)
        return r.json().get('is_logged_in')
