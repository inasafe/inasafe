# coding=utf-8
import unittest

from requests import codes
from realtime.push_rest import InaSAFEDjangoREST

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/2/15'


class TestPushREST(unittest.TestCase):

    def setUp(self):
        self.inasafe_django = InaSAFEDjangoREST()

    def test_login(self):
        headers = {
            'X-CSRFTOKEN': self.inasafe_django.csrf_token
        }
        r = self.inasafe_django.rest.is_logged_in.GET(headers=headers)
        self.assertEqual(r.status_code, codes.ok)
        self.assertTrue(r.json().get('is_logged_in'))
