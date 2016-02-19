# coding=utf-8
import logging
import os

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/11/16'


LOGGER = logging.getLogger('InaSAFE')
LOGGER.setLevel(logging.DEBUG)


def update_celery_configuration(app):
    """Update celery app configuration for test purposes

    Useful to toggle between eager test and async test

    :param app: App configuration
    :type app: celery.Celery
    :return:
    """
    celery_always_eager = os.environ.get(
        'CELERY_ALWAYS_EAGER', 'False') == 'True'
    app.conf.update(
        CELERY_ALWAYS_EAGER=celery_always_eager
    )
