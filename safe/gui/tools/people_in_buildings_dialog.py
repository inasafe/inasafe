# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid **People In BuildingsDialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""
__author__ = 'Christian Christelis <christian@kartoza.com>'
__revision__ = '$Format:%H$'
__date__ = '12/02/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QVariant  # , QPyNullVariant
from qgis.core import QgsField
from qgis.core import QgsGeometry
from qgis.core import QgsVectorLayer
from qgis.core import QgsMapLayerRegistry

from safe.utilities.resources import get_ui_class

FORM_CLASS = get_ui_class('people_in_buildings_base.ui')

People_Calculated = "People_Dec"
People_Rounded = "People_Rnd"


class PeopleInBuildingsDialog(QtGui.QDialog, FORM_CLASS):
    """People in buildings dialog for creating new exposure layer."""

    def __init__(self, iface, parent=None):
        """Constructor for the dialog.

        :param iface: A QGIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param parent: Parent widget of this dialog.
        :type parent: QWidget

        :param dock: Optional dock widget instance that we can notify of
            changes to the keywords.
        :type dock: Dock
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent

        self.load_layers_into_combo_box()

        self.buildingLayerComboBox.currentIndexChanged['QString'].connect(
            self.building_layer_changed)
        self.censusLayerComboBox.currentIndexChanged['QString'].connect(
            self.cencus_layer_changed)

        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(
            self.estimate_people_in_buildings)

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)

    def load_layers_into_combo_box(self):
        """Load the layer options and column options into the combobox.
        """
        layer_names = self._get_layer_names()
        self._update_combobox(self.buildingLayerComboBox, layer_names)
        self._update_combobox(self.censusLayerComboBox, layer_names)
        self.building_layer_changed(self.buildingLayerComboBox.currentText())
        self.cencus_layer_changed(self.censusLayerComboBox.currentText())

    def _select_layer_by_name(self, layer_name):
        """Get a layer by its name.

        :param layer_name: The layer's name.
        :type layer_name: basestring

        :returns: The layer that has the appropriate name or none.
        :rtype: QgsMapLayer, None
        """
        layers = self._get_layers()
        layer_names = [layer.name() for layer in layers]
        if not layer_name in layer_names:
            return None
        index = layer_names.index(layer_name)
        return layers[index]

    def _get_layers(self):
        """Get all layers.

        :returns: All layers currently loaded.
        :rtype: list
        """
        layers = QgsMapLayerRegistry.instance().mapLayers()
        layers = [l for l in layers.values() if isinstance(l, QgsVectorLayer)]
        return layers

    def _get_layer_names(self):
        """Get the names of all layers.

        :returns: A list of all layer names.
        :rtype: list
        """
        layers = self._get_layers()
        layer_names = [l.name() for l in layers]
        return layer_names

    @staticmethod
    def _get_field_names(layer):
        """Get all attribute names of the layer.

        :param layer: The layer to be investigated.
        :type layer: QgsVectorLayer

        :returns: Returns a list of all attribute names of the layer.
        :rtype: list
        """
        field_names = [field.name() for field in layer.pendingFields()]
        return field_names

    def building_layer_changed(self, layer_name):
        """Handler for change buildings layer event.

        :param layer_name: The name of the layer that was selected.
        :type layer_name: basestring
        """
        layer = self._select_layer_by_name(layer_name)
        if layer is None:
            return
        field_names = self._get_field_names(layer)
        self._update_combobox(self.usageColumnComboBox, field_names)
        self._update_combobox(self.levelsColumnComboBox, field_names)

    def cencus_layer_changed(self, layer_name):
        """Hander for change of population layer selection event.

        :param layer_name: The name of the layer that was selected.
        :type layer_name: basestring
        """
        layer = self._select_layer_by_name(layer_name)
        if layer is None:
            return
        field_names = self._get_field_names(layer)
        self._update_combobox(self.populationCountComboBox, field_names)

    @staticmethod
    def _update_combobox(combobox, options):
        """Shorthand for clearing and loading options (this happens a lot).
        """
        combobox.clear()
        combobox.addItems(options)

    @staticmethod
    def _add_attribute_to_layer(layer, attribute_name, data_type):
        """Add a new attribute to an existing layer.

        :param layer: The layer to be altered.
        :type layer: QgsVectorLayer

        :param attribute_name: The name of the new attribute.
        :type attribute_name: basestring

        :param data_type: The type of the new attribute.
        :type data_type: QVariant.Double, QVariant.Int

        :returns: The success state of the operation.
        :rtype: bool
        """
        provider = layer.dataProvider()
        # Check if attribute is already there, return "-1" if not
        field_index = provider.fieldNameIndex(attribute_name)
        if field_index != -1:
            return False
        field = QgsField(attribute_name, data_type)
        result = provider.addAttributes([field])
        return result

    def add_population_attribute(self, layer):
        """Add people estimate columns/attributes to the output layer.

        :param layer: Layer that the population attribute should be added to.
        :type layer: QgsVectorLayer
        """
        attributes = {
            People_Calculated: QVariant.Double,
            People_Rounded: QVariant.Int
        }
        for attribute_name, data_type in attributes.items():
            result = self._add_attribute_to_layer(
                layer, attribute_name, data_type)
            if result:
                layer.updateFields()

    @staticmethod
    def _get_attributes(feature, field_names):
        """Get the attribute dict based on the feature and the field names.

        :param feature: The feature to be investigated.
        :type feature:

        :param field_names: The field names list.
        :type field_names: list

        :return: A lookup of the field values by field name.
        :rtype: dict
        """
        attributes = feature.attributes()
        attribute_dict = dict(zip(field_names, attributes))
        return attribute_dict

    @staticmethod
    def _area_contained(feature, layer):
        """Get the area if feature centroid is within layer.

        :param feature: A feature
        :type feature: QgsFeature

        :param layer: A feature
        :type layer: QgsFeature

        :returns: overlapping area
        :rtype: float
        """
        geometry_feature = feature.geometry()
        geometry_layer = layer.geometry()
        centroid = geometry_feature.centroid()
        if not centroid.within(geometry_layer):
            return 0
        return geometry_feature.area()

    @staticmethod
    def _get_levels(attributes, levels_attribute):
        """Try to extract the levels from the attributes dict as an int.

        .. note:: If the levels of this building has not been set we will
            assume it to be 1.

        :param attributes: The attributes dict from the feature.
        :type attributes: dict

        :param levels_attribute: The name of the column that contains layer
            information.
        :type levels_attribute: basestring

        :returns: The number of levels (default 1).
        :rtype: int
        """
        levels = attributes[levels_attribute]
        # get the number of levels as a integer
        if not levels:
            return 1
        try:
            # get the number of levels as an integer
            return int(levels)
        except ValueError:
            return 1

    @staticmethod
    def _get_residential_proportion(attributes, building_use):
        """The proportion of the surface to be used for residential.

        :param attributes: The feature's attribute dictionary lookup.
        :type attributes: dict

        :param building_use: The name of the attribute containing the
            building use.
        :type building_use: basestring

        :returns: The residential proprtion
        :rtype: int, float

        .. note:: The residential proportion is based on the building type.
            Currently the types 'Residential' and 'House' are considered to be
            used 100% for residential.
        """
        use = attributes[building_use]
        if use in ['Residential', 'residential', 'house', 'House']:
            return 1
        # if use == '' or use is None or isinstance(use, QPyNullVariant):
        #     # Default to residential, if it is unclassified
        #     return 1
        return 0

    @staticmethod
    def _feature_fully_in_extent(layer, feature):
        """Determine whether the feature is fully within the layer's extent.

        :param layer: The layer to be considered.
        :type layer: QgsVectorLayer

        :param feature: The feature to be considered.
        :type feature:

        :return: The result of the test.
        :rtype: bool

        ...Note: This operation uses the internal centroid.

        """
        extent = layer.extent()
        geometry_extent = QgsGeometry.fromRect(extent)
        geometry_feature = feature.geometry()
        intersection = geometry_feature.intersection(geometry_extent)
        if intersection.area() < geometry_feature.area():
            return False
        return True

    def estimate_people_in_buildings(self):
        """Estimate the number of people in each building based on the census.

        .. note:: The user selects both a buildings layer and a census areas
            layer. The building layer is expected to have a column with
            building usages. In this column the values: 'Residential',
            'residential', 'house' and 'House' are considered to have a 100%
            residential proportion. All other types are considered to not have
            contributed to the census counts. The buildings layer is
            furthermore expected to to have a levels column. This column
            contains the number of levels that a given structure has. A blank
            value is assumed to be 1. The building layer is a vector layer
            with building features. The census area should have a column with
            the people counts.

            People in buildings is calculated by the following formulae:

            residential area = surface area * levels * residential proportion

                                 residential area * people in census area
            number of people =  --------------------------------------------
                                    total residential surface area

            Since this calculation may result in a fractional result, 2
            columns are created. One with the exact calculated value used in
            further calculations. The other with whole numbers to be used by
            the user directly.
        """
        building_layer_name = self.buildingLayerComboBox.currentText()
        buildings_layer = self._select_layer_by_name(building_layer_name)
        building_use_column = self.usageColumnComboBox.currentText()
        building_level_column = self.levelsColumnComboBox.currentText()
        population_layer_name = self.censusLayerComboBox.currentText()
        population_layer = self._select_layer_by_name(population_layer_name)
        population_column = self.populationCountComboBox.currentText()
        new_layer = self.newLayerCheckBox.isChecked()
        new_layer_name = self.newLayerLineEdit.text()
        if not buildings_layer or not population_layer:
            return

        if new_layer:
            buildings_layer = self.iface.addVectorLayer(
                buildings_layer.source(),
                new_layer_name,
                buildings_layer.providerType())

        self.add_population_attribute(buildings_layer)
        field_names_population = self._get_field_names(population_layer)
        field_names = self._get_field_names(buildings_layer)
        field_names += [People_Calculated, People_Rounded]

        #TODO: Make a better progress estimator
        self.progressBar.setValue(0)
        progress = 1
        progress_increment = 100.0/population_layer.featureCount()

        for population_area in population_layer.getFeatures():
            progress += progress_increment
            self.progressBar.setValue(progress)
            population_attributes = self._get_attributes(
                population_area,
                field_names_population
            )
            total_effective_area = 0
            building_lookup = {}
            population_count = population_attributes[population_column]
            for building in buildings_layer.getFeatures():
                area = self._area_contained(building, population_area)
                if not area:
                    continue
                attributes = self._get_attributes(building, field_names)
                levels = self._get_levels(attributes, building_level_column)
                residential_proportion = self._get_residential_proportion(
                    attributes,
                    building_use_column)
                if not residential_proportion:
                    continue
                effective_area = area * levels * residential_proportion
                total_effective_area += effective_area
                building_lookup[building] = effective_area
            if not total_effective_area:
                continue
            if not isinstance(population_count, (int, float, long)):
                continue
            population_density = population_count / total_effective_area
            buildings_layer.startEditing()
            for (building, area) in building_lookup.items():
                people_in_building = population_density * area
                building[People_Calculated] = people_in_building
                building[People_Rounded] = people_in_building
                buildings_layer.updateFeature(building)
            buildings_layer.commitChanges()
        self.progressBar.setValue(100)

