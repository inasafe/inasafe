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
        r = self.inasafe_django.rest.is_logged_in.GET()
        self.assertEqual(r.status_code, codes.ok)
        self.assertTrue(r.json()['is_logged_in'])
