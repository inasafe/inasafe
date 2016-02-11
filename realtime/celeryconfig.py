# coding=utf-8
"""
Celery configuration file
"""
import os

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/30/15'


BROKER_URL = os.environ.get('BROKER_URL', None)
