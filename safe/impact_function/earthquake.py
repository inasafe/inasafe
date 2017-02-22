# coding=utf-8

"""Earthquake functions."""

import logging

from qgis.core import (
    QGis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsVectorFileWriter,
)

from safe.definitions.fields import (
    aggregation_id_field,
    population_count_field,
    fatalities_field,
    displaced_field,
    population_exposed_per_mmi_field,
    population_displaced_per_mmi,
    fatalities_per_mmi_field,
)
from safe.definitions.layer_purposes import (
    layer_purpose_aggregation_impacted, layer_purpose_exposure_impacted)
from safe.definitions.earthquake import displacement_rate
from safe.definitions.processing_steps import earthquake_displaced
from safe.gis.vector.tools import create_field_from_definition
from safe.gis.raster.write_raster import array_to_raster, make_array
from safe.common.utilities import unique_filename
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


@profile
def exposed_people_stats(hazard, exposure, aggregation, fatality_rate):
    """Calculate the number of exposed people per MMI level per aggregation.

    Calculate the number of exposed people per MMI level per aggregation zone
    and prepare raster layer outputs.

    :param hazard: The earthquake raster layer.
    :type hazard: QgsRasterLayer

    :param exposure: The population raster layer.
    :type exposure: QgsVectorLayer

    :param aggregation: The aggregation layer.
    :type aggregation: QgsVectorLayer

    :param fatality_rate: The fatality rate to use.
    :type fatality_rate: function

    :return: A tuble with the exposed per MMI level par aggregation
        and the exposed raster.
        Tuple (mmi, agg_zone), value: number of exposed people
    :rtype: (dict, QgsRasterLayer)
    """
    output_layer_name = earthquake_displaced['output_layer_name']
    processing_step = earthquake_displaced['step_name']
    exposed_raster_filename = unique_filename(
        prefix=output_layer_name, suffix='.tif')

    hazard_provider = hazard.dataProvider()
    extent = hazard.extent()
    width, height = hazard_provider.xSize(), hazard_provider.ySize()
    hazard_block = hazard_provider.block(1, extent, width, height)

    exposure_provider = exposure.dataProvider()
    exposure_block = exposure_provider.block(1, extent, width, height)

    agg_provider = aggregation.dataProvider()
    agg_block = agg_provider.block(1, extent, width, height)

    exposed = {}  # key: tuple (mmi, agg_zone), value: number of exposed people

    exposed_array = make_array(width, height)

    # walk through the rasters pixel by pixel and aggregate numbers
    # of people in the combination of hazard zones and aggregation zones
    for i in xrange(width * height):
        hazard_mmi = hazard_block.value(long(i))
        people_count = exposure_block.value(long(i))

        if hazard_mmi >= 2.0 and people_count >= 0.0:
            hazard_mmi = int(round(hazard_mmi))
            mmi_fatalities = (
                int(hazard_mmi * fatality_rate[hazard_mmi]))  # rounding down
            mmi_displaced = (
                (people_count - mmi_fatalities) *
                displacement_rate()[hazard_mmi])

            agg_zone_index = int(agg_block.value(long(i)))

            key = (hazard_mmi, agg_zone_index)
            if key not in exposed:
                exposed[key] = 0

            exposed[key] += people_count
        else:
            # If hazard is less than 2 or population is less than 0
            mmi_displaced = -1

        exposed_array[i / width, i % width] = mmi_displaced

    # output raster data - e.g. displaced people
    array_to_raster(exposed_array, exposed_raster_filename, hazard)

    exposed_raster = QgsRasterLayer(exposed_raster_filename, 'exposed', 'gdal')
    assert exposed_raster.isValid()

    exposed_raster.keywords = dict(exposure.keywords)
    exposed_raster.keywords['layer_purpose'] = (
        layer_purpose_exposure_impacted['key'])
    exposed_raster.keywords['title'] = processing_step
    exposed_raster.keywords['exposure_keywords'] = dict(exposure.keywords)
    exposed_raster.keywords['hazard_keywords'] = dict(hazard.keywords)
    exposed_raster.keywords['aggregation_keywords'] = dict(
        aggregation.keywords)

    return exposed, exposed_raster


@profile
def make_summary_layer(exposed, aggregation, fatality_rate):
    """Add fields to the aggregation given the dictionary of affected people.

    The dictionary contains affected people counts per hazard and aggregation
    zones.

    :param exposed: The dictionary with affected people counts per hazard and
    aggregation zones.
    :type exposed: dict

    :param aggregation: The aggregation layer where we write statistics.
    :type aggregation: QgsVectorLayer

    :param fatality_rate: The fatality rate to use.
    :type fatality_rate: function

    :return: Tuple with the aggregation layer and a dictionary with totals.
    :rtype: tuple(QgsVectorLayer, dict)
    """
    field_mapping = {}

    aggregation.startEditing()
    inasafe_fields = aggregation.keywords['inasafe_fields']
    id_field = inasafe_fields[aggregation_id_field['key']]

    field = create_field_from_definition(population_count_field)
    aggregation.addAttribute(field)
    field_mapping[field.name()] = aggregation.fieldNameIndex(field.name())
    inasafe_fields[population_count_field['key']] = (
        population_count_field['field_name'])

    field = create_field_from_definition(fatalities_field)
    aggregation.addAttribute(field)
    field_mapping[field.name()] = aggregation.fieldNameIndex(field.name())
    inasafe_fields[fatalities_field['key']] = fatalities_field['field_name']

    field = create_field_from_definition(displaced_field)
    aggregation.addAttribute(field)
    field_mapping[field.name()] = aggregation.fieldNameIndex(field.name())
    inasafe_fields[displaced_field['key']] = displaced_field['field_name']

    for mmi in xrange(2, 11):
        field = create_field_from_definition(
            population_exposed_per_mmi_field, mmi)
        aggregation.addAttribute(field)
        field_mapping[field.name()] = aggregation.fieldNameIndex(field.name())
        value = population_exposed_per_mmi_field['field_name'] % mmi
        inasafe_fields[population_exposed_per_mmi_field['key'] % mmi] = value

        field = create_field_from_definition(fatalities_per_mmi_field, mmi)
        aggregation.addAttribute(field)
        field_mapping[field.name()] = aggregation.fieldNameIndex(field.name())
        value = fatalities_per_mmi_field['field_name'] % mmi
        inasafe_fields[fatalities_per_mmi_field['key'] % mmi] = value

        field = create_field_from_definition(population_displaced_per_mmi, mmi)
        aggregation.addAttribute(field)
        field_mapping[field.name()] = aggregation.fieldNameIndex(field.name())
        value = population_displaced_per_mmi['field_name'] % mmi
        inasafe_fields[population_displaced_per_mmi['key'] % mmi] = value

    exposed_per_agg_zone = {}
    for (mmi, agg), count in exposed.iteritems():
        if agg not in exposed_per_agg_zone:
            exposed_per_agg_zone[agg] = {}
        exposed_per_agg_zone[agg][mmi] = count

    for agg_feature in aggregation.getFeatures():
        agg_zone = agg_feature[id_field]

        total_exposed = 0
        total_fatalities = 0
        total_displaced = 0

        LOGGER.debug('Aggregation %s is being processed by EQ IF' % agg_zone)
        stats_aggregation = exposed_per_agg_zone[agg_zone]
        for mmi, mmi_exposed in stats_aggregation.iteritems():
            mmi_fatalities = (
                int(mmi_exposed * fatality_rate[mmi]))  # rounding down
            mmi_displaced = (
                (mmi_exposed - mmi_fatalities) * displacement_rate()[mmi])

            aggregation.changeAttributeValue(
                agg_feature.id(),
                field_mapping['mmi_%d_exposed' % mmi],
                mmi_exposed)

            aggregation.changeAttributeValue(
                agg_feature.id(),
                field_mapping['mmi_%d_fatalities' % mmi],
                mmi_fatalities)

            aggregation.changeAttributeValue(
                agg_feature.id(),
                field_mapping['mmi_%d_displaced' % mmi],
                mmi_displaced)

            total_exposed += mmi_exposed
            total_fatalities += mmi_fatalities
            total_displaced += mmi_displaced

        aggregation.changeAttributeValue(
            agg_feature.id(),
            field_mapping[population_count_field['field_name']],
            total_exposed)

        aggregation.changeAttributeValue(
            agg_feature.id(),
            field_mapping[fatalities_field['field_name']],
            total_fatalities)

        aggregation.changeAttributeValue(
            agg_feature.id(),
            field_mapping[displaced_field['field_name']],
            total_displaced)

    aggregation.keywords['layer_purpose'] = (
        layer_purpose_aggregation_impacted['key'])
    aggregation.keywords['title'] = layer_purpose_aggregation_impacted['key']

    return aggregation
