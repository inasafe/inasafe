# coding=utf-8
"""Sample file configuration for celery_app worker

This file is intended only for a sample.
Please copy it as celeryconfig.py so it can be read
"""
import os


__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/28/16'


# This is a default value
BROKER_URL = os.environ.get('INASAFE_HEADLESS_BROKER_HOST')

CELERY_RESULT_BACKEND = BROKER_URL

CELERY_ROUTES = {
    'headless.tasks.inasafe_wrapper': {
        'queue': 'inasafe-headless'
    }
}

DEPLOY_OUTPUT_DIR = os.environ.get('INASAFE_HEADLESS_DEPLOY_OUTPUT_DIR')
DEPLOY_OUTPUT_URL = os.environ.get('INASAFE_HEADLESS_DEPLOY_OUTPUT_URL')
