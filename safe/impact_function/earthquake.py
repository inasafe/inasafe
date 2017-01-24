# coding=utf-8

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
from safe.gis.vector.tools import create_field_from_definition
from safe.utilities.numerics import log_normal_cdf
from safe.gis.raster.write_raster import array_to_raster, make_array
from safe.common.utilities import unique_filename
from safe.utilities.profiling import profile
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def itb_fatality_rates():
    """Indonesian Earthquake Fatality Model.

    This model was developed by Institut Teknologi Bandung (ITB) and
    implemented by Dr. Hadi Ghasemi, Geoscience Australia.

    Reference:

    Indonesian Earthquake Building-Damage and Fatality Models and
    Post Disaster Survey Guidelines Development,
    Bali, 27-28 February 2012, 54pp.

    Algorithm:

    In this study, the same functional form as Allen (2009) is adopted
    to express fatality rate as a function of intensity (see Eq. 10 in the
    report). The Matlab built-in function (fminsearch) for  Nelder-Mead
    algorithm was used to estimate the model parameters. The objective
    function (L2G norm) that is minimised during the optimisation is the
    same as the one used by Jaiswal et al. (2010).

    The coefficients used in the indonesian model are
    x=0.62275231, y=8.03314466, zeta=2.15

    Allen, T. I., Wald, D. J., Earle, P. S., Marano, K. D., Hotovec, A. J.,
    Lin, K., and Hearne, M., 2009. An Atlas of ShakeMaps and population
    exposure catalog for earthquake loss modeling, Bull. Earthq. Eng. 7,
    701-718.

    Jaiswal, K., and Wald, D., 2010. An empirical model for global earthquake
    fatality estimation, Earthq. Spectra 26, 1017-1037.

    Caveats and limitations:

    The current model is the result of the above mentioned workshop and
    reflects the best available information. However, the current model
    has a number of issues listed below and is expected to evolve further
    over time.

    1 - The model is based on limited number of observed fatality
        rates during 4 past fatal events.

    2 - The model clearly over-predicts the fatality rates at
        intensities higher than VIII.

    3 - The model only estimates the expected fatality rate for a given
        intensity level; however the associated uncertainty for the proposed
        model is not addressed.

    4 - There are few known mistakes in developing the current model:
        - rounding MMI values to the nearest 0.5,
        - Implementing Finite-Fault models of candidate events, and
        - consistency between selected GMPEs with those in use by BMKG.
          These issues will be addressed by ITB team in the final report.

    Note: Because of these caveats, decisions should not be made solely on
    the information presented here and should always be verified by ground
    truthing and other reliable information sources.

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
    """USGS Pager fatality estimation model.

    Fatality rate(MMI) = cum. standard normal dist(1/BETA * ln(MMI/THETA)).

    Reference:

    Jaiswal, K. S., Wald, D. J., and Hearne, M. (2009a).
    Estimating casualties for large worldwide earthquakes using an empirical
    approach. U.S. Geological Survey Open-File Report 2009-1136.

    v1.0:
        Theta: 14.05, Beta: 0.17, Zeta 2.15
        Jaiswal, K, and Wald, D (2010)
        An Empirical Model for Global Earthquake Fatality Estimation
        Earthquake Spectra, Volume 26, No. 4, pages 1017–1037

    v2.0:
        Theta: 13.249, Beta: 0.151, Zeta: 1.641)
        (http://pubs.usgs.gov/of/2009/1136/pdf/
        PAGER%20Implementation%20of%20Empirical%20model.xls)

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


def itb_bayesian_fatality_rates():
    """ITB fatality model based on a Bayesian approach.

    This model was developed by Institut Teknologi Bandung (ITB) and
    implemented by Dr. Hyeuk Ryu, Geoscience Australia.

    Reference:

    An Empirical Fatality Model for Indonesia Based on a Bayesian Approach
    by W. Sengara, M. Suarjana, M.A. Yulman, H. Ghasemi, and H. Ryu
    submitted for Journal of the Geological Society

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

EARTHQUAKE_FUNCTIONS = (
    {
        'key': 'itb_bayesian_fatality_rates',
        'name': tr('ITB bayesian fatality rates'),
        'fatality_rates': itb_bayesian_fatality_rates
    }, {
        'key': 'itb_fatality_rates',
        'name': tr('ITB fatality rates'),
        'fatality_rates': itb_fatality_rates
    }, {
        'key': 'pager_fatality_rates',
        'name': tr('Pager fatality rates'),
        'fatality_rates': pager_fatality_rates
    }
)


def displacement_rate():
    """Return the displacement rate.

    :returns: The displacement rate.
    :rtype: dict
    """
    rate = {
        2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0,
        6: 1.0, 7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0
    }
    return rate


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

        mmi_fatalities = (
            int(hazard_mmi * fatality_rate[hazard_mmi]))  # rounding down
        mmi_displaced = (
            (people_count - mmi_fatalities) * displacement_rate()[hazard_mmi])

        agg_zone_index = int(agg_block.value(long(i)))

        key = (hazard_mmi, agg_zone_index)
        if key not in exposed:
            exposed[key] = 0

        exposed[key] += people_count

        exposed_array[i / width, i % width] = mmi_displaced

    # output raster data - e.g. displaced people
    array_to_raster(exposed_array, exposed_raster_filename, hazard)

    exposed_raster = QgsRasterLayer(exposed_raster_filename, 'exposed', 'gdal')
    assert exposed_raster.isValid()

    exposed_raster.keywords = dict(exposure.keywords)
    exposed_raster.keywords['layer_purpose'] = (
        layer_purpose_exposure_impacted['key'])
    exposed_raster.keywords['title'] = layer_purpose_exposure_impacted['key']
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

        for mmi, mmi_exposed in exposed_per_agg_zone[agg_zone].iteritems():
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
