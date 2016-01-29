# coding=utf-8
import os

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/28/16'


BROKER_URL = 'amqp://guest:guest@%s:5672//' % (os.environ['AMQP_HOST'], )

CELERY_RESULT_BACKEND = 'db+postgresql://%s:%s@db/gis' % (
    os.environ['DB_USERNAME'], os.environ['DB_PASS'])
