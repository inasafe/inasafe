# coding=utf-8
import unittest

from hammock import Hammock
from requests import codes

from realtime.push_rest import INASAFE_REALTIME_REST_URL, InaSAFEDjangoREST

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/2/15'


class TestInasafeDjangoRest(unittest.TestCase):

    def setUp(self):
        self.inasafe_django = Hammock(INASAFE_REALTIME_REST_URL)

    def test_login_url(self):
        r = self.inasafe_django.auth.login.GET()
        self.assertEqual(r.status_code, codes.ok)

    def test_notify_shakemap_push_url(self):
        r = self.inasafe_django.indicator.notify_shakemap_push.GET()
        self.assertEqual(r.status_code, codes.ok)

    def test_earthquake_url(self):
        r = self.inasafe_django.earthquake.GET()
        self.assertEqual(r.status_code, codes.ok)
