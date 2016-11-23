from safe.test.utilities import (
    load_test_vector_layer,
    get_qgis_app,
    get_dock)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
from safe.gui.tools.wizard.wizard_dialog import WizardDialog

dialog = WizardDialog(iface=IFACE)
dialog.dock = get_dock()
dialog.set_function_centric_mode()
QgsMapLayerRegistry.instance().removeAllMapLayers()
volcano_layer = load_test_vector_layer(
            'hazard',
            'volcano_krb.shp',
            clone=True)
structure_layer = load_test_vector_layer(
            'exposure',
            'buildings.shp',
            clone=True)
test_layers = [volcano_layer, structure_layer]
QgsMapLayerRegistry.instance().addMapLayers(test_layers)
count = len(dialog.iface.mapCanvas().layers())
count_iface = len(iface.mapCanvas().layers())
count_IFACE = len(IFACE.mapCanvas().layers())
print 'Wizard Dialog', dialog
print 'iface', iface
print iface == IFACE
print iface == dialog.iface
print IFACE == dialog.iface
print count, count_iface, count_IFACE
print len(test_layers)
assert count == len(test_layers)
print 'fin'
