# coding=utf-8
import logging

from realtime.celery_app import app
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/17/16'


# Initialized in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


@app.task(
    name='realtime.tasks.generic.check_broker_connection',
    queue='inasafe-realtime')
def check_broker_connection():
    """Check broker connection with Realtime Tasks

    :return: True
    """
    # We didn't do anything actually just return a boolean value
    # to indicate it is executed by the worker.
    return True
