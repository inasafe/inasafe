# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Functionality related to shake events.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__date__ = '1/08/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import shutil
#noinspection PyPep8Naming
import cPickle as pickle
import math
import logging
from datetime import datetime

import numpy
#noinspection PyPackageRequirements
import pytz  # sudo apt-get install python-tz

# This import is required to enable PyQt API v2
# noinspection PyUnresolvedReferences
# pylint: disable=W0611
import qgis
# pylint: enable=W0611
# TODO: I think QCoreApplication is needed for tr() check before removing
#noinspection PyPackageRequirements
from PyQt4.QtCore import (
    QCoreApplication,
    QObject,
    QVariant,
    QFileInfo,
    QUrl,
    QSize,
    Qt,
    QTranslator)
#noinspection PyPackageRequirements
from PyQt4.QtXml import QDomDocument
# We should remove the following pylint suppressions when we support only QGIS2
# pylint: disable=E0611
# pylint: disable=W0611
# Above for pallabelling
from qgis.core import (
    QgsPoint,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsVectorLayer,
    QgsRaster,
    QgsRasterLayer,
    QgsDataSourceURI,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem,
    QgsProject,
    QgsComposition,
    QgsMapLayerRegistry,
    QgsPalLabeling,
    QgsProviderRegistry,
    QgsFeatureRequest,
    QgsVectorDataProvider)

# pylint: enable=E0611
# pylint: enable=W0611
from safe.common.testing import get_qgis_app
from safe.api import get_plugins as safe_get_plugins
from safe.api import read_layer as safe_read_layer
from safe.api import calculate_impact as safe_calculate_impact
from safe.api import (
    Table,
    TableCell,
    TableRow,
    get_version,
    romanise)
from safe_qgis.utilities.utilities import get_wgs84_resolution
from safe_qgis.utilities.clipper import extent_to_geoarray, clip_layer
from safe_qgis.utilities.styling import mmi_colour
from safe_qgis.exceptions import TranslationLoadError
from safe_qgis.tools.shake_grid.shake_grid import ShakeGrid
from realtime.sftp_shake_data import SftpShakeData
from realtime.utilities import (
    shakemap_extract_dir,
    data_dir,
    realtime_logger_name)
from realtime.sftp_configuration.configuration import get_grid_source
from realtime.exceptions import (
    GridXmlFileNotFoundError,
    InvalidLayerError,
    ShapefileCreationError,
    CityMemoryLayerCreationError,
    FileNotFoundError,
    MapComposerError,
    SFTPEmptyError,
    NetworkError,
    EventIdError)

LOGGER = logging.getLogger(realtime_logger_name())
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class ShakeEvent(QObject):
    """Behaviour and data relating to an earthquake.

    Including epicenter, magnitude etc.
    """
    def __init__(self,
                 event_id=None,
                 locale='en',
                 population_raster_path=None,
                 geonames_sqlite_path=None,
                 force_flag=False,
                 data_is_local_flag=False):
        """Constructor for the shake event class.

        :param event_id: (Optional) Id of the event. Will be used to
            fetch the ShakeData for this event (either from cache or from ftp
            server as required). The grid.xml file in the unpacked event will
            be used to initialise the state of the a ShakeGridConvert instance.
            If no event id is supplied, the most recent event recorded on the
            server will be used.
        :type event_id: str

        :param locale:(Optional) string for iso locale to use for outputs.
            Defaults to en. Can also use 'id' or possibly more as translations
            are added.
        :type locale: str

        :param population_raster_path: (Optional) Path to the population
            raster that will be used if you want to calculate the impact.
            This is optional because there are various ways this can be
            specified before calling :func:`calculate_impacts`.
        :type population_raster_path: str

        :param geonames_sqlite_path: (Optional) Path to the geonames sqlite
            that will be used.
        :type geonames_sqlite_path: str

        :param force_flag: Whether to force retrieval of the dataset from the
            ftp server.
        :type force_flag: bool

        :param data_is_local_flag: Whether the data is already extracted and
            exists locally. Use this in cases where you manually want to run
            a grid.xml without first doing a download.
        :type data_is_local_flag: bool

        :return: Instance

        :raises: SFTPEmptyError, NetworkError, EventIdError, EventXmlParseError
        """
        # We inherit from QObject for translation support
        QObject.__init__(self)

        self.check_environment()

        if data_is_local_flag:
            self.event_id = event_id
        else:
            # fetch the data from (s)ftp
            #self.data = ShakeData(event_id, force_flag)
            try:
                self.data = SftpShakeData(
                    event=event_id,
                    force_flag=force_flag)
            except (SFTPEmptyError, NetworkError, EventIdError):
                raise
            self.data.extract()
            self.event_id = self.data.event_id

        # Convert grid.xml (we'll give the title with event_id)
        self.shake_grid = ShakeGrid(
            self.event_id, get_grid_source(), self.grid_file_path())

        self.population_raster_path = population_raster_path
        self.geonames_sqlite_path = geonames_sqlite_path
        # Path to tif of impact result - probably we wont even use it
        self.impact_file = None
        # Path to impact keywords file - this is GOLD here!
        self.impact_keywords_file = None
        # number of people killed per mmi band
        self.fatality_counts = None
        # Total number of predicted fatalities
        self.fatality_total = 0
        # number of people displaced per mmi band
        self.displaced_counts = None
        # number of people affected per mmi band
        self.affected_counts = None
        # After selecting affected cities near the event, the bbox of
        # shake map + cities
        self.extent_with_cities = None
        # How much to iteratively zoom out by when searching for cities
        self.zoom_factor = 1.25
        # The search boxes used to find extent_with_cities
        # Stored in the form [{'city_count': int, 'geometry': QgsRectangle()}]
        self.search_boxes = None
        # Stored as a dict with dir_to, dist_to,  dist_from etc e.g.
        #{'dir_from': 16.94407844543457,
        #'dir_to': -163.05592346191406,
        #'roman': 'II',
        #'dist_to': 2.504295825958252,
        #'mmi': 1.909999966621399,
        #'name': 'Tondano',
        #'id': 57,
        #'population': 33317}
        self.most_affected_city = None
        # for localization
        self.translator = None
        self.locale = locale
        self.setup_i18n()

    #noinspection PyMethodMayBeStatic
    def check_environment(self):
        """A helper class to check that QGIS is correctly initialised.

        :raises: EnvironmentError if the environment is not correct.
        """
        # noinspection PyArgumentList
        registry = QgsProviderRegistry.instance()
        registry_list = registry.pluginList()
        if len(registry_list) < 1:
            raise EnvironmentError('QGIS data provider list is empty!')

    def grid_file_path(self):
        """A helper to retrieve the path to the grid.xml file

        :return: An absolute filesystem path to the grid.xml file.
        :raise: GridXmlFileNotFoundError
        """
        LOGGER.debug('Event path requested.')
        grid_xml_path = os.path.join(
            shakemap_extract_dir(),
            self.event_id,
            'grid.xml')
        #short circuit if the tif is already created.
        if os.path.exists(grid_xml_path):
            return grid_xml_path
        else:
            LOGGER.error('Event file not found. %s' % grid_xml_path)
            raise GridXmlFileNotFoundError('%s not found' % grid_xml_path)

    def mmi_shaking(self, mmi_value):
        """Return the perceived shaking for an mmi value as translated string.

        :param mmi_value: The MMI value.
        :type mmi_value: int, float

        :return Internationalised string representing perceived shaking
            level e.g. weak, severe etc.

        :rtype: str
        """
        shaking_dict = {
            1: self.tr('Not felt'),
            2: self.tr('Weak'),
            3: self.tr('Weak'),
            4: self.tr('Light'),
            5: self.tr('Moderate'),
            6: self.tr('Strong'),
            7: self.tr('Very strong'),
            8: self.tr('Severe'),
            9: self.tr('Violent'),
            10: self.tr('Extreme'),
        }
        return shaking_dict[mmi_value]

    def mmi_potential_damage(self, mmi_value):
        """Return the potential damage for an mmi value as translated string.

        :param mmi_value: float or int required.

        :return str: internationalised string representing potential damage
         level e.g. Light, Moderate etc.
        """
        damage_dict = {
            1: self.tr('None'),
            2: self.tr('None'),
            3: self.tr('None'),
            4: self.tr('None'),
            5: self.tr('Very light'),
            6: self.tr('Light'),
            7: self.tr('Moderate'),
            8: self.tr('Mod/Heavy'),
            9: self.tr('Heavy'),
            10: self.tr('Very heavy')
        }
        return damage_dict[mmi_value]

    def cities_to_shapefile(self, force_flag=False):
        """Write a cities memory layer to a shapefile.

        :param force_flag: (Optional). Whether to force the overwrite
                of any existing data. Defaults to False.
        :type force_flag: bool

        :return str Path to the created shapefile
        :raise ShapefileCreationError

        .. note:: The file will be saved into the shakemap extract dir
           event id folder. Any existing shp by the same name will be
           overwritten if theForceFlag is False, otherwise it will
           be returned directly without creating a new file.
        """
        filename = 'mmi-cities'
        memory_layer = self.local_cities_memory_layer()
        return self.memory_layer_to_shapefile(
            file_name=filename,
            memory_layer=memory_layer,
            force_flag=force_flag)

    def city_search_boxes_to_shapefile(self, force_flag=False):
        """Write a cities memory layer to a shapefile.

        :param force_flag: bool (Optional). Whether to force the overwrite
                of any existing data. Defaults to False.
        :type force_flag: bool

        .. note:: The file will be saved into the shakemap extract dir
           event id folder. Any existing shp by the same name will be
           overwritten if force_flag is False, otherwise it will
           be returned directly without creating a new file.

        :return: Path to the created shapefile.
        :rtype: str

        :raise: ShapefileCreationError
        """
        filename = 'city-search-boxes'
        memory_layer = self.city_search_box_memory_layer()
        return self.memory_layer_to_shapefile(
            file_name=filename,
            memory_layer=memory_layer,
            force_flag=force_flag)

    def memory_layer_to_shapefile(
            self,
            file_name,
            memory_layer,
            force_flag=False):
        """Write a memory layer to a shapefile.

        :param file_name: Filename excluding path and ext. e.g. 'mmi-cities'
        :type file_name: str

        :param memory_layer: QGIS memory layer instance.
        :type memory_layer: QgsVectorLayer

        :param force_flag: (Optional). Whether to force the overwrite
                of any existing data. Defaults to False.
        :type force_flag: bool

        .. note:: The file will be saved into the shakemap extract dir
           event id folder. If a qml matching theFileName.qml can be
           found it will automatically copied over to the output dir.
           Any existing shp by the same name will be overridden if
           theForceFlag is True, otherwise the existing file will be returned.

        :return: Path to the created shapefile.
        :rtype: str

        :raise: ShapefileCreationError
        """
        LOGGER.debug('memory_layer_to_shapefile requested.')

        LOGGER.debug(str(memory_layer.dataProvider().attributeIndexes()))
        if memory_layer.featureCount() < 1:
            raise ShapefileCreationError('Memory layer has no features')

        geo_crs = QgsCoordinateReferenceSystem()
        geo_crs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)

        output_file_base = os.path.join(shakemap_extract_dir(),
                                        self.event_id,
                                        '%s.' % file_name)
        output_file = output_file_base + 'shp'
        if os.path.exists(output_file) and force_flag is not True:
            return output_file
        elif os.path.exists(output_file):
            try:
                os.remove(output_file_base + 'shp')
                os.remove(output_file_base + 'shx')
                os.remove(output_file_base + 'dbf')
                os.remove(output_file_base + 'prj')
            except OSError:
                LOGGER.exception(
                    'Old shape files not deleted'
                    ' - this may indicate a file permissions issue.')

        # Next two lines a workaround for a QGIS bug (lte 1.8)
        # preventing mem layer attributes being saved to shp.
        memory_layer.startEditing()
        memory_layer.commitChanges()

        LOGGER.debug('Writing mem layer to shp: %s' % output_file)
        # Explicitly giving all options, not really needed but nice for clarity
        error_message = ''
        options = []
        layer_options = []
        selected_only_flag = False
        skip_attributes_flag = False
        # May differ from output_file
        actual_new_file_name = ''
        # noinspection PyCallByClass,PyTypeChecker
        result = QgsVectorFileWriter.writeAsVectorFormat(
            memory_layer,
            output_file,
            'utf-8',
            geo_crs,
            "ESRI Shapefile",
            selected_only_flag,
            error_message,
            options,
            layer_options,
            skip_attributes_flag,
            actual_new_file_name)

        if result == QgsVectorFileWriter.NoError:
            LOGGER.debug('Wrote mem layer to shp: %s' % output_file)
        else:
            raise ShapefileCreationError(
                'Failed with error: %s' % result)

        # Lastly copy over the standard qml (QGIS Style file) for the mmi.tif
        qml_path = os.path.join(
            shakemap_extract_dir(),
            self.event_id,
            '%s.qml' % file_name)
        source_qml = os.path.join(data_dir(), '%s.qml' % file_name)
        shutil.copyfile(source_qml, qml_path)

        return output_file

    def local_city_features(self):
        """Create a list of features representing cities impacted.

        :return: List of QgsFeature instances, each representing a place/city.

        :raises: InvalidLayerError

        The following fields will be created for each city feature:

            QgsField('id', QVariant.Int),
            QgsField('name', QVariant.String),
            QgsField('population', QVariant.Int),
            QgsField('mmi', QVariant.Double),
            QgsField('dist_to', QVariant.Double),
            QgsField('dir_to', QVariant.Double),
            QgsField('dir_from', QVariant.Double),
            QgsField('roman', QVariant.String),
            QgsField('colour', QVariant.String),

        The 'name' and 'population' fields will be obtained from our geonames
        dataset.

        A raster lookup for each city will be done to set the mmi field
        in the city feature with the value on the raster. The raster should be
        one generated using :func:`mmiDatToRaster`. The raster will be created
        first if needed.

        The distance to and direction to/from fields will be set using QGIS
        geometry API.

        It is a requirement that there will always be at least one city
        on the map for context so we will iteratively do a city selection,
        starting with the extents of the MMI dataset and then zooming
        out by self.zoom_factor until we have some cities selected.

        After making a selection the extents used (taking into account the
        iterative scaling mentioned above) will be stored in the class
        attributes so that when producing a map it can be used to ensure
        the cities and the shake area are visible on the map. See
        :samp:`self.extent_with_cities` in :func:`__init__`.

        .. note:: We separate the logic of creating features from writing a
          layer so that we can write to any format we like whilst reusing the
          core logic.

        .. note:: The original dataset will be modified in place.
        """
        LOGGER.debug('localCityValues requested.')
        # Setup the raster layer for interpolated mmi lookups
        path = self.shake_grid.mmi_to_raster()
        file_info = QFileInfo(path)
        base_name = file_info.baseName()
        raster_layer = QgsRasterLayer(path, base_name)
        if not raster_layer.isValid():
            raise InvalidLayerError('Layer failed to load!\n%s' % path)

        # Setup the cities table, querying on event bbox
        # Path to sqlitedb containing geonames table
        db_path = self._get_sqlite_path()
        uri = QgsDataSourceURI()
        uri.setDatabase(db_path)
        table = 'geonames'
        geometry_column = 'geom'
        schema = ''
        uri.setDataSource(schema, table, geometry_column)
        layer = QgsVectorLayer(uri.uri(), 'Towns', 'spatialite')
        if not layer.isValid():
            raise InvalidLayerError(db_path)

        rectangle = self.shake_grid.grid_bounding_box

        # Do iterative selection using expanding selection area
        # Until we have got some cities selected
        attempts_limit = 5
        minimum_city_count = 1
        found_flag = False
        search_boxes = []
        request = None
        LOGGER.debug('Search polygons for cities:')
        for _ in range(attempts_limit):
            LOGGER.debug(rectangle.asWktPolygon())
            layer.removeSelection()
            request = QgsFeatureRequest().setFilterRect(rectangle)
            request.setFlags(QgsFeatureRequest.ExactIntersect)
            # This is klunky - must be a better way in the QGIS api!?
            # but layer.selectedFeatureCount() relates to gui
            # selection it seems...
            count = 0
            for _ in layer.getFeatures(request):
                count += 1
            # Store the box plus city count so we can visualise it later
            record = {'city_count': count, 'geometry': rectangle}
            LOGGER.debug('Found cities in search box: %s' % record)
            search_boxes.append(record)
            if count < minimum_city_count:
                rectangle.scale(self.zoom_factor)
            else:
                found_flag = True
                break

        self.search_boxes = search_boxes
        # TODO: Perhaps it might be neater to combine the bbox of cities and
        #       mmi to get a tighter AOI then do a small zoom out.
        self.extent_with_cities = rectangle
        if not found_flag:
            LOGGER.debug(
                'Could not find %s cities after expanding rect '
                '%s times.' % (minimum_city_count, attempts_limit))
        # Setup field indexes of our input and out datasets
        cities = []

        # For measuring distance and direction from each city to epicenter
        epicenter = QgsPoint(
            self.shake_grid.longitude,
            self.shake_grid.latitude)

        # Now loop through the db adding selected features to mem layer
        for feature in layer.getFeatures(request):
            if not feature.isValid():
                LOGGER.debug('Skipping feature')
                continue
                #LOGGER.debug('Writing feature to mem layer')
            # calculate the distance and direction from this point
            # to and from the epicenter
            feature_id = str(feature.id())

            # Make sure the fcode contains PPL (populated place)
            code = str(feature['fcode'])
            if 'PPL' not in code:
                continue

            # Make sure the place is populated
            population = int(feature['population'])
            if population < 1:
                continue

            point = feature.geometry().asPoint()
            distance = point.sqrDist(epicenter)
            direction_to = point.azimuth(epicenter)
            direction_from = epicenter.azimuth(point)
            place_name = str(feature['asciiname'])

            new_feature = QgsFeature()
            new_feature.setGeometry(feature.geometry())

            # Populate the mmi field by raster lookup
            # Get a {int, QVariant} back
            raster_values = raster_layer.dataProvider().identify(
                point, QgsRaster.IdentifyFormatValue).results()
            raster_values = raster_values.values()
            if not raster_values or len(raster_values) < 1:
                # position not found on raster
                continue
            value = raster_values[0]  # Band 1
            LOGGER.debug('Raster Value: %s' % value)
            if 'no data' not in str(value):
                mmi = float(value)
            else:
                mmi = 0

            LOGGER.debug(
                'Looked up mmi of %s on raster for %s' % (mmi, str(point)))

            roman = romanise(mmi)
            if roman is None:
                continue

            # new_feature.setFields(myFields)
            # Column positions are determined by setFields above
            attributes = [
                feature_id,
                place_name,
                population,
                mmi,
                distance,
                direction_to,
                direction_from,
                roman,
                mmi_colour(mmi)]
            new_feature.setAttributes(attributes)
            cities.append(new_feature)

        return cities

    def local_cities_memory_layer(self):
        """Fetch a collection of the cities that are nearby.

        :return: A QGIS memory layer
        :rtype: QgsVectorLayer

        :raises: Any exceptions will be propagated.
        """
        LOGGER.debug('local_cities_memory_layer requested.')
        # Now store the selection in a temporary memory layer
        memory_layer = QgsVectorLayer('Point', 'affected_cities', 'memory')
        layer_provider = memory_layer.dataProvider()
        provider_capabilities = layer_provider.capabilities()

        if provider_capabilities & QgsVectorDataProvider.AddAttributes:
            memory_layer.startEditing()
            # add field defs
            layer_provider.addAttributes([
                QgsField('id', QVariant.Int),
                QgsField('name', QVariant.String),
                QgsField('population', QVariant.Int),
                QgsField('mmi', QVariant.Double),
                QgsField('dist_to', QVariant.Double),
                QgsField('dir_to', QVariant.Double),
                QgsField('dir_from', QVariant.Double),
                QgsField('roman', QVariant.String),
                QgsField('colour', QVariant.String)])
            cities = self.local_city_features()
            result = layer_provider.addFeatures(cities)
            if not result:
                LOGGER.exception(
                    'Unable to add features to cities memory layer')
                raise CityMemoryLayerCreationError(
                    'Could not add any features to cities memory layer.')

            memory_layer.commitChanges()
            memory_layer.updateExtents()

            LOGGER.debug('Feature count of mem layer:  %s' %
                         memory_layer.featureCount())
            return memory_layer
        else:
            raise InvalidLayerError(
                'Could not add new attributes to this layer.')

    def city_search_box_memory_layer(self, force_flag=False):
        """Return the search boxes used to search for cities as a memory layer.

        This is mainly useful for diagnostic purposes.

        :param force_flag: (Optional). Whether to force the overwrite
                of any existing data. Defaults to False.
        :type force_flag: bool

        :return: A QGIS memory layer
        :rtype: QgsVectorLayer

        :raise: Any exceptions will be propagated.
        """
        LOGGER.debug('city_search_box_memory_layer requested.')
        # There is a dependency on local_cities_memory_layer so run it first
        if self.search_boxes is None or force_flag:
            self.local_cities_memory_layer()
        # Now store the selection in a temporary memory layer
        memory_layer = QgsVectorLayer(
            'Polygon',
            'City Search Boxes',
            'memory')
        memory_provider = memory_layer.dataProvider()
        # add field defs
        field = QgsField('cities_found', QVariant.Int)
        memory_provider.addAttributes([field])
        features = []
        for search_box in self.search_boxes:
            new_feature = QgsFeature()
            rectangle = search_box['geometry']
            # noinspection PyArgumentList
            geometry = QgsGeometry.fromWkt(rectangle.asWktPolygon())
            new_feature.setGeometry(geometry)
            new_feature.setAttributes([search_box['city_count']])
            features.append(new_feature)

        result = memory_provider.addFeatures(features)
        if not result:
            LOGGER.exception(
                'Unable to add features to city search boxes memory layer')
            raise CityMemoryLayerCreationError(
                'Could not add any features to city search boxes memory layer')

        memory_layer.commitChanges()
        memory_layer.updateExtents()

        LOGGER.debug(
            'Feature count of search box mem layer:  %s' %
            memory_layer.featureCount())

        return memory_layer

    def sorted_impacted_cities(self, row_count=5):
        """Return a data structure with place, mmi, pop sorted by mmi then pop.

        :param row_count: optional limit to how many rows should be
                returned. Defaults to 5 if not specified.
        :type row_count: int

        :return: An list of dicts containing the sorted cities and their
            attributes. See below for example output.
            ::

                  [{'dir_from': 16.94407844543457,
                  'dir_to': -163.05592346191406,
                  'roman': 'II',
                  'dist_to': 2.504295825958252,
                  'mmi': 1.909999966621399,
                  'name': 'Tondano',
                  'id': 57,
                  'population': 33317}]

        :rtype: list

        Straw man illustrating how sorting is done:
        ::

         m = [
             {'name': 'b', 'mmi': 10,  'pop':10},
             {'name': 'a', 'mmi': 100, 'pop': 20},
             {'name': 'c', 'mmi': 10, 'pop': 14}]

        ::

         sorted(m, key=lambda d: (-d['mmi'], -d['pop'], d['name']))
         Out[10]:
         [{'mmi': 100, 'name': 'a', 'pop': 20},
          {'mmi': 10, 'name': 'c', 'pop': 14},
          {'mmi': 10, 'name': 'b', 'pop': 10}]

        .. note:: self.most_affected_city will also be populated with
            the dictionary of details for the most affected city.

        .. note:: It is possible that there is no affected city! e.g. if
            all nearby cities fall outside of the shake raster.
        """
        layer = self.local_cities_memory_layer()
        fields = layer.dataProvider().fields()
        cities = []
        # pylint: disable=W0612
        count = 0
        # pylint: enable=W0612
        # Now loop through the db adding selected features to mem layer
        request = QgsFeatureRequest()

        for feature in layer.getFeatures(request):
            if not feature.isValid():
                LOGGER.debug('Skipping feature')
                continue
            count += 1
            # calculate the distance and direction from this point
            # to and from the epicenter
            feature_id = feature.id()
            # We should be able to do this:
            # place_name = str(feature['name'].toString())
            # But its not working so we do this:
            place_name = str(
                feature[fields.indexFromName('name')])
            mmi = float(feature[fields.indexFromName('mmi')])
            population = int(
                feature[fields.indexFromName('population')])
            roman = str(
                feature[fields.indexFromName('roman')])
            direction_to = float(
                feature[fields.indexFromName('dir_to')])
            direction_from = float(
                feature[fields.indexFromName('dir_from')])
            distance_to = float(
                feature[fields.indexFromName('dist_to')])
            city = {
                'id': feature_id,
                'name': place_name,
                'mmi-int': int(mmi),
                'mmi': mmi,
                'population': population,
                'roman': roman,
                'dist_to': distance_to,
                'dir_to': direction_to,
                'dir_from': direction_from}
            cities.append(city)
        LOGGER.debug('%s features added to sorted impacted cities list.')
        #LOGGER.exception(cities)
        sorted_cities = sorted(cities,
                               key=lambda d: (
                               # we want to use whole no's for sort
                               - d['mmi-int'],
                               - d['population'],
                               d['name'],
                               d['mmi'],  # not decimals
                               d['roman'],
                               d['dist_to'],
                               d['dir_to'],
                               d['dir_from'],
                               d['id']))
        # TODO: Assumption that place names are unique is bad....
        if len(sorted_cities) > 0:
            self.most_affected_city = sorted_cities[0]
        else:
            self.most_affected_city = None
        # Slice off just the top row_count records now
        if len(sorted_cities) > 5:
            sorted_cities = sorted_cities[0: row_count]
        return sorted_cities

    def write_html_table(self, file_name, table):
        """Write a Table object to disk with a standard header and footer.

        This is a helper function that allows you to easily write a table
        to disk with a standard header and footer. The header contains
        some inlined css markup for our mmi charts which will be ignored
        if you are not using the css classes it defines.

        The bootstrap.css file will also be written to the same directory
        where the table is written.

        :param file_name: file name (without full path) .e.g foo.html
        :type file_name: str

        :param table: A Table instance.
        :type table: Table

        :return: Full path to file that was created on disk.
        :rtype: str
        """
        path = os.path.join(shakemap_extract_dir(),
                            self.event_id,
                            file_name)
        html_file = file(path, 'w')
        header_file = os.path.join(data_dir(), 'header.html')
        footer_file = os.path.join(data_dir(), 'footer.html')
        header_file = file(header_file)
        header = header_file.read()
        header_file.close()
        footer_file = file(footer_file)
        footer = footer_file.read()
        footer_file.close()
        html_file.write(header)
        html_file.write(table.toNewlineFreeString())
        html_file.write(footer)
        html_file.close()
        # Also bootstrap gets copied to extract dir
        destination_path = os.path.join(
            shakemap_extract_dir(), self.event_id, 'bootstrap.css')
        source_path = os.path.join(data_dir(), 'bootstrap.css')
        shutil.copyfile(source_path, destination_path)

        return path

    def impacted_cities_table(self, row_count=5):
        """Return a table object of sorted impacted cities.

        :param row_count:optional maximum number of cities to show. Default
            is 5.

        The cities will be listed in the order computed by
        sorted_impacted_cities
        but will only list in the following format:

        +------+--------+-----------------+-----------+
        | Icon | Name   | People Affected | Intensity |
        +======+========+=================+===========+
        | img  | Padang |    2000         |    IV     +
        +------+--------+-----------------+-----------+

        .. note:: Population will be rounded pop / 1000

        The icon img will be an image with an icon showing the relevant colour.

        :returns:
            two tuple of:
                A Table object (see :func:`safe.impact_functions.tables.Table`)
                A file path to the html file saved to disk.

        :raise: Propagates any exceptions.
        """
        table_data = self.sorted_impacted_cities(row_count)
        table_body = []
        header = TableRow([
            '',
            self.tr('Name'),
            self.tr('Affected (x 1000)'),
            self.tr('Intensity')],
            header=True)
        for row_data in table_data:
            intensity = row_data['roman']
            name = row_data['name']
            population = int(round(row_data['population'] / 1000))
            colour = mmi_colour(row_data['mmi'])
            colour_box = (
                '<div style="width: 16px; height: 16px;'
                'background-color: %s"></div>' % colour)
            row = TableRow([
                colour_box,
                name,
                population,
                intensity])
            table_body.append(row)

        table = Table(
            table_body, header_row=header,
            table_class='table table-striped table-condensed')
        # Also make an html file on disk
        path = self.write_html_table(
            file_name='affected-cities.html', table=table)

        return table, path

    def impact_table(self):
        """Create the html listing affected people per mmi interval.

        Expects that calculate impacts has run and set pop affected etc.
        already.

        self.: A dictionary with keys mmi levels and values affected count
                as per the example below. This is typically going to be passed
                from the :func:`calculate_impacts` function defined below.


        :return: Full absolute path to the saved html content.
        :rtype: str

        Example:
                {2: 0.47386375223673427,
                3: 0.024892573693488258,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0}
        """
        header = [TableCell(self.tr('Intensity'), header=True)]
        affected_row = [
            TableCell(self.tr('People Affected (x 1000)'), header=True)]
        impact_row = [TableCell(self.tr('Perceived Shaking'), header=True)]
        for mmi in range(2, 10):
            header.append(
                TableCell(
                    romanise(mmi),
                    cell_class='mmi-%s' % mmi,
                    header=True))
            if mmi in self.affected_counts:
                # noinspection PyTypeChecker
                affected_row.append(
                    '%i' % round(self.affected_counts[mmi] / 1000))
            else:
                # noinspection PyTypeChecker
                affected_row.append(0.00)

            impact_row.append(TableCell(self.mmi_shaking(mmi)))

        table_body = list()
        table_body.append(affected_row)
        table_body.append(impact_row)
        table = Table(
            table_body, header_row=header,
            table_class='table table-striped table-condensed')
        # noinspection PyTypeChecker
        path = self.write_html_table(file_name='impacts.html', table=table)

        return path

    def calculate_impacts(
            self,
            population_raster_path=None,
            force_flag=False,
            algorithm='nearest'):
        """Use the SAFE ITB earthquake function to calculate impacts.

        :param population_raster_path: optional. see
                :func:`_get_population_path` for more details on how the path
                will be resolved if not explicitly given.
        :type population_raster_path: str

        :param force_flag: (Optional). Whether to force the
                regeneration of contour product. Defaults to False.
        :type force_flag: bool

        :param algorithm: (Optional) Which interpolation algorithm to
                use to create the underlying raster. see
                :func:`mmiToRasterData` for information about default
                behaviour
        :type algorithm: str

        :returns:
            str: the path to the computed impact file.
                The class members self.impact_file, self.fatality_counts,
                self.displaced_counts and self.affected_counts will be
                populated.
                self.*Counts are dicts containing fatality / displaced /
                affected counts for the shake events. Keys for the dict will be
                MMI classes (I-X) and values will be count type for that class.
            str: Path to the html report showing a table of affected people per
                mmi interval.
        """
        if (
                population_raster_path is None or (
                not os.path.isfile(population_raster_path) and not
                os.path.islink(population_raster_path))):

            exposure_path = self._get_population_path()
        else:
            exposure_path = population_raster_path

        hazard_path = self.shake_grid.mmi_to_raster(
            force_flag=force_flag,
            algorithm=algorithm)

        clipped_hazard, clipped_exposure = self.clip_layers(
            shake_raster_path=hazard_path,
            population_raster_path=exposure_path)

        clipped_hazard_layer = safe_read_layer(
            str(clipped_hazard.source()))
        clipped_exposure_layer = safe_read_layer(
            str(clipped_exposure.source()))
        layers = [clipped_hazard_layer, clipped_exposure_layer]

        function_id = 'I T B Fatality Function'
        function = safe_get_plugins(function_id)[0][function_id]

        result = safe_calculate_impact(layers, function)
        try:
            fatalities = result.keywords['fatalities_per_mmi']
            affected = result.keywords['exposed_per_mmi']
            displaced = result.keywords['displaced_per_mmi']
            total_fatalities = result.keywords['total_fatalities']
        except:
            LOGGER.exception(
                'Fatalities_per_mmi key not found in:\n%s' %
                result.keywords)
            raise
        # Copy the impact layer into our extract dir.
        tif_path = os.path.join(shakemap_extract_dir(),
                                self.event_id,
                                'impact-%s.tif' % algorithm)
        shutil.copyfile(result.filename, tif_path)
        LOGGER.debug('Copied impact result to:\n%s\n' % tif_path)
        # Copy the impact keywords layer into our extract dir.
        keywords_path = os.path.join(
            shakemap_extract_dir(),
            self.event_id,
            'impact-%s.keywords' % algorithm)
        keywords_source = os.path.splitext(result.filename)[0]
        keywords_source = '%s.keywords' % keywords_source
        shutil.copyfile(keywords_source, keywords_path)
        LOGGER.debug('Copied impact keywords to:\n%s\n' % keywords_path)

        self.impact_file = tif_path
        self.impact_keywords_file = keywords_path
        self.fatality_counts = fatalities
        self.fatality_total = total_fatalities
        self.displaced_counts = displaced
        self.affected_counts = affected
        LOGGER.info('***** Fatalities: %s ********' % self.fatality_counts)
        LOGGER.info('***** Displaced: %s ********' % self.displaced_counts)
        LOGGER.info('***** Affected: %s ********' % self.affected_counts)

        impact_table_path = self.impact_table()
        return self.impact_file, impact_table_path

    #noinspection PyMethodMayBeStatic
    def clip_layers(self, shake_raster_path, population_raster_path):
        """Clip population (exposure) layer to dimensions of shake data.

        It is possible (though unlikely) that the shake may be clipped too.

        :param shake_raster_path: Path to the shake raster.
        :type shake_raster_path: str

        :param population_raster_path: Path to the population raster.
        :type population_raster_path: str

        :return: Path to the clipped datasets (clipped shake, clipped pop).
        :rtype: tuple(str, str)

        :raise
            FileNotFoundError
        """
        # _ is a syntactical trick to ignore second returned value
        base_name, _ = os.path.splitext(shake_raster_path)
        hazard_layer = QgsRasterLayer(shake_raster_path, base_name)
        base_name, _ = os.path.splitext(population_raster_path)
        exposure_layer = QgsRasterLayer(population_raster_path, base_name)

        # Reproject all extents to EPSG:4326 if needed
        geo_crs = QgsCoordinateReferenceSystem()
        geo_crs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)

        # Get the Hazard extents as an array in EPSG:4326
        # Note that we will always clip to this extent regardless of
        # whether the exposure layer completely covers it. This differs
        # from safe_qgis which takes care to ensure that the two layers
        # have coincidental coverage before clipping. The
        # clipper function will take care to null padd any missing data.
        hazard_geo_extent = extent_to_geoarray(
            hazard_layer.extent(),
            hazard_layer.crs())

        # Next work out the ideal spatial resolution for rasters
        # in the analysis. If layers are not native WGS84, we estimate
        # this based on the geographic extents
        # rather than the layers native extents so that we can pass
        # the ideal WGS84 cell size and extents to the layer prep routines
        # and do all preprocessing in a single operation.
        # All this is done in the function getWGS84resolution
        extra_exposure_keywords = {}

        # Hazard layer is raster
        hazard_geo_cell_size = get_wgs84_resolution(hazard_layer)

        # In case of two raster layers establish common resolution
        exposure_geo_cell_size = get_wgs84_resolution(exposure_layer)

        if hazard_geo_cell_size < exposure_geo_cell_size:
            cell_size = hazard_geo_cell_size
        else:
            cell_size = exposure_geo_cell_size

        # Record native resolution to allow rescaling of exposure data
        if not numpy.allclose(cell_size, exposure_geo_cell_size):
            extra_exposure_keywords['resolution'] = exposure_geo_cell_size

        # The extents should already be correct but the cell size may need
        # resampling, so we pass the hazard layer to the clipper
        clipped_hazard = clip_layer(
            layer=hazard_layer,
            extent=hazard_geo_extent,
            cell_size=cell_size)

        clipped_exposure = clip_layer(
            layer=exposure_layer,
            extent=hazard_geo_extent,
            cell_size=cell_size,
            extra_keywords=extra_exposure_keywords)

        return clipped_hazard, clipped_exposure

    def _get_sqlite_path(self):
        """Helper to determine sqlite file with geonames places in it.

        The following priority will be used to determine the path:
            1) the class attribute self.geonames_sqlite_path
               will be checked and if not None and the file exists it will be
               used.
            2) the environment variable 'GEONAMES_SQLITE_PATH' will be
               checked and if the file exists if set it will be used.
            4) A hard coded path of
               :file:`/fixtures/indonesia.sqlite` will be appended
               to os.path.abspath(os.path.curdir)
            5) A hard coded path of
               :file:`/usr/local/share/inasafe/indonesia.tif`
               will be used.

        :returns: Path to a geonames sqlite file.
        :rtype: str

        :raises: FileNotFoundError
        """
        # When used via the scripts make_shakemap.sh
        fixture_path = os.path.join(
            data_dir(), 'indonesia.sqlite')

        local_path = '/usr/local/share/inasafe/indonesia.sqlite'
        if self.geonames_sqlite_path is not None:
            if os.path.exists(self.geonames_sqlite_path):
                return self.geonames_sqlite_path

        if 'GEONAMES_SQLITE_PATH' in os.environ:
            population_path = os.environ['GEONAMES_SQLITE_PATH']
            if os.path.exists(population_path):
                return population_path

        if os.path.exists(fixture_path):
            return fixture_path

        if os.path.exists(local_path):
            return local_path

        raise FileNotFoundError('Geonames sqlite file could not be found')

    def _get_population_path(self):
        """Helper to determine population raster's path.

        The following priority will be used to determine the path:
            1) the class attribute self.population_raster_path
               will be checked and if not None and the file exists it will be
               used.
            2) the environment variable 'INASAFE_POPULATION_PATH' will be
               checked and if the file exists if set it will be used.
            4) A hard coded path of
               :file:`/fixtures/exposure/population.tif` will be appended
               to os.path.abspath(os.path.curdir)
            5) A hard coded path of
               :file:`/usr/local/share/inasafe/exposure/population.tif`
               will be used.

        :return: path to a population raster file.
        :rtype: str

        :raises: FileNotFoundError

        TODO: Consider automatically fetching from
        http://web.clas.ufl.edu/users/atatem/pub/IDN.7z

        Also see http://web.clas.ufl.edu/users/atatem/pub/
        https://github.com/AIFDR/inasafe/issues/381
        """
        # When used via the scripts make_shakemap.sh
        fixture_path = os.path.join(
            data_dir(), 'exposure', 'population.tif')

        local_path = '/usr/local/share/inasafe/exposure/population.tif'
        if self.population_raster_path is not None:
            if os.path.exists(self.population_raster_path):
                return self.population_raster_path

        if 'INASAFE_POPULATION_PATH' in os.environ:
            population_path = os.environ['INASAFE_POPULATION_PATH']
            if os.path.exists(population_path):
                return population_path

        if os.path.exists(fixture_path):
            return fixture_path

        if os.path.exists(local_path):
            return local_path

        raise FileNotFoundError('Population file could not be found')

    def render_map(self, force_flag=False):
        """This is the 'do it all' method to render a pdf.

        :param force_flag: (Optional). Whether to force the
                regeneration of map product. Defaults to False.
        :type force_flag: bool

        :raise Propagates any exceptions.
        """
        pdf_path = os.path.join(
            shakemap_extract_dir(),
            self.event_id,
            '%s-%s.pdf' % (self.event_id, self.locale))
        image_path = os.path.join(
            shakemap_extract_dir(),
            self.event_id,
            '%s-%s.png' % (self.event_id, self.locale))
        thumbnail_image_path = os.path.join(
            shakemap_extract_dir(),
            self.event_id,
            '%s-thumb-%s.png' % (
            self.event_id, self.locale))
        pickle_path = os.path.join(
            shakemap_extract_dir(),
            self.event_id,
            '%s-metadata-%s.pickle' % (self.event_id, self.locale))

        if not force_flag:
            # Check if the images already exist and if so
            # short circuit.
            short_circuit_flag = True
            if not os.path.exists(pdf_path):
                short_circuit_flag = False
            if not os.path.exists(image_path):
                short_circuit_flag = False
            if not os.path.exists(thumbnail_image_path):
                short_circuit_flag = False
            if short_circuit_flag:
                LOGGER.info('%s (already exists)' % pdf_path)
                LOGGER.info('%s (already exists)' % image_path)
                LOGGER.info('%s (already exists)' % thumbnail_image_path)
                return pdf_path

        # Make sure the map layers have all been removed before we
        # start otherwise in batch mode we will get overdraws.
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().removeAllMapLayers()

        mmi_shape_file = self.shake_grid.mmi_to_shapefile(
            force_flag=force_flag)
        logging.info('Created: %s', mmi_shape_file)
        cities_html_path = None
        cities_shape_file = None

        # 'average', 'invdist', 'nearest' - currently only nearest works
        algorithm = 'nearest'
        try:
            contours_shapefile = self.shake_grid.mmi_to_contours(
                force_flag=force_flag,
                algorithm=algorithm)
        except:
            raise
        logging.info('Created: %s', contours_shapefile)
        #noinspection PyBroadException
        try:
            cities_shape_file = self.cities_to_shapefile(
                force_flag=force_flag)
            logging.info('Created: %s', cities_shape_file)
            search_box_file = self.city_search_boxes_to_shapefile(
                force_flag=force_flag)
            logging.info('Created: %s', search_box_file)
            _, cities_html_path = self.impacted_cities_table()
            logging.info('Created: %s', cities_html_path)
        except:  # pylint: disable=W0702
            logging.exception('No nearby cities found!')

        _, impacts_html_path = self.calculate_impacts()
        logging.info('Created: %s', impacts_html_path)

        # Load our project
        if 'INSAFE_REALTIME_PROJECT' in os.environ:
            project_path = os.environ['INSAFE_REALTIME_PROJECT']
        else:
            project_path = os.path.join(data_dir(), 'realtime.qgs')
        # noinspection PyArgumentList
        QgsProject.instance().setFileName(project_path)
        # noinspection PyArgumentList
        QgsProject.instance().read()

        # Load the contours and cities shapefile into the map
        layers_to_add = []
        contours_layer = QgsVectorLayer(
            contours_shapefile,
            'mmi-contours', 'ogr')
        layers_to_add.append(contours_layer)

        if cities_shape_file is not None:
            cities_layer = QgsVectorLayer(
                cities_shape_file,
                'mmi-cities', "ogr")
            if cities_layer.isValid():
                # noinspection PyArgumentList
                layers_to_add.append(cities_layer)
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayers(layers_to_add)

        # Load our template
        if 'INSAFE_REALTIME_TEMPLATE' in os.environ:
            template_path = os.environ['INSAFE_REALTIME_TEMPLATE']
        else:
            template_path = os.path.join(data_dir(), 'realtime-template.qpt')

        template_file = file(template_path)
        template_content = template_file.read()
        template_file.close()
        document = QDomDocument()
        document.setContent(template_content)

        # Set up the map renderer that will be assigned to the composition
        map_renderer = CANVAS.mapRenderer()
        # Set the labelling engine for the canvas
        labelling_engine = QgsPalLabeling()
        map_renderer.setLabelingEngine(labelling_engine)

        # Enable on the fly CRS transformations
        map_renderer.setProjectionsEnabled(False)
        # Now set up the composition
        composition = QgsComposition(map_renderer)

        # You can use this to replace any string like this [key]
        # in the template with a new value. e.g. to replace
        # [date] pass a map like this {'date': '1 Jan 2012'}
        location_info = self.event_info()
        LOGGER.debug(location_info)
        substitution_map = {
            'location-info': location_info,
            'version': self.version()}
        substitution_map.update(self.event_dict())
        LOGGER.debug(substitution_map)

        # Pickle substitution map
        pickle_file = file(pickle_path, 'w')
        pickle.dump(substitution_map, pickle_file)
        pickle_file.close()

        result = composition.loadFromTemplate(document, substitution_map)
        if not result:
            LOGGER.exception(
                'Error loading template %s with keywords\n %s',
                template_path, substitution_map)
            raise MapComposerError

        # Get the main map canvas on the composition and set
        # its extents to the event.
        map_canvas = composition.getComposerItemById('main-map')
        if map_canvas is not None:
            map_canvas.setNewExtent(self.extent_with_cities)
            map_canvas.renderModeUpdateCachedImage()
        else:
            LOGGER.exception('Map 0 could not be found in template %s',
                             template_path)
            raise MapComposerError

        # Set the impacts report up
        impacts_item = composition.getComposerItemById(
            'impacts-table')
        if impacts_item is None:
            message = 'impacts-table composer item could not be found'
            LOGGER.exception(message)
            raise MapComposerError(message)
        impacts_html = composition.getComposerHtmlByItem(
            impacts_item)
        if impacts_html is None:
            message = 'Impacts QgsComposerHtml could not be found'
            LOGGER.exception(message)
            raise MapComposerError(message)
        impacts_html.setUrl(QUrl(impacts_html_path))

        # Set the affected cities report up
        cities_item = composition.getComposerItemById('affected-cities')
        if cities_item is None:
            message = 'affected-cities composer item could not be found'
            LOGGER.exception(message)
            raise MapComposerError(message)
        cities_html = composition.getComposerHtmlByItem(cities_item)
        if cities_html is None:
            message = 'Cities QgsComposerHtml could not be found'
            LOGGER.exception(message)
            raise MapComposerError(message)

        if cities_html_path is not None:
            cities_html.setUrl(QUrl(cities_html_path))
        else:
            # We used to raise an error here but it is actually feasible that
            # no nearby cities with a valid mmi value are found - e.g.
            # if the event is way out in the ocean.
            LOGGER.info('No nearby cities found.')

        # Save a pdf.
        composition.exportAsPDF(pdf_path)
        LOGGER.info('Generated PDF: %s' % pdf_path)
        # Save a png
        page_number = 0
        image = composition.printPageAsRaster(page_number)
        image.save(image_path)
        LOGGER.info('Generated Image: %s' % image_path)
        # Save a thumbnail
        size = QSize(200, 200)
        thumbnail_image = image.scaled(
            size, Qt.KeepAspectRatioByExpanding)
        thumbnail_image.save(thumbnail_image_path)
        LOGGER.info('Generated Thumbnail: %s' % thumbnail_image_path)

        # Save a QGIS Composer template that you can open in QGIS
        template_document = QDomDocument()
        element = template_document.createElement('Composer')
        composition.writeXML(
            element, template_document)
        template_document.appendChild(element)
        template_path = os.path.join(
            shakemap_extract_dir(),
            self.event_id,
            'composer-template.qpt')
        template_file = file(template_path, 'w')
        template_file.write(template_document.toByteArray())
        template_file.close()

        # Save a QGIS project that you can open in QGIS
        # noinspection PyArgumentList
        project = QgsProject.instance()
        project_path = os.path.join(
            shakemap_extract_dir(),
            self.event_id,
            'project.qgs')
        project.write(QFileInfo(project_path))

    #noinspection PyMethodMayBeStatic
    def bearing_to_cardinal(self, bearing):
        """Given a bearing in degrees return it as compass units e.g. SSE.

        :param bearing: theBearing float (required)

        :return: Compass bearing derived from theBearing or None if
            theBearing is None or can not be resolved to a float.
        :rtype: str

        .. note:: This method is heavily based on http://hoegners.de/Maxi/geo/
           which is licensed under the GPL V3.
        """
        direction_list = [
            'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE',
            'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW',
            'NW', 'NNW']
        try:
            bearing = float(bearing)
        except ValueError:
            LOGGER.exception('Error casting bearing to a float')
            return None

        directions_count = len(direction_list)
        directions_interval = 360. / directions_count
        index = int(round(bearing / directions_interval))
        index %= directions_count
        return direction_list[index]

    def event_info(self):
        """Get a short paragraph describing the event.

        :return: A string describing the event e.g.
            'M 5.0 26-7-2012 2:15:35 Latitude: 0°12'36.00"S
            Longitude: 124°27'0.00"E Depth: 11.0km
            Located 2.50km SSW of Tondano'
        :rtype: str
        """
        event_dict = self.event_dict()
        event_string = (
            'M %(mmi)s %(date)s %(time)s '
            '%(latitude-name)s: %(latitude-value)s '
            '%(longitude-name)s: %(longitude-value)s '
            '%(depth-name)s: %(depth-value)s%(depth-unit)s '
            '%(located-label)s %(distance)s%(distance-unit)s '
            '%(bearing-compass)s '
            '%(direction-relation)s %(place-name)s') % event_dict
        return event_string

    def event_dict(self):
        """Get a dict of key value pairs that describe the event.

        :return: key-value pairs describing the event.
        :rtype: dict

        :raises: Propagates any exceptions
        """
        map_name = self.tr('Estimated Earthquake Impact')
        exposure_table_name = self.tr(
            'Estimated number of people affected by each MMI level')
        fatalities_name = self.tr('Estimated fatalities')
        fatalities_count = self.fatality_total

        # put the estimate into neat ranges 0-100, 100-1000, 1000-10000. etc
        lower_limit = 0
        upper_limit = 100
        while fatalities_count > upper_limit:
            lower_limit = upper_limit
            upper_limit = math.pow(upper_limit, 2)
        fatalities_range = '%i - %i' % (lower_limit, upper_limit)

        city_table_name = self.tr('Places Affected')
        legend_name = self.tr('Population density')
        limitations = self.tr(
            'This impact estimation is automatically generated and only takes'
            ' into account the population and cities affected by different '
            'levels of ground shaking. The estimate is based on ground '
            'shaking data from BMKG, population density data from asiapop'
            '.org, place information from geonames.org and software developed'
            ' by BNPB. Limitations in the estimates of ground shaking, '
            'population  data and place names datasets may result in '
            'significant misrepresentation of the on-the-ground situation in '
            'the figures shown here. Consequently decisions should not be '
            'made solely on the information presented here and should always '
            'be verified by ground truthing and other reliable information '
            'sources. The fatality calculation assumes that '
            'no fatalities occur for shake levels below MMI 4. Fatality '
            'counts of less than 50 are disregarded.')
        software_tag = self.tr(
            'This report was created using InaSAFE version %s. Visit '
            'http://inasafe.org for more information.') % get_version()
        credits_text = self.tr(
            'Supported by the Australia-Indonesia Facility for Disaster '
            'Reduction, Geoscience Australia and the World Bank-GFDRR.')
        #Format the lat lon from decimal degrees to dms
        point = QgsPoint(
            self.shake_grid.longitude,
            self.shake_grid.latitude)
        coordinates = point.toDegreesMinutesSeconds(2)
        tokens = coordinates.split(',')
        longitude = tokens[0]
        latitude = tokens[1]
        km_text = self.tr('km')
        directionality_text = self.tr('of')
        bearing_text = self.tr('bearing')
        LOGGER.debug(longitude)
        LOGGER.debug(latitude)
        if self.most_affected_city is None:
            # Check why we have this line - perhaps setting class state?
            self.sorted_impacted_cities()
            direction = 0
            distance = 0
            key_city_name = self.tr('n/a')
            bearing = self.tr('n/a')
        else:
            direction = self.most_affected_city['dir_to']
            distance = self.most_affected_city['dist_to']
            key_city_name = self.most_affected_city['name']
            bearing = self.bearing_to_cardinal(direction)

        elapsed_time_text = self.tr('Elapsed time since event')
        elapsed_time = self.elapsed_time()[1]
        degree_symbol = '\xb0'
        event_dict = {
            'map-name': map_name,
            'exposure-table-name': exposure_table_name,
            'city-table-name': city_table_name,
            'legend-name': legend_name,
            'limitations': limitations,
            'software-tag': software_tag,
            'credits': credits_text,
            'fatalities-name': fatalities_name,
            'fatalities-range': fatalities_range,
            'fatalities-count': '%s' % fatalities_count,
            'mmi': '%s' % self.shake_grid.magnitude,
            'date': '%s-%s-%s' % (
                self.shake_grid.day,
                self.shake_grid.month,
                self.shake_grid.year),
            'time': '%s:%s:%s' % (
                self.shake_grid.hour,
                self.shake_grid.minute,
                self.shake_grid.second),
            'formatted-date-time': self.elapsed_time()[0],
            'latitude-name': self.tr('Latitude'),
            'latitude-value': '%s' % latitude,
            'longitude-name': self.tr('Longitude'),
            'longitude-value': '%s' % longitude,
            'depth-name': self.tr('Depth'),
            'depth-value': '%s' % self.shake_grid.depth,
            'depth-unit': km_text,
            'located-label': self.tr('Located'),
            'distance': '%.2f' % distance,
            'distance-unit': km_text,
            'direction-relation': directionality_text,
            'bearing-degrees': '%.2f%s' % (direction, degree_symbol),
            'bearing-compass': '%s' % bearing,
            'bearing-text': bearing_text,
            'place-name': key_city_name,
            'elapsed-time-name': elapsed_time_text,
            'elapsed-time': elapsed_time
        }
        return event_dict

    def elapsed_time(self):
        """Calculate how much time has elapsed since the event.

        :return: local formatted date
        :rtype: str

        :raises: None

        .. note:: Code based on Ole's original impact_map work.
        """
        # Work out interval since earthquake (assume both are GMT)
        year = self.shake_grid.year
        month = self.shake_grid.month
        day = self.shake_grid.day
        hour = self.shake_grid.hour
        minute = self.shake_grid.minute
        second = self.shake_grid.second

        eq_date = datetime(year, month, day, hour, minute, second)

        # Hack - remove when ticket:10 has been resolved
        tz = pytz.timezone('Asia/Jakarta')  # Or 'Etc/GMT+7'
        now = datetime.utcnow()
        now_jakarta = now.replace(tzinfo=pytz.utc).astimezone(tz)
        eq_jakarta = eq_date.replace(tzinfo=tz).astimezone(tz)
        time_delta = now_jakarta - eq_jakarta

        # Work out string to report time elapsed after quake
        if time_delta.days == 0:
            # This is within the first day after the quake
            hours = int(time_delta.seconds / 3600)
            minutes = int((time_delta.seconds % 3600) / 60)

            if hours == 0:
                lapse_string = '%i %s' % (minutes, self.tr('minute(s)'))
            else:
                lapse_string = '%i %s %i %s' % (
                    hours,
                    self.tr('hour(s)'),
                    minutes,
                    self.tr('minute(s)'))
        else:
            # This at least one day after the quake

            weeks = int(time_delta.days / 7)
            days = int(time_delta.days % 7)

            if weeks == 0:
                lapse_string = '%i %s' % (days, self.tr('days'))
            else:
                lapse_string = '%i %s %i %s' % (
                    weeks,
                    self.tr('weeks'),
                    days,
                    self.tr('days'))

        # Convert date to GMT+7
        # FIXME (Ole) Hack - Remove this as the shakemap data always
        # reports the time in GMT+7 but the timezone as GMT.
        # This is the topic of ticket:10
        #tz = pytz.timezone('Asia/Jakarta')  # Or 'Etc/GMT+7'
        #eq_date_jakarta = eq_date.replace(tzinfo=pytz.utc).astimezone(tz)
        eq_date_jakarta = eq_date

        # The character %b will use the local word for month
        # However, setting the locale explicitly to test, does not work.
        #locale.setlocale(locale.LC_TIME, 'id_ID')

        date_str = eq_date_jakarta.strftime('%d-%b-%y %H:%M:%S %Z')
        return date_str, lapse_string

    def version(self):
        """Return a string showing the version of Inasafe.

        Args: None

        Returns: str
        """
        return self.tr('Version: %s' % get_version())

    def __str__(self):
        """The unicode representation for an event object's state.

        :return: A string describing the ShakeGridConverter instance
        :rtype: str

        :raises: None
        """
        if self.extent_with_cities is not None:
            # noinspection PyUnresolvedReferences
            extent_with_cities = self.extent_with_cities.asWktPolygon()
        else:
            extent_with_cities = 'Not set'

        if self.shake_grid.mmi_data:
            mmi_data = 'Populated'
        else:
            mmi_data = 'Not populated'

        event_dict = {
            'latitude': self.shake_grid.latitude,
            'longitude': self.shake_grid.longitude,
            'event_id': self.event_id,
            'magnitude': self.shake_grid.magnitude,
            'depth': self.shake_grid.depth,
            'description': self.shake_grid.description,
            'location': self.shake_grid.location,
            'day': self.shake_grid.day,
            'month': self.shake_grid.month,
            'year': self.shake_grid.year,
            'time': self.shake_grid.time,
            'time_zone': self.shake_grid.time_zone,
            'x_minimum': self.shake_grid.x_minimum,
            'x_maximum': self.shake_grid.x_maximum,
            'y_minimum': self.shake_grid.y_minimum,
            'y_maximum': self.shake_grid.y_maximum,
            'rows': self.shake_grid.rows,
            'columns': self.shake_grid.columns,
            'mmi_data': mmi_data,
            'population_raster_path': self.population_raster_path,
            'impact_file': self.impact_file,
            'impact_keywords_file': self.impact_keywords_file,
            'fatality_counts': self.fatality_counts,
            'displaced_counts': self.displaced_counts,
            'affected_counts': self.affected_counts,
            'extent_with_cities': extent_with_cities,
            'zoom_factor': self.zoom_factor,
            'search_boxes': self.search_boxes}

        event_string = (
            'latitude: %(latitude)s\n'
            'longitude: %(longitude)s\n'
            'event_id: %(event_id)s\n'
            'magnitude: %(magnitude)s\n'
            'depth: %(depth)s\n'
            'description: %(description)s\n'
            'location: %(location)s\n'
            'day: %(day)s\n'
            'month: %(month)s\n'
            'year: %(year)s\n'
            'time: %(time)s\n'
            'time_zone: %(time_zone)s\n'
            'x_minimum: %(x_minimum)s\n'
            'x_maximum: %(x_maximum)s\n'
            'y_minimum: %(y_minimum)s\n'
            'y_maximum: %(y_maximum)s\n'
            'rows: %(rows)s\n'
            'columns: %(columns)s\n'
            'mmi_data: %(mmi_data)s\n'
            'population_raster_path: %(population_raster_path)s\n'
            'impact_file: %(impact_file)s\n'
            'impact_keywords_file: %(impact_keywords_file)s\n'
            'fatality_counts: %(fatality_counts)s\n'
            'displaced_counts: %(displaced_counts)s\n'
            'affected_counts: %(affected_counts)s\n'
            'extent_with_cities: %(extent_with_cities)s\n'
            'zoom_factor: %(zoom_factor)s\n'
            'search_boxes: %(search_boxes)s\n'
            % event_dict)
        return event_string

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
        # Also set the system locale to the user overridden local
        # so that the inasafe library functions gettext will work
        # .. see:: :py:func:`common.utilities`
        os.environ['LANG'] = str(locale_name)

        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        translation_path = os.path.join(
            root, 'safe_qgis', 'i18n',
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
