# coding=utf-8

from celery import Celery

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/11/15'

app = Celery('realtime.tasks')
app.config_from_object('realtime.celeryconfig')

packages = (
    'realtime',
)

# initialize qgis_app
from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

app.autodiscover_tasks(packages)

if __name__ == '__main__':
    app.worker_main()
