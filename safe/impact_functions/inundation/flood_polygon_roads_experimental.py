import os.path

from PyQt4.QtCore import QVariant
from qgis.core import (
    QgsField,
    QgsVectorLayer,
    QgsFeature,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem
)

from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.common.tables import Table, TableRow
from safe.common.utilities import ugettext as tr
from safe.storage.vector import Vector
from safe_qgis.safe_interface import temp_dir


class FloodVectorRoadsExperimentalFunction(FunctionProvider):
    """
    Simple experimental impact function for inundation

    :author Dmitry Kolesov
    :rating 1
    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype=='vector'
    :param requires category=='exposure' and \
                    subcategory in ['road'] and \
                    layertype=='vector'
    """

    target_field = 'flooded'
    title = tr('Be flooded')

    def get_function_type(self):
        """Get type of the impact function.

        :returns:   'qgis2.0' or 'numpy'
        """
        return 'qgis2.0'

    def run(self, layers, extent=None):
        """
        Experimental impact function

        Input
          layers: List of layers expected to contain
              H: Polygon layer of inundation areas
              E: Vector layer of roads
        """

        # Extract data

        # TODO: Add QgsMapLayer to Layer class definition
        # as possible layer type.
        H = get_hazard_layer(layers)    # Flood
        E = get_exposure_layer(layers)  # Roads

        question = get_question(H.get_name(),
                                E.get_name(),
                                self)

        # FIXME: use QgsVectorLayer directly.
        # (Transformation safelayer to QgsVectorLayer is used as a stub)
        temp_name = os.path.join(temp_dir(), 'exposure_tmp.shp')
        E = E.write_to_file(temp_name)
        E = QgsVectorLayer(temp_name, "exposure_tmp", "ogr")
        e_provider = E.dataProvider()
        fields = e_provider.fields()
        # If target_field does not exist, add it:
        if fields.indexFromName(self.target_field) == -1:
            e_provider.addAttributes([QgsField(self.target_field,
                                               QVariant.Int)])
        target_field_index = e_provider.fieldNameIndex(self.target_field)
        fields = e_provider.fields()

        # TODO: use extent to set area of interest like
        #request=QgsFeatureRequest()
        #request.setFilterRect(extent)
        #  for f in layer.getFeatures(request):
        #    ...

        # TODO: call new inasafe Vector class, set type = QgsMapLayer
        V = QgsVectorLayer('LineString', 'impact_lines', 'memory')
        v_provider = V.dataProvider()

        # Copy attributes
        v_provider.addAttributes(fields.toList())
        V.startEditing()
        V.commitChanges()

        # Copy geometry and data
        e_data = E.getFeatures()
        for feat in e_data:
            geom = feat.geometry()
            attrs = feat.attributes()

            # TODO: check intersection E & H
            v_feat = QgsFeature()
            v_feat.setGeometry(geom)
            v_feat.setAttributes(attrs)
            v_feat.setAttribute(target_field_index, 1)
            (res, out_feat) = V.dataProvider().addFeatures([v_feat])
            fid = out_feat[0].id()
            v_provider.changeAttributeValues({fid: {target_field_index: 1}})

        V.updateExtents()

        # TODO: use QgsVectorLayer directly.
        # (Transformation QgsVectorLayer -> safelayer is used as a stub)
        temp_name = os.path.join(temp_dir(), 'impact_tmp.shp')
        error = QgsVectorFileWriter.writeAsVectorFormat(
            V,
            temp_name,
            "UTF8",
            E.crs(),
            "ESRI Shapefile")
        if error != QgsVectorFileWriter.NoError:
            raise IOError
        # Generate simple impact report
        N = 100         # Jast a stub
        count = N/2     # Jast a stub
        table_body = [question,
                      TableRow([tr('Road Type'),
                                tr('Temporarily closed'),
                                tr('Total')],
                               header=True),
                      TableRow([tr('All'), count, N])]
        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('Roads inundated')

        style_classes = [dict(label=tr('Not Inundated'), value=0,
                              colour='#1EFC7C', transparency=0, size=1),
                         dict(label=tr('Inundated'), value=1,
                              colour='#F31A1C', transparency=0, size=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='categorizedSymbol')

        # Create vector layer and return
        V = Vector(data=temp_name,
                   projection=H.get_projection(),
                   name=tr('Flooder roads'),
                   keywords={'impact_summary': impact_summary,
                             'map_title': map_title,
                             'target_field': self.target_field},
                   style_info=style_info)
        return V
