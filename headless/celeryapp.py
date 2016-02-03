# coding=utf-8
import sys
from celery import Celery

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/28/16'


app = Celery('headless.tasks')
app.config_from_object('headless.celeryconfig')

packages = (
    'headless',
)

# import all tasks package
import headless.tasks.inasafe_wrapper

app.autodiscover_tasks(packages)

if __name__ == '__main__':
    app.worker_main()
