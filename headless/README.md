# InaSAFE Headless Package

***

## Introduction

This package is dedicated to store InaSAFE Headless module. InaSAFE Headless 
module (shortened as just Headless) is created to provide celery based utility 
module to execute InaSAFE related tasks, such as filtering available impact 
function, or running an anlysis, and also some trivial things like reading a 
keyword file.

This is a celery based package, so it has to be setup as a celery worker and 
paired it with broker of your choices. This celery app will have a name 
**headless.tasks** and will process a queue named **inasafe-headless**.

## How to Use

This is a celery based package. So we need to setup the broker, worker, and 
client code which uses this package. Each will be described. Consult 
[Celery documentation](http://docs.celeryproject.org/en/latest/index.html) 
for more info about celery terminology

### Setup the broker

First, you need to setup the broker to handle the messaging part. Any broker 
supported by celery works fine. You can have a centralized broker or dedicated 
broker to handle Headless. 

Centralized means Headless queue will be handled 
along with other queue of other celery app. It will work as long as the app 
name and queue name doesn't clash. So you can have one broker which handles 
other celery app and also with Headless app.

Dedicated broker means Headless queue will be handled by one broker dedicated 
only for Headless app. You basically create another broker to handle Headless 
and set it up accordingly. This broker will be different than the broker your 
other celery app uses.

### Setup the worker

You need worker with QGIS Installed and configured so it would be able to run 
InaSAFE headlessly. Follow InaSAFE installation for development, also installs 
necessary packages in headless/REQUIREMENTS.txt.

A typical way of running the worker would be (all commands relative to InaSAFE 
directory)

```
# Sourcing InaSAFE Environment
# This will provide QGIS related environment variable
source run-env-linux.sh /usr

# Sourcing Headless Environment
# see headless/inasafe-headless-env.sh.sample
# also see headless/celeryconfig_sample.py to configure the config file needed
source inasafe-headless-env.sh

# Run using xvfb for headless environment
# -l for log level
# -Q for the queue name
xvfb-run --server-args="-screen 0, 1024x768x24" -e xvfb.log celery -A headless.celery_app worker -l info -Q inasafe-headless
```

### Setup the client code

The client code only needs to specify the app configuration. It can be as 
as simple as this (save this file as celery_app.py):

```
from celery import Celery

app = Celery('headless.tasks')
app.config_from_object('package.to.celeryconfig')

```

The package.to.celeryconfig is a python module that contains celery config 
settings. A minimal configuration will be like this:

```
BROKER_URL = 'redis://localhost:6379/0'

CELERY_RESULT_BACKEND = BROKER_URL

CELERY_ROUTES = {
	'headless.tasks.inasafe_wrapper': {
		'queue': 'inasafe-headless'
	}
}
```

To easily calls Headless celery tasks, you need to define a proxy method. 
This methods/functions are only python functions with the same signature as 
in the Headless tasks functions, and tagged with the same task name. For 
example, to use headless.tasks.inasafe_wrapper.filter_impact_function task:

```
@app.task(
    name='headless.tasks.inasafe_wrapper.filter_impact_function',
    queue='inasafe-headless')
def filter(hazard=None, exposure=None):
    """Filter available impact function for a given hazard and exposure.

    Proxy tasks for celery broker. It is not actually implemented here.
    It is implemented in InaSAFE headless.tasks package

    :param hazard: Hazard url path
    :type hazard: str

    :param exposure: Exposure url path
    :type exposure: str

    :return: The list of Impact Function ID
    :rtype: list(str)
    """
    LOGGER.info('This function is intended to be executed by celery task')
```

Note the following from above sample:

- **app** variable is imported from celery app configuration module: ```celery_app.py```
- function name: ```filter``` doesn't necessarily the same name with the task name in headless.tasks package  
- you should always specify the target task name in the name keyword of **app.task** decorator, also don't forget the queue name.

After creating a proxy task/method/function. You can use it as a regular 
celery task like this:

```
async_result = filter.delay(hazard_url, exposure_url)
result = async_result.get()
```
