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

from safe.gis.numerics import log_normal_cdf
from safe.gisv4.raster.align import align_rasters
from safe.gisv4.raster.write_raster import array_to_raster, make_array
from safe.gisv4.raster.rasterize import rasterize_vector_layer
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


def make_aggregation_layer(crs, extent):
    """Create a polygon layer with single geometry covering the given extent.

    This is to generate aggregation layer if none was given to us.

    TODO We will remove this function and use the function in
        safe.impact_function.create_extra_layers
    """
    output_filename = unique_filename(
        prefix='aggregation_extent', suffix='.shp')

    fields = QgsFields()
    fields.append(QgsField('name', QVariant.String))
    QgsVectorFileWriter.deleteShapeFile(output_filename)
    writer = QgsVectorFileWriter(
        output_filename, 'utf-8', fields, QGis.WKBPolygon, crs)
    feature = QgsFeature(fields)
    feature.setGeometry(QgsGeometry.fromRect(extent))
    feature['name'] = 'all'
    writer.addFeature(feature)
    del writer

    layer = QgsVectorLayer(output_filename, 'agg extent', 'ogr')
    assert layer.isValid()
    return layer


def temporary_aggregation_layer(aggregation_layer, aggregation_field, crs):
    """Add integer attribute to the aggregation layer if the aggregation field
    is not integer and also reproject aggregation layer if not in the same CRS.

    TODO : We will remove this function and use the function in
        safe.impact_function.create_extra_layers

    :returns: The layer and dictionary of mapping { name: index }.
    :rtype: (QgsVectorLayer, dict)
    """
    aggregation_name_to_index = {}
    last_feature_index = 0
    ct = None

    if crs != aggregation_layer.crs():
        ct = QgsCoordinateTransform(aggregation_layer.crs(), crs)

    output_filename = unique_filename(prefix='aggregation_tmp', suffix='.shp')

    fields = QgsFields()
    fields.append(QgsField('name_index', QVariant.Int))
    writer = QgsVectorFileWriter(
        output_filename,
        'utf-8',
        fields,
        aggregation_layer.wkbType(),
        aggregation_layer.crs())

    for f in aggregation_layer.getFeatures():
        feature_name = f[aggregation_field]
        if feature_name not in aggregation_name_to_index:
            last_feature_index += 1
            aggregation_name_to_index[feature_name] = last_feature_index

        f2 = QgsFeature(fields)
        f2['name_index'] = aggregation_name_to_index[feature_name]
        geom = f.geometry()
        if ct:
            geom.transform(ct)
        f2.setGeometry(geom)

        writer.addFeature(f2)

    del writer
    aggregation_layer_tmp = QgsVectorLayer(
        output_filename, 'agg tmp', 'memory')

    return aggregation_layer_tmp, aggregation_name_to_index


def exposed_people_stats(hazard, exposure, aggregation):
    """Calculate the number of exposed people per MMI level per aggregation
    zone and prepare raster layer outputs.

    :param hazard: The earthquake raster layer.
    :type hazard: QgsRasterLayer

    :param exposure: The population raster layer.
    :type exposure: QgsVectorLayer

    :param aggregation: The aggregation layer.
    :type aggregation: QgsVectorLayer

    :return: A tuple with the aggregation vector layer and the exposed raster.
    :rtype: (QgsVectorLayer, QgsRasterLayer)
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

    return exposed, exposed_raster


def make_summary_layer(
        exposed,
        aggregation_layer,
        aggregation_field,
        aggregation_name_to_index,
        fatality_rate):
    """Given the dictionary of affected people counts per hazard and
    aggregation zones, create a copy of the aggregation layer with statistics.
    """

    output_filename = unique_filename(prefix='summary', suffix='.shp')

    displacement_rate = {
        2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 1.0,
        7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0
    }

    fields = QgsFields()
    fields.append(QgsField('name', QVariant.String))
    fields.append(QgsField('total_exposed', QVariant.Int))
    fields.append(QgsField('total_fatalities', QVariant.Int))
    fields.append(QgsField('total_displaced', QVariant.Int))
    for mmi in xrange(2, 11):
        fields.append(QgsField('mmi_%d_exposed' % mmi, QVariant.Int))
        fields.append(QgsField('mmi_%d_fatalities' % mmi, QVariant.Int))
        fields.append(QgsField('mmi_%d_displaced' % mmi, QVariant.Int))

    exposed_per_agg_zone = {}
    for (mmi, agg), count in exposed.iteritems():
        if agg not in exposed_per_agg_zone:
            exposed_per_agg_zone[agg] = {}
        exposed_per_agg_zone[agg][mmi] = count

    # sums over the whole area
    grand_total_exposed = 0
    grand_total_fatalities = 0
    grand_total_displaced = 0

    writer = QgsVectorFileWriter(
        output_filename,
        'utf-8',
        fields,
        aggregation_layer.wkbType(),
        aggregation_layer.crs())

    for agg_feature in aggregation_layer.getFeatures():
        agg_zone_name = agg_feature[aggregation_field]
        agg_zone = aggregation_name_to_index[agg_zone_name]

        feature = QgsFeature(fields)
        feature.setGeometry(agg_feature.geometry())

        total_exposed = 0
        total_fatalities = 0
        total_displaced = 0

        for mmi, mmi_exposed in exposed_per_agg_zone[agg_zone].iteritems():
            mmi_fatalities = (
                int(mmi_exposed * fatality_rate[mmi]))  # rounding down
            mmi_displaced = (
                (mmi_exposed - mmi_fatalities) * displacement_rate[mmi])

            feature['mmi_%d_exposed' % mmi] = mmi_exposed
            feature['mmi_%d_fatalities' % mmi] = mmi_fatalities
            feature['mmi_%d_displaced' % mmi] = mmi_displaced

            total_exposed += mmi_exposed
            total_fatalities += mmi_fatalities
            total_displaced += mmi_displaced

        feature['name'] = agg_zone_name
        feature['total_exposed'] = total_exposed
        feature['total_fatalities'] = total_fatalities
        feature['total_displaced'] = total_displaced

        grand_total_exposed += total_exposed
        grand_total_fatalities += total_fatalities
        grand_total_displaced += total_displaced

        writer.addFeature(feature)

    totals = {
        'exposed': grand_total_exposed,
        'fatalities': grand_total_fatalities,
        'displaced': grand_total_displaced,
    }

    del writer
    layer = QgsVectorLayer(output_filename, 'summary', 'ogr')
    assert layer.isValid()
    return layer, totals


def calc_impact(
        hazard,
        exposure,
        aggregation,
        aggregation_field,
        extent,
        fatality_rate):
    """Main function to calculate the impact of earthquake on population.

    1. Prepare hazard, exposure, aggregation raster layers to common grid.

    2. Get sums of exposed people per hazard MMI level and aggregation zone.

    3. Create vector output based on aggregation layer with statistics of
        fatalities and displaced people for each aggregation zone and MMI
        level.
    """

    # STEP 1: prepare data

    hazard_aligned, exposure_aligned = align_rasters(
        hazard, exposure, extent)

    if not aggregation:
        # If we didn't get an aggregation layer, we will make one ourselves
        # covering the whole analysis area.
        aggregation = make_aggregation_layer(
            hazard_aligned.crs(), hazard_aligned.extent())
        aggregation_field = 'name'

    aggregation_layer_tmp, mapping = temporary_aggregation_layer(
        aggregation, aggregation_field, hazard_aligned.crs())

    hazard_provider = hazard_aligned.dataProvider()
    aggregation_aligned = rasterize_vector_layer(
        aggregation_layer_tmp,
        'name_index',
        hazard_provider.xSize(),
        hazard_provider.ySize(),
        hazard_aligned.extent())

    # STEP 2: calculate statistics

    exposed, exposed_raster = exposed_people_stats(
        hazard_aligned, exposure_aligned, aggregation_aligned)

    # STEP 3: make output vector layer with aggregate counts

    summary_vector, totals = make_summary_layer(
        exposed, aggregation, aggregation_field, mapping, fatality_rate)

    return summary_vector, exposed_raster, totals
