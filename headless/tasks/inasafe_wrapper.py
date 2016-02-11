# coding=utf-8
import logging


from headless import LOGGER_NAME
from headless.celeryapp import app
from headless.tasks.layer_downloader import download_layer
from bin.inasafe import CommandLineArguments, get_impact_function_list

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/19/16'

LOGGER = logging.getLogger(LOGGER_NAME)


@app.task()
def filter_impact_function(hazard, exposure):
    # download the file first
    hazard_file = download_layer(hazard)
    exposure_file = download_layer(exposure)
    arguments = CommandLineArguments()
    arguments.hazard = hazard_file
    arguments.exposure = exposure_file
    ifs = get_impact_function_list(arguments)
    LOGGER.info('Impact functions : %s' % ifs)
    return ifs
