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
__author__ = 'christian@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '12/02/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QVariant  # , QPyNullVariant
from qgis.core import QgsField
from qgis.core import QgsGeometry

from safe.utilities.resources import get_ui_class

FORM_CLASS = get_ui_class('people_in_buildings_base.ui')

People_Calculated = "People_Dec"
People_Rounded = "People_Rnd"


class PeopleInBuildingsDialog(QtGui.QDialog, FORM_CLASS):
    """Options dialog for the InaSAFE plugin."""

    def __init__(self, iface, parent=None):
        """Constructor for the dialog.

        :param iface: A Quantum GIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param parent: Parent widget of this dialog
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
            self.handle_building_layer)
        self.censusLayerComboBox.currentIndexChanged['QString'].connect(
            self.handle_census_layer)

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
        self.handle_building_layer(self.buildingLayerComboBox.currentText())
        self.handle_census_layer(self.censusLayerComboBox.currentText())

    def _select_layer_by_name(self, layer_name):
        """Get a layer by name
        :param layer_name: The layer's name
        :type layer_name: basestring

        :returns: The layer that has the appropriate name or none
        :rtype: QgsMapLayer, None
        """
        layers = self._get_layers()
        layer_names = [layer.name() for layer in layers]
        if not layer_name in layer_names:
            return None
        index = layer_names.index(layer_name)
        return layers[index]

    def _get_layers(self):
        layers = self.iface.legendInterface().layers()
        return layers

    def _get_layer_names(self):
        layers = self._get_layers()
        layer_names = [l.name() for l in layers]
        return layer_names

    @staticmethod
    def _get_field_names(layer):
        field_names = [field.name() for field in layer.pendingFields()]
        return field_names

    def handle_building_layer(self, layer_name):
        layer = self._select_layer_by_name(layer_name)
        if layer is None:
            return
        field_names = self._get_field_names(layer)
        self._update_combobox(self.usageColumnComboBox, field_names)
        self._update_combobox(self.levelsColumnComboBox, field_names)

    def handle_census_layer(self, layer_name):
        layer = self._select_layer_by_name(layer_name)
        if layer is None:
            return
        field_names = self._get_field_names(layer)
        self._update_combobox(self.populationCountComboBox, field_names)

    @staticmethod
    def _update_combobox(combobox, options):
        """Shorthand for clearing and loading options (this happens a lot)
        """
        combobox.clear()
        combobox.addItems(options)

    @staticmethod
    def _add_attribute_to_layer(layer, attribute_name, data_type):
        provider = layer.dataProvider()
        # Check if attribute is already there, return "-1" if not
        ind = provider.fieldNameIndex(attribute_name)
        if ind != -1:
            return False
        field = QgsField(attribute_name, data_type)
        result = provider.addAttributes([field])
        return result

    def add_population_attribute(self, layer):
        """Add people estimate columns/attributes to the output layer

        :param layer:
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
        attributes = feature.attributes()
        attribute_dict = dict(zip(field_names, attributes))
        return attribute_dict

    @staticmethod
    def _overlapping_area(feature, layer):
        """Get the area overlapping area if feature is within layer

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
        ..Note: If the levels of this building has not been set we will
        assume it to be 1.

        :param attributes: The attributes dict from the feature
        :type attributes: dict

        :param levels_attribute: The name of the column that contains layer
        information
        :type levels_attribute: basestring

        :returns: Number of levels (default 1)
        :rtype: int
        """
        levels = attributes[levels_attribute]
        # get the number of levels as a integer
        if not levels:
            return 1
        try:
            # get the number of levels as an intiger
            return int(levels)
        except ValueError:
            return 1

    @staticmethod
    def _get_residential_proportion(attributes, building_use):
        use = attributes[building_use]
        if use in ['Residential', 'residential', 'house', 'House']:
            return 1
        # if use == '' or use is None or isinstance(use, QPyNullVariant):
        #     # Default to residential, if it is unclassified
        #     return 1
        return 0

    @staticmethod
    def _feature_fully_in_extent(layer, feature):
        extent = layer.extent()
        geometry_extent = QgsGeometry.fromRect(extent)
        geometry_feature = feature.geometry()
        intersection = geometry_feature.intersection(geometry_extent)
        if intersection.area() < geometry_feature.area():
            return False
        return True

    def estimate_people_in_buildings(self):
        building_layer_name = self.buildingLayerComboBox.currentText()
        buildings_layer = self._select_layer_by_name(building_layer_name)
        building_use_column = self.usageColumnComboBox.currentText()
        building_level_column = self.levelsColumnComboBox.currentText()
        population_layer_name = self.censusLayerComboBox.currentText()
        population_layer = self._select_layer_by_name(population_layer_name)
        population_column = self.populationCountComboBox.currentText()
        new_layer = self.newLayerCheckBox.isChecked()
        new_layer_name = self.newLayerLineEdit.text()

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
        progress_increment = 100.0/len(
            [p for p in population_layer.getFeatures()])

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
                area = self._overlapping_area(building, population_area)
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
            population_density = population_count / total_effective_area
            buildings_layer.startEditing()
            for (building, area) in building_lookup.items():
                people_in_building = population_density * area
                building[People_Calculated] = people_in_building
                building[People_Rounded] = people_in_building
                buildings_layer.updateFeature(building)
            buildings_layer.commitChanges()
        self.progressBar.setValue(100)

