# coding=utf-8
import logging
import os
import shutil
from zipfile import ZipFile

import pytz
import datetime

import re
from PyQt4.QtCore import QObject, QFileInfo, QVariant, QTranslator, \
    QCoreApplication
from PyQt4.QtXml import QDomDocument
from qgis.core import QgsMapLayerRegistry
from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
    QgsVectorFileWriter,
    QgsField,
    QgsExpression,
    QgsPalLabeling,
    QgsComposition,
    QgsCoordinateReferenceSystem,
    QgsProject)
from openlayers_plugin.openlayers_plugin import OpenlayersPlugin
from openlayers_plugin.weblayers.map_quest import OlMapQuestOSMLayer
from realtime.exceptions import PetaJakartaAPIError, MapComposerError
from realtime.flood.dummy_source_api import DummySourceAPI
from realtime.flood.peta_jakarta_api import PetaJakartaAPI
from realtime.utilities import realtime_logger_name
from safe.common.exceptions import ZeroImpactException, TranslationLoadError
from safe.engine.core import calculate_impact as safe_calculate_impact
from safe.impact_functions.impact_function_manager import \
    ImpactFunctionManager
from safe.report.impact_report import ImpactReport
from safe.storage.safe_layer import SafeLayer
from safe.storage.core import read_layer, read_qgis_layer
from safe.test.utilities import get_qgis_app
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.styling import set_vector_categorized_style, \
    set_vector_graduated_style, setRasterStyle

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'

__date__ = '11/24/15'


LOGGER = logging.getLogger(realtime_logger_name())
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class FloodEvent(QObject):

    def __init__(
            self,
            working_dir,
            locale,
            population_raster_path,
            year,
            month,
            day,
            hour,
            duration,
            level,
            dummy_report_folder=None):

        QObject.__init__(self)
        self.dummy_report_folder = dummy_report_folder
        self.working_dir = working_dir
        self.duration = duration
        self.level = level
        if self.dummy_report_folder:
            pattern = r'^(?P<year>\d{4})' \
                      r'(?P<month>\d{2})' \
                      r'(?P<day>\d{2})' \
                      r'(?P<hour>\d{2})-' \
                      r'(?P<duration>\d{1})-' \
                      r'(?P<level>\w+)$'
            prog = re.compile(pattern)
            result = prog.match(self.dummy_report_folder)
            year = int(result.group('year'))
            month = int(result.group('month'))
            day = int(result.group('day'))
            hour = int(result.group('hour'))
            duration = int(result.group('duration'))
            level = result.group('level')

        self.report_id = '%d%02d%02d%02d-%d-%s' % (
            year,
            month,
            day,
            hour,
            duration,
            level
        )

        self.time = datetime.datetime(year, month, day, hour, tzinfo=pytz.utc)
        self.source = 'PetaJakarta - Jakarta'
        self.region = 'Jakarta'

        self.report_path = os.path.join(self.working_dir, self.report_id)

        if not os.path.exists(self.report_path):
            os.mkdir(self.report_path)

        self.hazard_path = os.path.join(self.report_path, 'flood_data.json')
        self.hazard_layer = None
        self.hazard_zip_path = os.path.join(self.report_path, 'hazard.zip')

        self.population_path = population_raster_path
        self.exposure_layer = None

        if not os.path.exists(self.hazard_path) or self.dummy_report_folder:
            self.save_hazard_data()

        self.load_hazard_data()
        self.load_exposure_data()

        # Impact layers
        self.function_id = 'FloodEvacuationVectorHazardFunction'
        self.impact_path = os.path.join(self.report_path, 'impact.tif')
        self.impact_layer = None

        # Setup i18n
        self.locale = locale
        self.translator = None
        self.setup_i18n()

        # Report
        self.map_report_path = os.path.join(
            self.report_path, 'impact-map-%s.pdf' % self.locale)
        self.table_report_path = os.path.join(
            self.report_path, 'impact-table-%s.pdf' % self.locale)

    @property
    def impact_exists(self):
        return os.path.exists(self.impact_path)

    def save_hazard_data(self):
        if self.dummy_report_folder:
            filename = os.path.join(
                self.working_dir, self.dummy_report_folder, 'flood_data.json')
            hazard_geojson = DummySourceAPI.get_aggregate_report(filename)
        else:
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
        hazard_layer = QgsVectorLayer(
            self.hazard_path, file_info.baseName(), 'ogr')

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
            'field': 'state',
            'hazard': 'generic',
            'hazard_category': 'single_event',
            'keyword_version': '3.3',
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'hazard',
            'title': 'Flood',
            'value_map': '{"wet": [2], "dry": [0]}',
            'vector_hazard_classification': 'flood_vector_hazard_classes'
        }

        keyword_io.write_keywords(hazard_layer, keywords)

        # copy layer styles
        style_path = self.flood_fixtures_dir(
            'flood_data_classified_state.qml')
        target_style_path = os.path.join(
            self.report_path, 'flood_data.qml')
        shutil.copy(style_path, target_style_path)

        # archiving hazard layer
        with ZipFile(self.hazard_zip_path, 'w') as zf:
            for root, dirs, files in os.walk(self.report_path):
                for f in files:
                    _, ext = os.path.splitext(f)
                    if 'flood_data' in f:
                        filename = os.path.join(root, f)
                        zf.write(filename, arcname=f)

    def load_hazard_data(self):
        self.hazard_path = os.path.join(self.report_path, 'flood_data.shp')
        self.hazard_layer = read_layer(self.hazard_path)

    def load_exposure_data(self):
        self.exposure_layer = read_layer(self.population_path)

    def calculate_impact(self):
        if_manager = ImpactFunctionManager()
        function_id = self.function_id
        impact_function = if_manager.get_instance(function_id)

        impact_function.hazard = SafeLayer(self.hazard_layer)
        impact_function.exposure = SafeLayer(self.exposure_layer)

        try:
            self.impact_layer = safe_calculate_impact(impact_function)
            self.set_style()
        except ZeroImpactException as e:
            # in case zero impact, just return
            LOGGER.info('No impact detected')
            LOGGER.info(e.message)
            return

        # copy results of impact to report_path directory
        base_name, _ = os.path.splitext(self.impact_layer.filename)
        dir_name = os.path.dirname(self.impact_layer.filename)
        for (root, dirs, files) in os.walk(dir_name):
            for f in files:
                source_filename = os.path.join(root, f)
                if source_filename.find(base_name) >= 0:
                    extensions = source_filename.replace(base_name, '')
                    new_path = os.path.join(
                        self.report_path, 'impact' + extensions)
                    shutil.copy(source_filename, new_path)

        self.impact_layer = read_layer(self.impact_path)

    def set_style(self):
        # Get requested style for impact layer of either kind
        impact = self.impact_layer
        style = impact.get_style_info()
        style_type = impact.get_style_type()

        # Determine styling for QGIS layer
        qgis_impact_layer = impact.as_qgis_native()
        if impact.is_vector:
            LOGGER.debug('myEngineImpactLayer.is_vector')
            if not style:
                # Set default style if possible
                pass
            elif style_type == 'categorizedSymbol':
                LOGGER.debug('use categorized')
                set_vector_categorized_style(qgis_impact_layer, style)
            elif style_type == 'graduatedSymbol':
                LOGGER.debug('use graduated')
                set_vector_graduated_style(qgis_impact_layer, style)

        elif impact.is_raster:
            LOGGER.debug('myEngineImpactLayer.is_raster')
            if not style:
                qgis_impact_layer.setDrawingStyle("SingleBandPseudoColor")
            else:
                setRasterStyle(qgis_impact_layer, style)

    @classmethod
    def flood_fixtures_dir(cls, fixtures_path=None):
        dirpath = os.path.dirname(__file__)
        path = os.path.join(dirpath, 'fixtures')
        if fixtures_path:
            return os.path.join(path, fixtures_path)
        return path

    def event_dict(self):
        # timezone GMT+07:00
        # FixMe: Localize me
        tz = pytz.timezone('Asia/Jakarta')
        timestamp = self.time.astimezone(tz=tz)
        time_format = '%-d %B %Y %I:%M %p'
        id_time_format = 'EN-%Y%m%d'
        timestamp_string = timestamp.strftime(time_format)
        event = {
            'report-head': """THE GOVERNMENT OF DKI JAKARTA PROVINCE
REGIONAL DISASTER MANAGEMENT AGENCY
""",
            'report-title': 'FLOOD REPORT',
            'report-timestamp': 'Based on flood %s' % timestamp_string,
            'report-id': timestamp.strftime(id_time_format),
            'header-legend': 'Legend',
            'header-analysis-result': 'InaSAFE Analysis Result',
            'header-provenance': 'Data Source',
            'header-contact': 'Contact',
            'header-supporter': 'Supported by',
            'header-notes': 'Disclaimer',
            'content-provenance': """1. Disaster Data :
    Flood Data ........ BPBD DKI Jakarta
2. Base Data
    Population ........ Population Agency DKI Jakarta Prov.
    Administration Boundaries ...... OpenStreetMap
""",
            'content-disclaimer': 'Disclaimer...',
            'content-analysis-result': 'Analysis Result',
            'content-contact': """Pusat Pengendalian dan Operasi (Pusdalops)
BPBD Provinsi DKI Jakarta
Jl. Medan Merdeka Selatan No. 8-9 Blok F lantai 3
Telp. (021)164 atau 3521623
"""
        }
        return event

    def generate_report(self):
        # Generate pdf report from impact/hazard
        if not self.impact_exists:
            # Cannot generate report when no impact layer present
            return

        project_path = os.path.join(
            self.report_path, 'project-%s.qgs' % self.locale)
        project_instance = QgsProject.instance()
        project_instance.setFileName(project_path)
        project_instance.read()

        # Set up the map renderer that will be assigned to the composition
        map_renderer = CANVAS.mapRenderer()
        # Set the labelling engine for the canvas
        labelling_engine = QgsPalLabeling()
        map_renderer.setLabelingEngine(labelling_engine)

        # Enable on the fly CRS transformations
        map_renderer.setProjectionsEnabled(True)

        default_crs = map_renderer.destinationCrs()
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        map_renderer.setDestinationCrs(crs)

        # get layer registry
        layer_registry = QgsMapLayerRegistry.instance()
        layer_registry.removeAllMapLayers()
        # add boundary mask
        boundary_mask = read_qgis_layer(
            self.flood_fixtures_dir('boundary-mask.shp'))
        layer_registry.addMapLayer(boundary_mask, False)
        # add hazard layer
        hazard_layer = read_qgis_layer(
            self.hazard_path, 'Flood Depth (cm)')
        layer_registry.addMapLayer(hazard_layer, True)
        # add boundary layer
        boundary_layer = read_qgis_layer(
            self.flood_fixtures_dir('boundary-5.shp'))
        layer_registry.addMapLayer(boundary_layer, False)
        CANVAS.setExtent(boundary_layer.extent())
        CANVAS.refresh()
        # add basemap layer
        # this code uses OpenlayersPlugin
        ol_plugin = OpenlayersPlugin(IFACE)
        ol_plugin.addLayer(OlMapQuestOSMLayer())
        CANVAS.refresh()

        template_path = self.flood_fixtures_dir('realtime-flood.qpt')

        with open(template_path) as f:
            template_content = f.read()

        document = QDomDocument()
        document.setContent(template_content)

        # set destination CRS to Jakarta CRS
        # EPSG:32748
        # This allows us to use the scalebar in meter unit scale
        crs = QgsCoordinateReferenceSystem('EPSG:32748')
        map_renderer.setDestinationCrs(crs)

        # Now set up the composition
        composition = QgsComposition(map_renderer)

        subtitution_map = self.event_dict()
        LOGGER.debug(subtitution_map)

        # load composition object from template
        result = composition.loadFromTemplate(document, subtitution_map)
        if not result:
            LOGGER.exception(
                'Error loading template %s with keywords\n %s',
                template_path, subtitution_map)
            raise MapComposerError

        # get main map canvas on the composition and set extent
        map_canvas = composition.getComposerItemById('map-canvas')
        if map_canvas:
            map_canvas.setNewExtent(map_canvas.currentMapExtent())
            map_canvas.renderModeUpdateCachedImage()
        else:
            LOGGER.exception('Map canvas could not be found in template %s',
                             template_path)
            raise MapComposerError

        # get map legend on the composition
        map_legend = composition.getComposerItemById('map-legend')
        if map_legend:
            # show only legend for Flood Depth
            # ''.star
            # showed_legend = [layer_id for layer_id in map_renderer.layerSet()
            #                  if layer_id.startswith('Flood_Depth')]
            # LOGGER.info(showed_legend)
            # LOGGER.info(map_renderer.layerSet())
            # LOGGER.info(hazard_layer.id())

            # map_legend.model().setLayerSet(showed_legend)
            map_legend.model().setLayerSet([hazard_layer.id()])
        else:
            LOGGER.exception('Map legend could not be found in template %s',
                             template_path)
            raise MapComposerError

        # save a pdf
        composition.exportAsPDF(self.map_report_path)

        impact_qgis_layer = read_qgis_layer(self.impact_path)
        report = ImpactReport(
            IFACE, template=None, layer=impact_qgis_layer)

        # report.print_map_to_pdf(self.map_report_path)
        report.print_impact_table(self.table_report_path)

        project_instance.write(QFileInfo(project_path))

        layer_registry.removeAllMapLayers()
        map_renderer.setDestinationCrs(default_crs)
        map_renderer.setProjectionsEnabled(False)

    def setup_i18n(self):
        """Setup internationalisation for the reports.

        Args:
           None
        Returns:
           None.
        Raises:
           TranslationLoadException
        """
        locale_name = self.locale

        root = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                os.pardir))
        translation_path = os.path.join(
            root,
            'i18n',
            'inasafe_' + str(locale_name) + '.qm')
        if os.path.exists(translation_path):
            self.translator = QTranslator()
            result = self.translator.load(translation_path)
            LOGGER.debug('Switched locale to %s' % translation_path)
            if not result:
                message = 'Failed to load translation for %s' % locale_name
                LOGGER.exception(message)
                raise TranslationLoadError(message)
            # noinspection PyTypeChecker, PyCallByClass, PyArgumentList
            QCoreApplication.installTranslator(self.translator)
        else:
            if locale_name != 'en':
                message = 'No translation exists for %s' % locale_name
                LOGGER.exception(message)
