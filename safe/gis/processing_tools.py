# coding=utf-8

"""Processing utilities and tools."""

import processing

from qgis.core import (
    QgsApplication,
    QgsFeatureRequest,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProject)
from qgis.analysis import QgsNativeAlgorithms

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def initialize_processing():
    """
    Initializes processing, if it's not already been done
    """

    need_initialize = False

    needed_algorithms = [
        'native:clip',
        'gdal:cliprasterbyextent',
        'native:union',
        'native:intersection'
    ]

    if not QgsApplication.processingRegistry().algorithms():
        need_initialize = True

    if not need_initialize:
        for needed_algorithm in needed_algorithms:
            if not QgsApplication.processingRegistry().algorithmById(
                    needed_algorithm):
                need_initialize = True
                break

    if need_initialize:
        QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
        processing.Processing.initialize()


def create_processing_context(feedback):
    """
    Creates a default processing context

    :param feedback: Linked processing feedback object
    :type feedback: QgsProcessingFeedback

    :return: Processing context
    :rtype: QgsProcessingContext
    """
    context = QgsProcessingContext()
    context.setFeedback(feedback)
    context.setProject(QgsProject.instance())

    # skip Processing geometry checks - Inasafe has its own geometry validation
    # routines which have already been used
    context.setInvalidGeometryCheck(QgsFeatureRequest.GeometryNoCheck)
    return context


def create_processing_feedback():
    """
    Creates a default processing feedback object

    :return: Processing feedback
    :rtype: QgsProcessingFeedback
    """
    return QgsProcessingFeedback()
