# coding=utf-8

from PyQt4.QtCore import QVariant

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
    aggregation_id_field, aggregation_name_field)
from safe.definitions.layer_purposes import (
    layer_purpose_aggregation_impacted, layer_purpose_exposure_impacted)
from safe.gis.numerics import log_normal_cdf
from safe.gisv4.raster.write_raster import array_to_raster, make_array
from safe.common.utilities import unique_filename

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def itb_fatality_rates():
    """ITB method to compute fatality rate.

    :returns: Fatality rate.
    :rtype: dic
    """
    # As per email discussion with Ole, Trevor, Hadi, mmi < 4 will have
    # a fatality rate of 0 - Tim
    mmi_range = range(2, 11)
    # Model coefficients
    x = 0.62275231
    y = 8.03314466
    fatality_rate = {
        mmi: 0 if mmi < 4 else 10 ** (x * mmi - y) for mmi in mmi_range}
    return fatality_rate


def pager_fatality_rates():
    """Pager method to compute fatality rate.

    :returns: Fatality rate calculated as:
        lognorm.cdf(mmi, shape=Beta, scale=Theta)
    :rtype: dic
    """
    # Model coefficients
    theta = 13.249
    beta = 0.151
    mmi_range = range(2, 11)
    fatality_rate = {mmi: 0 if mmi < 4 else log_normal_cdf(
        mmi, median=theta, sigma=beta) for mmi in mmi_range}
    return fatality_rate


def bayesian_fatality_rates():
    """Fatality rate by MMI from Bayesian approach.

    :returns: Fatality rates as medians
        It comes worden_berngamma_log_fat_rate_inasafe_10.csv in InaSAFE 3.
    :rtype: dict
    """
    fatality_rate = {
        2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0,
        6: 3.41733122522e-05,
        7: 0.000387804494226,
        8: 0.001851451786,
        9: 0.00787294191661,
        10: 0.0314512157378,
    }
    return fatality_rate


def exposed_people_stats(hazard, exposure, aggregation):
    """Calculate the number of exposed people per MMI level per aggregation.

    Calculate the number of exposed people per MMI level per aggregation zone
    and prepare raster layer outputs.

    :param hazard: The earthquake raster layer.
    :type hazard: QgsRasterLayer

    :param exposure: The population raster layer.
    :type exposure: QgsVectorLayer

    :param aggregation: The aggregation layer.
    :type aggregation: QgsVectorLayer

    :return: A tuble with the exposed per MMI level par aggregation
        and the exposed raster.
        Tuple (mmi, agg_zone), value: number of exposed people
    :rtype: (dict, QgsRasterLayer)
    """
    exposed_raster_filename = unique_filename(prefix='exposed', suffix='.tif')

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
        hazard_mmi = int(round(hazard_mmi))

        people_count = exposure_block.value(long(i))

        agg_zone_index = int(agg_block.value(long(i)))

        key = (hazard_mmi, agg_zone_index)
        if key not in exposed:
            exposed[key] = 0

        exposed[key] += people_count

        exposed_array[i / width, i % width] = people_count

    # output raster data - e.g. displaced people
    array_to_raster(exposed_array, exposed_raster_filename, hazard)

    exposed_raster = QgsRasterLayer(exposed_raster_filename, 'exposed', 'gdal')
    assert exposed_raster.isValid()

    exposed_raster.keywords = dict(exposure.keywords)
    exposed_raster.keywords['layer_purpose'] = (
        layer_purpose_exposure_impacted['key'])
    exposed_raster.keywords['title'] = layer_purpose_exposure_impacted['key']

    return exposed, exposed_raster


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
    displacement_rate = {
        2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 1.0,
        7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0
    }

    field_mapping = {}

    aggregation.startEditing()

    field = QgsField('total_exposed', QVariant.Int)
    aggregation.addAttribute(field)
    field_mapping[field.name()] = aggregation.fieldNameIndex(field.name())

    field = QgsField('total_fatalities', QVariant.Int)
    aggregation.addAttribute(field)
    field_mapping[field.name()] = aggregation.fieldNameIndex(field.name())

    field = QgsField('total_displaced', QVariant.Int)
    aggregation.addAttribute(field)
    field_mapping[field.name()] = aggregation.fieldNameIndex(field.name())

    for mmi in xrange(2, 11):
        field = QgsField('mmi_%d_exposed' % mmi, QVariant.Int)
        aggregation.addAttribute(field)
        field_mapping[field.name()] = aggregation.fieldNameIndex(field.name())

        field = QgsField('mmi_%d_fatalities' % mmi, QVariant.Int)
        aggregation.addAttribute(field)
        field_mapping[field.name()] = aggregation.fieldNameIndex(field.name())

        field = QgsField('mmi_%d_displaced' % mmi, QVariant.Int)
        aggregation.addAttribute(field)
        field_mapping[field.name()] = aggregation.fieldNameIndex(field.name())

        exposed_per_agg_zone = {}
    for (mmi, agg), count in exposed.iteritems():
        if agg not in exposed_per_agg_zone:
            exposed_per_agg_zone[agg] = {}
        exposed_per_agg_zone[agg][mmi] = count

    # sums over the whole area
    grand_total_exposed = 0
    grand_total_fatalities = 0
    grand_total_displaced = 0

    inasafe_fields = aggregation.keywords['inasafe_fields']
    id_field = inasafe_fields[aggregation_id_field['key']]

    for agg_feature in aggregation.getFeatures():
        agg_zone = agg_feature[id_field]

        total_exposed = 0
        total_fatalities = 0
        total_displaced = 0

        for mmi, mmi_exposed in exposed_per_agg_zone[agg_zone].iteritems():
            mmi_fatalities = (
                int(mmi_exposed * fatality_rate[mmi]))  # rounding down
            mmi_displaced = (
                (mmi_exposed - mmi_fatalities) * displacement_rate[mmi])

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
            agg_feature.id(), field_mapping['total_exposed'], total_exposed)

        aggregation.changeAttributeValue(
            agg_feature.id(),
            field_mapping['total_fatalities'],
            total_fatalities)

        aggregation.changeAttributeValue(
            agg_feature.id(),
            field_mapping['total_displaced'],
            total_displaced)

        grand_total_exposed += total_exposed
        grand_total_fatalities += total_fatalities
        grand_total_displaced += total_displaced

    totals = {
        'exposed': grand_total_exposed,
        'fatalities': grand_total_fatalities,
        'displaced': grand_total_displaced,
    }

    aggregation.keywords['layer_purpose'] = (
        layer_purpose_aggregation_impacted['key'])
    aggregation.keywords['title'] = layer_purpose_aggregation_impacted['key']

    return aggregation, totals
