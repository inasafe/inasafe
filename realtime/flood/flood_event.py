# coding=utf-8
import logging
import os
import shutil
from zipfile import ZipFile

import pytz
import datetime
import re
from PyQt4.QtCore import (
    QObject,
    QFileInfo,
    QVariant,
    QTranslator,
    QCoreApplication)
from PyQt4.QtXml import QDomDocument
from qgis.core import QgsMapLayerRegistry
from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
    QgsVectorFileWriter,
    QgsField,
    QgsPalLabeling,
    QgsComposition,
    QgsCoordinateReferenceSystem,
    QgsProject,
    QgsComposerHtml)
from realtime.exceptions import PetaJakartaAPIError, MapComposerError
from realtime.flood.dummy_source_api import DummySourceAPI
from realtime.flood.peta_jakarta_api import PetaJakartaAPI
from realtime.utilities import realtime_logger_name

from safe.test.utilities import get_qgis_app
from safe.utilities.styling import (
    set_vector_categorized_style,
    set_vector_graduated_style,
    setRasterStyle)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.common.exceptions import ZeroImpactException, TranslationLoadError
from safe.impact_functions.impact_function_manager import \
    ImpactFunctionManager
from safe.storage.core import read_layer, read_qgis_layer
from safe.utilities.keyword_io import KeywordIO
from safe.common.utilities import format_int
from safe.impact_functions.core import population_rounding
from safe import messaging as m


__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '11/24/15'


LOGGER = logging.getLogger(realtime_logger_name())


class FloodImpactData(object):

    def __init__(self):
        self.total_affected_population = 0
        self.estimates_idp = 0
        self.minimum_needs = None


class FloodEvent(QObject):

    def __init__(
            self,
            working_dir,
            locale,
            population_path,
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

        self.report_path = os.path.join(
            self.working_dir, self.report_id, locale)

        if not os.path.exists(self.report_path):
            os.makedirs(self.report_path)

        self.hazard_path = os.path.join(self.report_path, 'flood_data.json')
        self.hazard_layer = None
        self.hazard_zip_path = os.path.join(self.report_path, 'hazard.zip')

        self.population_path = population_path
        self.exposure_layer = None

        if not os.path.exists(self.hazard_path) or self.dummy_report_folder:
            self.save_hazard_data()

        self.load_hazard_data()
        self.load_exposure_data()

        # population aggregate
        self.population_aggregate_path = os.path.join(
            self.report_path, 'population_aggregate.shp')
        self.affect_field = 'Pop_affect'
        self.target_field = 'safe_ag'
        self.affected_aggregate = None

        # Impact layers
        self.function_id = 'ClassifiedPolygonHazardPolygonPeopleFunction'
        self.impact_path = os.path.join(self.report_path, 'impact.shp')
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

        # Impact data
        self.impact_data = FloodImpactData()

        # Setup i18n
        self.setup_i18n()

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

        # hazard_layer.startEditing()
        # field = QgsField('flooded', QVariant.Int)
        # hazard_layer.dataProvider().addAttributes([field])
        # hazard_layer.commitChanges()
        # idx = hazard_layer.fieldNameIndex('flooded')
        # expression = QgsExpression('count > 0')
        # expression.prepare(hazard_layer.pendingFields())
        #
        # hazard_layer.startEditing()
        # for feature in hazard_layer.getFeatures():
        #     feature[idx] = expression.evaluate(feature)
        #     hazard_layer.updateFeature(feature)
        #
        # hazard_layer.commitChanges()

        # writing keywords
        keyword_io = KeywordIO()

        keywords = {
            'field': 'state',
            'hazard': 'generic',
            'hazard_category': 'single_event',
            'keyword_version': '3.5',
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'hazard',
            'title': 'Flood',
            'value_map': '{"high": [4], "medium": [3], '
                         '"low": [2], '
                         '"unaffected": ["None","","NULL",0,1]}',
            'vector_hazard_classification': 'generic_vector_hazard_classes'
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

        impact_function.hazard = self.hazard_layer.as_qgis_native()
        impact_function.exposure = self.exposure_layer.as_qgis_native()
        extent = impact_function.hazard.extent()
        impact_function.requested_extent = [
            extent.xMinimum(), extent.yMinimum(),
            extent.xMaximum(), extent.yMaximum()]
        impact_function.requested_extent_crs = impact_function.hazard.crs()
        # impact_function.setup_aggregator()
        # impact_function.aggregator.validate_keywords()

        try:
            # skip process if hazard not contain significant flood
            skip_process = True
            qgis_hazard_layer = self.hazard_layer.as_qgis_native()
            keyword_io = KeywordIO()
            hazard_attribute_key = keyword_io.read_keywords(
                qgis_hazard_layer, 'field')

            # Do not skip if there are significant hazard class (2,3,4)
            for f in qgis_hazard_layer.getFeatures():
                try:
                    # try cast to int
                    hazard_state = f[hazard_attribute_key]
                    hazard_state = int(str(hazard_state))
                    if hazard_state >= 2:
                        skip_process = False
                        break
                except ValueError:
                    # this is expected
                    pass

            if skip_process:
                return

            impact_function.run_analysis()
            self.impact_layer = impact_function.impact
            self.target_field = impact_function.target_field
            # impact_function.aggregator.set_layers(
            #     self.hazard_layer.as_qgis_native(),
            #     self.exposure_layer.as_qgis_native())
            self.calculate_aggregate_impact(impact_function)
            # impact_function.run_aggregator()
            # impact_function.run_post_processor()
            # self.generate_aggregation(impact_function)
            self.generate_population_aggregation()
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

    def calculate_aggregate_impact(self, impact_function):

        # total affected population only calculated for hazard class >=2
        # total minimum needs should be recalculated with new affected
        # population
        total_affected = 0
        needs_dict = {}

        # qgis_impact_layer = impact_function.impact.as_qgis_native()
        # keyword_io = KeywordIO()
        # attribute_field = keyword_io.read_keywords(
        #     qgis_impact_layer, 'field')
        # features = impact_function.impact.as_qgis_native().getFeatures()

        # for f in features:
        #     # 2 is the minimum hazard
        #     if f[self.target_field] >= 2:
        #         total_affected += f[self.]

        self.impact_data.total_affected_population = \
            impact_function.total_affected_population
        # Fixme for now, it was estimated that 1% of impacted is IDP
        self.impact_data.estimates_idp = \
            impact_function.total_affected_population * 0.01
        self.impact_data.minimum_needs = impact_function.total_needs

    def generate_population_aggregation(self):

        # duplicate exposure data
        QgsVectorFileWriter.writeAsVectorFormat(
            self.exposure_layer.as_qgis_native(),
            self.population_aggregate_path,
            'CP1250',
            None,
            'ESRI Shapefile')
        population_aggregate = read_qgis_layer(
            self.population_aggregate_path, 'Impacted Population')
        shutil.copy(
            self.population_path.replace('.shp', '.xml'),
            self.population_aggregate_path.replace('.shp', '.xml'))

        # add affected population field
        population_aggregate.startEditing()
        field = QgsField(self.affect_field, QVariant.Int)
        field2 = QgsField(self.target_field, QVariant.Int)
        population_aggregate.dataProvider().addAttributes([field, field2])
        population_aggregate.commitChanges()

        idx = population_aggregate.fieldNameIndex(self.affect_field)
        idx2 = population_aggregate.fieldNameIndex(self.target_field)
        impact_layer = self.impact_layer.as_qgis_native()
        keyword_io = KeywordIO()
        name_field = keyword_io.read_keywords(
            population_aggregate, 'area_name_field')
        attribute_field = keyword_io.read_keywords(
            population_aggregate, 'field')

        # calculate affected data
        district_dict = {}
        for f in impact_layer.getFeatures():
            if f[self.target_field] >= 1:
                if f[name_field] in district_dict:
                    district_dict[f[name_field]] += f[attribute_field]
                else:
                    district_dict[f[name_field]] = f[attribute_field]

        population_aggregate.startEditing()
        for f in population_aggregate.getFeatures():
            f[idx] = district_dict.get(f[name_field], 0)
            if f[idx] == 0:
                # mark as unaffected
                f[idx2] = 0
            else:
                # mark as affected
                f[idx2] = 1

            population_aggregate.updateFeature(f)
        population_aggregate.commitChanges()
        self.affected_aggregate = district_dict

        # calculate total affected people
        total_affected = 0
        for k, v in district_dict.iteritems():
            total_affected += v

        # calculate new minimum needs
        min_needs = self.impact_data.minimum_needs
        for k, v in min_needs.iteritems():
            for need in v:
                need['amount'] = need['value'] * total_affected

        # self.impact_data.total_affected_population = total_affected
        # self.impact_data.estimates_idp = 0.01 * total_affected

    def set_style(self):
        # get requested style of impact

        qml_path = self.flood_fixtures_dir(
            'impact-template.qml')
        target_style_path = os.path.join(
            self.report_path, 'population_aggregate.qml')
        keyword_io = KeywordIO()
        qgis_exposure_layer = self.exposure_layer.as_qgis_native()
        attribute_field = keyword_io.read_keywords(
            qgis_exposure_layer, 'field')
        with open(qml_path) as f_template:
            str_template = f_template.read()

            # search max_population in an RW
            # use generator for memory efficiency
            maximum_population = max(
                f[attribute_field] for f
                in qgis_exposure_layer.getFeatures()
            )
            range_increment = maximum_population / 5
            legend_expressions = {}
            for i in range(5):
                if i == 0:
                    marker_label = '&lt; %s' % format_int(range_increment)
                elif i < 4:
                    marker_label = '%s - %s' % (
                        format_int(range_increment * i),
                        format_int(range_increment * (i + 1))
                    )
                else:
                    marker_label = '> %s' % format_int(range_increment * 4)
                marker_size = \
                    'scale_linear(' \
                    'attribute($currentfeature, &quot;%s&quot;) ' \
                    ', %d, %d, %d, %d)' % (
                        self.affect_field,
                        int(range_increment * i),
                        int(range_increment * (i + 1)),
                        i * 2,
                        (i + 1) * 2,
                    )
                marker_color = \
                    "set_color_part(" \
                    "set_color_part('0,0,255','saturation', %d ), 'alpha', " \
                    "if(attribute($currentfeature, '%s') = 0, " \
                    "0, 255))" % (i * 20, self.affect_field)
                marker_border = \
                    "set_color_part(" \
                    "'0,0,0','alpha', " \
                    "if (to_int(attribute(" \
                    "$currentfeature, '%s')) = 0, 0, 255))" % \
                    self.affect_field

                legend_expressions['marker-min-range-%d' % i] = \
                    '%s' % (range_increment * i)
                legend_expressions['marker-max-range-%d' % i] = \
                    '%s' % (range_increment * (i + 1))
                legend_expressions['marker-label-%d' % i] = marker_label
                legend_expressions['marker-size-%d' % i] = marker_size
                legend_expressions['marker-color-%d' % i] = marker_color
                legend_expressions['marker-border-%d' % i] = marker_border

            for k, v in legend_expressions.iteritems():
                str_template = str_template.replace('[%s]' % k, v)

            with open(target_style_path, mode='w') as target_f:
                target_f.write(str_template)

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
        id_time_format = 'EN-%Y%m%d-%H'
        timestamp_string = timestamp.strftime(time_format)
        event = {
            'report-head': self.tr("""THE GOVERNMENT OF DKI JAKARTA PROVINCE
REGIONAL DISASTER MANAGEMENT AGENCY
"""),
            'report-title': self.tr('FLOOD IMPACT REPORT FOR POPULATION'),
            'report-timestamp': self.tr('Based on flood %s') % (
                timestamp_string, ),
            'report-id': timestamp.strftime(id_time_format),
            'header-legend': self.tr('Legend'),
            'header-analysis-result': self.tr('InaSAFE Analysis Result'),
            'header-provenance': self.tr('Data Source'),
            'header-contact': self.tr('Contact'),
            'header-supporter': self.tr('Supported by'),
            'header-notes': self.tr('Disclaimer'),
            'content-provenance': self.tr("""Data Sources:
1. Hazard Data
   Flood: BPBD DKI Jakarta / PetaJakarta.org
2. Exposure Data
   Population: Population Agency DKI Jakarta Prov.
"""),
            'content-disclaimer': self.tr(
                'This impact estimate is automatically generated and only '
                'takes into account the population affected by flood hazard '
                'in Jakarta. The estimate is based on flood hazard data from '
                'BPBD DKI Jakarta and population exposure data from the '
                'Population Agency, DKI Jakarta Province. Limitations in the '
                'estimates of flood hazard and population may result in '
                'significant misrepresentation of the on-the-surface '
                'situation in the figures shown here. Consequently, '
                'decisions '
                'should not be made solely on the information presented here '
                'and should always be verified with other reliable '
                'information sources.'
            ),
            'content-contact': self.tr("""Pusat Pengendalian Operasi (Pusdalops)
BPBD Provinsi DKI Jakarta
Gedung Dinas Teknis Lt. 5
Jl. Abdul Muis No. 66
Telp. 121
"""),
        }
        return event

    def generate_analysis_result_html(self):
        """Return a HTML table of the analysis result

        :return: A file path to the html file saved to disk.
        """
        message = m.Message(style_class='report')
        # Table for affected population
        table = m.Table(style_class='table table-condensed table-striped')
        row = m.Row()
        total_people = self.tr('%s') % format_int(population_rounding(
            self.impact_data.total_affected_population))
        estimates_idp = self.tr('%s') % format_int(population_rounding(
            self.impact_data.estimates_idp))
        row.add(m.Cell(
            self.tr('Total affected population (people)'), header=True))
        row.add(m.Cell(total_people, style_class="text-right"))
        table.add(row)
        row = m.Row()
        row.add(m.Cell(self.tr('Estimates of IDP (people)'), header=True))
        row.add(m.Cell(estimates_idp, style_class="text-right"))
        table.add(row)
        message.add(table)
        # Table for minimum needs
        for k, v in self.impact_data.minimum_needs.iteritems():
            section = self.tr('Relief items to be provided %s :') % k
            # text = m.Text(section)
            row = m.Row(style_class='alert-info')
            row.add(m.Cell(section, header=True, attributes='colspan=2'))
            # message.add(text)
            table = m.Table(
                header=row,
                style_class='table table-condensed table-striped')
            for e in v:
                row = m.Row()
                need_name = self.tr(e['name'])
                need_number = format_int(
                    population_rounding(e['amount']))
                need_unit = self.tr(e['unit']['abbreviation'])
                if need_unit:
                    need_string = '%s (%s)' % (need_name, need_unit)
                else:
                    need_string = need_name
                row.add(m.Cell(need_string, header=True))
                row.add(m.Cell(need_number, style_class="text-right"))
                table.add(row)
            message.add(table)

        path = self.write_html_table('impact_analysis_report.html', message)
        return path

    def write_html_table(self, file_name, message):
        """Writing a Table object to report folder

        The table will be wrapped by HTML header and footer.
        This file will be rendered by QgsComposer in a HTML Frame

        :param file_name: file name of the html file output
        :param message: the Message object to write
        :return:
        """
        path = os.path.join(
            self.report_path, file_name)
        header_file = self.flood_fixtures_dir('header.html')
        footer_file = self.flood_fixtures_dir('footer.html')

        with open(header_file) as f:
            header = f.read()

        with open(footer_file) as f:
            footer = f.read()

        with open(path, 'w') as html_file:
            html_file.write(header)
            html_file.write(message.to_html(in_div_flag=True))
            html_file.write(footer)

        return path

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
        # add impact layer
        population_affected_layer = read_qgis_layer(
            self.population_aggregate_path, self.tr('People Affected'))
        layer_registry.addMapLayer(population_affected_layer, True)
        # add boundary mask
        boundary_mask = read_qgis_layer(
            self.flood_fixtures_dir('boundary-mask.shp'))
        layer_registry.addMapLayer(boundary_mask, False)
        # add hazard layer
        hazard_layer = read_qgis_layer(
            self.hazard_path, self.tr('Flood Depth (cm)'))
        layer_registry.addMapLayer(hazard_layer, True)
        # add boundary layer
        boundary_layer = read_qgis_layer(
            self.flood_fixtures_dir('boundary-5.shp'))
        layer_registry.addMapLayer(boundary_layer, False)
        CANVAS.setExtent(boundary_layer.extent())
        CANVAS.refresh()
        # add basemap layer
        # this code uses OpenlayersPlugin
        base_map = QgsRasterLayer(
            self.flood_fixtures_dir('jakarta.jpg'))
        layer_registry.addMapLayer(base_map, False)
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
            # map_legend.modelV2().clear()
            # print dir(map_legend.modelV2())
            # map_legend.setLegendFilterByMapEnabled(True)

            map_legend.model().setLayerSet(
                [hazard_layer.id(), population_affected_layer.id()])

        else:
            LOGGER.exception('Map legend could not be found in template %s',
                             template_path)
            raise MapComposerError

        content_analysis = composition.getComposerItemById(
            'content-analysis-result')
        if not content_analysis:
            message = 'Content analysis composer item could not be found'
            LOGGER.exception(message)
            raise MapComposerError(message)
        content_analysis_html = content_analysis.multiFrame()
        if content_analysis_html:
            # set url to generated html
            analysis_html_path = self.generate_analysis_result_html()
            # We're using manual HTML to avoid memory leak and segfault
            # happened when using Url Mode
            content_analysis_html.setContentMode(QgsComposerHtml.ManualHtml)
            with open(analysis_html_path) as f:
                content_analysis_html.setHtml(f.read())
                content_analysis_html.loadHtml()
        else:
            message = 'Content analysis HTML not found in template'
            LOGGER.exception(message)
            raise MapComposerError(message)

        # save a pdf
        composition.exportAsPDF(self.map_report_path)

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
