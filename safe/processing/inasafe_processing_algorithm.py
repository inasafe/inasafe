# coding=utf-8

__copyright__ = "Copyright 2019, Kartoza"
__license__ = "GPL version 3"
__email__ = "rohmat@kartoza.com"
__revision__ = "$Format:%H$"

import os
import tempfile

from PyQt5.QtCore import QCoreApplication, QDate, QSettings
from PyQt5.QtWidgets import QDateEdit
from processing.gui.wrappers import WidgetWrapper
from qgis.core import (
    QgsProcessing,
    QgsFeatureSink,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterEnum,
    QgsProcessingParameterString,
    QgsCoordinateReferenceSystem,
    QgsProcessingParameterNumber)


class InaSAFEReportGenerator(QgsProcessingAlgorithm):
    """Extended QgsProcessingAlgorithm class for generating InaSAFE report.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """
    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    TEMPLATE = 'TEMPLATE'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """Translate string on processing context."""
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        """MapCoverageDownloader instance."""
        return InaSAFEReportGenerator()

    def name(self):
        """Unique name of the algorithm.
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'generate_inasafe_report'

    def displayName(self):
        """Display name of the algorithm.
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Generate InaSAFE Report')

    def initAlgorithm(self, config=None):
        """Algorithm initialisation.
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # Add the input vector features source.
        # It only allows InaSAFE impact layer geopackage.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Impact layer'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        # Add the report template source.
        self.addParameter(
            QgsProcessingParameterFile(
                self.TEMPLATE,
                self.tr('Report template'),
                extension='qpt'
            )
        )

        # Add the report output destination.
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Report output'),
                fileFilter='pdf(*.pdf)'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """Here is where the processing itself takes place.
        """
        # Retrieve the feature source.
        source = self.parameterAsSource(parameters, self.INPUT, context)

        # Retrieve report template file source.
        template = self.parameterAsFile(parameters, self.TEMPLATE, context)

        # Retrieve output layer destination.
        self.output_destination = self.parameterAsOutputLayer(
            parameters, self.OUTPUT, context)

        """Report generation starts here"""

        # METHOD 1 - IMPACT FUNCTION REPORT GENERATION

        # get impact function object using `load_from_metadata` method

        # create a map report component using `overide_component_template`
        # method

        # generate report using IF report generation method and use the
        # new component as the parameter

        # METHOD 2 - QGIS REPORT PROCESSOR

        # create new report processor to use QGIS Report (only in QGIS 3)
        # *still not sure how it's work but I think for the section that will
        # print the map report, we can use our qgis composer processor

        # make sure all qgis expressions is implemented and registered as
        # InaSAFE's expression
        # list of expressions:
        #   - impact report title
        #   - image resource path resolver
        #   - get value of field from layer
        #   - get value of inasafe keyword from layer
        #   - aggregation summary layer path resolver (for aggregation table)
        #   - impact layer path resolver
        #       (for impact table grouped by aggregation)

        # generate report using the output destination as a parameter

        # open the report as pdf --> see print_report_dialog.py as a reference
