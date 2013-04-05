"""**Minimum Needs Implementation.**

.. tip:: Provides minimum needs assessment for a polygon layer containing
    counts of people affected per polygon.

"""

__author__ = 'tim@linfiniti.com, ole.moller.nielsen@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '20/1/2013'
__license__ = "GPL"
__copyright__ = 'Copyright 2013, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import logging

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature

from qgis.core import QgsMapLayerRegistry, QgsVectorLayer

from safe_qgis.safe_interface import get_version, safe_read_layer, Vector
from safe_qgis.minimum_needs_base import Ui_MinimumNeedsBase
from safe_qgis.utilities import (addComboItemInOrder,
                                 isPolygonLayer,
                                 isPointLayer)

LOGGER = logging.getLogger('InaSAFE')


class MinimumNeeds(QtGui.QDialog, Ui_MinimumNeedsBase):
    """Dialog implementation class for the InaSAFE keywords editor."""

    def __init__(self, parent):
        """Constructor for the dialog.

        Args:
           * parent - parent widget of this dialog.
           * iface - a Quantum GIS QGisAppInterface instance.

        Returns:
           not applicable.
        Raises:
           no exceptions explicitly raised.
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr(
            'InaSAFE %1 Minimum Needs Tool').arg(get_version()))
        self.polygonLayersToCombo()

    def minimum_needs(self, input_layer, population_name):
        """
            Args
                input_layer: InaSAFE layer object assumed to contain
                             population counts
                population_name: Attribute name that holds population count
            Returns
                InaSAFE layer with attributes for minimum needs as per Perka 7


        """

        needs_attributes = []
        for attributes in input_layer.get_data():
            attribute_dict = attributes

            # Get population count
            population = attributes[population_name]
            # Clean up and turn into integer
            if population in ['-', None]:
                displaced = 0
            else:
                population = str(population).replace(',', '')
                try:
                    displaced = int(population)
                except ValueError:
                    QtGui.QMessageBox.information(
                        None,
                        self.tr('Format error'),
                        self.tr('Please change the value of %s in '
                                'attribute %s to integer format') %
                        (population, population_name))
                    raise ValueError

            # Calculate estimated needs based on BNPB Perka 7/2008
            # minimum bantuan

            # 400g per person per day
            rice = int(displaced * 2.8)
            # 2.5L per person per day
            drinking_water = int(displaced * 17.5)
            # 15L per person per day
            water = int(displaced * 105)
            # assume 5 people per family (not in perka)
            family_kits = int(displaced / 5)
            # 20 people per toilet
            toilets = int(displaced / 20)

            # Add to attributes

            attribute_dict['Beras'] = rice
            attribute_dict['Air minum'] = drinking_water
            attribute_dict['Air bersih'] = water
            attribute_dict['Kit keluarga'] = family_kits
            attribute_dict['Jamban'] = toilets

            # Record attributes for this feature
            needs_attributes.append(attribute_dict)

        output_layer = Vector(geometry=input_layer.get_geometry(),
                              data=needs_attributes,
                              projection=input_layer.get_projection())
        return output_layer

    def polygonLayersToCombo(self):
        """Populate the combo with all polygon layers loaded in QGIS."""

        myRegistry = QgsMapLayerRegistry.instance()
        myLayers = myRegistry.mapLayers().values()
        myFoundFlag = False
        for myLayer in myLayers:
            myName = myLayer.name()
            mySource = str(myLayer.id())
            #check if layer is a vector polygon layer
            if isPolygonLayer(myLayer) or isPointLayer(myLayer):
                myFoundFlag = True
                addComboItemInOrder(self.cboPolygonLayers, myName, mySource)
        if myFoundFlag:
            self.cboPolygonLayers.setCurrentIndex(0)

    @pyqtSignature('int')
    def on_cboPolygonLayers_currentIndexChanged(self, theIndex=None):
        """Automatic slot executed when the layer is changed to update fields.

        Args:
           theIndex: int - passed by the signal that triggers this slot.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        myLayerId = self.cboPolygonLayers.itemData(
            theIndex, QtCore.Qt.UserRole).toString()
        myLayer = QgsMapLayerRegistry.instance().mapLayer(myLayerId)
        myFields = myLayer.dataProvider().fieldNameMap().keys()
        self.cboFields.clear()
        for myField in myFields:
            addComboItemInOrder(self.cboFields, myField, myField)

    def accept(self):
        """Process the layer and field and generate a new layer.

        .. note:: This is called on ok click.

        """
        myIndex = self.cboFields.currentIndex()
        myFieldName = self.cboFields.itemData(
            myIndex, QtCore.Qt.UserRole).toString()

        myIndex = self.cboPolygonLayers.currentIndex()
        myLayerId = self.cboPolygonLayers.itemData(
            myIndex, QtCore.Qt.UserRole).toString()
        myLayer = QgsMapLayerRegistry.instance().mapLayer(myLayerId)

        myFileName = str(myLayer.source())

        myInputLayer = safe_read_layer(myFileName)

        try:
            myOutputLayer = self.minimum_needs(myInputLayer, str(myFieldName))
        except ValueError:
            return

        myNewFile = myFileName[:-4] + '_perka7' + '.shp'

        myOutputLayer.write_to_file(myNewFile)

        myNewLayer = QgsVectorLayer(myNewFile, 'Minimum Needs', 'ogr')
        QgsMapLayerRegistry.instance().addMapLayers([myNewLayer])
        self.done(QtGui.QDialog.Accepted)
