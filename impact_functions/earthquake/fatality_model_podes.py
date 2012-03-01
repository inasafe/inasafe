"""Fatality model using BNPB Podes data.

This was obtained from the WFS server

http://gisserver.bnpb.go.id:8399/arcgis/rest/services
http://gisserver.bnpb.go.id:8399/arcgis/rest/services/demografi
http://gisserver.bnpb.go.id:8399/arcgis/rest/services/demografi/
Populasi_Penduduk_Kecamatan/FeatureServer?f=pjson

using wget, followed by processing the gml to swap coordinates using the script
https://github.com/AIFDR/riab/blob/develop/extras/swap_gml_coords.py

Finally, it was converted to the .shp format.

Eventually, this will be scripted and eventually work directly with the WFS
- see https://github.com/AIFDR/riab/issues/62
"""

import numpy
from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.raster import Raster
from storage.vector import Vector


class EarthquakeFatalityFunctionPodes(FunctionProvider):
    """Risk plugin for earthquake fatalities using Podes polygon data

    :author Allen
    :rating 1
    :param requires category=='hazard' and \
                subcategory.startswith('earthquake') and \
                layertype=='raster' and \
                unit=='MMI'

    :param requires category=='exposure' and \
                subcategory.startswith('population') and \
                layertype=='vector' and \
                geometry=='polygon'
    """

    target_field = 'FATALITIES'

    def run(self, layers,
            a=0.97429, b=11.037):
        """Risk plugin for earthquake fatalities

        Input
          layers: List of layers expected to contain
                  H: Raster layer of MMI ground shaking
                  E: Polygon population data
          a: Parameter for Allen impact function
          b: Parameter for Allen impact function
        """

        # Identify input layers
        H = get_hazard_layer(layers)   # Intensity
        E = get_exposure_layer(layers)  # Exposure - population counts

        # Interpolate hazard level to building locations
        H = H.interpolate(E)

        # Extract relevant numerical data
        coordinates = E.get_geometry()  # Stay with polygons
        shaking = H.get_data()
        N = len(shaking)

        # List attributes to carry forward to result layer
        attributes = E.get_attribute_names()

        # Calculate fatilities
        count = 0
        total = 0

        result_feature_set = []
        for i in range(N):
            mmi = float(shaking[i].values()[0])
            if mmi < 0.0:
                # FIXME: Hack until interpolation is fixed
                mmi = 0.0

            population_count = E.get_data('Jumlah_Pen', i)

            # Calculate impact
            F = 10 ** (a * mmi - b) * population_count

            # Collect shake level and calculated damage
            result_dict = {self.target_field: F,
                           'MMI': mmi}

            # Carry all orginal attributes forward
            for key in attributes:
                result_dict[key] = E.get_data(key, i)

            # Record result for this feature
            result_feature_set.append(result_dict)

            # Calculate statistics
            if not numpy.isnan(F):
                count += F
            total += population_count

        # Create report
        impact_summary =  ('<table border="0" width="320px">'
                   '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                   '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                   '</table>' % ('Jumlah Penduduk', int(total),
                                 'Perkiraan Orang Meninggal', int(count)))

        # Create vector layer and return
        V = Vector(data=result_feature_set,
                   projection=E.get_projection(),
                   geometry=coordinates,
                   name='Estimated fatalities',
                   keywords={'impact_summary': impact_summary})

        return V
