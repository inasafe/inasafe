# coding=utf-8

"""QGIS Expressions which are available in the QGIS GUI interface."""

import codecs
from qgis.core import qgsfunction, QgsExpressionContextUtils
from os.path import dirname, join, exists

from safe.definitions.provenance import provenance_layer_analysis_impacted
from safe.utilities.i18n import tr
from safe.utilities.utilities import generate_expression_help

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

group = tr('InaSAFE - HTML Elements')

##
# For QGIS < 2.18.13 and QGIS < 2.14.19, docstrings are used in the QGIS GUI
# in the Expression dialog and also in the InaSAFE Help dialog.
#
# For QGIS >= 2.18.13, QGIS >= 2.14.19 and QGIS 3, the translated variable will
# be used in QGIS.
# help_text is used for QGIS 2.18 and 2.14
# helpText is used for QGIS 3 : https://github.com/qgis/QGIS/pull/5059
##

description = tr('Retrieve an HTML table report of current selected analysis.')
examples = {
    'analysis_summary_report()': None
}
help_message = generate_expression_help(description, examples)


@qgsfunction(
    args='auto', group=group, usesGeometry=False, referencedColumns=[],
    help_text=help_message.to_html(), helpText=help_message.to_html())
def analysis_summary_report(with_style, feature, parent):
    """Retrieve an HTML table report of current selected analysis.
    """
    _ = feature, parent  # NOQA
    project_context_scope = QgsExpressionContextUtils.projectScope()
    key = provenance_layer_analysis_impacted['provenance_key']
    if not project_context_scope.hasVariable(key):
        return None

    analysis_dir = dirname(project_context_scope.variable(key))
    table_report_path = join(analysis_dir, 'output/impact-report-output.html')
    if not exists(table_report_path):
        return None

    # We can display an impact report.
    # We need to open the file in UTF-8, the HTML may have some accents
    with codecs.open(table_report_path, 'r', 'utf-8') as table_report_file:
        report = table_report_file.read()
        return report
