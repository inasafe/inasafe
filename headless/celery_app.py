# coding=utf-8
from celery import Celery

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/28/16'


app = Celery('headless.tasks')
app.config_from_object('headless.celeryconfig')

packages = (
    'headless',
)


# initialize qgis_app
from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


app.autodiscover_tasks(packages)

if __name__ == '__main__':
    app.worker_main()
