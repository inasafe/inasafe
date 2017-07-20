# coding=utf-8
import json
import logging
import os
import datetime
from collections import OrderedDict
from zipfile import ZipFile

import pytz
import shutil

from PyQt4.QtCore import QCoreApplication, QObject, QFileInfo, QUrl, QTranslator
from PyQt4.QtXml import QDomDocument
from qgis.core import (
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsMapLayerRegistry,
    QgsRasterLayer,
    QgsComposition,
    QgsPoint,
    QgsRectangle)
from jinja2 import Template
from headless.tasks.utilities import download_file
from realtime.exceptions import MapComposerError
from realtime.utilities import realtime_logger_name
from safe.common.exceptions import (
    ZeroImpactException,
    KeywordNotFoundError,
    TranslationLoadError)
from safe.common.utilities import format_int
from safe.impact_functions.core import population_rounding
from safe.impact_functions.impact_function_manager import \
    ImpactFunctionManager
from safe.test.utilities import get_qgis_app
from safe.utilities.clipper import clip_layer
from safe.utilities.gis import get_wgs84_resolution
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.styling import set_vector_categorized_style, \
    set_vector_graduated_style, setRasterStyle
from safe.common.version import get_version
from safe.storage.core import read_qgis_layer

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

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
            overview_path=None,
            highlight_base_path=None,
            population_path=None,
            volcano_path=None,
            landcover_path=None,
            cities_path=None,
            airport_path=None):
        """

        :param event_time:
        :param volcano_name:
        :param volcano_location:
        :param eruption_height:
        :param region:
        :param alert_level:
        :param locale:
        :param working_dir:
        :param hazard_path: It can be a url or local file path
        :param population_path:
        :param landcover_path:
        :param cities_path:
        :param airport_path:
        """
        QObject.__init__(self)
        if event_time:
            self.time = event_time
        else:
            self.time = datetime.datetime.now().replace(
                tzinfo=pytz.timezone('Asia/Jakarta'))

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

        self.setup_i18n()

        if not working_dir:
            raise Exception("Working directory can't be empty")
        self.working_dir = working_dir
        if not os.path.exists(self.working_dir_path()):
            os.makedirs(self.working_dir_path())

        dateformat = '%Y%m%d%H%M%S'
        timestring = self.time.strftime(dateformat)
        self.event_id = '%s-%s' % (timestring, self.volcano_name)

        LOGGER.info('Ash ID: %s' % self.event_id)

        # save hazard layer
        self.hazard_path = self.working_dir_path('hazard.tif')
        self.save_hazard_layer(hazard_path)

        if not os.path.exists(self.hazard_path):
            IOError("Hazard path doesn't exists")

        self.population_html_path = self.working_dir_path(
            'population-table.html')
        self.nearby_html_path = self.working_dir_path('nearby-table.html')
        self.landcover_html_path = self.working_dir_path(
            'landcover-table.html')
        self.map_report_path = self.working_dir_path('report.pdf')
        self.project_path = self.working_dir_path('project.qgs')
        self.impact_exists = None
        self.impact_zip_path = self.working_dir_path('impact.zip')

        self.population_path = population_path
        self.cities_path = cities_path
        self.airport_path = airport_path
        self.landcover_path = landcover_path
        self.volcano_path = volcano_path
        self.highlight_base_path = highlight_base_path
        self.overview_path = overview_path

        # load layers
        self.hazard_layer = read_qgis_layer(self.hazard_path, 'Ash Fall')
        self.population_layer = read_qgis_layer(
            self.population_path, 'Population')
        self.landcover_layer = read_qgis_layer(
            self.landcover_path, 'Landcover')
        self.cities_layer = read_qgis_layer(
            self.cities_path, 'Cities')
        self.airport_layer = read_qgis_layer(
            self.airport_path, 'Airport')
        self.volcano_layer = read_qgis_layer(
            self.volcano_path, 'Volcano')
        self.highlight_base_layer = read_qgis_layer(
            self.highlight_base_path, 'Base Map')
        self.overview_layer = read_qgis_layer(
            self.overview_path, 'Overview')

        # Write metadata for self reference
        self.write_metadata()

    def save_hazard_layer(self, hazard_path):
        # download or copy hazard path/url
        # It is a single tif file
        if not hazard_path and not os.path.exists(self.hazard_path):
            raise IOError('Hazard file not specified')

        if hazard_path:
            temp_hazard = download_file(hazard_path)
            shutil.copy(temp_hazard, self.hazard_path)

        # copy qml and metadata
        shutil.copy(
            self.ash_fixtures_dir('hazard.qml'),
            self.working_dir_path('hazard.qml'))

        keyword_io = KeywordIO()

        keywords = {
            'hazard_category': u'single_event',
            'keyword_version': u'3.5',
            'title': u'Ash Fall',
            'hazard': u'volcanic_ash',
            'continuous_hazard_unit': u'centimetres',
            'layer_geometry': u'raster',
            'layer_purpose': u'hazard',
            'layer_mode': u'continuous'
        }

        hazard_layer = read_qgis_layer(self.hazard_path, 'Ash Fall')
        keyword_io.write_keywords(hazard_layer, keywords)

    def write_metadata(self):
        """Write metadata file for this event folder

        write metadata
        example metadata json:
        {
            'volcano_name': 'Sinabung',
            'volcano_location': [107, 6],
            'alert_level': 'Siaga',
            'eruption_height': 7000,  # eruption height in meters
            'event_time': '2016-07-20 11:22:33 +0700',
            'region': 'North Sumatra'
        }

        :return:
        """
        dateformat = '%Y-%m-%d %H:%M:%S %z'
        metadata_dict = {
            'volcano_name': self.volcano_name,
            'volcano_location': self.volcano_location,
            'alert_level': self.alert_level,
            'eruption_height': self.erupction_height,
            'event_time': self.time.strftime(dateformat),
            'region': self.region
        }
        with open(self.working_dir_path('metadata.json'), 'w') as f:
            f.write(json.dumps(metadata_dict))

    def working_dir_path(self, path=''):
        dateformat = '%Y%m%d%H%M%S'
        timestring = self.time.strftime(dateformat)
        event_folder = '%s-%s' % (timestring, self.volcano_name)
        return os.path.join(self.working_dir, event_folder, path)

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
        elapsed_time = datetime.datetime.utcnow().replace(
            tzinfo=pytz.utc) - self.time
        elapsed_hour = elapsed_time.seconds / 3600
        elapsed_minute = (elapsed_time.seconds / 60) % 60
        event = {
            'report-title': self.tr('Volcanic Ash Impact'),
            'report-timestamp': self.tr('Volcano: %s, %s') % (
                self.volcano_name,
                timestamp_string),
            'report-province': self.tr('Province: %s') % (self.region,),
            'report-alert-level': self.tr('Alert Level: %s') % (
                self.alert_level.capitalize(), ),
            'report-location': self.tr(
                'Position: %s, %s;'
                ' Eruption Column Height (a.s.l) - %d m') % (
                longitude_string, latitude_string, self.erupction_height),
            'report-elapsed': self.tr(
                'Elapsed time since event: %s hour(s) and %s minute(s)') % (
                elapsed_hour, elapsed_minute),
            'header-impact-table': self.tr(
                'Potential impact at each fallout level'),
            'header-nearby-table': self.tr('Nearby places'),
            'header-landcover-table': self.tr('Land Cover Impact'),
            'content-disclaimer': self.tr(
                'The impact estimation is automatically generated and only '
                'takes into account the population, cities and land cover '
                'affected by different levels of volcanic ash fallout at '
                'surface level. The estimate is based on volcanic ash '
                'fallout data from Badan Geologi, population count data '
                'derived by DMInnovation from worldpop.org.uk, place '
                'information and land cover classification data provided by '
                'Indonesian Geospatial Portal at http://portal.ina-sdi.or.id '
                'and software developed by BNPB. Limitation in the estimates '
                'of surface fallout, population and place names datasets may '
                'result in a significant misrepresentation of the '
                'on-the-surface situation in the figures shown here. '
                'Consequently, decisions should not be made solely on the '
                'information presented here and should always be verified '
                'by ground truthing and other reliable information sources.'
            ),
            'content-notes': self.tr(
                'This report was created using InaSAFE version %s. Visit '
                'http://inasafe.org for more information. ') % get_version(),
            'content-support': self.tr(
                'Supported by DMInnovation, Geoscience Australia and the World Bank-GFDRR')
        }
        return event

    @classmethod
    def ash_fixtures_dir(cls, fixtures_path=None):
        dirpath = os.path.dirname(__file__)
        path = os.path.join(dirpath, 'fixtures')
        if fixtures_path:
            return os.path.join(path, fixtures_path)
        return path

    def render_population_table(self):
        with open(self.working_dir_path('population_impact.json')) as f:
            population_impact_data = json.loads(f.read())

        impact_summary = population_impact_data['impact summary']['fields']

        key_mapping = {
            'Population in very low hazard zone': 'very_low',
            'Population in medium hazard zone': 'medium',
            'Population in high hazard zone': 'high',
            'Population in very high hazard zone': 'very_high',
            'Population in low hazard zone': 'low'
        }

        population_dict = {}
        for val in impact_summary:
            if val[0] in key_mapping:
                population_dict[key_mapping[val[0]]] = val[1]

        for key, val in key_mapping.iteritems():
            if val not in population_dict:
                population_dict[val] = 0
            else:
                # divide per 1000 people (unit used in the report)
                population_dict[val] /= 1000
                population_dict[val] = format_int(
                    population_rounding(population_dict[val]))

        # format:
        # {
        #     'very_low': 1,
        #     'low': 2,
        #     'medium': 3,
        #     'high': 4,
        #     'very_high': 5
        # }
        population_template = self.ash_fixtures_dir(
            'population-table.template.html')
        with open(population_template) as f:
            template = Template(f.read())
            html_string = template.render(**population_dict)

        with open(self.population_html_path, 'w') as f:
            f.write(html_string)

    def render_landcover_table(self):
        with open(self.working_dir_path('landcover_impact.json')) as f:
            landcover_impact_data = json.loads(f.read())

        landcover_dict = OrderedDict()

        for entry in landcover_impact_data['impact table']['data']:
            land_type = entry[0]
            area = entry[3]
            # convert from ha to km^2
            area /= 100
            if land_type in landcover_dict:
                landcover_dict[land_type] += area
            else:
                landcover_dict[land_type] = area

        # format:
        # landcover_list =
        # [
        #     {
        #         'type': 'settlement',
        #         'area': 1000
        #     },
        #     {
        #         'type': 'rice field',
        #         'area': 10
        #     },
        # ]
        landcover_list = []
        for land_type, area in landcover_dict.iteritems():
            if not land_type.lower() == 'other':
                landcover_list.append({
                    'type': land_type,
                    'area': format_int(int(area))
                })

        landcover_list.sort(key=lambda x: x['area'], reverse=True)
        landcover_template = self.ash_fixtures_dir(
            'landcover-table.template.html')
        with open(landcover_template) as f:
            template = Template(f.read())
            # generate table here
            html_string = template.render(landcover_list=landcover_list)

        with open(self.landcover_html_path, 'w') as f:
            f.write(html_string)

    def render_nearby_table(self):

        hazard_mapping = {
            0: 'Very Low',
            1: 'Low',
            2: 'Moderate',
            3: 'High',
            4: 'Very High'
        }

        # load PLACES
        keyword_io = KeywordIO()
        try:
            cities_impact = read_qgis_layer(
                self.working_dir_path('cities_impact.shp'),
                'Cities')
            hazard = keyword_io.read_keywords(
                cities_impact, 'target_field')
            hazard_field_index = cities_impact.fieldNameIndex(hazard)

            name_field = keyword_io.read_keywords(
                self.cities_layer, 'name_field')
            name_field_index = cities_impact.fieldNameIndex(name_field)

            try:
                population_field = keyword_io.read_keywords(
                    self.cities_layer, 'population_field')
                population_field_index = cities_impact.fieldNameIndex(
                    population_field)
            except KeywordNotFoundError:
                population_field = None
                population_field_index = None

            table_places = []
            for f in cities_impact.getFeatures():
                haz_class = f.attributes()[hazard_field_index]
                city_name = f.attributes()[name_field_index]
                if population_field_index >= 0:
                    city_pop = f.attributes()[population_field_index]
                else:
                    city_pop = 1
                # format:
                # [
                # 'hazard class',
                # 'city's population',
                # 'city's name',
                # 'the type'
                # ]
                haz = hazard_mapping[haz_class]
                item = {
                    'class': haz_class,
                    'hazard': haz,
                    'css': haz.lower().replace(' ', '-'),
                    'pop_val': city_pop,
                    'population': format_int(
                        population_rounding(city_pop / 1000)),
                    'name': city_name.title(),
                    'type': 'places'
                }
                table_places.append(item)

            # sort table by hazard zone, then population
            table_places = sorted(
                table_places,
                key=lambda x: (-x['class'], -x['pop_val']))
        except Exception as e:
            LOGGER.exception(e)
            table_places = []

        # load AIRPORTS
        try:
            airport_impact = read_qgis_layer(
                self.working_dir_path('airport_impact.shp'),
                'Airport')
            hazard = keyword_io.read_keywords(
                airport_impact, 'target_field')
            hazard_field_index = airport_impact.fieldNameIndex(hazard)

            name_field = keyword_io.read_keywords(
                self.airport_layer, 'name_field')
            name_field_index = airport_impact.fieldNameIndex(name_field)

            # airport doesnt have population, so enter 0 for population
            table_airports = []
            for f in airport_impact.getFeatures():
                haz_class = f.attributes()[hazard_field_index]
                airport_name = f.attributes()[name_field_index]
                haz = hazard_mapping[haz_class]
                item = {
                    'class': haz_class,
                    'hazard': haz,
                    'css': haz.lower().replace(' ', '-'),
                    'pop_val': 0,
                    'population': '0',
                    'name': airport_name.title(),
                    'type': 'airport'
                }
                table_airports.append(item)

            # Sort by hazard class
            table_airports = sorted(
                table_airports,
                key=lambda x: -x['class'])
        except Exception as e:
            LOGGER.exception(e)
            table_airports = []

        # decide which to show
        # maximum 2 airport
        max_airports = 2
        airport_count = min(max_airports, len(table_airports))
        # maximum total 7 entries to show
        max_rows = 6
        places_count = min(len(table_places), max_rows - airport_count)

        # get top airport
        table_airports = table_airports[:airport_count]
        # get top places
        table_places = table_places[:places_count]

        item_list = table_places + table_airports

        # sort entry by hazard level
        item_list = sorted(
            item_list,
            key=lambda x: (-x['class'], -x['pop_val']))

        nearby_template = self.ash_fixtures_dir(
            'nearby-table.template.html')
        with open(nearby_template) as f:
            template = Template(f.read())
            # generate table here
            html_string = template.render(item_list=item_list)

        with open(self.nearby_html_path, 'w') as f:
            f.write(html_string)

        # copy airport logo
        shutil.copy(
            self.ash_fixtures_dir('logo/airport.jpg'),
            self.working_dir_path('airport.jpg'))

    def copy_layer(self, layer, target_base_name):
        """Copy layer to working directory with specified base_name

        :param layer: Safe layer
        :return:
        """
        base_name, _ = os.path.splitext(layer.filename)
        dir_name = os.path.dirname(layer.filename)
        for (root, dirs, files) in os.walk(dir_name):
            for f in files:
                source_filename = os.path.join(root, f)
                if source_filename.find(base_name) >= 0:
                    extensions = source_filename.replace(base_name, '')
                    new_path = self.working_dir_path(
                        target_base_name + extensions)
                    shutil.copy(source_filename, new_path)

    @classmethod
    def set_impact_style(cls, impact):
        # Determine styling for QGIS layer
        qgis_impact_layer = impact.as_qgis_native()
        style = impact.get_style_info()
        style_type = impact.get_style_type()
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

    def calculate_specified_impact(
            self, function_id, hazard_layer,
            exposure_layer, output_basename):
        LOGGER.info('Calculate %s' % function_id)
        try:
            if_manager = ImpactFunctionManager()
            impact_function = if_manager.get_instance(function_id)

            impact_function.hazard = hazard_layer

            extent = impact_function.hazard.extent()
            hazard_extent = [
                extent.xMinimum(), extent.yMinimum(),
                extent.xMaximum(), extent.yMaximum()]

            # clip exposure if required (if it is too large)
            if isinstance(exposure_layer, QgsRasterLayer):
                cell_size, _ = get_wgs84_resolution(exposure_layer)
            else:
                cell_size = None
            clipped_exposure = clip_layer(
                layer=exposure_layer,
                extent=hazard_extent,
                cell_size=cell_size)
            exposure_layer = clipped_exposure

            impact_function.exposure = exposure_layer
            impact_function.requested_extent = hazard_extent
            impact_function.requested_extent_crs = impact_function.hazard.crs()
            impact_function.force_memory = True

            impact_function.run_analysis()
            impact_layer = impact_function.impact

            if impact_layer:
                self.set_impact_style(impact_layer)

                # copy results of impact to report_path directory
                self.copy_layer(impact_layer, output_basename)
        except ZeroImpactException as e:
            # in case zero impact, just return
            LOGGER.info('No impact detected')
            LOGGER.info(e.message)
            return False
        except Exception as e:
            LOGGER.info('Calculation error')
            LOGGER.exception(e)
            return False
        LOGGER.info('Calculation completed.')
        return True

    def calculate_impact(self):
        # calculate population impact
        LOGGER.info('Calculating Impact Function')
        population_impact_success = self.calculate_specified_impact(
            'AshRasterPopulationFunction',
            self.hazard_layer,
            self.population_layer,
            'population_impact')

        # calculate landcover impact
        landcover_impact_success = self.calculate_specified_impact(
            'AshRasterLandCoverFunction',
            self.hazard_layer,
            self.landcover_layer,
            'landcover_impact')

        # calculate cities impact
        cities_impact_success = self.calculate_specified_impact(
            'AshRasterPlacesFunction',
            self.hazard_layer,
            self.cities_layer,
            'cities_impact')

        # calculate airport impact
        airport_impact_success = self.calculate_specified_impact(
            'AshRasterPlacesFunction',
            self.hazard_layer,
            self.airport_layer,
            'airport_impact')
        self.impact_exists = True
        # Create a zipped impact layer

        with ZipFile(self.impact_zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(self.working_dir_path()):
                for f in files:
                    _, ext = os.path.splitext(f)
                    if ('impact' in f and
                            not f == 'impact.zip' and
                            not ext == '.pdf'):
                        filename = os.path.join(root, f)
                        zipf.write(filename, arcname=f)

    def generate_report(self):
        # Generate pdf report from impact/hazard
        LOGGER.info('Generating report')
        if not self.impact_exists:
            # Cannot generate report when no impact layer present
            LOGGER.info('Cannot Generate report when no impact present.')
            return

        project_instance = QgsProject.instance()
        project_instance.setFileName(self.project_path)
        project_instance.read()

        # get layer registry
        layer_registry = QgsMapLayerRegistry.instance()
        layer_registry.removeAllMapLayers()

        # Set up the map renderer that will be assigned to the composition
        map_renderer = CANVAS.mapRenderer()

        # Enable on the fly CRS transformations
        map_renderer.setProjectionsEnabled(True)

        default_crs = map_renderer.destinationCrs()
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        map_renderer.setDestinationCrs(crs)

        # add place name layer
        layer_registry.addMapLayer(self.cities_layer, False)

        # add airport layer
        layer_registry.addMapLayer(self.airport_layer, False)

        # add volcano layer
        layer_registry.addMapLayer(self.volcano_layer, False)

        # add impact layer
        hazard_layer = read_qgis_layer(
            self.hazard_path, self.tr('People Affected'))
        layer_registry.addMapLayer(hazard_layer, False)

        # add basemap layer
        layer_registry.addMapLayer(self.highlight_base_layer, False)

        # add basemap layer
        layer_registry.addMapLayer(self.overview_layer, False)

        CANVAS.setExtent(hazard_layer.extent())
        CANVAS.refresh()

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
            map_impact.setKeepLayerSet(True)
            impact_layers = [
                self.volcano_layer.id(),
                self.airport_layer.id(),
                self.cities_layer.id(),
                hazard_layer.id(),
                self.highlight_base_layer.id(),
            ]
            map_impact.setLayerSet(impact_layers)
            map_impact.zoomToExtent(hazard_layer.extent())
            map_impact.renderModeUpdateCachedImage()
        else:
            LOGGER.exception('Map canvas could not be found in template %s',
                             template_path)
            raise MapComposerError

        # get overview map canvas on the composition and set extent
        map_overall = composition.getComposerItemById('map-overall')
        if map_overall:
            map_overall.setLayerSet([self.overview_layer.id()])
            # this is indonesia extent
            indonesia_extent = QgsRectangle(
                94.0927980005593554,
                -15.6629591962689343,
                142.0261493318861312,
                10.7379406374101816)
            map_overall.zoomToExtent(indonesia_extent)
            map_overall.renderModeUpdateCachedImage()
        else:
            LOGGER.exception(
                'Map canvas could not be found in template %s',
                template_path)
            raise MapComposerError

        # setup impact table
        self.render_population_table()
        self.render_nearby_table()
        self.render_landcover_table()

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
        logos_id = ['logo-bnpb', 'logo-geologi', 'logo-inasafe']
        for logo_id in logos_id:
            logo_picture = composition.getComposerItemById(logo_id)
            if logo_picture is None:
                message = '%s composer item could not be found' % logo_id
                LOGGER.exception(message)
                raise MapComposerError(message)
            pic_path = os.path.basename(logo_picture.picturePath())
            pic_path = os.path.join('logo', pic_path)
            logo_picture.setPicturePath(self.ash_fixtures_dir(pic_path))

        # save a pdf
        composition.exportAsPDF(self.map_report_path)

        project_instance.write(QFileInfo(self.project_path))

        layer_registry.removeAllMapLayers()
        map_renderer.setDestinationCrs(default_crs)
        map_renderer.setProjectionsEnabled(False)
        LOGGER.info('Report generation completed.')

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
            'realtime',
            'i18n',
            'inasafe_realtime_' + str(locale_name) + '.qm')
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
