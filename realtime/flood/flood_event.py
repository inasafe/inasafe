# coding=utf-8
import logging
import os
import shutil

from PyQt4.QtCore import QObject, QFileInfo, QVariant
from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
    QgsVectorFileWriter,
    QgsField,
    QgsExpression)
from realtime.exceptions import PetaJakartaAPIError
from realtime.flood.peta_jakarta_api import PetaJakartaAPI
from realtime.utilities import realtime_logger_name
from safe.common.exceptions import ZeroImpactException
from safe.engine.core import calculate_impact as safe_calculate_impact
from safe.impact_functions.impact_function_manager import \
    ImpactFunctionManager
from safe.storage.safe_layer import SafeLayer
from safe.storage.core import read_layer
from safe.utilities.gis import convert_to_safe_layer
from safe.test.utilities import get_qgis_app
from safe.utilities.keyword_io import KeywordIO

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'

__date__ = '11/24/15'


LOGGER = logging.getLogger(realtime_logger_name())
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class FloodEvent(QObject):

    def __init__(
            self,
            working_dir,
            population_raster_path,
            year,
            month,
            day,
            hour,
            duration,
            level):

        QObject.__init__(self)
        self.working_dir = working_dir
        self.duration = duration
        self.level = level
        self.report_id = '%d%02d%02d%02d-%d-%s' % (
            year,
            month,
            day,
            hour,
            duration,
            level
        )

        self.report_path = os.path.join(self.working_dir, self.report_id)

        if not os.path.exists(self.report_path):
            os.mkdir(self.report_path)

        self.hazard_path = os.path.join(self.report_path, 'flood_data.json')
        self.hazard_layer = None

        self.population_path = population_raster_path
        self.exposure_layer = None

        if not os.path.exists(self.hazard_path):
            self.save_hazard_data()

        self.load_hazard_data()
        self.load_exposure_data()

        # Impact layers
        self.impact = None
        self.impact_path = os.path.join(self.report_path, 'impact.tif')
        self.impact_layer = None

    def save_hazard_data(self):
        hazard_geojson = PetaJakartaAPI.get_aggregate_report(
            self.duration, self.level)

        if not hazard_geojson:
            raise PetaJakartaAPIError("Can't access PetaJakarta REST API")

        with open(self.hazard_path, 'w+') as f:
            f.write(hazard_geojson)

        # Save the layer as shp
        file_info = QFileInfo(self.hazard_path)
        hazard_layer = QgsVectorLayer(
            self.hazard_path, file_info.baseName(), 'ogr', False)

        target_name = 'flood_data.shp'
        self.hazard_path = os.path.join(self.report_path, target_name)
        QgsVectorFileWriter.writeAsVectorFormat(
            hazard_layer,
            self.hazard_path,
            'CP1250',
            None,
            'ESRI Shapefile')

        file_info = QFileInfo(self.hazard_path)
        self.hazard_layer = QgsVectorLayer(
            self.hazard_path, file_info.baseName(), 'ogr')

        hazard_layer = self.hazard_layer
        hazard_layer.startEditing()
        field = QgsField('flooded', QVariant.Int)
        hazard_layer.dataProvider().addAttributes([field])
        hazard_layer.commitChanges()
        idx = hazard_layer.fieldNameIndex('flooded')
        expression = QgsExpression('count > 0')
        expression.prepare(hazard_layer.pendingFields())

        hazard_layer.startEditing()
        for feature in hazard_layer.getFeatures():
            feature[idx] = expression.evaluate(feature)
            hazard_layer.updateFeature(feature)

        hazard_layer.commitChanges()

        # writing keywords
        keyword_io = KeywordIO()

        keywords = {
            'field': 'flooded',
            'hazard': 'flood',
            'hazard_category': 'single_event',
            'keyword_version': '3.2',
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'hazard',
            'title': 'Flood',
            'value_map': '{"wet": [1], "dry": [0]}',
            'vector_hazard_classification': 'flood_vector_hazard_classes'
        }

        keyword_io.write_keywords(self.hazard_layer, keywords)

    def load_hazard_data(self):
        self.hazard_path = os.path.join(self.report_path, 'flood_data.shp')

        # file_info = QFileInfo(self.hazard_path)
        # self.hazard_layer = QgsVectorLayer(
        #     self.hazard_path, file_info.baseName(), 'ogr')
        self.hazard_layer = read_layer(self.hazard_path)

    def load_exposure_data(self):
        # file_info = QFileInfo(self.population_path)
        # self.exposure_layer = QgsRasterLayer(
        #     self.population_path, file_info.baseName())
        self.exposure_layer = read_layer(self.population_path)

    def calculate_impact(self):
        if_manager = ImpactFunctionManager()
        function_id = 'FloodEvacuationVectorHazardFunction'
        impact_function = if_manager.get_instance(function_id)

        impact_function.hazard = SafeLayer(self.hazard_layer)
        impact_function.exposure = SafeLayer(self.exposure_layer)

        try:
            self.impact = safe_calculate_impact(impact_function)
        except ZeroImpactException as e:
            # in case zero impact, just return
            LOGGER.info('No impact detected')
            LOGGER.info(e.message)
            return

        # copy results of impact to report_path directory
        base_name, _ = os.path.splitext(self.impact.filename)
        dir_name = os.path.dirname(self.impact.filename)
        for (root, dirs, files) in os.walk(dir_name):
            for f in files:
                source_filename = os.path.join(root, f)
                if source_filename.find(base_name) >= 0:
                    extensions = source_filename.replace(base_name, '')
                    new_path = os.path.join(
                        self.report_path, 'impact' + extensions)
                    shutil.copy(source_filename, new_path)

        self.impact = SafeLayer(read_layer(self.impact_path))
