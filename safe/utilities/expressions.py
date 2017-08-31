# coding=utf-8

"""Utilities module related to QGIS Expressions."""

from inspect import getmembers


from safe.gis import generic_expressions
from safe.report.expressions import infographic, map_report


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def qgis_expressions():
    """Retrieve all QGIS Expressions provided by InaSAFE.

    :return: Dictionary of expression name and the expression itself.
    :rtype: dict
    """
    all_expressions = {
        fct[0]: fct[1] for fct in getmembers(generic_expressions)
        if fct[1].__class__.__name__ == 'QgsExpressionFunction'}
    all_expressions.update({
        fct[0]: fct[1] for fct in getmembers(infographic)
        if fct[1].__class__.__name__ == 'QgsExpressionFunction'})
    all_expressions.update({
        fct[0]: fct[1] for fct in getmembers(map_report)
        if fct[1].__class__.__name__ == 'QgsExpressionFunction'})
    return all_expressions
