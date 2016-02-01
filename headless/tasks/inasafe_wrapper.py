# coding=utf-8
import logging

import datetime

import os
import tempfile

import shutil
import urlparse

from headless import LOGGER_NAME
from headless.celeryapp import app
from headless.celeryconfig import deploy_output_dir, deploy_output_url
from headless.tasks.utilities import download_layer, archive_layer, \
    generate_styles
from bin.inasafe import CommandLineArguments, get_impact_function_list, \
    run_impact_function, build_report
from safe.storage.utilities import safe_to_qgis_layer

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/19/16'

LOGGER = logging.getLogger('InaSAFE')


@app.task
def filter_impact_function(hazard, exposure):
    """Filter impact functions

    :param hazard: URL or filepath of hazard
    :type hazard: str

    :param exposure: URL or filepath of exposure
    :type exposure: str

    :return: List of Impact Function metadata as dict
    :rtype: list(dict)

    """
    # download the file first
    hazard_file = download_layer(hazard)
    exposure_file = download_layer(exposure)
    arguments = CommandLineArguments()
    arguments.hazard = hazard_file
    arguments.exposure = exposure_file
    ifs = get_impact_function_list(arguments)
    return [f.metadata().as_dict() for f in ifs]


@app.task
def run_analysis(hazard, exposure, function, aggregation=None,
                 generate_report=False):
    """Run analysis"""
    hazard_file = download_layer(hazard)
    exposure_file = download_layer(exposure)
    aggregation_file = None
    if aggregation:
        aggregation_file = download_layer(aggregation)
    arguments = CommandLineArguments()
    arguments.hazard = hazard_file
    arguments.exposure = exposure_file
    arguments.aggregation = aggregation_file
    arguments.impact_function = function

    # generate names for impact results
    # create date timestamp
    date_folder = datetime.datetime.now().strftime('%Y%m%d')
    deploy_dir = os.path.join(deploy_output_dir, date_folder)
    try:
        os.mkdir(deploy_dir)
    except:
        pass

    # create temporary file name without extension
    tmp = tempfile.mktemp(dir=deploy_dir)
    arguments.output_file = tmp
    impact_layer = run_impact_function(arguments)

    if impact_layer.is_raster:
        new_name = '%s.tif' % tmp
    else:
        new_name = '%s.shp' % tmp

    # if asked to generate report
    if generate_report:
        arguments.report_template = ''
        arguments.output_file = new_name
        build_report(arguments)

    # generating qml styles file
    qgis_impact_layer = safe_to_qgis_layer(impact_layer)
    generate_styles(impact_layer, qgis_impact_layer)

    # archiving the layer
    new_name = archive_layer(new_name)
    # new_name is a file path to archived layer
    # we need to return the url
    new_basename = os.path.basename(new_name)
    output_url = urlparse.urljoin(
        deploy_output_url,
        '%s/%s' % (date_folder, new_basename)
    )
    return output_url
