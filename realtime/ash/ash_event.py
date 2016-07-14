# coding=utf-8
import logging
import os

import datetime
import pytz
from PyQt4.QtCore import QObject, QFileInfo, QUrl
from PyQt4.QtXml import QDomDocument
from qgis.core import QgsProject, QgsPalLabeling, \
    QgsCoordinateReferenceSystem, QgsMapLayerRegistry, QgsRasterLayer, \
    QgsComposition, QgsPoint, QgsMapSettings

from realtime.exceptions import MapComposerError
from realtime.utilities import realtime_logger_name
from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
from safe.common.version import get_version
from safe.storage.core import read_qgis_layer

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/13/16'


LOGGER = logging.getLogger(realtime_logger_name())


class AshEvent(QObject):

    def __init__(
            self,
            event_time=None,
            volcano_name=None,
            volcano_location=None,
            eruption_height=None,
            region=None,
            alert_level=None,
            locale=None,
            working_dir=None,
            hazard_path=None,
            landcover_path=None,
            cities_path=None,
            airport_path=None):
        QObject.__init__(self)
        if event_time:
            self.time = event_time
        else:
            self.time = datetime.datetime.now().replace(tzinfo=pytz.timezone('Asia/Jakarta'))

        # Check timezone awareness
        if not self.time.tzinfo:
            raise Exception('Need timezone aware object for event time')

        self.volcano_name = volcano_name
        self.volcano_location = volcano_location
        if self.volcano_location:
            self.longitude = self.volcano_location[0]
            self.latitude = self.volcano_location[1]
        else:
            self.longitude = None
            self.latitude = None
        self.erupction_height = eruption_height
        self.region = region
        self.alert_level = alert_level
        self.locale = locale
        if not self.locale:
            self.locale = 'en'

        if not working_dir:
            raise Exception("Working directory can't be empty")
        self.working_dir = working_dir
        self.hazard_path = hazard_path
        self.population_html_path = self.working_dir_path('population-table.html')
        self.nearby_html_path = self.working_dir_path('nearby-table.html')
        self.landcover_html_path = self.working_dir_path('landcover-table.html')
        self.map_report_path = self.working_dir_path('report.pdf')
        self.impact_exists = None
        self.locale = 'en'

    def working_dir_path(self, path):
        return os.path.join(self.working_dir, path)

    def event_dict(self):
        tz = pytz.timezone('Asia/Jakarta')
        timestamp = self.time.astimezone(tz=tz)
        time_format = '%-d-%b-%Y %H:%M:%S'
        timestamp_string = timestamp.strftime(time_format)
        point = QgsPoint(
            self.longitude,
            self.latitude)
        coordinates = point.toDegreesMinutesSeconds(2)
        tokens = coordinates.split(',')
        longitude_string = tokens[0]
        latitude_string = tokens[1]
        elapsed_time = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - self.time
        elapsed_hour = elapsed_time.seconds/3600
        elapsed_minute = (elapsed_time.seconds/60) % 60
        event = {
            'report-title': self.tr('Volcanic Ash Impact'),
            'report-timestamp': self.tr('Alert Level: %s %s') % (
                self.alert_level, timestamp_string),
            'report-province': self.tr('Province: %s') % (self.region,),
            'report-location': self.tr(
                'Longitude %s Latitude %s;'
                ' Eruption Column Height (a.s.l) - %d m') % (
                longitude_string, latitude_string, self.erupction_height),
            'report-elapsed': self.tr('Elapsed time since event %s hour(s) and %s minute(s)') % (elapsed_hour, elapsed_minute),
            'header-impact-table': self.tr('Potential impact at each fallout level'),
            'header-nearby-table': self.tr('Nearby places'),
            'header-landcover-table': self.tr('Land Cover Impact'),
            'content-disclaimer': self.tr(
                'The impact estimation is automatically generated and only '
                'takes into account the population, cities and land cover '
                'affected by different levels of volcanic ash fallout at '
                'surface level. The estimate is based on volcanic ash '
                'fallout data from Badan Geologi, population count data '
                'derived by DMInnovation from worldpop.org.uk, place '
                'information from geonames.org, land cover classification '
                'data provided by Indonesian Geospatial Portal at '
                'http://portal.ina-sdi.or.id and software developed by BNPB. '
                'Limitation in the estimates of surface fallout, population '
                'and place names datasets may result in significant '
                'misrepresentation of the on-the-surface situation in the '
                'figures shown here. Consequently decisions should not be '
                'made soley on the information presented here and should '
                'always be verified by ground truthing and other reliable '
                'information sources.'
            ),
            'content-notes': self.tr(
                'This report was created using InaSAFE version %s. Visit '
                'http://inasafe.org for more information. ') % get_version()
        }
        return event

    @classmethod
    def ash_fixtures_dir(cls, fixtures_path=None):
        dirpath = os.path.dirname(__file__)
        path = os.path.join(dirpath, 'fixtures')
        if fixtures_path:
            return os.path.join(path, fixtures_path)
        return path

    def generate_report(self):
        # Generate pdf report from impact/hazard
        if not self.impact_exists:
            # Cannot generate report when no impact layer present
            return

        project_path = self.working_dir_path('project-%s.qgs' % self.locale)
        project_instance = QgsProject.instance()
        project_instance.setFileName(project_path)
        project_instance.read()

        # Set up the map renderer that will be assigned to the composition
        map_renderer = CANVAS.mapRenderer()
        # Set the labelling engine for the canvas
        # labelling_engine = QgsPalLabeling()
        # map_renderer.setLabelingEngine(labelling_engine)

        # Enable on the fly CRS transformations
        map_renderer.setProjectionsEnabled(True)

        default_crs = map_renderer.destinationCrs()
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        map_renderer.setDestinationCrs(crs)

        # get layer registry
        layer_registry = QgsMapLayerRegistry.instance()
        layer_registry.removeAllMapLayers()
        # add impact layer
        population_impact_layer = read_qgis_layer(
            self.hazard_path, self.tr('People Affected'))
        layer_registry.addMapLayer(population_impact_layer, False)
        # add volcano layer
        volcano_layer = read_qgis_layer(
            self.ash_fixtures_dir('volcano-layer.shp'))
        layer_registry.addMapLayer(volcano_layer, False)
        # add place name layer
        placename_layer = read_qgis_layer(
            self.ash_fixtures_dir('places-layer.shp'))
        layer_registry.addMapLayer(placename_layer, False)
        CANVAS.setExtent(population_impact_layer.extent())
        CANVAS.refresh()
        # add basemap layer
        base_map = QgsRasterLayer(
            self.ash_fixtures_dir('indonesia-base.tif'))
        layer_registry.addMapLayer(base_map, False)
        # CANVAS.refresh()

        template_path = self.ash_fixtures_dir('realtime-ash.qpt')

        with open(template_path) as f:
            template_content = f.read()

        document = QDomDocument()
        document.setContent(template_content)

        # Now set up the composition
        # map_settings = QgsMapSettings()
        # composition = QgsComposition(map_settings)
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
        map_impact = composition.getComposerItemById('map-impact')
        if map_impact:
            map_impact.zoomToExtent(population_impact_layer.extent())
            map_impact.renderModeUpdateCachedImage()
        else:
            LOGGER.exception('Map canvas could not be found in template %s',
                             template_path)
            raise MapComposerError

        # setup impact table
        impact_table = composition.getComposerItemById(
            'table-impact')
        if impact_table is None:
            message = 'table-impact composer item could not be found'
            LOGGER.exception(message)
            raise MapComposerError(message)
        impacts_html = composition.getComposerHtmlByItem(
            impact_table)
        if impacts_html is None:
            message = 'Impacts QgsComposerHtml could not be found'
            LOGGER.exception(message)
            raise MapComposerError(message)
        impacts_html.setUrl(QUrl(self.population_html_path))

        # setup nearby table
        nearby_table = composition.getComposerItemById(
            'table-nearby')
        if nearby_table is None:
            message = 'table-nearby composer item could not be found'
            LOGGER.exception(message)
            raise MapComposerError(message)
        nearby_html = composition.getComposerHtmlByItem(
            nearby_table)
        if nearby_html is None:
            message = 'Nearby QgsComposerHtml could not be found'
            LOGGER.exception(message)
            raise MapComposerError(message)
        nearby_html.setUrl(QUrl(self.nearby_html_path))

        # setup landcover table
        landcover_table = composition.getComposerItemById(
            'table-landcover')
        if landcover_table is None:
            message = 'table-landcover composer item could not be found'
            LOGGER.exception(message)
            raise MapComposerError(message)
        landcover_html = composition.getComposerHtmlByItem(
            landcover_table)
        if landcover_html is None:
            message = 'Landcover QgsComposerHtml could not be found'
            LOGGER.exception(message)
            raise MapComposerError(message)
        landcover_html.setUrl(QUrl(self.landcover_html_path))

        # setup logos
        logos_id = ['logo-bnpb', 'logo-geologi']
        for logo_id in logos_id:
            logo_picture = composition.getComposerItemById(logo_id)
            if logo_picture is None:
                message = '%s composer item could not be found' % logo_id
                LOGGER.exception(message)
                raise MapComposerError(message)
            pic_path = os.path.basename(logo_picture.picturePath())
            pic_path = os.path.join('logo', pic_path)
            logo_picture.setPicturePath(self.ash_fixtures_dir(pic_path))

        # map_overall = composition.getComposerItemById('map-overall')
        # if map_overall:
        #     map_overall.renderModelUpdateCachedImage()
        # else:
        #     LOGGER.exception('Map canvas could not be found in template %s',
        #                      template_path)
        #     raise MapComposerError

        # save a pdf
        composition.exportAsPDF(self.map_report_path)

        # impact_qgis_layer = read_qgis_layer(self.impact_path)
        # report = ImpactReport(
        #     IFACE, template=None, layer=impact_qgis_layer)

        # report.print_map_to_pdf(self.map_report_path)
        # report.print_impact_table(self.table_report_path)

        project_instance.write(QFileInfo(project_path))

        layer_registry.removeAllMapLayers()
        map_renderer.setDestinationCrs(default_crs)
        map_renderer.setProjectionsEnabled(False)
