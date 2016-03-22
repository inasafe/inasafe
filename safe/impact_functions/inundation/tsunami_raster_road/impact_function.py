# coding=utf-8
"""Impact of flood on roads."""
from collections import OrderedDict

from qgis.core import (
    QGis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsGeometry,
    QgsPoint,
    QgsRectangle,
    QgsSpatialIndex,
    QgsVectorFileWriter,
    QgsVectorLayer
)
from PyQt4.QtCore import QVariant

from safe.common.exceptions import ZeroImpactException
from safe.impact_functions.bases.continuous_rh_classified_ve import \
    ContinuousRHClassifiedVE
from safe.impact_functions.inundation.tsunami_raster_road\
    .metadata_definitions import TsunamiRasterRoadMetadata
from safe.utilities.i18n import tr
from safe.utilities.gis import (
    raster_to_vector_cells,
    intersect_lines_with_vector_cells)
from safe.storage.vector import Vector
from safe.common.utilities import get_utm_epsg, unique_filename
from safe.gis.qgis_raster_tools import clip_raster
from safe.gis.qgis_vector_tools import (
    extent_to_geo_array,
    create_layer)
from safe.impact_reports.road_exposure_report_mixin import\
    RoadExposureReportMixin
import safe.messaging as m
from safe.messaging import styles

__author__ = 'etiennetrimaille'
__project_name__ = 'inasafe-dev'
__filename__ = 'impact_function.py'
__date__ = '11/03/16'
__copyright__ = 'etienne@kartoza.com'


class TsunamiRasterRoadsFunction(
        ContinuousRHClassifiedVE,
        RoadExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Simple impact function for tsunami on roads."""
    _metadata = TsunamiRasterRoadMetadata()

    def __init__(self):
        """Constructor."""
        super(TsunamiRasterRoadsFunction, self).__init__()
        RoadExposureReportMixin.__init__(self)
        self.add_unaffected_column = False
        self.hazard_classes = [
            tr('Dry Zone'),
            tr('Low Hazard Zone'),
            tr('Medium Hazard Zone'),
            tr('High Hazard Zone'),
            tr('Very High Hazard Zone'),
        ]

    def notes(self):
        """Return the notes section of the report.

        :return: The notes that should be attached to this impact report.
        :rtype: safe.messaging.Message
        """
        message = m.Message(style_class='container')
        message.add(
            m.Heading(tr('Notes and assumptions'), **styles.INFO_STYLE))
        checklist = m.BulletedList()

        # Thresholds for tsunami hazard zone breakdown.
        low_max = self.parameters['low_threshold']
        medium_max = self.parameters['medium_threshold']
        high_max = self.parameters['high_threshold']

        checklist.add(tr(
            'Dry zone is defined as non-inundated area or has inundation '
            'depth is 0 %s') % low_max.unit.abbreviation
        )

        checklist.add(tr(
            'Low tsunami hazard zone is defined as inundation depth is more '
            'than 0 %s but less than %.1f %s') % (
            low_max.unit.abbreviation,
            low_max.value,
            low_max.unit.abbreviation)
        )
        checklist.add(tr(
            'Moderate tsunami hazard zone is defined as inundation depth is '
            'more than %.1f %s but less than %.1f %s') % (
            low_max.value,
            low_max.unit.abbreviation,
            medium_max.value,
            medium_max.unit.abbreviation)
        )
        checklist.add(tr(
            'High tsunami hazard zone is defined as inundation depth is '
            'more than %.1f %s but less than %.1f %s') % (
            medium_max.value,
            medium_max.unit.abbreviation,
            high_max.value,
            high_max.unit.abbreviation)
        )
        checklist.add(tr(
            'Very high tsunami hazard zone is defined as inundation depth is '
            'more than %.1f %s') % (
            high_max.value, high_max.unit.abbreviation))

        checklist.add(tr(
            'Roads are closed if they are in low, moderate, high, or very '
            'high tsunami hazard zone.'))
        checklist.add(tr(
            'Roads are opened if they are in dry zone.'))
        message.add(checklist)
        return message

    def run(self):
        """Run the impact function.

        :returns: A new line layer with inundated roads marked.
        :type: safe_layer
        """
        self.validate()
        self.prepare()

        self.provenance.append_step(
            'Calculating Step',
            'Impact function is calculating the impact.')

        # Thresholds for tsunami hazard zone breakdown.
        low_max = self.parameters['low_threshold'].value
        medium_max = self.parameters['medium_threshold'].value
        high_max = self.parameters['high_threshold'].value

        target_field = self.target_field
        # Get parameters from layer's keywords
        road_class_field = self.exposure.keyword('road_class_field')

        # reproject self.extent to the hazard projection
        hazard_crs = self.hazard.layer.crs()
        hazard_authid = hazard_crs.authid()

        if hazard_authid == 'EPSG:4326':
            viewport_extent = self.requested_extent
        else:
            geo_crs = QgsCoordinateReferenceSystem()
            geo_crs.createFromSrid(4326)
            viewport_extent = extent_to_geo_array(
                QgsRectangle(*self.requested_extent), geo_crs, hazard_crs)

        # Align raster extent and viewport
        # assuming they are both in the same projection
        raster_extent = self.hazard.layer.dataProvider().extent()
        clip_xmin = raster_extent.xMinimum()
        # clip_xmax = raster_extent.xMaximum()
        clip_ymin = raster_extent.yMinimum()
        # clip_ymax = raster_extent.yMaximum()
        if viewport_extent[0] > clip_xmin:
            clip_xmin = viewport_extent[0]
        if viewport_extent[1] > clip_ymin:
            clip_ymin = viewport_extent[1]

        height = ((viewport_extent[3] - viewport_extent[1]) /
                  self.hazard.layer.rasterUnitsPerPixelY())
        height = int(height)
        width = ((viewport_extent[2] - viewport_extent[0]) /
                 self.hazard.layer.rasterUnitsPerPixelX())
        width = int(width)

        raster_extent = self.hazard.layer.dataProvider().extent()
        xmin = raster_extent.xMinimum()
        xmax = raster_extent.xMaximum()
        ymin = raster_extent.yMinimum()
        ymax = raster_extent.yMaximum()

        x_delta = (xmax - xmin) / self.hazard.layer.width()
        x = xmin
        for i in range(self.hazard.layer.width()):
            if abs(x - clip_xmin) < x_delta:
                # We have found the aligned raster boundary
                break
            x += x_delta
            _ = i

        y_delta = (ymax - ymin) / self.hazard.layer.height()
        y = ymin
        for i in range(self.hazard.layer.width()):
            if abs(y - clip_ymin) < y_delta:
                # We have found the aligned raster boundary
                break
            y += y_delta
        clip_extent = [x, y, x + width * x_delta, y + height * y_delta]

        # Clip hazard raster
        small_raster = clip_raster(
            self.hazard.layer, width, height, QgsRectangle(*clip_extent))

        # Create vector features from the flood raster
        # For each raster cell there is one rectangular polygon
        # Data also get spatially indexed for faster operation
        ranges = OrderedDict()
        ranges[0] = [0.0, 0.0]
        ranges[1] = [0.0, low_max]
        ranges[2] = [low_max, medium_max]
        ranges[3] = [medium_max, high_max]
        ranges[4] = [high_max, None]

        index, flood_cells_map = raster_to_vector_cells(
            small_raster,
            ranges,
            self.exposure.layer.crs())

        # Filter geometry and data using the extent
        ct = QgsCoordinateTransform(
            QgsCoordinateReferenceSystem("EPSG:4326"),
            self.exposure.layer.crs())
        extent = ct.transformBoundingBox(QgsRectangle(*self.requested_extent))
        request = QgsFeatureRequest()
        request.setFilterRect(extent)

        # create template for the output layer
        line_layer_tmp = create_layer(self.exposure.layer)
        new_field = QgsField(target_field, QVariant.Int)
        line_layer_tmp.dataProvider().addAttributes([new_field])
        line_layer_tmp.updateFields()

        # create empty output layer and load it
        filename = unique_filename(suffix='.shp')
        QgsVectorFileWriter.writeAsVectorFormat(
            line_layer_tmp, filename, "utf-8", None, "ESRI Shapefile")
        line_layer = QgsVectorLayer(filename, "flooded roads", "ogr")

        # Do the heavy work - for each road get flood polygon for that area and
        # do the intersection/difference to find out which parts are flooded
        intersect_lines_with_vector_cells(
            self.exposure.layer,
            request,
            index,
            flood_cells_map,
            line_layer,
            target_field)

        target_field_index = line_layer.dataProvider().\
            fieldNameIndex(target_field)

        # Generate simple impact report
        epsg = get_utm_epsg(self.requested_extent[0], self.requested_extent[1])
        output_crs = QgsCoordinateReferenceSystem(epsg)
        transform = QgsCoordinateTransform(
            self.exposure.layer.crs(), output_crs)

        # Roads breakdown
        self.road_lengths = OrderedDict()
        self.affected_road_categories = self.hazard_classes
        # Impacted roads breakdown
        self.affected_road_lengths = OrderedDict([
            (self.hazard_classes[0], {}),
            (self.hazard_classes[1], {}),
            (self.hazard_classes[2], {}),
            (self.hazard_classes[3], {}),
            (self.hazard_classes[4], {}),
        ])

        if line_layer.featureCount() < 1:
            raise ZeroImpactException()

        roads_data = line_layer.getFeatures()
        road_type_field_index = line_layer.fieldNameIndex(road_class_field)
        for road in roads_data:
            attributes = road.attributes()
            affected = attributes[target_field_index]
            hazard_zone = self.hazard_classes[affected]
            road_type = attributes[road_type_field_index]
            if road_type.__class__.__name__ == 'QPyNullVariant':
                road_type = tr('Other')
            geom = road.geometry()
            geom.transform(transform)
            length = geom.length()

            if road_type not in self.road_lengths:
                self.road_lengths[road_type] = 0

            if hazard_zone not in self.affected_road_lengths:
                self.affected_road_lengths[hazard_zone] = {}

            if road_type not in self.affected_road_lengths[hazard_zone]:
                self.affected_road_lengths[hazard_zone][road_type] = 0

            self.road_lengths[road_type] += length
            num_classes = len(self.hazard_classes)
            if attributes[target_field_index] in range(num_classes):
                self.affected_road_lengths[hazard_zone][road_type] += length

        impact_summary = self.html_report()

        # For printing map purpose
        map_title = tr('Roads inundated')
        legend_title = tr('Road inundated status')

        style_classes = [
            # FIXME 0 - 0.1
            dict(
                label=self.hazard_classes[0] + ': 0m',
                value=0,
                colour='#00FF00',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[1] + ': <0 - %.1f m' % low_max,
                value=1,
                colour='#FFFF00',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[2] + ': %.1f - %.1f m' % (
                    low_max + 0.1, medium_max),
                value=2,
                colour='#FFB700',
                transparency=0,
                size=1
            ),
            dict(
                label=self.hazard_classes[3] + ': %.1f - %.1f m' % (
                    medium_max + 0.1, high_max),
                value=3,
                colour='#FF6F00',
                transparency=0,
                size=1
            ),

            dict(
                label=self.hazard_classes[4] + ' > %.1f m' % high_max,
                value=4,
                colour='#FF0000',
                transparency=0,
                size=1
            ),
        ]
        style_info = dict(
            target_field=target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')

        extra_keywords = {
            'impact_summary': impact_summary,
            'map_title': map_title,
            'legend_title': legend_title,
            'target_field': target_field
        }

        self.set_if_provenance()

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Convert QgsVectorLayer to inasafe layer and return it
        line_layer = Vector(
            data=line_layer,
            name=tr('Flooded roads'),
            keywords=impact_layer_keywords,
            style_info=style_info)
        self._impact = line_layer
        return line_layer
