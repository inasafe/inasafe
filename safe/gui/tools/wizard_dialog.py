# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid **GUI InaSAFE Wizard Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""
__author__ = 'qgis@borysjurgiel.pl'
__revision__ = '$Format:%H$'
__date__ = '21/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import logging
import re
import json
from collections import OrderedDict
from sqlite3 import OperationalError

from qgis.core import (
    QgsCoordinateTransform,
    QgsBrowserModel,
    QgsDataItem,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsDataSourceURI,
    QgsMapLayerRegistry)

# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
# noinspection PyPackageRequirements
from PyQt4.QtCore import pyqtSignature, QSettings
# noinspection PyPackageRequirements
from PyQt4.QtGui import (
    QDialog,
    QListWidgetItem,
    QPixmap,
    QApplication,
    QSortFilterProxyModel)

# pylint: disable=F0401
from db_manager.db_plugins.postgis.connector import PostGisDBConnector
# pylint: enable=F0401

from safe import definitions
from safe.definitions import (
    layer_vector_point,
    layer_vector_line,
    layer_vector_polygon,
    layer_raster_continuous,
    layer_raster_classified)
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.analysis_handler import AnalysisHandler
from safe.utilities.gis import (
    is_raster_layer,
    is_point_layer,
    is_polygon_layer,
    layer_attribute_names)
from safe.utilities.utilities import (
    get_error_message,
    get_safe_impact_function)
from safe.defaults import get_defaults
from safe.common.exceptions import (
    HashNotFoundError,
    NoKeywordsFoundError,
    KeywordNotFoundError,
    InvalidParameterError,
    UnsupportedProviderError,
    InaSAFEError)
from safe.utilities.resources import get_ui_class, resources_path
from safe.impact_statistics.function_options_dialog import (
    FunctionOptionsDialog)


LOGGER = logging.getLogger('InaSAFE')

FORM_CLASS = get_ui_class('wizard_dialog_base.ui')

# Constants for categories
category_question = QApplication.translate(
    'WizardDialog',
    'By following the simple steps in this wizard, you can assign '
    'keywords to your layer: <b>%s</b>. First you need to define '
    'the category of your layer.')   # (layer name)


category_question_hazard = QApplication.translate(
    'WizardDialog',
    'You have selected a layer that has no keywords assigned. '
    'In the next steps you can assign keywords to that layer. '
    'First you need to confirm the layer represents a hazard.')

category_question_exposure = QApplication.translate(
    'WizardDialog',
    'You have selected a layer that has no keywords assigned. '
    'In the next steps you can assign keywords to that layer. '
    'First you need to confirm the layer represents an '
    'exposure.')

category_question_aggregation = QApplication.translate(
    'WizardDialog',
    'You have selected a layer that has no keywords assigned. '
    'In the next steps you can assign keywords to that layer. '
    'First you need to confirm the layer is an aggregation '
    'layer.')

# Constants for hazards
hazard_question = QApplication.translate(
    'WizardDialog',
    'What kind of <b>hazard</b> does this '
    'layer represent? The choice you make here will determine '
    'which impact functions this hazard layer can be used with. '
    'For example, if you choose <b>flood</b> you will be '
    'able to use this hazard layer with impact functions such '
    'as <b>flood impact on population</b>.')

# Constants for exposures
exposure_question = QApplication.translate(
    'WizardDialog',
    'What kind of <b>exposure</b> does this '
    'layer represent? The choice you make here will determine '
    'which impact functions this exposure layer can be used with. '
    'For example, if you choose <b>population</b> you will be '
    'able to use this exposure layer with impact functions such '
    'as <b>flood impact on population</b>.')

# Constants for data types
datatype_question = QApplication.translate(
    'WizardDialog',
    'You have selected <b>%s %s</b> '
    'for this raster layer. We need to know whether each cell '
    'in this raster represents a continuous '
    'value or a classified code.')   # (subcategory, category)

continuous_datatype_description = definitions.unit_continuous['description']

classified_datatype_description = definitions.unit_classified['description']

# Constants for units
unit_question = QApplication.translate(
    'WizardDialog',
    'You have selected <b>%s</b> '
    'for this <b>%s</b> layer type. We need to know what units the '
    'data are in. For example in a raster layer, each cell might '
    'represent depth in metres or depth in feet. If the dataset '
    'is a vector layer, each polygon might represent an inundated '
    'area, while areas with no polygon coverage would be assumed '
    'to be dry.')   # (subcategory, category)

# Constants for allow_resampling
allow_resampling_question = QApplication.translate(
    'WizardDialog',
    'You have selected <b>%s %s</b> for this <b>%s data</b> raster layer. '
    'For some exposure types you may want InaSAFE to not resample '
    'the raster to the hazard layer resolution during analyses. Please '
    'select the check box below if you want to set the <i>allow_resample</i> '
    'keyword to <i>False</i>.')   # (subcategory, category, data_type)

# Constants for subcategory-unit relations
# These texts below will be inserted as the fourth variable
# to the field_question_subcategory_unit constant.
# noinspection PyCallByClass
flood_metres_depth_question = QApplication.translate(
    'WizardDialog',
    'flood depth in meters')
flood_feet_depth_question = QApplication.translate(
    'WizardDialog',
    'flood depth in feet')
flood_wetdry_question = QApplication.translate(
    'WizardDialog',
    'flood extent as wet/dry')
tsunami_metres_depth_question = QApplication.translate(
    'WizardDialog',
    'tsunami depth in meters')
tsunami_feet_depth_question = QApplication.translate(
    'WizardDialog',
    'tsunami depth in feet')
tsunami_wetdry_question = QApplication.translate(
    'WizardDialog',
    'tsunami extent as wet/dry')
earthquake_mmi_question = QApplication.translate(
    'WizardDialog',
    'earthquake intensity in MMI')
tephra_kgm2_question = QApplication.translate(
    'WizardDialog',
    'tephra intensity in kg/m<sup>2</sup>')
volcano_volcano_categorical_question = QApplication.translate(
    'WizardDialog',
    'volcano hazard categorical level')
population_number_question = QApplication.translate(
    'WizardDialog',
    'the number of people')
population_density_question = QApplication.translate(
    'WizardDialog',
    'people density in people/km<sup>2</sup>')
road_road_type_question = QApplication.translate(
    'WizardDialog',
    'type for your road')
structure_building_type_question = QApplication.translate(
    'WizardDialog',
    'type for your building')

# Constants for field selection
# noinspection PyCallByClass
field_question_subcategory_unit = QApplication.translate(
    'WizardDialog',
    'You have selected a <b>%s %s</b> layer measured in '
    '<b>%s</b>, and the selected layer is a vector layer. Please '
    'select the attribute in this layer that represents %s.')
# (category, subcategory, unit, subcategory-unit relation))

# noinspection PyCallByClass,PyCallByClass
field_question_aggregation = QApplication.translate(
    'WizardDialog',
    'You have selected an aggregation layer, and it is a vector '
    'layer. Please select the attribute in this layer that represents '
    'names of the aggregation areas.')

# Constants for classify values for categorized units
# noinspection PyCallByClass
classify_question = QApplication.translate(
    'WizardDialog',
    'You have selected <b>%s %s</b> measured in <b>%s</b> categorical '
    'unit, and the data column is <b>%s</b>. Below on the left you '
    'can see all unique values found in that column. Please drag them '
    'to the right panel in order to classify them to appropriate '
    'categories.')   # (subcategory, category, unit, field)

# Constants for the layer origin selector
layer_constraint_memo = QApplication.translate(
    'WizardDialog',
    'Based on your selection of <b>%s %s %s</b> on the previous page, '
    'you should select a <b>%s</b> layer containing <b>%s</b> data now.'
    )  # (subcategory, data_type, category, data_type2, subcategory )

# Constants for the browser
# noinspection PyCallByClass
create_postGIS_connection_first = QApplication.translate(
    'WizardDialog',
    '<html>In order to use PostGIS layers, please close the wizard, '
    'create a new PostGIS connection and run the wizard again. <br/><br/> '
    'You can manage connections under the '
    '<i>Layer</i> > <i>Add Layer</i> > <i>Add PostGIS Layers</i> '
    'menu.</html>')

# Constants: tab numbers for steps

step_kw_category = 1
step_kw_subcategory = 2
step_kw_datatype = 3
step_kw_unit = 4
step_kw_field = 5
step_kw_resample = 6
step_kw_classify = 7
step_kw_aggregation = 8
step_kw_source = 9
step_kw_title = 10
step_fc_function_1 = 11
step_fc_function_2 = 12
step_fc_function_3 = 13
step_fc_hazlayer_origin = 14
step_fc_hazlayer_from_canvas = 15
step_fc_hazlayer_from_browser = 16
step_fc_explayer_origin = 17
step_fc_explayer_from_canvas = 18
step_fc_explayer_from_browser = 19
step_fc_disjoint_layers = 20
step_fc_agglayer_origin = 21
step_fc_agglayer_from_canvas = 22
step_fc_agglayer_from_browser = 23
step_fc_agglayer_disjoint = 24
step_fc_extent = 25
step_fc_extent_disjoint = 26
step_fc_params = 27
step_fc_summary = 28
step_fc_analysis = 29

# Aggregations' keywords
DEFAULTS = get_defaults()
female_ratio_attribute_key = DEFAULTS['FEMALE_RATIO_ATTR_KEY']
female_ratio_default_key = DEFAULTS['FEMALE_RATIO_KEY']
youth_ratio_attribute_key = DEFAULTS['YOUTH_RATIO_ATTR_KEY']
youth_ratio_default_key = DEFAULTS['YOUTH_RATIO_KEY']
adult_ratio_attribute_key = DEFAULTS['ADULT_RATIO_ATTR_KEY']
adult_ratio_default_key = DEFAULTS['ADULT_RATIO_KEY']
elderly_ratio_attribute_key = DEFAULTS['ELDERLY_RATIO_ATTR_KEY']
elderly_ratio_default_key = DEFAULTS['ELDERLY_RATIO_KEY']

# Data roles
RoleFunctions = QtCore.Qt.UserRole
RoleHazard = QtCore.Qt.UserRole + 1
RoleExposure = QtCore.Qt.UserRole + 2
RoleHazardConstraint = QtCore.Qt.UserRole + 3
RoleExposureConstraint = QtCore.Qt.UserRole + 4


def get_question_text(constant):
    """Find a constant by name and return its value.

    :param constant: The name of the constant to look for.
    :type constant: string

    :returns: The value of the constant or red error message.
    :rtype: string
    """
    try:
        # TODO Eval = bad
        return eval(constant)  # pylint: disable=eval-used
    except NameError:
        return '<b>MISSING CONSTANT: %s</b>' % constant


class LayerBrowserProxyModel(QSortFilterProxyModel):

    """Proxy model for hiding unsupported branches in the layer browser."""

    def __init__(self, parent):
        """Constructor for the model.

        :param parent: Parent widget of this model.
        :type parent: QWidget
        """
        QSortFilterProxyModel.__init__(self, parent)

    def filterAcceptsRow(self, source_row, source_parent):
        """The filter method

        .. note:: This filter hides top-level items of unsupported branches.

           Enabled root items: QgsDirectoryItem, QgsFavouritesItem,
           QgsPGRootItem.

           Disabled root items: QgsMssqlRootItem, QgsSLRootItem,
           QgsOWSRootItem, QgsWCSRootItem, QgsWFSRootItem, QgsWMSRootItem.

        :param source_row: Parent widget of the model
        :type source_row: int

        :param source_parent: Parent item index
        :type source_parent: QModelIndex

        :returns: Item validation result
        :rtype: bool
        """
        source_index = self.sourceModel().index(source_row, 0, source_parent)
        item = self.sourceModel().dataItem(source_index)
        if item.metaObject().className() in ['QgsMssqlRootItem',
                                             'QgsSLRootItem',
                                             'QgsOWSRootItem',
                                             'QgsWCSRootItem',
                                             'QgsWFSRootItem',
                                             'QgsWMSRootItem']:
            return False
        return True


class WizardDialog(QDialog, FORM_CLASS):

    """Dialog implementation class for the InaSAFE wizard."""

    def __init__(self, parent=None, iface=None, dock=None):
        """Constructor for the dialog.

        .. note:: In QtDesigner the advanced editor's predefined keywords
           list should be shown in english always, so when adding entries to
           cboKeyword, be sure to choose :safe_qgis:`Properties<<` and untick
           the :safe_qgis:`translatable` property.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget

        :param iface: QGIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param dock: Dock widget instance that we can notify of changes to
            the keywords. Optional.
        :type dock: Dock
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle('InaSAFE')
        # Note the keys should remain untranslated as we need to write
        # english to the keywords file.
        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        self.dock = dock
        self.suppress_warning_dialog = False
        self.set_tool_tip()
        # Set icons
        self.lblMainIcon.setPixmap(
            QPixmap(resources_path('img', 'icons', 'icon.svg')))
        self.lblIconDisjoint_1.setPixmap(
            QPixmap(resources_path('img', 'wizard', 'icon-stop.svg')))
        self.lblIconDisjoint_2.setPixmap(
            QPixmap(resources_path('img', 'wizard', 'icon-stop.svg')))
        self.lblIconDisjoint_3.setPixmap(
            QPixmap(resources_path('img', 'wizard', 'icon-stop.svg')))
        # Set models for browsers
        browser_model = QgsBrowserModel()
        proxy_model = LayerBrowserProxyModel(self)
        proxy_model.setSourceModel(browser_model)
        self.tvBrowserHazard.setModel(proxy_model)

        browser_model = QgsBrowserModel()
        proxy_model = LayerBrowserProxyModel(self)
        proxy_model.setSourceModel(browser_model)
        self.tvBrowserExposure.setModel(proxy_model)

        browser_model = QgsBrowserModel()
        proxy_model = LayerBrowserProxyModel(self)
        proxy_model.setSourceModel(browser_model)
        self.tvBrowserAggregation.setModel(proxy_model)

        self.parameter_dialog = None

        self.keyword_io = KeywordIO()
        self.twParams = None

        # TODO document it:
        self.is_selected_layer_keywordless = False
        self.parent_step = None

        self.pbnBack.setEnabled(False)
        self.pbnNext.setEnabled(False)

        # noinspection PyUnresolvedReferences
        self.tvBrowserHazard.selectionModel().selectionChanged.connect(
            self.tvBrowserHazard_selection_changed)
        self.tvBrowserExposure.selectionModel().selectionChanged.connect(
            self.tvBrowserExposure_selection_changed)
        self.tvBrowserAggregation.selectionModel().selectionChanged.connect(
            self.tvBrowserAggregation_selection_changed)
        self.treeClasses.itemChanged.connect(self.update_dragged_item_flags)
        self.lblDefineExtentNow.linkActivated.connect(
            self.lblDefineExtentNow_clicked)
        self.pbnCancel.released.connect(self.reject)

        # string constants
        self.global_default_string = definitions.global_default_attribute[
            'name']
        self.global_default_data = definitions.global_default_attribute['id']
        self.do_not_use_string = definitions.do_not_use_attribute['name']
        self.do_not_use_data = definitions.do_not_use_attribute['id']
        self.defaults = get_defaults()

        # Initialize attributes
        self.existing_keywords = None
        self.layer = None
        self.hazard_layer = None
        self.exposure_layer = None
        self.aggregation_layer = None
        self.if_params = None
        self.analysis_handler = None

    def set_keywords_creation_mode(self, layer=None):
        """Set the Wizard to the Keywords Creation mode
        :param layer: Layer to set the keywords for
        :type layer: QgsMapLayer
        """
        self.lblSubtitle.setText(self.tr('Keywords creation...'))
        self.layer = layer or self.iface.mapCanvas().currentLayer()
        try:
            self.existing_keywords = self.keyword_io.read_keywords(self.layer)
            if 'category' not in self.existing_keywords:
                self.existing_keywords = None
        except (HashNotFoundError,
                OperationalError,
                NoKeywordsFoundError,
                KeywordNotFoundError,
                InvalidParameterError,
                UnsupportedProviderError):
            self.existing_keywords = None

        self.set_widgets_step_kw_category()
        self.go_to_step(step_kw_category)

    def set_function_centric_mode(self):
        """Set the Wizard to the Function Centric mode"""
        self.lblSubtitle.setText(self.tr('Guided impact assessment wizard...'))
        new_step = step_fc_function_1
        self.set_widgets_step_fc_function_1()
        self.pbnNext.setEnabled(self.is_ready_to_next_step(new_step))
        self.go_to_step(new_step)

    def categories_for_layer(self, layer_type, data_type):
        """Return a list of valid categories for a layer.

        This method is used to determine if a given layer can be used as a
        hazard, exposure or aggregation layer.

        :param layer_type: The type for this layer.
        :type layer_type: str

        :param data_type: The data_type for this layer.
        :type data_type: str

        :returns: A list where each value represents a valid category.
        :rtype: list
        """
        if layer_type == 'raster':
            # Ignore data_type and collect categories for both continuous
            # and classified rasters. Sort hazard prior to exposure.
            categories = []
            for data_type in ['continuous', 'classified']:
                for c in ImpactFunctionManager().categories_for_layer(
                        'raster', data_type):
                    if c not in categories:
                        categories += [c]
        else:
            categories = ImpactFunctionManager().categories_for_layer(
                layer_type, data_type)
        return categories

    def subcategories_for_layer(self, category_id, layer_type, data_type):
        """Return a list of valid subcategories for a layer.

        This method is used to determine if a given layer can be used as a
        hazard, exposure or aggregation layer.

        :param category_id: The category for this layer.
        :type category_id: str

        :param layer_type: The type for this layer.
        :type layer_type: str

        :param data_type: The data_type for this layer.
        :type data_type: str

        :returns: A list where each value represents a valid subcategory.
        :rtype: list
        """
        if layer_type == 'raster':
            # Ignore data_type and collect subcategories for both continuous
            # and classified rasters. Sort hazard prior to exposure.
            subcategories = []
            for data_type in ['continuous', 'classified']:
                for sc in ImpactFunctionManager().subcategories_for_layer(
                        category_id, 'raster', data_type):
                    if sc not in subcategories:
                        subcategories += [sc]
        else:
            subcategories = ImpactFunctionManager().subcategories_for_layer(
                category_id, layer_type, data_type)
        return subcategories

    # ===========================
    # STEP_KW_CATEGORY
    # ===========================

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_lstCategories_itemSelectionChanged(self):
        """Update category description label and subcategory widgets.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        self.lstSubcategories.clear()
        category = self.selected_category()
        # Exit if no selection
        if not category:
            return
        # Set description label
        self.lblDescribeCategory.setText(category["description"])
        self.lblIconCategory.setPixmap(QPixmap(
            resources_path('img', 'wizard', 'keyword-category-%s.svg'
                           % (category['id'] or 'notset'))))
        # Enable the next button
        self.pbnNext.setEnabled(True)

    def selected_category(self):
        """Obtain the category selected by user.

        :returns: Metadata of the selected category.
        :rtype: dict, None
        """
        item = self.lstCategories.currentItem()

        try:
            # pylint: disable=eval-used
            return eval(item.data(QtCore.Qt.UserRole))
            # pylint: enable=eval-used
        except (AttributeError, NameError):
            return None

    def set_widgets_step_kw_category(self):
        """Set widgets on the Category tab."""
        self.lstCategories.clear()
        self.lstSubcategories.clear()
        self.lstDataTypes.clear()
        self.lstUnits.clear()
        self.lblDescribeCategory.setText('')
        self.lblIconCategory.setPixmap(QPixmap())
        self.lblSelectCategory.setText(
            category_question % self.layer.name())
        categories = self.categories_for_layer(
            self.get_layer_type(), self.get_data_type())
        if self.get_data_type() == 'polygon':
            categories += ['aggregation']
        for category in categories:
            if type(category) != dict:
                # pylint: disable=eval-used
                category = eval('definitions.%s_definition' % category)
                # pylint: enable=eval-used
            item = QListWidgetItem(category['name'], self.lstCategories)
            item.setData(QtCore.Qt.UserRole, unicode(category))
            self.lstCategories.addItem(item)

        # Set values based on existing keywords (if already assigned)
        category_keyword = self.get_existing_keyword('category')
        if category_keyword == 'postprocessing':
            category_keyword = 'aggregation'
        if category_keyword:
            categories = []
            for index in xrange(self.lstCategories.count()):
                item = self.lstCategories.item(index)
                # pylint: disable=eval-used
                category = eval(item.data(QtCore.Qt.UserRole))
                # pylint: enable=eval-used
                categories.append(category['id'])
            if category_keyword in categories:
                self.lstCategories.setCurrentRow(
                    categories.index(category_keyword))

        self.auto_select_one_item(self.lstCategories)

    # ===========================
    # STEP_KW_SUBCATEGORY
    # ===========================

    # noinspection PyPep8Naming
    def on_lstSubcategories_itemSelectionChanged(self):
        """Update subcategory description label and unit widgets.

        .. note:: This is an automatic Qt slot
           executed when the subcategory selection changes.
        """
        self.lstDataTypes.clear()
        self.lstUnits.clear()
        subcategory = self.selected_subcategory()
        # Exit if no selection
        if not subcategory:
            return
        # Set description label
        self.lblDescribeSubcategory.setText(subcategory['description'])
        self.lblIconSubcategory.setPixmap(QPixmap(
            resources_path('img', 'wizard', 'keyword-subcategory-%s.svg'
                           % (subcategory['id'] or 'notset'))))
        # Enable the next button
        self.pbnNext.setEnabled(True)

    def selected_subcategory(self):
        """Obtain the subcategory selected by user.

        :returns: Metadata of the selected subcategory.
        :rtype: dict, None
        """
        item = self.lstSubcategories.currentItem()
        try:
            # pylint: disable=eval-used
            return eval(item.data(QtCore.Qt.UserRole))
            # pylint: enable=eval-used
        except (AttributeError, NameError):
            return None

    def set_widgets_step_kw_subcategory(self):
        """Set widgets on the Subcategory tab."""
        category = self.selected_category()
        self.lstSubcategories.clear()
        self.lstDataTypes.clear()
        self.lstUnits.clear()
        self.lblDescribeSubcategory.setText('')
        self.lblIconSubcategory.setPixmap(QPixmap())
        self.lblSelectSubcategory.setText(
            get_question_text('%s_question' % category['id']))
        for i in self.subcategories_for_layer(
                category['id'], self.get_layer_type(), self.get_data_type()):
            item = QListWidgetItem(i['name'], self.lstSubcategories)
            item.setData(QtCore.Qt.UserRole, unicode(i))
            self.lstSubcategories.addItem(item)

        # Set values based on existing keywords (if already assigned)
        subcategory_keyword = self.get_existing_keyword('subcategory')
        if subcategory_keyword:
            subcategories = []
            for index in xrange(self.lstSubcategories.count()):
                item = self.lstSubcategories.item(index)
                # pylint: disable=eval-used
                subcategory = eval(item.data(QtCore.Qt.UserRole))
                # pylint: enable=eval-used
                subcategories.append(subcategory['id'])
            if subcategory_keyword in subcategories:
                self.lstSubcategories.setCurrentRow(
                    subcategories.index(subcategory_keyword))

        self.auto_select_one_item(self.lstSubcategories)

    # ===========================
    # STEP_KW_DATATYPE
    # ===========================

    # noinspection PyPep8Naming
    def on_lstDataTypes_itemSelectionChanged(self):
        """Update data type description label and unit widgets.

        .. note:: This is an automatic Qt slot
           executed when the subcategory selection changes.
        """
        self.lstUnits.clear()
        # Set description label
        if self.selected_datatype() == 'continuous':
            self.lblDescribeDataType.setText(continuous_datatype_description)
        elif self.selected_datatype() == 'classified':
            self.lblDescribeDataType.setText(classified_datatype_description)
        else:
            self.lblDescribeDataType.setText('')
            return
        # Enable the next button
        self.pbnNext.setEnabled(True)

    def selected_datatype(self):
        """Obtain the data type selected by user.
        :returns: id of the selected datatype.
        :rtype: string, None
        """
        if self.lstDataTypes.selectedItems():
            item = self.lstDataTypes.currentItem()
        else:
            return None
        try:
            return item.data(QtCore.Qt.UserRole)
        except (AttributeError, NameError):
            return None

    def set_widgets_step_kw_datatype(self):
        """Set widgets on the DataType tab."""
        category = self.selected_category()
        subcategory = self.selected_subcategory()
        self.lblSelectDataType .setText(
            datatype_question % (subcategory['name'], category['name']))
        self.lblDescribeDataType.setText('')
        self.lstDataTypes.clear()
        self.lstUnits.clear()
        self.lstFields.clear()
        data_types = ['continuous', 'classified']
        for data_type in data_types:
            item = QListWidgetItem(data_type, self.lstDataTypes)
            item.setData(QtCore.Qt.UserRole, data_type)
            self.lstUnits.addItem(item)

        # Set value to existing keyword or default value
        datatype_keyword = self.get_existing_keyword('data_type')
        if datatype_keyword in data_types:
            indx = data_types.index(datatype_keyword)
        else:
            indx = data_types.index('continuous')  # default
        self.lstDataTypes.setCurrentRow(indx)

    # ===========================
    # STEP_KW_UNIT
    # ===========================

    # noinspection PyPep8Naming
    def on_lstUnits_itemSelectionChanged(self):
        """Update unit description label and field widgets.

        .. note:: This is an automatic Qt slot
           executed when the unit selection changes.
        """
        self.lstFields.clear()
        unit = self.selected_unit()
        # Exit if no selection
        if not unit:
            return
        self.lblDescribeUnit.setText(unit['description'])
        # Enable the next button
        self.pbnNext.setEnabled(True)

    def selected_unit(self):
        """Obtain the unit selected by user.

        :returns: Metadata of the selected unit.
        :rtype: dict, None
        """
        item = self.lstUnits.currentItem()
        try:
            # pylint: disable=eval-used
            return eval(item.data(QtCore.Qt.UserRole))
            # pylint: enable=eval-used
        except (AttributeError, NameError):
            return None

    def set_widgets_step_kw_unit(self):
        """Set widgets on the Unit tab."""
        category = self.selected_category()
        subcategory = self.selected_subcategory()
        self.lblSelectUnit.setText(
            unit_question % (subcategory['name'], category['name']))
        self.lblDescribeUnit.setText('')
        self.lstUnits.clear()
        self.lstFields.clear()
        for unit_for_layer in ImpactFunctionManager().units_for_layer(
                subcategory['id'],
                self.get_layer_type(), self.get_data_type()):
            if (self.get_layer_type() == 'raster' and
                    'constraint' in unit_for_layer and
                    unit_for_layer['constraint'] == 'categorical'):
                continue
            else:
                item = QListWidgetItem(unit_for_layer['name'], self.lstUnits)
                item.setData(QtCore.Qt.UserRole, unicode(unit_for_layer))
                self.lstUnits.addItem(item)

        # Set values based on existing keywords (if already assigned)
        unit_id = self.get_existing_keyword('unit')
        unit_id = definitions.old_to_new_unit_id(unit_id)
        if unit_id:
            units = []
            for index in xrange(self.lstUnits.count()):
                item = self.lstUnits.item(index)
                # pylint: disable=eval-used
                unit = eval(item.data(QtCore.Qt.UserRole))
                # pylint: enable=eval-used
                units.append(unit['id'])
            if unit_id in units:
                self.lstUnits.setCurrentRow(units.index(unit_id))

        self.auto_select_one_item(self.lstUnits)

    # ===========================
    # STEP_KW_FIELD
    # ===========================

    # noinspection PyPep8Naming
    def on_lstFields_itemSelectionChanged(self):
        """Update field description label and unlock the Next button.

        .. note:: This is an automatic Qt slot
           executed when the field selection changes.
        """
        self.treeClasses.clear()
        field = self.selected_field()
        # Exit if no selection
        if not field:
            return

        fields = self.layer.dataProvider().fields()
        field_type = fields.field(field).typeName()
        field_index = fields.indexFromName(self.selected_field())
        unique_values = self.layer.uniqueValues(field_index)[0:48]
        unique_values_str = [i and unicode(i) or 'NULL' for i in unique_values]
        if unique_values != self.layer.uniqueValues(field_index):
            unique_values_str += ['...']
        desc = '<br/>%s: %s<br/><br/>' % (self.tr('Field type'), field_type)
        desc += self.tr('Unique values: %s') % ', '.join(unique_values_str)
        self.lblDescribeField.setText(desc)
        # Enable the next button
        self.pbnNext.setEnabled(True)

    def selected_field(self):
        """Obtain the field selected by user.

        :returns: Keyword of the selected field.
        :rtype: string, None
        """
        item = self.lstFields.currentItem()
        if item:
            return item.text()
        else:
            return None

    def set_widgets_step_kw_field(self):
        """Set widgets on the Field tab."""
        category = self.selected_category()
        subcategory = self.selected_subcategory()
        unit = self.selected_unit()
        if subcategory and unit:
            subcategory_unit_relation = get_question_text(
                '%s_%s_question' % (subcategory['id'], unit['id']))
        else:
            subcategory_unit_relation = self.tr(
                '<b><font color="red">ERROR! '
                'Missing subcategory or unit!</font></b>')
        if category['id'] == 'aggregation':
            question_text = field_question_aggregation
        else:
            # unique values, continuous or categorical data
            question_text = field_question_subcategory_unit % (
                category['name'],
                subcategory['name'],
                unit['name'],
                subcategory_unit_relation)
        self.lblSelectField.setText(question_text)
        self.lstFields.clear()
        default_item = None
        for field in self.layer.dataProvider().fields():
            field_name = field.name()
            item = QListWidgetItem(field_name, self.lstFields)
            item.setData(QtCore.Qt.UserRole, field_name)
            # Select the item if it match the unit's default_attribute
            if unit and unit['id'] == 'building_generic':
                pass
            else:
                if unit and 'default_attribute' in unit \
                        and field_name == unit['default_attribute']:
                    default_item = item
                # For continuous data, gray out id, gid, fid and text fields
                if unit and unit['constraint'] == 'continuous':
                    field_type = field.type()
                    if field_type > 9 or re.match(
                            '.{0,2}id$', field_name, re.I):
                        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
        if default_item:
            self.lstFields.setCurrentItem(default_item)
        self.lblDescribeField.clear()

        # Set values based on existing keywords (if already assigned)
        if self.selected_category()['id'] != 'aggregation':
            field = self.get_existing_keyword('field')
        else:
            field = self.get_existing_keyword('aggregation attribute')
        if field:
            fields = []
            for index in xrange(self.lstFields.count()):
                fields.append(str(self.lstFields.item(index).text()))
            if field in fields:
                self.lstFields.setCurrentRow(fields.index(field))
        self.auto_select_one_item(self.lstFields)

    # ===========================
    # STEP_KW_RESAMPLE
    # ===========================

    def selected_allowresample(self):
        """Obtain the allow_resample state selected by user.

        .. note:: Returns none if not set or not relevant

        :returns: Value of the allow_resample or None for not-set.
        :rtype: boolean or None
        """
        if not is_raster_layer(self.layer):
            return None

        if self.selected_category()['id'] != 'exposure':
            return None

        # Only return false if checked, otherwise None for not-set.
        if self.chkAllowResample.isChecked():
            return False
        else:
            return None

    def set_widgets_step_kw_resample(self):
        """Set widgets on the Resample tab."""
        category = self.selected_category()
        subcategory = self.selected_subcategory()
        data_type = self.selected_datatype()
        self.lblSelectAllowResample.setText(
            allow_resampling_question % (subcategory['name'],
                                         category['name'], data_type))

    # ===========================
    # STEP_KW_CLASSIFY
    # ===========================

    # noinspection PyMethodMayBeStatic
    def update_dragged_item_flags(self, item, column):
        """Fix the drop flag after the item is dropped.

        Check if it looks like an item dragged from QListWidget
        to QTreeWidget and disable the drop flag.
        For some reasons the flag is set when dragging.

        :param item:
        :param column:

        .. note:: This is a slot executed when the item change.
        """

        # Treat var as unused
        _ = column

        if int(item.flags() & QtCore.Qt.ItemIsDropEnabled) \
                and int(item.flags() & QtCore.Qt.ItemIsDragEnabled):
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsDropEnabled)

    def selected_mapping(self):
        """Obtain the value-to-class mapping set by user.

        :returns: The complete mapping as a dict of lists.
        :rtype: dict
        """
        value_map = {}
        tree_clone = self.treeClasses.invisibleRootItem().clone()
        for tree_branch in tree_clone.takeChildren():
            value_list = []
            for tree_leaf in tree_branch.takeChildren():
                value_list += [tree_leaf.text(0)]
            if value_list:
                value_map[tree_branch.text(0)] = value_list
        return value_map

    def set_widgets_step_kw_classify(self):
        """Set widgets on the Classify tab."""
        category = self.selected_category()
        subcategory = self.selected_subcategory()
        unit = self.selected_unit()
        default_classes = unit['classes']
        field = self.selected_field()
        field_index = self.layer.dataProvider().fields().indexFromName(
            self.selected_field())
        field_type = self.layer.dataProvider().fields()[field_index].type()
        self.lblClassify.setText(classify_question %
                                 (subcategory['name'], category['name'],
                                  unit['name'], field.upper()))
        # Assign unique values to classes
        unassigned_values = list()
        assigned_values = dict()
        for default_class in default_classes:
            assigned_values[default_class['name']] = list()
        for value in self.layer.uniqueValues(field_index):
            value_as_string = value and unicode(value) or 'NULL'
            assigned = False
            for default_class in default_classes:
                if (field_type > 9
                    and value_as_string in default_class['string_defaults']) \
                        or (field_type < 10
                            and (default_class['numeric_default_min'] <=
                                 value < default_class[
                                 'numeric_default_max'])):
                    assigned_values[default_class['name']] += [value_as_string]
                    assigned = True
            if not assigned:
                # add to unassigned values list otherwise
                unassigned_values += [value_as_string]
        self.populate_classified_values(
            unassigned_values, assigned_values, default_classes)

        # Set values based on existing keywords (if already assigned)
        unit_id = self.get_existing_keyword('unit')
        unit_name = definitions.old_to_new_unit_id(unit_id)
        # Do not continue if user select different unit
        if unit_name != self.selected_unit()['name']:
            return

        field = self.get_existing_keyword('field')
        # Do not continue if user select different field
        if field != self.selected_field():
            return

        # Do not continue if there is no value_map in existing keywords
        value_map = self.get_existing_keyword('value_map')

        if value_map is None:
            return

        # Assign unique values to classes
        unit = self.selected_unit()
        default_classes = unit['classes']
        unassigned_values = list()
        assigned_values = dict()
        for default_class in default_classes:
            assigned_values[default_class['name']] = list()
        if type(value_map) == str:
            try:
                value_map = json.loads(value_map)
            except ValueError:
                return
        field_index = self.layer.dataProvider().fields().indexFromName(
            self.selected_field())
        for unique_value in self.layer.uniqueValues(field_index):
            value_as_string = (
                unique_value and unicode(unique_value) or 'NULL')
            # check in value map
            assigned = False
            for key, value in value_map.iteritems():
                if value_as_string in value:
                    assigned_values[key] += [value_as_string]
                    assigned = True
            if not assigned:
                unassigned_values += [value_as_string]
        self.populate_classified_values(
            unassigned_values, assigned_values, default_classes)

    def populate_classified_values(
            self, unassigned_values, assigned_values, default_classes):
        """Populate lstUniqueValues and treeClasses.from the parameters.

        :param unassigned_values: List of values that haven't been assigned
            to a class. It will be put in self.lstUniqueValues.
        :type unassigned_values: list

        :param assigned_values: Dictionary with class as the key and list of
            value as the the value of the dictionary. It will be put in
            self.treeClasses.
        :type assigned_values: dict

        :param default_classes: Default classes from unit.
        :type default_classes: list
        """
        # Populate the unique values list
        self.lstUniqueValues.clear()
        for value in unassigned_values:
            list_item = QtGui.QListWidgetItem(self.lstUniqueValues)
            list_item.setFlags(QtCore.Qt.ItemIsEnabled |
                               QtCore.Qt.ItemIsSelectable |
                               QtCore.Qt.ItemIsDragEnabled)
            list_item.setText(value)
            self.lstUniqueValues.addItem(list_item)
        # Populate assigned values tree
        self.treeClasses.clear()
        bold_font = QtGui.QFont()
        bold_font.setItalic(True)
        bold_font.setBold(True)
        bold_font.setWeight(75)
        self.treeClasses.invisibleRootItem().setFlags(
            QtCore.Qt.ItemIsEnabled)
        for default_class in default_classes:
            # Create branch for class
            tree_branch = QtGui.QTreeWidgetItem(self.treeClasses)
            tree_branch.setFlags(QtCore.Qt.ItemIsDropEnabled |
                                 QtCore.Qt.ItemIsEnabled)
            tree_branch.setExpanded(True)
            tree_branch.setFont(0, bold_font)
            tree_branch.setText(0, default_class['name'])
            if 'description' in default_class:
                tree_branch.setToolTip(0, default_class['description'])
            # Assign known values
            for value in assigned_values[default_class['name']]:
                tree_leaf = QtGui.QTreeWidgetItem(tree_branch)
                tree_leaf.setFlags(QtCore.Qt.ItemIsEnabled |
                                   QtCore.Qt.ItemIsSelectable |
                                   QtCore.Qt.ItemIsDragEnabled)
                tree_leaf.setText(0, value)

    # ===========================
    # STEP_KW_AGGREGATION
    # ===========================

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def on_cboFemaleRatioAttribute_currentIndexChanged(self):
        """Automatic slot executed when the female ratio attribute is changed.

        When the user changes the female ratio attribute
        (cboFemaleRatioAttribute), it will change the enabled value of
        dsbFemaleRatioDefault. If value is 'Use default', enable
        dsbFemaleRatioDefault. Otherwise, disabled it.
        """
        value = self.cboFemaleRatioAttribute.currentText()
        if value == self.global_default_string:
            self.dsbFemaleRatioDefault.setEnabled(True)
        else:
            self.dsbFemaleRatioDefault.setEnabled(False)

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def on_cboYouthRatioAttribute_currentIndexChanged(self):
        """Automatic slot executed when the youth ratio attribute is changed.

        When the user changes the youth ratio attribute
        (cboYouthRatioAttribute), it will change the enabled value of
        dsbYouthRatioDefault. If value is 'Use default', enable
        dsbYouthRatioDefault. Otherwise, disabled it.
        """
        value = self.cboYouthRatioAttribute.currentText()
        if value == self.global_default_string:
            self.dsbYouthRatioDefault.setEnabled(True)
        else:
            self.dsbYouthRatioDefault.setEnabled(False)

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def on_cboAdultRatioAttribute_currentIndexChanged(self):
        """Automatic slot executed when the adult ratio attribute is changed.

        When the user changes the adult ratio attribute
        (cboAdultRatioAttribute), it will change the enabled value of
        dsbAdultRatioDefault. If value is 'Use default', enable
        dsbAdultRatioDefault. Otherwise, disabled it.
        """
        value = self.cboAdultRatioAttribute.currentText()
        if value == self.global_default_string:
            self.dsbAdultRatioDefault.setEnabled(True)
        else:
            self.dsbAdultRatioDefault.setEnabled(False)

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def on_cboElderlyRatioAttribute_currentIndexChanged(self):
        """Automatic slot executed when the adult ratio attribute is changed.

        When the user changes the elderly ratio attribute
        (cboElderlyRatioAttribute), it will change the enabled value of
        dsbElderlyRatioDefault. If value is 'Use default', enable
        dsbElderlyRatioDefault. Otherwise, disabled it.
        """
        value = self.cboElderlyRatioAttribute.currentText()
        if value == self.global_default_string:
            self.dsbElderlyRatioDefault.setEnabled(True)
        else:
            self.dsbElderlyRatioDefault.setEnabled(False)

    def get_aggregation_attributes(self):
        """Obtain the value of aggregation attributes set by user.

        :returns: The key and value of aggregation attributes.
        :rtype: dict
        """
        aggregation_attributes = dict()

        current_index = self.cboFemaleRatioAttribute.currentIndex()
        data = self.cboFemaleRatioAttribute.itemData(current_index)
        aggregation_attributes[female_ratio_attribute_key] = data

        value = self.dsbFemaleRatioDefault.value()
        aggregation_attributes[female_ratio_default_key] = value

        current_index = self.cboYouthRatioAttribute.currentIndex()
        data = self.cboYouthRatioAttribute.itemData(current_index)
        aggregation_attributes[youth_ratio_attribute_key] = data

        value = self.dsbYouthRatioDefault.value()
        aggregation_attributes[youth_ratio_default_key] = value

        current_index = self.cboAdultRatioAttribute.currentIndex()
        data = self.cboAdultRatioAttribute.itemData(current_index)
        aggregation_attributes[adult_ratio_attribute_key] = data

        value = self.dsbAdultRatioDefault.value()
        aggregation_attributes[adult_ratio_default_key] = value

        current_index = self.cboElderlyRatioAttribute.currentIndex()
        data = self.cboElderlyRatioAttribute.itemData(current_index)
        aggregation_attributes[elderly_ratio_attribute_key] = data

        value = self.dsbElderlyRatioDefault.value()
        aggregation_attributes[elderly_ratio_default_key] = value

        return aggregation_attributes

    def age_ratios_are_valid(self):
        """Return true if the sum of age ratios is good, otherwise False.

        Good means their sum does not exceed 1.

        :returns: Tuple of boolean and float. Boolean represent good or not
            good, while float represent the summation of age ratio. If some
            ratio do not use global default, the summation is set to 0.
        :rtype: tuple

        """
        youth_ratio_index = self.cboYouthRatioAttribute.currentIndex()
        adult_ratio_index = self.cboAdultRatioAttribute.currentIndex()
        elderly_ratio_index = self.cboElderlyRatioAttribute.currentIndex()

        ratio_indexes = [
            youth_ratio_index, adult_ratio_index, elderly_ratio_index]

        if ratio_indexes.count(0) == len(ratio_indexes):
            youth_ratio_default = self.dsbYouthRatioDefault.value()
            adult_ratio_default = self.dsbAdultRatioDefault.value()
            elderly_ratio_default = self.dsbElderlyRatioDefault.value()

            sum_ratio_default = youth_ratio_default + adult_ratio_default
            sum_ratio_default += elderly_ratio_default
            if sum_ratio_default > 1:
                return False, sum_ratio_default
            else:
                return True, sum_ratio_default
        return True, 0

    # noinspection PyUnresolvedReferences,PyStatementEffect
    def populate_cbo_aggregation_attribute(
            self, ratio_attribute_key, cbo_ratio_attribute):
        """Populate the combo box cbo_ratio_attribute for ratio_attribute_key.

        :param ratio_attribute_key: A ratio attribute key that saved in
               keywords.
        :type ratio_attribute_key: str

        :param cbo_ratio_attribute: A combo box that wants to be populated.
        :type cbo_ratio_attribute: QComboBox
        """
        cbo_ratio_attribute.clear()
        ratio_attribute = self.get_existing_keyword(ratio_attribute_key)
        fields, attribute_position = layer_attribute_names(
            self.layer, [QtCore.QVariant.Double], ratio_attribute)

        cbo_ratio_attribute.addItem(
            self.global_default_string, self.global_default_data)
        cbo_ratio_attribute.addItem(
            self.do_not_use_string, self.do_not_use_data)
        for field in fields:
            cbo_ratio_attribute.addItem(field, field)
        # For backward compatibility, still use Use default
        if (ratio_attribute == self.global_default_data or
                ratio_attribute == self.tr('Use default')):
            cbo_ratio_attribute.setCurrentIndex(0)
        elif ratio_attribute == self.do_not_use_data:
            cbo_ratio_attribute.setCurrentIndex(1)
        elif ratio_attribute is None or attribute_position is None:
            # current_keyword was not found in the attribute table.
            # Use default
            cbo_ratio_attribute.setCurrentIndex(0)
        else:
            # + 2 is because we add use defaults and don't use
            cbo_ratio_attribute.setCurrentIndex(attribute_position + 2)

    def set_widgets_step_kw_aggregation(self):
        """Set widgets on the aggregation tab."""
        # Set values based on existing keywords (if already assigned)
        self.defaults = get_defaults()

        female_ratio_default = self.get_existing_keyword(
            female_ratio_default_key)
        if female_ratio_default:
            self.dsbFemaleRatioDefault.setValue(
                float(female_ratio_default))
        else:
            self.dsbFemaleRatioDefault.setValue(self.defaults['FEMALE_RATIO'])

        youth_ratio_default = self.get_existing_keyword(
            youth_ratio_default_key)
        if youth_ratio_default:
            self.dsbYouthRatioDefault.setValue(float(youth_ratio_default))
        else:
            self.dsbYouthRatioDefault.setValue(self.defaults['YOUTH_RATIO'])

        adult_ratio_default = self.get_existing_keyword(
            adult_ratio_default_key)
        if adult_ratio_default:
            self.dsbAdultRatioDefault.setValue(float(adult_ratio_default))
        else:
            self.dsbAdultRatioDefault.setValue(self.defaults['ADULT_RATIO'])

        elderly_ratio_default = self.get_existing_keyword(
            elderly_ratio_default_key)
        if elderly_ratio_default:
            self.dsbElderlyRatioDefault.setValue(float(elderly_ratio_default))
        else:
            self.dsbElderlyRatioDefault.setValue(
                self.defaults['ELDERLY_RATIO'])

        ratio_attribute_keys = [
            female_ratio_attribute_key,
            youth_ratio_attribute_key,
            adult_ratio_attribute_key,
            elderly_ratio_attribute_key]

        cbo_ratio_attributes = [
            self.cboFemaleRatioAttribute,
            self.cboYouthRatioAttribute,
            self.cboAdultRatioAttribute,
            self.cboElderlyRatioAttribute]

        for i in range(len(cbo_ratio_attributes)):
            self.populate_cbo_aggregation_attribute(
                ratio_attribute_keys[i], cbo_ratio_attributes[i])

    # ===========================
    # STEP_KW_SOURCE
    # ===========================

    def set_widgets_step_kw_source(self):
        """Set widgets on the Source tab."""
        # Just set values based on existing keywords
        source = self.get_existing_keyword('source')
        self.leSource.setText(source)
        source_scale = self.get_existing_keyword('source_scale')
        self.leSource_scale.setText(source_scale)
        source_date = self.get_existing_keyword('source_date')
        self.leSource_date.setText(source_date)
        source_url = self.get_existing_keyword('source_url')
        self.leSource_url.setText(source_url)

    # ===========================
    # STEP_KW_TITLE
    # ===========================

    # noinspection PyPep8Naming
    def on_leTitle_textChanged(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the title value changes.
        """
        self.pbnNext.setEnabled(bool(self.leTitle.text()))

    def set_widgets_step_kw_title(self):
        """Set widgets on the Title tab."""
        # Just set values based on existing keywords
        if self.layer:
            title = self.layer.name()
            self.leTitle.setText(title)

    # ===========================
    # STEP_FC_FUNCTION_1
    # ===========================

    def available_constraints(self):
        """Collect available layer_constraints from all impact functions.

        :returns: List of metadata of the available constraints.
        :rtype: list
        """
        return [layer_vector_point, layer_vector_line, layer_vector_polygon,
                layer_raster_continuous]

    def selected_functions_1(self):
        """Obtain functions available for hazarda an exposure selected by user.

        :returns: List of the available functions metadata.
        :rtype: list, None
        """
        selection = self.tblFunctions1.selectedItems()
        if len(selection) != 1:
            return []
        return selection[0].data(RoleFunctions)

    def selected_imfunc_constraints(self):
        """Obtain impact function constraints selected by user.

        :returns: Tuple of metadata of hazard, exposure,
            hazard layer constraints and exposure layer constraints
        :rtype: tuple
        """
        selection = self.tblFunctions1.selectedItems()
        if len(selection) != 1:
            return None, None, None, None

        h = selection[0].data(RoleHazard)
        e = selection[0].data(RoleExposure)

        selection = self.tblFunctions2.selectedItems()
        if len(selection) != 1:
            return h, e, None, None

        hc = selection[0].data(RoleHazardConstraint)
        ec = selection[0].data(RoleExposureConstraint)
        return h, e, hc, ec

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_tblFunctions1_itemSelectionChanged(self):
        """Choose selected hazard x exposure combination.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        functions = self.selected_functions_1()
        if not functions:
            self.lblAvailableFunctions1.clear()
        else:
            txt = "Available functions: " + ", ".join(
                [f['name'] for f in functions])
            self.lblAvailableFunctions1.setText(txt)

        # Clear the selection on the 2nd matrix
        self.tblFunctions2.clearContents()
        self.lblAvailableFunctions2.clear()
        self.pbnNext.setEnabled(True)

        # Put a dot to the selected cell - note there is no way
        # to center an icon without using a custom ItemDelegate
        selection = self.tblFunctions1.selectedItems()
        selItem = (len(selection) == 1) and selection[0] or None
        for row in range(self.tblFunctions1.rowCount()):
            for col in range(self.tblFunctions1.columnCount()):
                item = self.tblFunctions1.item(row, col)
                item.setText((item == selItem) and u'\u2022' or '')

    # pylint: disable=W0613
    def on_tblFunctions1_cellDoubleClicked(self, row, column):
        """Choose selected hazard x exposure combination and go ahead.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        self.pbnNext.click()
    # pylint: enable=W0613

    def set_widgets_step_fc_function_1(self):
        """Set widgets on the Impact Functions Table 1 tab."""
        self.tblFunctions1.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)
        self.tblFunctions1.verticalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)

        hazards = ImpactFunctionManager().get_available_hazards()
        # Remove 'generic' from hazards
        for h in hazards:
            if h['id'] == 'generic':
                hazards.remove(h)
        exposures = ImpactFunctionManager().get_available_exposures()

        self.lblAvailableFunctions1.clear()
        self.tblFunctions1.setColumnCount(len(hazards))
        self.tblFunctions1.setRowCount(len(exposures))
        for i in range(len(hazards)):
            h = hazards[i]
            item = QtGui.QTableWidgetItem()
            item.setIcon(QtGui.QIcon(
                resources_path('img', 'wizard', 'keyword-subcategory-%s.svg'
                               % (h['id'] or 'notset'))))
            item.setText(h['name'].capitalize())
            self.tblFunctions1.setHorizontalHeaderItem(i, item)
        for i in range(len(exposures)):
            e = exposures[i]
            item = QtGui.QTableWidgetItem()
            item.setIcon(QtGui.QIcon(
                resources_path('img', 'wizard', 'keyword-subcategory-%s.svg'
                               % (e['id'] or 'notset'))))
            item.setText(e['name'].capitalize())
            self.tblFunctions1.setVerticalHeaderItem(i, item)

        big_font = QtGui.QFont()
        big_font.setPointSize(80)

        for h in hazards:
            for e in exposures:
                item = QtGui.QTableWidgetItem()
                functions = ImpactFunctionManager(
                    ).get_functions_for_constraint(h, e)
                if len(functions):
                    bgcolor = QtGui.QColor(120, 255, 120)
                else:
                    bgcolor = QtGui.QColor(220, 220, 220)
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
                item.setBackground(QtGui.QBrush(bgcolor))
                item.setFont(big_font)
                item.setTextAlignment(QtCore.Qt.AlignCenter |
                                      QtCore.Qt.AlignHCenter)
                item.setData(RoleFunctions, functions)
                item.setData(RoleHazard, h)
                item.setData(RoleExposure, e)
                self.tblFunctions1.setItem(exposures.index(e),
                                           hazards.index(h),
                                           item)

    # ===========================
    # STEP_FC_FUNCTION_2
    # ===========================

    def selected_functions_2(self):
        """Obtain functions available for hazard and exposure selected by user.

        :returns: List of the available functions metadata.
        :rtype: list, None
        """
        selection = self.tblFunctions2.selectedItems()
        if len(selection) != 1:
            return []
        return selection[0].data(RoleFunctions)

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_tblFunctions2_itemSelectionChanged(self):
        """Choose selected hazard x exposure constraints combination.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        functions = self.selected_functions_2()
        if not functions:
            self.lblAvailableFunctions2.clear()
        else:
            txt = "Available functions: " + ", ".join(
                [f['name'] for f in functions])
            self.lblAvailableFunctions2.setText(txt)
        self.pbnNext.setEnabled(True)

        # Put a dot to the selected cell - note there is no way
        # to center an icon without using a custom ItemDelegate
        selection = self.tblFunctions2.selectedItems()
        selItem = (len(selection) == 1) and selection[0] or None
        for row in range(self.tblFunctions2.rowCount()):
            for col in range(self.tblFunctions2.columnCount()):
                item = self.tblFunctions2.item(row, col)
                item.setText((item == selItem) and u'\u2022' or '')

    # pylint: disable=W0613
    def on_tblFunctions2_cellDoubleClicked(self, row, column):
        """Choose selected hazard x exposure constraints combination
           and go ahead.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        self.pbnNext.click()
    # pylint: enable=W0613

    def set_widgets_step_fc_function_2(self):
        """Set widgets on the Impact Functions Table 2 tab."""

        self.tblFunctions2.clear()
        h, e, _hc, _ec = self.selected_imfunc_constraints()
        haz_datatypes = [layer_raster_continuous, layer_raster_classified,
                         layer_vector_polygon, layer_vector_point]
        exp_datatypes = [layer_raster_continuous, layer_vector_point,
                         layer_vector_line, layer_vector_polygon]
        self.tblFunctions2.setColumnCount(len(haz_datatypes))
        self.tblFunctions2.setRowCount(len(exp_datatypes))
        self.tblFunctions2.setHorizontalHeaderLabels(
            [i['data_type'].capitalize() if i['layer_type'] != 'raster'
             else ('%s %s' % (i['data_type'], i['layer_type'])).capitalize()
             for i in haz_datatypes])
        for i in range(len(exp_datatypes)):
            constr = exp_datatypes[i]
            item = QtGui.QTableWidgetItem()
            if constr['layer_type'] == 'raster':
                text = '%s\n%s' % (constr['data_type'], constr['layer_type'])
            else:
                text = constr['data_type']
            item.setText(text.capitalize())
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tblFunctions2.setVerticalHeaderItem(i, item)

        self.tblFunctions2.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)
        self.tblFunctions2.verticalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)

        big_font = QtGui.QFont()
        big_font.setPointSize(80)

        active_items = []
        for col in range(len(haz_datatypes)):
            for row in range(len(exp_datatypes)):
                hc = haz_datatypes[col]
                ec = exp_datatypes[row]
                functions = ImpactFunctionManager(
                    ).get_functions_for_constraint(h, e, hc, ec)
                item = QtGui.QTableWidgetItem()
                if len(functions):
                    bgcolor = QtGui.QColor(120, 255, 120)
                    active_items += [item]
                else:
                    bgcolor = QtGui.QColor(220, 220, 220)
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
                item.setBackground(QtGui.QBrush(bgcolor))
                item.setFont(big_font)
                item.setTextAlignment(QtCore.Qt.AlignCenter |
                                      QtCore.Qt.AlignHCenter)
                item.setData(RoleFunctions, functions)
                item.setData(RoleHazard, h)
                item.setData(RoleExposure, e)
                item.setData(RoleHazardConstraint, hc)
                item.setData(RoleExposureConstraint, ec)
                self.tblFunctions2.setItem(row, col, item)
        # Automatically select one item...
        if len(active_items) == 1:
            active_items[0].setSelected(True)
            # set focus, as the inactive selection style is gray
            self.tblFunctions2.setFocus()

    # ===========================
    # STEP_FC_FUNCTION_3
    # ===========================

    # noinspection PyPep8Naming
    def on_lstFunctions_itemSelectionChanged(self):
        """Update function description label

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        imfunc = self.selected_function()
        # Exit if no selection
        if not imfunc:
            self.lblDescribeFunction.clear()
            self.pbnNext.setEnabled(False)
            # Set the branch description if selected
            branch = self.selected_function_group()
            if branch and "description" in branch.keys():
                self.lblDescribeFunction.setText(branch['description'])
            return

        # Set description label
        description = ""
        if "name" in imfunc.keys():
            description += "<b>Name</b>: %s<br/>" % imfunc['name']
        if "overview" in imfunc.keys():
            description += "<b>Overview</b>: %s<br/>" % imfunc['overview']

        self.lblDescribeFunction.setText(description)
        # Enable the next button if anything selected
        self.pbnNext.setEnabled(bool(self.selected_function()))

    def selected_function(self):
        """Obtain the impact function selected by user.

        :returns: metadata of the selected function.
        :rtype: dict, None
        """
        item = self.lstFunctions.currentItem()
        if not item:
            return None

        data = item.data(QtCore.Qt.UserRole)
        if data:
            return data
        else:
            return None

    def set_widgets_step_fc_function_3(self):
        """Set widgets on the Impact Functions tab."""
        self.lstFunctions.clear()
        self.lblDescribeFunction.setText('')

        h, e, hc, ec = self.selected_imfunc_constraints()
        functions = ImpactFunctionManager().get_functions_for_constraint(
            h, e, hc, ec)
        for f in functions:
            item = QtGui.QListWidgetItem(self.lstFunctions)
            item.setText(f['name'])
            item.setData(QtCore.Qt.UserRole, f)
        self.auto_select_one_item(self.lstFunctions)

    # ===========================
    # STEP_FC_HAZLAYER_ORIGIN
    # ===========================

    # noinspection PyPep8Naming
    def on_rbHazLayerFromCanvas_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_rbHazLayerFromBrowser_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.pbnNext.setEnabled(True)

    def is_layer_compatible(self, layer, category, keywords=None):
        """Validate if a given layer is compatible for selected IF
           as a given category

        :param layer: The layer to be validated
        :type layer: QgsVectorLayer | QgsRasterLayer

        :param category: The category the layer is validated for
        :type category: string

        :param keywords: The layer keywords
        :type keywords: KeywordIO | None

        :returns: True if layer is appropriate for the selected role
        :rtype: boolean
        """

        # Get allowed subcategory, layer_type and data_type from IF constraints
        h, e, hc, ec = self.selected_imfunc_constraints()
        if category == 'hazard':
            subcategory = h['id']
            layer_type = hc['layer_type']
            data_type = hc['data_type']
        elif category == 'exposure':
            subcategory = e['id']
            layer_type = ec['layer_type']
            data_type = ec['data_type']
        else:
            # For aggregation layers, use a simplified test
            if (keywords and 'category' in keywords
                    and keywords['category'] == category):
                return True
            if not keywords and is_polygon_layer(layer):
                return True
            return False

        # Get allowed units from selected IF if possible
        imfunc = self.selected_function()
        if (imfunc and category in imfunc['categories']
                and 'units' in imfunc['categories'][category]):
            allowed_units = imfunc['categories'][category]['units']
            if type(allowed_units) != list:
                allowed_units = [allowed_units]
        else:
            allowed_units = None

        # Test the layer type and the data type
        if is_raster_layer(layer):
            if layer_type != 'raster':
                return False
            # Only test the data type if keywords present
            # WARNING: if keywords present, but data_type not set,
            # the value 'continuous' will be assumed by default.
            if keywords:
                if 'data_type' in keywords:
                    # if set, get data_type from keywords
                    layer_datatype = keywords['data_type']
                else:
                    # if not set, assume default value
                    layer_datatype = 'continuous'  # default
                if layer_datatype != data_type:
                    return False
        else:
            if layer_type == 'raster':
                return False
            if is_point_layer(layer):
                if data_type != 'point':
                    return False
            elif is_polygon_layer(layer):
                if data_type != 'polygon':
                    return False
            else:
                if data_type != 'line':
                    return False

        # Test the category if keywords provided
        if (keywords and 'category' in keywords
                and keywords['category'] != category):
            return False

        # Test the subcategory if keywords provided
        if (keywords and 'subcategory' in keywords
                and keywords['subcategory'] != subcategory):
            return False

        # Test the units if keywords provided
        if (allowed_units and keywords and 'units' in keywords
                and keywords['units'] in allowed_units):
            return False

        # Finally return True
        return True

    def get_compatible_layers_from_canvas(self, category):
        """Collect compatible layers from map canvas.

        .. note:: Returns layers with keywords and datatype matching
           the category and compatible with the selected impact function.
           Also returns layers without keywords with datatype
           compatible with the selected impact function.

        :param category: The category to filter for.
        :type category: string

        :returns: Metadata of found layers.
        :rtype: list of dicts
        """

        # Collect compatible layers
        layers = []
        for layer in self.iface.mapCanvas().layers():
            try:
                keywords = self.keyword_io.read_keywords(layer)
                if 'category' not in keywords:
                    keywords = None
            except (HashNotFoundError,
                    OperationalError,
                    NoKeywordsFoundError,
                    KeywordNotFoundError,
                    InvalidParameterError,
                    UnsupportedProviderError):
                keywords = None

            if self.is_layer_compatible(layer, category, keywords):
                layers += [
                    {'id': layer.id(),
                     'name': layer.name(),
                     'keywords': keywords}]

        # Move layers without keywords to the end
        l1 = [l for l in layers if l['keywords']]
        l2 = [l for l in layers if not l['keywords']]
        layers = l1 + l2

        return layers

    def list_compatible_layers_from_canvas(self, category, list_widget):
        """Fill given list widget with compatible layers.

        .. note:: Uses get_compatible_layers_from_canvas() to filter layers

        :param category: The category to filter for.
        :type category: string

        :param list_widget: The list widget to be filled with layers.
        :type list_widget: QListWidget


        :returns: Metadata of found layers.
        :rtype: list of dicts
        """

        italic_font = QtGui.QFont()
        italic_font.setItalic(True)

        # Add compatible layers
        list_widget.clear()
        for layer in self.get_compatible_layers_from_canvas(category):
            item = QListWidgetItem(layer['name'], list_widget)
            item.setData(QtCore.Qt.UserRole, layer['id'])
            if not layer['keywords']:
                item.setFont(italic_font)
            list_widget.addItem(item)

    def set_widgets_step_fc_hazlayer_origin(self):
        """Set widgets on the Hazard Layer Origin Type tab."""
        # First, list available layers in order to check if there are
        # any available layers. Note This will be repeated in
        # set_widgets_step_fc_hazlayer_from_canvas because we need
        # to list them again after coming back from the Keyword Wizard.
        self.list_compatible_layers_from_canvas(
            'hazard', self.lstCanvasHazLayers)
        if self.lstCanvasHazLayers.count():
            self.rbHazLayerFromCanvas.setText(QApplication.translate(
                'WizardDialog',
                'I would like to use a hazard layer already loaded in QGIS\n'
                '(launches the hazard data registration wizard if needed)'))
            self.rbHazLayerFromCanvas.setEnabled(True)
            self.rbHazLayerFromCanvas.click()
        else:
            self.rbHazLayerFromCanvas.setText(QApplication.translate(
                'WizardDialog',
                'I would like to use a hazard layer already loaded in QGIS\n'
                '(no suitable layers found)'))
            self.rbHazLayerFromCanvas.setEnabled(False)
            self.rbHazLayerFromBrowser.click()

        # Set the memo labels on this and next (hazard) steps
        (hazard,
         _,
         hazard_constraints,
         _) = self.selected_imfunc_constraints()
        if hazard_constraints['layer_type'] == 'raster':
            data_type = '%s %s' % (
                hazard_constraints['data_type'],
                hazard_constraints['layer_type'])
        else:
            data_type = hazard_constraints['data_type']
        text = layer_constraint_memo % (hazard['name'], data_type,
                                        'hazard', data_type, hazard['name'])

        self.lblHazLayerOriginConstraint.setText(text)
        self.lblHazLayerFromCanvasConstraint.setText(text)
        self.lblHazLayerFromBrowserConstraint.setText(text)

    # ===========================
    # STEP_FC_HAZLAYER_FROM_CANVAS
    # ===========================

    def get_layer_description_from_canvas(self, layer):
        """Obtain the description of a canvas layer selected by user.

        :param layer: The QGIS layer.
        :type layer: QgsMapLayer

        :returns: description of the selected layer.
        :rtype: string
        """

        # set the current layer (e.g. for the keyword creation sub-thread
        self.layer = layer

        if not layer:
            return ""

        try:
            keywords = self.keyword_io.read_keywords(layer)
            if 'category' not in keywords:
                keywords = None
        except (HashNotFoundError,
                OperationalError,
                NoKeywordsFoundError,
                KeywordNotFoundError,
                InvalidParameterError,
                UnsupportedProviderError):
            keywords = None

        self.is_selected_layer_keywordless = not bool(keywords)

        if keywords:
            label_text = """
                <b>Title</b>: %s<br/>
                <b>Category</b>: %s<br/>
                <b>Subcategory</b>: %s<br/>
                <b>Unit</b>: %s<br/>
                <b>Source</b>: %s<br/><br/>
            """ % (keywords.get('title'),
                   keywords.get('category'),
                   keywords.get('subcategory'),
                   keywords.get('unit'),
                   keywords.get('source'))
        else:
            if is_point_layer(layer):
                geom_type = 'point'
            elif is_polygon_layer(layer):
                geom_type = 'polygon'
            else:
                geom_type = 'line'

            # hide password in the layer source
            source = re.sub(r'password=\'.*\'',
                            r'password=*****',
                            layer.source())

            label_text = """
                This layer has no keywords assigned<br/><br/>
                <b>SOURCE</b>: %s<br/>
                <b>TYPE</b>: %s<br/><br/>
                In the next step you will be able to register this layer.
            """ % (source, is_raster_layer(layer)
                   and 'raster' or 'vector (%s)' % geom_type)

        return label_text

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_lstCanvasHazLayers_itemSelectionChanged(self):
        """Update layer description label

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """

        self.hazard_layer = self.selected_canvas_hazlayer()
        lblText = self.get_layer_description_from_canvas(self.hazard_layer)
        self.lblDescribeCanvasHazLayer.setText(lblText)
        self.pbnNext.setEnabled(True)

    def selected_canvas_hazlayer(self):
        """Obtain the canvas layer selected by user.

        :returns: The currently selected map layer in the list.
        :rtype: QgsMapLayer
        """

        if self.lstCanvasHazLayers.selectedItems():
            item = self.lstCanvasHazLayers.currentItem()
        else:
            return None
        try:
            layer_id = item.data(QtCore.Qt.UserRole)
        except (AttributeError, NameError):
            layer_id = None

        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    def set_widgets_step_fc_hazlayer_from_canvas(self):
        """Set widgets on the Hazard Layer From TOC tab"""
        # The list is already populated in the previous step, but now we
        # need to do it again in case we're back from the Keyword Wizard.
        # First, preserve self.layer before clearing the list
        last_layer = self.layer and self.layer.id() or None
        self.lblDescribeCanvasHazLayer.clear()
        self.list_compatible_layers_from_canvas(
            'hazard', self.lstCanvasHazLayers)
        self.auto_select_one_item(self.lstCanvasHazLayers)
        # Try to select the last_layer, if found:
        if last_layer:
            layers = []
            for indx in xrange(self.lstCanvasHazLayers.count()):
                item = self.lstCanvasHazLayers.item(indx)
                layers += [item.data(QtCore.Qt.UserRole)]
            if last_layer in layers:
                self.lstCanvasHazLayers.setCurrentRow(layers.index(last_layer))

    # ===========================
    # STEP_FC_HAZLAYER_FROM_BROWSER
    # ===========================

    def pg_path_to_uri(self, path):
        """Convert layer path from QgsBrowserModel to full QgsDataSourceURI

        :param path: The layer path from QgsBrowserModel
        :type path: string

        :returns: layer uri
        :rtype: QgsDataSourceURI
        """

        conn_name = path.split('/')[1]
        schema = path.split('/')[2]
        table = path.split('/')[3]

        settings = QSettings()
        key = "/PostgreSQL/connections/" + conn_name
        service = settings.value(key + "/service")
        host = settings.value(key + "/host")
        port = settings.value(key + "/port")
        if not port:
            port = "5432"
        db = settings.value(key + "/database")
        use_estimated_metadata = settings.value(
            key + "/estimatedMetadata", False, type=bool)
        sslmode = settings.value(
            key + "/sslmode", QgsDataSourceURI.SSLprefer, type=int)
        username = ""
        password = ""
        if settings.value(key + "/saveUsername") == "true":
            username = settings.value(key + "/username")

        if settings.value(key + "/savePassword") == "true":
            password = settings.value(key + "/password")

        # Old save setting
        if settings.contains(key + "/save"):
            username = settings.value(key + "/username")
            if settings.value(key + "/save") == "true":
                password = settings.value(key + "/password")

        uri = QgsDataSourceURI()
        if service:
            uri.setConnection(service, db, username, password, sslmode)
        else:
            uri.setConnection(host, port, db, username, password, sslmode)

        uri.setUseEstimatedMetadata(use_estimated_metadata)

        # Obtain the geometry column name
        connector = PostGisDBConnector(uri)
        tbls = connector.getVectorTables(schema)
        tbls = [tbl for tbl in tbls if tbl[1] == table]
        # if len(tbls) != 1:
        #    In the future, also look for raster layers?
        #    tbls = connector.getRasterTables(schema)
        #    tbls = [tbl for tbl in tbls if tbl[1]==table]
        if not tbls:
            return None
        tbl = tbls[0]
        geom_col = tbl[8]

        uri.setDataSource(schema, table, geom_col)
        return uri

    def get_layer_description_from_browser(self, category):
        """Obtain the description of the browser layer selected by user.

        :param category: The category of the layer to get the description.
        :type category: string

        :returns: Tuple of boolean and string. Boolean is true if layer is
            validated as compatible for current role (impact function and
            category) and false otherwise. String contains a description
            of the selected layer or an error message.
        :rtype: tuple
        """

        if category == 'hazard':
            browser = self.tvBrowserHazard
        elif category == 'exposure':
            browser = self.tvBrowserExposure
        elif category == 'postprocessing':
            browser = self.tvBrowserAggregation
        else:
            raise InaSAFEError

        index = browser.selectionModel().currentIndex()
        if not index:
            return False, ''

        # Map the proxy model index to the source model index
        index = browser.model().mapToSource(index)
        item = browser.model().sourceModel().dataItem(index)
        if not item:
            return False, ''

        item_class_name = item.metaObject().className()
        # if not itemClassName.endswith('LayerItem'):
        if not item.type() == QgsDataItem.Layer:
            if item_class_name == 'QgsPGRootItem' and not item.children():
                return False, create_postGIS_connection_first
            else:
                return False, ''

        if item_class_name not in [
                'QgsOgrLayerItem', 'QgsLayerItem', 'QgsPGLayerItem']:
            return False, ''

        path = item.path()

        if item_class_name in ['QgsOgrLayerItem',
                               'QgsLayerItem'] and not os.path.exists(path):
            return False, ''

        # try to create the layer
        if item_class_name == 'QgsOgrLayerItem':
            layer = QgsVectorLayer(path, '', 'ogr')
        elif item_class_name == 'QgsPGLayerItem':
            uri = self.pg_path_to_uri(path)
            if uri:
                layer = QgsVectorLayer(uri.uri(), uri.table(), 'postgres')
            else:
                layer = None
        else:
            layer = QgsRasterLayer(path, '', 'gdal')

        if not layer or not layer.isValid():
            return False, "Not a valid layer"

        try:
            keywords = self.keyword_io.read_keywords(layer)
            if 'category' not in keywords:
                keywords = None
        except (HashNotFoundError,
                OperationalError,
                NoKeywordsFoundError,
                KeywordNotFoundError,
                InvalidParameterError,
                UnsupportedProviderError):
            keywords = None

        # set the layer name for further use in the step_fc_summary
        if keywords:
            layer.setLayerName(keywords.get('title'))

        if not self.is_layer_compatible(layer, category, keywords):
            return False, "This layer's keywords or type are not suitable."

        # set the current layer (e.g. for the keyword creation sub-thread
        #                          or for adding the layer to mapCanvas)
        self.layer = layer

        if category == 'hazard':
            self.hazard_layer = layer
        elif category == 'exposure':
            self.exposure_layer = layer
        else:
            self.aggregation_layer = layer

        self.is_selected_layer_keywordless = not bool(keywords)

        if keywords:
            desc = (
                '<b>Title</b>: %s<br/>'
                '<b>Category</b>: %s<br/>'
                '<b>Subcategory</b>: %s<br/>'
                '<b>Unit</b>: %s<br/>'
                '<b>Source</b>: %s<br/><br/>') % (
                keywords.get('title'), keywords.get('category'),
                keywords.get('subcategory'), keywords.get('unit'),
                keywords.get('source'))
        else:
            if is_point_layer(layer):
                geom_type = 'point'
            elif is_polygon_layer(layer):
                geom_type = 'polygon'
            else:
                geom_type = 'line'

            # hide password in the layer source
            source = re.sub(r'password=\'.*\'',
                            r'password=*****',
                            layer.source())

            desc = """
                This layer has no keywords assigned<br/><br/>
                <b>SOURCE</b>: %s<br/>
                <b>TYPE</b>: %s<br/><br/>
                In the next step you will be able to register this layer.
            """ % (source, is_raster_layer(layer) and 'raster' or
                   'vector (%s)' % geom_type)

        return True, desc

    # noinspection PyPep8Naming
    def tvBrowserHazard_selection_changed(self):
        """Update layer description label"""
        (is_compatible, desc) = self.get_layer_description_from_browser(
            'hazard')
        self.lblDescribeBrowserHazLayer.setText(desc)
        self.pbnNext.setEnabled(is_compatible)

    def set_widgets_step_fc_hazlayer_from_browser(self):
        """Set widgets on the Hazard Layer From Browser tab"""
        self.tvBrowserHazard_selection_changed()

    # ===========================
    # STEP_FC_EXPLAYER_ORIGIN
    # ===========================

    # noinspection PyPep8Naming
    def on_rbExpLayerFromCanvas_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_rbExpLayerFromBrowser_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.pbnNext.setEnabled(True)

    def set_widgets_step_fc_explayer_origin(self):
        """Set widgets on the Exposure Layer Origin Type tab"""
        # First, list available layers in order to check if there are
        # any available layers. Note This will be repeated in
        # set_widgets_step_fc_explayer_from_canvas because we need
        # to list them again after coming back from the Keyword Wizard.
        self.list_compatible_layers_from_canvas(
            'exposure', self.lstCanvasExpLayers)
        if self.lstCanvasExpLayers.count():
            self.rbExpLayerFromCanvas.setText(QApplication.translate(
                'WizardDialog',
                'I would like to use an exposure layer already loaded in QGIS'
                '\n'
                '(launches the hazard data registration wizard if needed)'))
            self.rbExpLayerFromCanvas.setEnabled(True)
            self.rbExpLayerFromCanvas.click()
        else:
            self.rbExpLayerFromCanvas.setText(QApplication.translate(
                'WizardDialog',
                'I would like to use an exposure layer already loaded in QGIS'
                '\n'
                '(no suitable layers found)'))
            self.rbExpLayerFromCanvas.setEnabled(False)
            self.rbExpLayerFromBrowser.click()

        # Set the memo labels on this and next (exposure) steps
        (_,
         exposure,
         _,
         exposure_constraints) = self.selected_imfunc_constraints()
        if exposure_constraints['layer_type'] == 'raster':
            data_type = '%s %s' % (
                exposure_constraints['data_type'],
                exposure_constraints['layer_type'])
        else:
            data_type = exposure_constraints['data_type']
        text = layer_constraint_memo % (
            exposure['name'], data_type,
            'exposure', data_type, exposure['name'])

        self.lblExpLayerOriginConstraint.setText(text)
        self.lblExpLayerFromCanvasConstraint.setText(text)
        self.lblExpLayerFromBrowserConstraint.setText(text)

    # ===========================
    # STEP_FC_EXPLAYER_FROM_CANVAS
    # ===========================

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_lstCanvasExpLayers_itemSelectionChanged(self):
        """Update layer description label

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        self.exposure_layer = self.selected_canvas_explayer()
        lblText = self.get_layer_description_from_canvas(self.exposure_layer)
        self.lblDescribeCanvasExpLayer.setText(lblText)
        self.pbnNext.setEnabled(True)

    def selected_canvas_explayer(self):
        """Obtain the canvas exposure layer selected by user.

        :returns: The currently selected map layer in the list.
        :rtype: QgsMapLayer
        """
        if self.lstCanvasExpLayers.selectedItems():
            item = self.lstCanvasExpLayers.currentItem()
        else:
            return None
        try:
            layer_id = item.data(QtCore.Qt.UserRole)
        except (AttributeError, NameError):
            layer_id = None

        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    def set_widgets_step_fc_explayer_from_canvas(self):
        """Set widgets on the Exposure Layer From Canvas tab"""
        # The list is already populated in the previous step, but now we
        # need to do it again in case we're back from the Keyword Wizard.
        # First, preserve self.layer before clearing the list
        last_layer = self.layer and self.layer.id() or None
        self.lblDescribeCanvasExpLayer.clear()
        self.list_compatible_layers_from_canvas(
            'exposure', self.lstCanvasExpLayers)
        self.auto_select_one_item(self.lstCanvasExpLayers)
        # Try to select the last_layer, if found:
        if last_layer:
            layers = []
            for indx in xrange(self.lstCanvasExpLayers.count()):
                item = self.lstCanvasExpLayers.item(indx)
                layers += [item.data(QtCore.Qt.UserRole)]
            if last_layer in layers:
                self.lstCanvasExpLayers.setCurrentRow(layers.index(last_layer))

    # ===========================
    # STEP_FC_EXPLAYER_FROM_BROWSER
    # ===========================

    def tvBrowserExposure_selection_changed(self):
        """Update layer description label"""
        (is_compatible, desc) = self.get_layer_description_from_browser(
            'exposure')
        self.lblDescribeBrowserExpLayer.setText(desc)
        self.pbnNext.setEnabled(is_compatible)

    def set_widgets_step_fc_explayer_from_browser(self):
        """Set widgets on the Exposure Layer From Browser tab"""
        self.tvBrowserExposure_selection_changed()

    # ===========================
    # STEP_FC_DISJOINT_LAYERS
    # ===========================

    def layers_intersect(self, layer_a, layer_b):
        """Check if extents of two layers intersect.

        :param layer_a: One of the two layers to test overlapping
        :type layer_a: QgsMapLayer

        :param layer_b: The second of the two layers to test overlapping
        :type layer_b: QgsMapLayer

        :returns: true if the layers intersect, false if they are disjoint
        :rtype: boolean
        """
        extent_a = layer_a.extent()
        extent_b = layer_b.extent()
        if self.iface.mapCanvas().hasCrsTransformEnabled():
            coordTransform = QgsCoordinateTransform(layer_a.crs(),
                                                    layer_b.crs())
            extent_b = (coordTransform.transform(extent_b,
                        QgsCoordinateTransform.ReverseTransform))
        return extent_a.intersects(extent_b)

    def set_widgets_step_fc_disjoint_layers(self):
        """Set widgets on the Disjoint Layers tab"""
        pass

    # ===========================
    # STEP_FC_AGGLAYER_ORIGIN
    # ===========================

    # noinspection PyPep8Naming
    def on_rbAggLayerFromCanvas_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_rbAggLayerFromBrowser_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_rbAggLayerNoAggregation_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.pbnNext.setEnabled(True)

    def set_widgets_step_fc_agglayer_origin(self):
        """Set widgets on the Aggregation Layer Origin Type tab"""
        # First, list available layers in order to check if there are
        # any available layers. Note This will be repeated in
        # set_widgets_step_fc_agglayer_from_canvas because we need
        # to list them again after coming back from the Keyword Wizard.
        self.list_compatible_layers_from_canvas(
            'postprocessing', self.lstCanvasAggLayers)
        if self.lstCanvasAggLayers.count():
            self.rbAggLayerFromCanvas.setText(QApplication.translate(
                'WizardDialog',
                'I would like to use an aggregation layer already loaded '
                'in QGIS\n'
                '(launches the hazard data registration wizard if needed)'))
            self.rbAggLayerFromCanvas.setEnabled(True)
            self.rbAggLayerFromCanvas.click()
        else:
            self.rbAggLayerFromCanvas.setText(QApplication.translate(
                'WizardDialog',
                'I would like to use an aggregation layer already loaded '
                'in QGIS\n'
                '(no suitable layers found)'))
            self.rbAggLayerFromCanvas.setEnabled(False)
            self.rbAggLayerFromBrowser.click()

    # ===========================
    # STEP_FC_AGGLAYER_FROM_CANVAS
    # ===========================

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_lstCanvasAggLayers_itemSelectionChanged(self):
        """Update layer description label

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        self.aggregation_layer = self.selected_canvas_agglayer()
        lblText = self.get_layer_description_from_canvas(
            self.aggregation_layer)
        self.lblDescribeCanvasAggLayer.setText(lblText)
        self.pbnNext.setEnabled(True)

    def selected_canvas_agglayer(self):
        """Obtain the canvas aggregation layer selected by user.

        :returns: The currently selected map layer in the list.
        :rtype: QgsMapLayer
        """
        if self.lstCanvasAggLayers.selectedItems():
            item = self.lstCanvasAggLayers.currentItem()
        else:
            return None
        try:
            layer_id = item.data(QtCore.Qt.UserRole)
        except (AttributeError, NameError):
            layer_id = None

        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    def set_widgets_step_fc_agglayer_from_canvas(self):
        """Set widgets on the Aggregation Layer from Canvas tab"""
        # The list is already populated in the previous step, but now we
        # need to do it again in case we're back from the Keyword Wizard.
        # First, preserve self.layer before clearing the list
        last_layer = self.layer and self.layer.id() or None
        self.lblDescribeCanvasAggLayer.clear()
        self.list_compatible_layers_from_canvas(
            'postprocessing', self.lstCanvasAggLayers)
        self.auto_select_one_item(self.lstCanvasAggLayers)
        # Try to select the last_layer, if found:
        if last_layer:
            layers = []
            for indx in xrange(self.lstCanvasAggLayers.count()):
                item = self.lstCanvasAggLayers.item(indx)
                layers += [item.data(QtCore.Qt.UserRole)]
            if last_layer in layers:
                self.lstCanvasAggLayers.setCurrentRow(layers.index(last_layer))

    # ===========================
    # STEP_FC_AGGLAYER_FROM_BROWSER
    # ===========================

    # noinspection PyPep8Naming
    def tvBrowserAggregation_selection_changed(self):
        """Update layer description label"""
        (is_compatible, desc) = self.get_layer_description_from_browser(
            'postprocessing')
        self.lblDescribeBrowserAggLayer.setText(desc)
        self.pbnNext.setEnabled(is_compatible)

    def set_widgets_step_fc_agglayer_from_browser(self):
        """Set widgets on the Aggregation Layer From Browser tab"""
        self.tvBrowserAggregation_selection_changed()

    # ===========================
    # STEP_FC_AGGLAYER_DISJOINT
    # ===========================

    def set_widgets_step_fc_agglayer_disjoint(self):
        """Set widgets on the Aggregation Layer Disjoint tab"""
        pass

    # ===========================
    # STEP_FC_EXTENT
    # ===========================

    # noinspection PyPep8Naming
    def on_rbExtentUser_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_rbExtentLayer_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_rbExtentScreen_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.pbnNext.setEnabled(True)

    def extent_selector_closed(self):
        """Slot called when the users clears the analysis extents."""
        self.show()

    # noinspection PyPep8Naming
    def lblDefineExtentNow_clicked(self):
        """Show the extent selector widget for defining analysis extents."""
        # import here only so that it is AFTER i18n set up
        from safe.gui.tools.extent_selector_dialog import ExtentSelectorDialog
        widget = ExtentSelectorDialog(
            self.iface,
            self.iface.mainWindow(),
            extent=self.dock.extent.user_extent,
            crs=self.dock.extent.user_extent_crs)
        widget.clear_extent.connect(
            self.dock.extent.clear_user_analysis_extent)
        widget.extent_defined.connect(self.dock.define_user_analysis_extent)
        widget.extent_selector_closed.connect(self.extent_selector_closed)
        self.hide()
        # Needs to be non modal to support hide -> interact with map -> show
        widget.show()
        # Also select the radio button
        self.rbExtentUser.click()

    def set_widgets_step_fc_extent(self):
        """Set widgets on the Extent tab"""
        pass

    # ===========================
    # STEP_FC_EXTENT_DISJOINT
    # ===========================

    def validate_extent(self):
        """Check if the selected extent intersects source data.

        :returns: true if extent intersects both layers, false if is disjoint
        :rtype: boolean
        """
        if self.rbExtentUser.isChecked():
            # Get user extent
            extent = self.dock.extent.user_extent
            extent_crs = self.dock.extent.user_extent_crs
        elif self.rbExtentScreen.isChecked():
            # Get screen extent
            extent = self.iface.mapCanvas().extent()
            extent_crs = self.iface.mapCanvas().mapRenderer().destinationCrs()
        else:
            # The layer extent is chosen, no need to validate
            return True

        haz_extent = self.hazard_layer.extent()
        exp_extent = self.exposure_layer.extent()

        if self.iface.mapCanvas().hasCrsTransformEnabled():
            coord_transform = QgsCoordinateTransform(
                extent_crs, self.hazard_layer.crs())
            haz_extent = (coord_transform.transform(
                haz_extent, QgsCoordinateTransform.ReverseTransform))
            coord_transform = QgsCoordinateTransform(
                extent_crs, self.exposure_layer.crs())
            exp_extent = (coord_transform.transform(
                exp_extent, QgsCoordinateTransform.ReverseTransform))
        return extent.intersects(haz_extent) and extent.intersects(exp_extent)

    def set_widgets_step_fc_extent_disjoint(self):
        """Set widgets on the Extent Disjoint tab"""
        pass

    # ===========================
    # STEP_FC_PARAMS
    # ===========================

    def set_widgets_step_fc_params(self):
        """Set widgets on the Params tab"""

        # TODO Put the params to metadata! Now we need to import the IF class.
        # Notes: Why don't we store impact_function to class attribute?
        imfunc_id = self.selected_function()['id']
        imfunctions = get_safe_impact_function(imfunc_id)
        if not imfunctions:
            return
        imfunc = imfunctions[0][imfunc_id]
        self.if_params = None
        if hasattr(imfunc, 'parameters'):
            self.if_params = imfunc.parameters

        text = self.tr(
            'Please set impact functions parameters.<br/>Parameters for '
            'impact function "%s" that can be modified are:' % imfunc_id)
        self.lblSelectIFParameters.setText(text)

        self.parameter_dialog = FunctionOptionsDialog(self)
        self.parameter_dialog.set_dialog_info(imfunc_id)
        self.parameter_dialog.build_form(self.if_params)

        if self.twParams:
            self.twParams.hide()

        self.twParams = self.parameter_dialog.tabWidget
        self.layoutIFParams.addWidget(self.twParams)

    # ===========================
    # STEP_FC_SUMMARY
    # ===========================

    def set_widgets_step_fc_summary(self):
        """Set widgets on the Summary tab"""
        def format_postprocessor(val):
            """ make nested OrderedDicts more flat"""
            if type(val) == OrderedDict:
                result = []
                for v in val:
                    if type(val[v]) == OrderedDict:
                        # omit the v key and unpack the dict directly
                        result += [u'%s: %s' % (unicode(k), unicode(val[v][k]))
                                   for k in val[v]]
                    else:
                        result += [u'%s: %s' % (unicode(v), unicode(val[v]))]
                return u', '.join(result)
            else:
                return unicode(val)

        self.if_params = self.parameter_dialog.parse_input(
            self.parameter_dialog.values)

        # (IS) Set the current impact function to use parameter from user.
        # We should do it prettier (put it on analysis or impact calculator
        imfunc_id = self.selected_function()['id']
        imfunctions = get_safe_impact_function(imfunc_id)
        if not imfunctions:
            return
        imfunc = imfunctions[0][imfunc_id]
        imfunc.parameters = self.if_params

        params = []
        for p in self.if_params:
            if type(self.if_params[p]) == OrderedDict:
                subparams = [u'<b>%s</b>: %s' % (unicode(pp),
                             format_postprocessor(self.if_params[p][pp]))
                             for pp in self.if_params[p]]
                subparams = u'<br/>'.join(subparams)
                print '!!!', subparams
            elif type(self.if_params[p]) == list and p == 'minimum needs':
                subparams = ''
                for need in self.if_params[p]:
                    subparams += '%s %.0f' % (need.name, need.value)
                    if need.unit.abbreviation:
                        subparams += need.unit.abbreviation
                    if need != self.if_params[p][-1]:
                        subparams += ', '
                if not subparams:
                    subparams = 'Not applicable'
            elif type(self.if_params[p]) == list:
                subparams = ', '.join([unicode(i) for i in self.if_params[p]])
            else:
                subparams = unicode(self.if_params[p])

            params += [(p, subparams)]

        if self.aggregation_layer:
            aggr = self.aggregation_layer.name()
        else:
            aggr = self.tr('no aggregation')

        html = self.tr('Please ensure the following information '
                       'is correct and press Run.')
        html += '<br/><table cellspacing="4">'
        html += ('<tr>'
                 '  <td><b>%s</b></td><td width="10"></td><td>%s</td>'
                 '</tr><tr>'
                 '  <td colspan="3"></td>'
                 '</tr><tr>'
                 '  <td><b>%s</b></td><td></td><td>%s</td>'
                 '</tr><tr>'
                 '  <td><b>%s</b></td><td></td><td>%s</td>'
                 '</tr><tr>'
                 '  <td><b>%s</b></td><td></td><td>%s</td>'
                 '</tr><tr>'
                 '  <td colspan="3"></td>'
                 '</tr>' % (
                     self.tr('impact function').capitalize().replace(
                         ' ', '&nbsp;'),
                     self.selected_function()['name'],
                     self.tr('hazard layer').capitalize().replace(
                         ' ', '&nbsp;'),
                     self.hazard_layer.name(),
                     self.tr('exposure layer').capitalize().replace(
                         ' ', '&nbsp;'),
                     self.exposure_layer.name(),
                     self.tr('aggregation layer').capitalize().replace(
                         ' ', '&nbsp;'), aggr))

        def humanize(my_string):
            """Humanize string.

            :param my_string: A not human friendly string

            :type my_string: str

            :returns: A human friendly string
            :rtype: str
            """
            my_string = my_string.replace('_', ' ')
            my_string = my_string.capitalize()
            return my_string

        for p in params:
            html += ('<tr>'
                     '  <td><b>%s</b></td><td></td><td>%s</td>'
                     '</tr>' % (humanize(p[0]), p[1]))
        html += '</table>'

        self.lblSummary.setText(html)

    # ===========================
    # STEP_FC_ANALYSIS
    # ===========================

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnReportWeb_released(self):
        """Handle the Open Report in Web Browser button release.

        .. note:: This is an automatic Qt slot
           executed when the Next button is released.
        """
        self.wvResults.open_current_in_browser()

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnReportPDF_released(self):
        """Handle the Generate PDF button release.

        .. note:: This is an automatic Qt slot
           executed when the Next button is released.
        """
        self.analysis_handler.print_map('pdf')

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnReportComposer_released(self):
        """Handle the Open Report in Web Broseer button release.

        .. note:: This is an automatic Qt slot
           executed when the Next button is released.
        """
        self.analysis_handler.print_map('composer')

    def setup_and_run_analysis(self):
        """Execute analysis after the tab is displayed"""
        # noinspection PyTypeChecker
        self.analysis_handler = AnalysisHandler(self)
        self.analysis_handler.setup_and_run_analysis()

    def set_widgets_step_fc_analysis(self):
        """Set widgets on the Progress tab"""
        self.pbProgress.setValue(0)
        self.wvResults.setHtml('')
        self.pbnReportWeb.hide()
        self.pbnReportPDF.hide()
        self.pbnReportComposer.hide()
        self.lblAnalysisStatus.setText('Running analysis...')

    # ===========================
    # STEPS NAVIGATION
    # ===========================

    def go_to_step(self, step):
        """Set the stacked widget to the given step.

        :param step: The step number to be moved to.
        :type step: int
        """
        self.stackedWidget.setCurrentIndex(step - 1)
        self.lblStep.clear()
        self.pbnBack.setEnabled(True)
        if (step in [step_kw_category, step_fc_function_1] and self.parent_step
                is None):
            self.pbnBack.setEnabled(False)

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnNext_released(self):
        """Handle the Next button release.

        .. note:: This is an automatic Qt slot
           executed when the Next button is released.
        """
        current_step = self.get_current_step()

        # Save keywords if it's the end of the keyword creation mode
        if current_step == step_kw_title:
            self.save_current_keywords()

        if current_step == step_kw_aggregation:
            good_age_ratio, sum_age_ratios = self.age_ratios_are_valid()
            if not good_age_ratio:
                message = self.tr(
                    'The sum of age ratio default is %s and it is more '
                    'than 1. Please adjust the age ratio default so that they '
                    'will not more than 1.' % sum_age_ratios)
                if not self.suppress_warning_dialog:
                    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                    QtGui.QMessageBox.warning(
                        self, self.tr('InaSAFE'), message)
                return

        # After each browser step, add selected layer to map canvas
        if current_step in [step_fc_hazlayer_from_browser,
                            step_fc_explayer_from_browser,
                            step_fc_agglayer_from_browser]:
            if not QgsMapLayerRegistry.instance().mapLayersByName(
                    self.layer.name()):
                QgsMapLayerRegistry.instance().addMapLayers([self.layer])

        # Determine the new step to be switched
        new_step = self.compute_next_step(current_step)

        # Prepare the next tab
        if new_step == step_kw_category:
            self.set_widgets_step_kw_category()
        if new_step == step_kw_subcategory:
            self.set_widgets_step_kw_subcategory()
        elif new_step == step_kw_datatype:
            self.set_widgets_step_kw_datatype()
        elif new_step == step_kw_unit:
            self.set_widgets_step_kw_unit()
        elif new_step == step_kw_field:
            self.set_widgets_step_kw_field()
        elif new_step == step_kw_resample:
            self.set_widgets_step_kw_resample()
        elif new_step == step_kw_classify:
            self.set_widgets_step_kw_classify()
        elif new_step == step_kw_aggregation:
            self.set_widgets_step_kw_aggregation()
        elif new_step == step_kw_source:
            self.set_widgets_step_kw_source()
        elif new_step == step_kw_title:
            self.set_widgets_step_kw_title()
        elif new_step == step_fc_function_1:
            self.set_widgets_step_fc_function_1()
        elif new_step == step_fc_function_2:
            self.set_widgets_step_fc_function_2()
        elif new_step == step_fc_function_3:
            self.set_widgets_step_fc_function_3()
        elif new_step == step_fc_hazlayer_origin:
            self.set_widgets_step_fc_hazlayer_origin()
        elif new_step == step_fc_hazlayer_from_canvas:
            self.set_widgets_step_fc_hazlayer_from_canvas()
        elif new_step == step_fc_hazlayer_from_browser:
            self.set_widgets_step_fc_hazlayer_from_browser()
        elif new_step == step_fc_explayer_origin:
            self.set_widgets_step_fc_explayer_origin()
        elif new_step == step_fc_explayer_from_canvas:
            self.set_widgets_step_fc_explayer_from_canvas()
        elif new_step == step_fc_explayer_from_browser:
            self.set_widgets_step_fc_explayer_from_browser()
        elif new_step == step_fc_disjoint_layers:
            self.set_widgets_step_fc_disjoint_layers()
        elif new_step == step_fc_agglayer_origin:
            self.set_widgets_step_fc_agglayer_origin()
        elif new_step == step_fc_agglayer_from_canvas:
            self.set_widgets_step_fc_agglayer_from_canvas()
        elif new_step == step_fc_agglayer_from_browser:
            self.set_widgets_step_fc_agglayer_from_browser()
        elif new_step == step_fc_agglayer_disjoint:
            self.set_widgets_step_fc_agglayer_disjoint()
        elif new_step == step_fc_extent:
            self.set_widgets_step_fc_extent()
        elif new_step == step_fc_extent_disjoint:
            self.set_widgets_step_fc_extent_disjoint()
        elif new_step == step_fc_params:
            self.set_widgets_step_fc_params()
        elif new_step == step_fc_summary:
            self.set_widgets_step_fc_summary()
        elif new_step == step_fc_analysis:
            self.set_widgets_step_fc_analysis()
        elif new_step is None:
            # Wizard complete
            self.accept()
            return
        else:
            # unknown step
            pass

        # Set Next button label
        if (new_step in [step_kw_title, step_fc_analysis] and
                self.parent_step is None):
            self.pbnNext.setText(self.tr('Finish'))
        elif new_step == step_fc_summary:
            self.pbnNext.setText(self.tr('Run'))
        else:
            self.pbnNext.setText(self.tr('Next'))

        # Disable the Next button unless new data already entered
        self.pbnNext.setEnabled(self.is_ready_to_next_step(new_step))
        self.go_to_step(new_step)

        # Run analysis after switching to the new step
        if new_step == step_fc_analysis:
            self.setup_and_run_analysis()

        if new_step == step_kw_category and self.parent_step:
            if self.parent_step in [step_fc_hazlayer_from_canvas,
                                    step_fc_hazlayer_from_browser]:
                text_label = category_question_hazard
            elif self.parent_step in [step_fc_explayer_from_canvas,
                                      step_fc_explayer_from_browser]:
                text_label = category_question_exposure
            else:
                text_label = category_question_aggregation
            self.lblSelectCategory.setText(text_label)

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnBack_released(self):
        """Handle the Back button release.

        .. note:: This is an automatic Qt slot
           executed when the Back button is released.
        """
        current_step = self.get_current_step()
        new_step = self.compute_previous_step(current_step)
        # set focus to table widgets, as the inactive selection style is gray
        if new_step == step_fc_function_1:
            self.tblFunctions1.setFocus()
        if new_step == step_fc_function_2:
            self.tblFunctions2.setFocus()
        # Set Next button label
        self.pbnNext.setText(self.tr('Next'))
        self.pbnNext.setEnabled(True)
        self.go_to_step(new_step)

    def is_ready_to_next_step(self, step):
        """Check if the step we enter is initially complete. If so, there is
            no reason to block the Next button.

        :param step: The present step number.
        :type step: int

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        if step == step_kw_category:
            return bool(self.selected_category())
        if step == step_kw_subcategory:
            return bool(self.selected_subcategory())
        if step == step_kw_datatype:
            return bool(self.selected_datatype())
        if step == step_kw_unit:
            return bool(self.selected_unit())
        if step == step_kw_field:
            return bool(self.selected_field() or not self.lstFields.count())
        if step == step_kw_resample:
            # Allow to not set allow resample  # TODO: really?
            return True
        if step == step_kw_classify:
            # Allow to not classify any values
            return True
        if step == step_kw_aggregation:
            # Not required
            return True
        if step == step_kw_source:
            # The source_* keywords are not required
            return True
        if step == step_kw_title:
            return bool(self.leTitle.text())
        if step == step_fc_function_1:
            return bool(self.tblFunctions1.selectedItems())
        if step == step_fc_function_2:
            return bool(self.tblFunctions2.selectedItems())
        if step == step_fc_function_3:
            return bool(self.selected_function())
        if step == step_fc_hazlayer_origin:
            return (bool(self.rbHazLayerFromCanvas.isChecked() or
                         self.rbHazLayerFromBrowser.isChecked()))
        if step == step_fc_hazlayer_from_canvas:
            return bool(self.selected_canvas_hazlayer())
        if step == step_fc_hazlayer_from_browser:
            return bool(len(self.lblDescribeBrowserHazLayer.text()) > 32)
        if step == step_fc_explayer_origin:
            return (bool(self.rbExpLayerFromCanvas.isChecked() or
                         self.rbExpLayerFromBrowser.isChecked()))
        if step == step_fc_explayer_from_canvas:
            return bool(self.selected_canvas_explayer())
        if step == step_fc_explayer_from_browser:
            return bool(len(self.lblDescribeBrowserExpLayer.text()) > 32)
        if step == step_fc_disjoint_layers:
            # Never go further if layers disjoint
            return False
        if step == step_fc_agglayer_origin:
            return (bool(self.rbAggLayerFromCanvas.isChecked() or
                         self.rbAggLayerFromBrowser.isChecked() or
                         self.rbAggLayerNoAggregation.isChecked()))
        if step == step_fc_agglayer_from_canvas:
            return bool(self.selected_canvas_agglayer())
        if step == step_fc_agglayer_from_browser:
            return bool(len(self.lblDescribeBrowserAggLayer.text()) > 32)
        if step == step_fc_agglayer_disjoint:
            # Never go further if layers disjoint
            return False
        if step == step_fc_extent:
            return (bool(self.rbExtentUser.isChecked() or
                         self.rbExtentLayer.isChecked() or
                         self.rbExtentScreen.isChecked()))
        if step == step_fc_params:
            return True
        if step == step_fc_summary:
            return True
        if step == step_fc_analysis:
            return True
        return True

    def compute_next_step(self, current_step):
        """Determine the next step to be switched to.

        :param current_step: The present step number.
        :type current_step: int

        :returns: The next step number or None if finished.
        :rtype: int
        """
        if current_step == step_kw_category:
            category = self.selected_category()
            if category['id'] == 'aggregation':
                new_step = step_kw_field
            elif self.subcategories_for_layer(
                    category['id'],
                    self.get_layer_type(), self.get_data_type()):
                new_step = step_kw_subcategory
            else:
                new_step = step_kw_field
        elif current_step == step_kw_subcategory:
            subcategory = self.selected_subcategory()
            # skip field and classify step if point layer and it's a volcano
            if (self.get_data_type() == 'point' and subcategory['id'] ==
                    'volcano'):
                new_step = step_kw_source
            elif self.get_layer_type() == 'raster':
                new_step = step_kw_datatype
            elif ImpactFunctionManager().units_for_layer(
                    subcategory['id'],
                    self.get_layer_type(), self.get_data_type()):
                new_step = step_kw_unit
            else:
                new_step = step_kw_field
        elif current_step == step_kw_datatype:
            if ImpactFunctionManager().units_for_layer(
                    self.selected_subcategory()['id'],
                    self.get_layer_type(), self.get_data_type()):
                new_step = step_kw_unit
            else:
                new_step = step_kw_field
        elif current_step == step_kw_unit:
            unit = self.selected_unit()
            if unit and unit['id'] == 'building_generic':
                new_step = step_kw_source
                # TODO: why not step_kw_aggregation ?
            else:
                new_step = step_kw_field
        elif current_step == step_kw_field:
            unit = self.selected_unit()
            if unit and unit['constraint'] == 'categorical':
                new_step = step_kw_classify
            elif self.selected_category()['id'] == 'aggregation':
                new_step = step_kw_aggregation
            else:
                new_step = step_kw_source
        elif current_step == step_kw_resample:
            new_step = step_kw_source
        elif current_step == step_kw_classify:
            new_step = step_kw_source
        elif current_step in (step_kw_aggregation, step_kw_source):
            new_step = current_step + 1
        elif current_step == step_kw_title:
            if self.parent_step:
                # Come back to the parent thread
                new_step = self.parent_step
                self.parent_step = None
                self.is_selected_layer_keywordless = False
                self.lblSubtitle.setText(self.tr(
                    'Guided InaSAFE analysis wizard...'))
            else:
                # Wizard complete
                new_step = None

        elif current_step == step_fc_hazlayer_origin:
            if self.rbHazLayerFromCanvas.isChecked():
                new_step = step_fc_hazlayer_from_canvas
            else:
                new_step = step_fc_hazlayer_from_browser
        elif current_step in [step_fc_hazlayer_from_canvas,
                              step_fc_hazlayer_from_browser]:
            if self.is_selected_layer_keywordless:
                # insert keyword creation thread here
                self.parent_step = current_step
                self.set_keywords_creation_mode(self.layer)
                new_step = step_kw_category
            else:
                new_step = step_fc_explayer_origin
        elif current_step == step_fc_explayer_origin:
            if self.rbExpLayerFromCanvas.isChecked():
                new_step = step_fc_explayer_from_canvas
            else:
                new_step = step_fc_explayer_from_browser
        elif current_step in [step_fc_explayer_from_canvas,
                              step_fc_explayer_from_browser]:
            if self.is_selected_layer_keywordless:
                # insert keyword creation thread here
                self.parent_step = current_step
                self.existing_keywords = None
                new_step = step_kw_category
            else:
                if not self.layers_intersect(self.hazard_layer,
                                             self.exposure_layer):
                    new_step = step_fc_disjoint_layers
                else:
                    new_step = step_fc_agglayer_origin
        elif current_step == step_fc_disjoint_layers:
            new_step = step_fc_agglayer_origin
        elif current_step == step_fc_agglayer_origin:
            if self.rbAggLayerFromCanvas.isChecked():
                new_step = step_fc_agglayer_from_canvas
            elif self.rbAggLayerFromBrowser.isChecked():
                new_step = step_fc_agglayer_from_browser
            else:
                new_step = step_fc_extent
        elif current_step in [step_fc_agglayer_from_canvas,
                              step_fc_agglayer_from_browser]:
            if self.is_selected_layer_keywordless:
                # insert keyword creation thread here
                self.parent_step = current_step
                self.existing_keywords = None
                new_step = step_kw_category
            else:
                flag = self.layers_intersect(
                    self.exposure_layer, self.aggregation_layer)
                if not flag:
                    new_step = step_fc_agglayer_disjoint
                else:
                    new_step = step_fc_extent
        elif current_step == step_fc_agglayer_disjoint:
            new_step = step_fc_extent
        elif current_step == step_fc_extent:
            if self.validate_extent():
                new_step = step_fc_params
            else:
                new_step = step_fc_extent_disjoint
        elif current_step in [step_fc_function_1, step_fc_function_2,
                              step_fc_function_3,
                              step_fc_params, step_fc_summary]:
            new_step = current_step + 1
        elif current_step == step_fc_analysis:
            new_step = None  # Wizard complete

        elif current_step < self.stackedWidget.count():
            raise Exception('Unhandled step')
        else:
            raise Exception('Unexpected number of steps')

        # Skip the field and classify tab if raster layer
        if new_step == step_kw_field and is_raster_layer(self.layer):
            # Insert the resample step for exposure layers
            if self.selected_category()['id'] == 'exposure':
                new_step = step_kw_resample
            else:
                new_step = step_kw_source

        return new_step

    def compute_previous_step(self, current_step):
        """Determine the previous step to be switched to (by the Back button).

        :param current_step: The present step number.
        :type current_step: int

        :returns: The previous step number.
        :rtype: int
        """
        if current_step == step_kw_category:
            if self.parent_step:
                # Come back to the parent thread
                new_step = self.parent_step
                self.parent_step = None
            else:
                new_step = step_kw_category
        elif current_step == step_kw_unit:
            if self.selected_datatype():
                new_step = step_kw_datatype
            else:
                new_step = step_kw_subcategory
        elif current_step == step_kw_field:
            if self.selected_unit():
                new_step = step_kw_unit
            elif self.selected_subcategory():
                new_step = step_kw_subcategory
            elif self.selected_category()['id'] == 'aggregation':
                new_step = step_kw_category
            else:
                new_step = step_kw_category
        elif current_step == step_kw_resample:
            if self.selected_unit():
                new_step = step_kw_unit
            else:
                new_step = step_kw_datatype
        elif current_step == step_kw_aggregation:
            new_step = step_kw_field
        elif current_step == step_kw_source:
            if self.selected_mapping():
                new_step = step_kw_classify
            elif self.selected_category()['id'] == 'aggregation':
                new_step = step_kw_aggregation
            elif (is_raster_layer(self.layer)
                  and self.selected_category()['id'] == 'exposure'):
                new_step = step_kw_resample
            elif self.selected_field():
                new_step = step_kw_field
            elif self.selected_unit():
                new_step = step_kw_unit
            elif self.selected_datatype():
                new_step = step_kw_datatype
            elif self.selected_subcategory():
                new_step = step_kw_subcategory
            else:
                new_step = step_kw_category

        elif current_step == step_fc_function_1:
            # TODO block the Back button
            new_step = step_fc_function_1
        elif current_step == step_fc_hazlayer_from_browser:
            new_step = step_fc_hazlayer_origin
        elif current_step == step_fc_explayer_origin:
            if self.rbHazLayerFromCanvas.isChecked():
                new_step = step_fc_hazlayer_from_canvas
            else:
                new_step = step_fc_hazlayer_from_browser
        elif current_step == step_fc_explayer_from_browser:
            new_step = step_fc_explayer_origin
        elif current_step == step_fc_disjoint_layers:
            if self.rbExpLayerFromCanvas.isChecked():
                new_step = step_fc_explayer_from_canvas
            else:
                new_step = step_fc_explayer_from_browser
        elif current_step == step_fc_agglayer_origin:
            if self.rbExpLayerFromCanvas.isChecked():
                new_step = step_fc_explayer_from_canvas
            else:
                new_step = step_fc_explayer_from_browser
        elif current_step == step_fc_agglayer_from_browser:
            new_step = step_fc_agglayer_origin
        elif current_step == step_fc_agglayer_disjoint:
            if self.rbAggLayerFromCanvas.isChecked():
                new_step = step_fc_agglayer_from_canvas
            else:
                new_step = step_fc_agglayer_from_browser
        elif current_step == step_fc_extent:
            if self.rbAggLayerFromCanvas.isChecked():
                new_step = step_fc_agglayer_from_canvas
            elif self.rbAggLayerFromBrowser.isChecked():
                new_step = step_fc_agglayer_from_browser
            else:
                new_step = step_fc_agglayer_origin
        elif current_step == step_fc_params:
            new_step = step_fc_extent
        else:
            new_step = current_step - 1
        return new_step

    # ===========================
    # COMMON METHODS
    # ===========================

    def get_current_step(self):
        """Return current step of the wizard.

        :returns: Current step of the wizard.
        :rtype: int
        """
        return self.stackedWidget.currentIndex() + 1

    def get_layer_type(self, layer=None):
        """Obtain the type of a given layer.

        If no layer specified, the current layer is used

        :param layer : layer to examine
        :type layer: QgsMapLayer or None

        :returns: The layer type.
        :rtype: str
        """
        if not layer:
            layer = self.layer
        return is_raster_layer(layer) and 'raster' or 'vector'

    def get_data_type(self, layer=None):
        """Obtain data type of a given layer.

        If no layer specified, the current layer is used

        :param layer : layer to examine
        :type layer: QgsMapLayer or None

        :returns: The data type.
        :rtype: str
        """
        if not layer:
            layer = self.layer
        if self.get_layer_type() == 'vector':
            if is_point_layer(layer):
                return 'point'
            elif is_polygon_layer(layer):
                return 'polygon'
            else:
                return 'line'
        else:
            # Try to get the value from the category list
            item = self.lstDataTypes.currentItem()
            if item:
                data_type = item.data(QtCore.Qt.UserRole)
                if data_type:
                    return data_type
            # Fallback to the default value
            return 'continuous'

    def get_existing_keyword(self, keyword):
        """Obtain an existing keyword's value.

        :param keyword: A keyword from keywords.
        :type keyword: str

        :returns: The value of the keyword.
        :rtype: str
        """
        if self.existing_keywords is None:
            return None
        if keyword is not None:
            return self.existing_keywords.get(keyword, None)
        else:
            return None

    def get_keywords(self):
        """Obtain the state of the dialog as a keywords dict.

        :returns: Keywords reflecting the state of the dialog.
        :rtype: dict
        """
        keywords = {}
        if self.selected_category():
            keywords['category'] = self.selected_category()['id']
            if keywords['category'] == 'aggregation':
                keywords['category'] = 'postprocessing'
                keywords.update(self.get_aggregation_attributes())
        if self.selected_subcategory():
            keywords['subcategory'] = self.selected_subcategory()['id']
        if self.selected_datatype() and self.get_layer_type() == 'raster':
            keywords['data_type'] = self.selected_datatype()
        if self.selected_unit():
            keywords['unit'] = self.selected_unit()['id']
        if self.selected_allowresample() is not None:
            keywords['allow_resample'] = self.selected_allowresample()
        if self.lstFields.currentItem():
            if 'category' in keywords.keys():
                if keywords['category'] != 'postprocessing':
                    key_field = 'field'
                else:
                    key_field = 'aggregation attribute'
                keywords[key_field] = self.lstFields.currentItem().text()
        if self.leSource.text():
            keywords['source'] = self.leSource.text()
        if self.leSource_url.text():
            keywords['source_url'] = self.leSource_url.text()
        if self.leSource_scale.text():
            keywords['source_scale'] = self.leSource_scale.text()
        if self.leSource_date.text():
            keywords['source_date'] = self.leSource_date.text()
        if self.leTitle.text():
            keywords['title'] = self.leTitle.text()
        value_map = self.selected_mapping()
        if value_map:
            keywords['value_map'] = json.dumps(value_map)

        return keywords

    def save_current_keywords(self):
        """Save keywords to the layer.

        It will write out the keywords for the current layer.
        This method is based on the KeywordsDialog class.
        """
        current_keywords = self.get_keywords()
        try:
            self.keyword_io.write_keywords(
                layer=self.layer, keywords=current_keywords)
        except InaSAFEError, e:
            error_message = get_error_message(e)
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QtGui.QMessageBox.warning(
                self, self.tr('InaSAFE'),
                ((self.tr(
                    'An error was encountered when saving the keywords:\n'
                    '%s') % error_message.to_html())))
        if self.dock is not None:
            # noinspection PyUnresolvedReferences
            self.dock.get_layers()

    # noinspection PyUnresolvedReferences,PyMethodMayBeStatic
    def auto_select_one_item(self, list_widget):
        """Select item in the list in list_widget if it's the only item.

        :param list_widget: The list widget that want to be checked.
        :type list_widget: QListWidget
        """
        if list_widget.count() == 1 and list_widget.currentRow() == -1:
            list_widget.setCurrentRow(0)

    def set_tool_tip(self):
        """Set tool tip as helper text for some objects."""

        title_tooltip = self.tr('Title of the layer.')
        source_tooltip = self.tr(
            'Please record who is the custodian of this layer i.e. '
            'OpenStreetMap')
        date_tooltip = self.tr(
            'When was this data collected or downloaded i.e. 1-May-2014')
        scale_tooltip = self.tr('What is the scale of this layer?')
        url_tooltip = self.tr(
            'Does the custodians have their own website '
            'i.e. www.openstreetmap.org')

        self.lblTitle.setToolTip(title_tooltip)
        self.lblSource.setToolTip(source_tooltip)
        self.lblDate.setToolTip(date_tooltip)
        self.lblScale.setToolTip(scale_tooltip)
        self.lblURL.setToolTip(url_tooltip)

        self.leTitle.setToolTip(title_tooltip)
        self.leSource.setToolTip(source_tooltip)
        self.leSource_date.setToolTip(date_tooltip)
        self.leSource_scale.setToolTip(scale_tooltip)
        self.leSource_url.setToolTip(url_tooltip)
