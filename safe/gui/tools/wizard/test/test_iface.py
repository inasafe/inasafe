from qgis.core import QgsMapLayerRegistry, QgsVectorLayer
from qgis.utils import iface
from qgis.gui import QgsMapCanvasLayer

QgsMapLayerRegistry.instance().removeAllMapLayers()

vector_layer = QgsVectorLayer(
    "Point?crs=epsg:4326&field=id:integer&field=name:string(20)&index=yes",
    "temporary_points",
    "memory")
QgsMapLayerRegistry.instance().addMapLayer(vector_layer)

# iface.mapCanvas().setLayerSet(
# [QgsMapCanvasLayer(vector_layer), QgsMapCanvasLayer(vector_layer)])
test_variable = len(iface.mapCanvas().layers())
len(iface.mapCanvas().layers())
test_variable_2 = len(iface.mapCanvas().layers())
print 'something'

test_variable_3 = len(iface.mapCanvas().layers())

print 'test_variable', test_variable
print 'test_variable_2', test_variable_2
print 'test_variable_3', test_variable_3

print 'fin'
