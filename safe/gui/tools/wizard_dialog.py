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

from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
import numpy

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
from PyQt4.QtCore import pyqtSignature, QSettings, QPyNullVariant, QDateTime
# noinspection PyPackageRequirements
from PyQt4.QtGui import (
    QDialog,
    QListWidgetItem,
    QPixmap,
    QSortFilterProxyModel)

# pylint: disable=F0401
from db_manager.db_plugins.postgis.connector import PostGisDBConnector
# pylint: enable=F0401

import safe.definitions
from safe.definitions import (
    inasafe_keyword_version,
    inasafe_keyword_version_key,
    global_default_attribute,
    do_not_use_attribute,
    continuous_hazard_unit,
    exposure_unit,
    raster_hazard_classification,
    vector_hazard_classification,
    layer_purpose_hazard,
    layer_purpose_exposure,
    layer_purpose_aggregation,
    hazard_category_single_event,
    layer_geometry_point,
    layer_geometry_line,
    layer_geometry_polygon,
    layer_geometry_raster,
    layer_mode_continuous,
    layer_mode_classified)
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.analysis_handler import AnalysisHandler
from safe.utilities.gis import (
    is_raster_layer,
    is_point_layer,
    is_polygon_layer,
    layer_attribute_names)
from safe.utilities.utilities import get_error_message, compare_version
from safe.defaults import get_defaults
from safe.common.exceptions import (
    HashNotFoundError,
    NoKeywordsFoundError,
    KeywordNotFoundError,
    InvalidParameterError,
    UnsupportedProviderError,
    InsufficientOverlapError,
    InaSAFEError)
from safe.common.resource_parameter import ResourceParameter
from safe.common.version import get_version
from safe_extras.parameters.group_parameter import GroupParameter
from safe.utilities.resources import get_ui_class, resources_path
from safe.gui.tools.function_options_dialog import (
    FunctionOptionsDialog)
from safe.utilities.unicode import get_unicode
from safe.utilities.i18n import tr
import safe.gui.tools.wizard_strings
from safe.gui.tools.wizard_strings import (
    category_question,
    category_question_hazard,
    category_question_exposure,
    category_question_aggregation,
    hazard_category_question,
    layermode_raster_question,
    layermode_vector_question,
    unit_question,
    allow_resampling_question,
    field_question_subcategory_unit,
    field_question_subcategory_classified,
    field_question_aggregation,
    classification_question,
    classify_vector_question,
    classify_raster_question,
    select_function_constraints2_question,
    select_function_question,
    select_hazard_origin_question,
    select_hazlayer_from_canvas_question,
    select_hazlayer_from_browser_question,
    select_exposure_origin_question,
    select_explayer_from_canvas_question,
    select_explayer_from_browser_question,
    create_postGIS_connection_first)

LOGGER = logging.getLogger('InaSAFE')

FORM_CLASS = get_ui_class('wizard_dialog_base.ui')


# Constants: tab numbers for steps
step_kw_category = 1
step_kw_subcategory = 2
step_kw_hazard_category = 3
step_kw_layermode = 4
step_kw_unit = 5
step_kw_classification = 6
step_kw_field = 7
step_kw_resample = 8
step_kw_classify = 9
step_kw_extrakeywords = 10
step_kw_aggregation = 11
step_kw_source = 12
step_kw_title = 13
step_kw_summary = 14
step_fc_function_1 = 15
step_fc_function_2 = 16
step_fc_function_3 = 17
step_fc_hazlayer_origin = 18
step_fc_hazlayer_from_canvas = 19
step_fc_hazlayer_from_browser = 20
step_fc_explayer_origin = 21
step_fc_explayer_from_canvas = 22
step_fc_explayer_from_browser = 23
step_fc_disjoint_layers = 24
step_fc_agglayer_origin = 25
step_fc_agglayer_from_canvas = 26
step_fc_agglayer_from_browser = 27
step_fc_agglayer_disjoint = 28
step_fc_extent = 29
step_fc_extent_disjoint = 30
step_fc_params = 31
step_fc_summary = 32
step_fc_analysis = 33


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
    if constant in dir(safe.gui.tools.wizard_strings):
        return getattr(safe.gui.tools.wizard_strings, constant)
    else:
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

        .. note:: This filter hides top-level items of unsupported branches
                  and also leaf items containing xml files.

           Enabled root items: QgsDirectoryItem, QgsFavouritesItem,
           QgsPGRootItem.

           Disabled root items: QgsMssqlRootItem, QgsSLRootItem,
           QgsOWSRootItem, QgsWCSRootItem, QgsWFSRootItem, QgsWMSRootItem.

           Disabled leaf items: QgsLayerItem and QgsOgrLayerItem with path
           ending with '.xml'

        :param source_row: Parent widget of the model
        :type source_row: int

        :param source_parent: Parent item index
        :type source_parent: QModelIndex

        :returns: Item validation result
        :rtype: bool
        """
        source_index = self.sourceModel().index(source_row, 0, source_parent)
        item = self.sourceModel().dataItem(source_index)

        if item.metaObject().className() in [
                'QgsMssqlRootItem',
                'QgsSLRootItem',
                'QgsOWSRootItem',
                'QgsWCSRootItem',
                'QgsWFSRootItem',
                'QgsWMSRootItem']:
            return False

        if (item.metaObject().className() in [
                'QgsLayerItem',
                'QgsOgrLayerItem'] and
                item.path().endswith('.xml')):
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
        # Constants
        self.keyword_creation_wizard_name = 'InaSAFE Keywords Creation Wizard'
        self.ifcw_name = 'InaSAFE Impact Function Centric Wizard'
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
            QPixmap(resources_path('img', 'icons', 'icon-white.svg')))
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
        self.extent_dialog = None

        self.keyword_io = KeywordIO()
        self.twParams = None
        self.swExtent = None

        self.is_selected_layer_keywordless = False
        self.parent_step = None

        self.pbnBack.setEnabled(False)
        self.pbnNext.setEnabled(False)

        # Collect some serial widgets
        self.extra_keywords_widgets = [
            {'cbo': self.cboExtraKeyword1, 'lbl': self.lblExtraKeyword1},
            {'cbo': self.cboExtraKeyword2, 'lbl': self.lblExtraKeyword2},
            {'cbo': self.cboExtraKeyword3, 'lbl': self.lblExtraKeyword3},
            {'cbo': self.cboExtraKeyword4, 'lbl': self.lblExtraKeyword4},
            {'cbo': self.cboExtraKeyword5, 'lbl': self.lblExtraKeyword5},
            {'cbo': self.cboExtraKeyword6, 'lbl': self.lblExtraKeyword6},
            {'cbo': self.cboExtraKeyword7, 'lbl': self.lblExtraKeyword7},
            {'cbo': self.cboExtraKeyword8, 'lbl': self.lblExtraKeyword8}
        ]
        for ekw in self.extra_keywords_widgets:
            ekw['key'] = None
            ekw['slave_key'] = None

        # noinspection PyUnresolvedReferences
        self.tvBrowserHazard.selectionModel().selectionChanged.connect(
            self.tvBrowserHazard_selection_changed)
        self.tvBrowserExposure.selectionModel().selectionChanged.connect(
            self.tvBrowserExposure_selection_changed)
        self.tvBrowserAggregation.selectionModel().selectionChanged.connect(
            self.tvBrowserAggregation_selection_changed)
        self.treeClasses.itemChanged.connect(self.update_dragged_item_flags)
        self.pbnCancel.released.connect(self.reject)

        # string constants
        self.global_default_string = global_default_attribute['name']
        self.global_default_data = global_default_attribute['id']
        self.do_not_use_string = do_not_use_attribute['name']
        self.do_not_use_data = do_not_use_attribute['id']
        self.defaults = get_defaults()

        # Initialize attributes
        self.impact_function_manager = ImpactFunctionManager()
        self.existing_keywords = None
        self.layer = None
        self.hazard_layer = None
        self.exposure_layer = None
        self.aggregation_layer = None
        self.if_params = None
        self.analysis_handler = None

    def set_mode_label_to_keywords_creation(self):
        """Set the mode label to the Keywords Creation/Update mode
        """
        self.setWindowTitle(self.keyword_creation_wizard_name)
        if self.get_existing_keyword('layer_purpose'):
            mode_name = (self.tr(
                'Keywords update wizard for layer <b>%s</b>'
            ) % self.layer.name())
        else:
            mode_name = (self.tr(
                'Keywords creation wizard for layer <b>%s</b>'
            ) % self.layer.name())
        self.lblSubtitle.setText(mode_name)

    def set_mode_label_to_ifcw(self):
        """Set the mode label to the IFCW
        """
        self.setWindowTitle(self.ifcw_name)
        self.lblSubtitle.setText(self.tr(
            'Use this wizard to run a guided impact assessment'))

    def set_keywords_creation_mode(self, layer=None):
        """Set the Wizard to the Keywords Creation mode
        :param layer: Layer to set the keywords for
        :type layer: QgsMapLayer
        """
        self.layer = layer or self.iface.mapCanvas().currentLayer()
        try:
            self.existing_keywords = self.keyword_io.read_keywords(self.layer)
            # if 'layer_purpose' not in self.existing_keywords:
            #     self.existing_keywords = None
        except (HashNotFoundError,
                OperationalError,
                NoKeywordsFoundError,
                KeywordNotFoundError,
                InvalidParameterError,
                UnsupportedProviderError):
            self.existing_keywords = None
        self.set_mode_label_to_keywords_creation()
        self.set_widgets_step_kw_category()
        self.go_to_step(step_kw_category)

    def set_function_centric_mode(self):
        """Set the Wizard to the Function Centric mode"""
        self.set_mode_label_to_ifcw()
        new_step = step_fc_function_1
        self.set_widgets_step_fc_function_1()
        self.pbnNext.setEnabled(self.is_ready_to_next_step(new_step))
        self.go_to_step(new_step)

    def update_MessageViewer_size(self):
        """Update maximumHeight size of the MessageViewer to fit its parent tab

        This is a workaround for a bug that makes MessageViewer
        flooding up to maximumHeight on Windows.
        """
        self.wvResults.setMaximumHeight(self.pgF25Progress.height() - 90)

    # pylint: disable=unused-argument
    def resizeEvent(self, ev):
        """Trigger MessageViewer size update on window resize

        .. note:: This is an automatic Qt slot
           executed when the window size changes.
        """
        pass
        # self.update_MessageViewer_size()
    # pylint: disable=unused-argument

    def purposes_for_layer(self):
        """Return a list of valid purposes for the current layer.

        :returns: A list where each value represents a valid purpose.
        :rtype: list
        """
        layer_geometry_id = self.get_layer_geometry_id()
        return self.impact_function_manager.purposes_for_layer(
            layer_geometry_id)

    def subcategories_for_layer(self):
        """Return a list of valid subcategories for a layer.
           Subcategory is hazard type or exposure type.

        :returns: A list where each value represents a valid subcategory.
        :rtype: list
        """
        purpose = self.selected_category()
        layer_geometry_id = self.get_layer_geometry_id()
        if purpose == layer_purpose_hazard:
            return self.impact_function_manager.hazards_for_layer(
                layer_geometry_id)
        elif purpose == layer_purpose_exposure:
            return self.impact_function_manager.exposures_for_layer(
                layer_geometry_id)

    def hazard_categories_for_layer(self):
        """Return a list of valid hazard categories for a layer.

        :returns: A list where each value represents a valid hazard category.
        :rtype: list
        """
        layer_geometry_id = self.get_layer_geometry_id()
        if self.selected_category() != layer_purpose_hazard:
            return []
        hazard_type_id = self.selected_subcategory()['key']
        return self.impact_function_manager.hazard_categories_for_layer(
            layer_geometry_id, hazard_type_id)

    def layermodes_for_layer(self):
        """Return a list of valid layer modes for a layer.

        :returns: A list where each value represents a valid layer mode.
        :rtype: list
        """
        purpose = self.selected_category()
        subcategory = self.selected_subcategory()
        layer_geometry_id = self.get_layer_geometry_id()
        if purpose == layer_purpose_hazard:
            hazard_category = self.selected_hazard_category()
            return self.impact_function_manager.available_hazard_layer_modes(
                subcategory['key'], layer_geometry_id, hazard_category['key'])
        elif purpose == layer_purpose_exposure:
            return self.impact_function_manager.available_exposure_layer_modes(
                subcategory['key'], layer_geometry_id)

    def classifications_for_layer(self):
        """Return a list of valid classifications for a layer.

        :returns: A list where each value represents a valid classification.
        :rtype: list
        """
        layer_geometry_id = self.get_layer_geometry_id()
        layer_mode_id = self.selected_layermode()['key']
        subcategory_id = self.selected_subcategory()['key']
        if self.selected_category() == layer_purpose_hazard:
            hazard_category_id = self.selected_hazard_category()['key']
            if is_raster_layer(self.layer):
                return self.impact_function_manager.\
                    raster_hazards_classifications_for_layer(
                        subcategory_id,
                        layer_geometry_id,
                        layer_mode_id,
                        hazard_category_id)
            else:
                return self.impact_function_manager\
                    .vector_hazards_classifications_for_layer(
                        subcategory_id,
                        layer_geometry_id,
                        layer_mode_id,
                        hazard_category_id)
        else:
            # There are no classifications for exposures defined yet
            return []

    def additional_keywords_for_the_layer(self):
        """Return a list of valid additional keywords for the current layer.

        :returns: A list where each value represents a valid additional kw.
        :rtype: list
        """
        layer_geometry_key = self.get_layer_geometry_id()
        layer_mode_key = self.selected_layermode()['key']
        if self.selected_category() == layer_purpose_hazard:
            hazard_category_key = self.selected_hazard_category()['key']
            hazard_key = self.selected_subcategory()['key']
            return self.impact_function_manager.hazard_additional_keywords(
                layer_mode_key, layer_geometry_key,
                hazard_category_key, hazard_key)
        else:
            exposure_key = self.selected_subcategory()['key']
            return self.impact_function_manager.exposure_additional_keywords(
                layer_mode_key, layer_geometry_key, exposure_key)

    def field_keyword_for_the_layer(self):
        """Return the proper keyword for field for the current layer.
        Expected values are: 'field', 'structure_class_field', road_class_field

        :returns: the field keyword
        :rtype: string
        """

        if self.selected_category() == layer_purpose_aggregation:
            # purpose: aggregation
            return 'aggregation attribute'
        elif self.selected_category() == layer_purpose_hazard:
            # purpose: hazard
            if (self.selected_layermode() == layer_mode_classified and
                    is_point_layer(self.layer)):
                # No field for classified point hazards
                return ''
        else:
            # purpose: exposure
            layer_mode_key = self.selected_layermode()['key']
            layer_geometry_key = self.get_layer_geometry_id()
            exposure_key = self.selected_subcategory()['key']
            exposure_class_fields = self.impact_function_manager.\
                exposure_class_fields(
                    layer_mode_key, layer_geometry_key, exposure_key)
            if exposure_class_fields and len(exposure_class_fields) == 1:
                return exposure_class_fields[0]['key']
        # Fallback to default
        return 'field'

    def get_parent_mode_constraints(self):
        """Return the category and subcategory keys to be set in the
        subordinate mode.

        :returns: (the category definition, the hazard/exposure definition)
        :rtype: (dict, dict)
        """
        h, e, _hc, _ec = self.selected_impact_function_constraints()
        if self.parent_step in [step_fc_hazlayer_from_canvas,
                                step_fc_hazlayer_from_browser]:
            category = layer_purpose_hazard
            subcategory = h
        elif self.parent_step in [step_fc_explayer_from_canvas,
                                  step_fc_explayer_from_browser]:
            category = layer_purpose_exposure
            subcategory = e
        elif self.parent_step:
            category = layer_purpose_aggregation
            subcategory = None
        else:
            category = None
            subcategory = None
        return category, subcategory

    # ===========================
    # STEP_KW_CATEGORY
    # ===========================

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_lstCategories_itemSelectionChanged(self):
        """Update purpose description label.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        # Clear all further steps in order to properly calculate the prev step
        self.lstHazardCategories.clear()
        self.lstSubcategories.clear()
        self.lstLayerModes.clear()
        self.lstUnits.clear()
        self.lstFields.clear()
        self.lstClassifications.clear()
        # Set widgets
        category = self.selected_category()
        # Exit if no selection
        if not category:
            return
        # Set description label
        self.lblDescribeCategory.setText(category["description"])
        self.lblIconCategory.setPixmap(QPixmap(
            resources_path('img', 'wizard', 'keyword-category-%s.svg'
                           % (category['key'] or 'notset'))))
        # Enable the next button
        self.pbnNext.setEnabled(True)

    def selected_category(self):
        """Obtain the layer purpose selected by user.

        :returns: Metadata of the selected layer purpose.
        :rtype: dict, None
        """
        item = self.lstCategories.currentItem()
        try:
            return KeywordIO().definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def set_widgets_step_kw_category(self):
        """Set widgets on the layer purpose tab."""
        # Clear all further steps in order to properly calculate the prev step
        self.lstHazardCategories.clear()
        self.lstSubcategories.clear()
        self.lstLayerModes.clear()
        self.lstUnits.clear()
        self.lstFields.clear()
        self.lstClassifications.clear()
        # Set widgets
        self.lstCategories.clear()
        self.lblDescribeCategory.setText('')
        self.lblIconCategory.setPixmap(QPixmap())
        self.lblSelectCategory.setText(
            category_question % self.layer.name())
        categories = self.purposes_for_layer()
        if self.get_layer_geometry_id() == 'polygon':
            categories += ['aggregation']
        for category in categories:
            if not isinstance(category, dict):
                category = KeywordIO().definition(category)
            item = QListWidgetItem(category['name'], self.lstCategories)
            item.setData(QtCore.Qt.UserRole, category['key'])
            self.lstCategories.addItem(item)

        # Check if layer keywords are already assigned
        category_keyword = self.get_existing_keyword('layer_purpose')

        # Overwrite the category_keyword if it's KW mode embedded in IFCW mode
        if self.parent_step:
            category_keyword = self.get_parent_mode_constraints()[0]['key']

        # Set values based on existing keywords or parent mode
        if category_keyword:
            categories = []
            for index in xrange(self.lstCategories.count()):
                item = self.lstCategories.item(index)
                categories.append(item.data(QtCore.Qt.UserRole))
            if category_keyword in categories:
                self.lstCategories.setCurrentRow(
                    categories.index(category_keyword))

        self.auto_select_one_item(self.lstCategories)

    # ===========================
    # STEP_KW_SUBCATEGORY
    # ===========================

    # noinspection PyPep8Naming
    def on_lstSubcategories_itemSelectionChanged(self):
        """Update subcategory description label.

        .. note:: This is an automatic Qt slot
           executed when the subcategory selection changes.
        """
        # Clear all further steps in order to properly calculate the prev step
        self.lstHazardCategories.clear()
        self.lstLayerModes.clear()
        self.lstUnits.clear()
        self.lstFields.clear()
        self.lstClassifications.clear()
        # Set widgets
        subcategory = self.selected_subcategory()
        # Exit if no selection
        if not subcategory:
            return
        # Set description label
        self.lblDescribeSubcategory.setText(subcategory['description'])

        icon_path = resources_path('img', 'wizard',
                                   'keyword-subcategory-%s.svg'
                                   % (subcategory['key'] or 'notset'))
        if not os.path.exists(icon_path):
            category = self.selected_category()
            icon_path = resources_path('img', 'wizard',
                                       'keyword-category-%s.svg'
                                       % (category['key']))
        self.lblIconSubcategory.setPixmap(QPixmap(icon_path))
        # Enable the next button
        self.pbnNext.setEnabled(True)

    def selected_subcategory(self):
        """Obtain the subcategory selected by user.

        :returns: Metadata of the selected subcategory.
        :rtype: dict, None
        """
        item = self.lstSubcategories.currentItem()
        try:
            return KeywordIO().definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def set_widgets_step_kw_subcategory(self):
        """Set widgets on the Subcategory tab."""
        # Clear all further steps in order to properly calculate the prev step
        self.lstHazardCategories.clear()
        self.lstLayerModes.clear()
        self.lstUnits.clear()
        self.lstFields.clear()
        self.lstClassifications.clear()
        # Set widgets
        category = self.selected_category()
        self.lstSubcategories.clear()
        self.lblDescribeSubcategory.setText('')
        self.lblIconSubcategory.setPixmap(QPixmap())
        self.lblSelectSubcategory.setText(
            get_question_text('%s_question' % category['key']))
        for i in self.subcategories_for_layer():
            item = QListWidgetItem(i['name'], self.lstSubcategories)
            item.setData(QtCore.Qt.UserRole, i['key'])
            self.lstSubcategories.addItem(item)

        # Check if layer keywords are already assigned
        key = self.selected_category()['key']
        keyword = self.get_existing_keyword(key)

        # Overwrite the keyword if it's KW mode embedded in IFCW mode
        if self.parent_step:
            keyword = self.get_parent_mode_constraints()[1]['key']

        # Set values based on existing keywords or parent mode
        if keyword:
            subcategories = []
            for index in xrange(self.lstSubcategories.count()):
                item = self.lstSubcategories.item(index)
                subcategories.append(item.data(QtCore.Qt.UserRole))
            if keyword in subcategories:
                self.lstSubcategories.setCurrentRow(
                    subcategories.index(keyword))

        self.auto_select_one_item(self.lstSubcategories)

    # ===========================
    # STEP_KW_HAZARD_CATEGORY
    # ===========================

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_lstHazardCategories_itemSelectionChanged(self):
        """Update hazard category description label.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        # Clear all further steps in order to properly calculate the prev step
        self.lstLayerModes.clear()
        self.lstUnits.clear()
        self.lstFields.clear()
        self.lstClassifications.clear()
        # Set widgets
        hazard_category = self.selected_hazard_category()
        # Exit if no selection
        if not hazard_category:
            return
        # Set description label
        self.lblDescribeHazardCategory.setText(hazard_category["description"])
        # Enable the next button
        self.pbnNext.setEnabled(True)

    def selected_hazard_category(self):
        """Obtain the hazard category selected by user.

        :returns: Metadata of the selected hazard category.
        :rtype: dict, None
        """
        item = self.lstHazardCategories.currentItem()
        try:
            return KeywordIO().definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def set_widgets_step_kw_hazard_category(self):
        """Set widgets on the Hazard Category tab."""
        # Clear all further steps in order to properly calculate the prev step
        self.lstLayerModes.clear()
        self.lstUnits.clear()
        self.lstFields.clear()
        self.lstClassifications.clear()
        # Set widgets
        self.lstHazardCategories.clear()
        self.lblDescribeHazardCategory.setText('')
        self.lblSelectHazardCategory.setText(
            hazard_category_question)
        hazard_categories = self.hazard_categories_for_layer()
        for hazard_category in hazard_categories:
            if not isinstance(hazard_category, dict):
                hazard_category = KeywordIO().definition(hazard_category)
            item = QListWidgetItem(hazard_category['name'],
                                   self.lstHazardCategories)
            item.setData(QtCore.Qt.UserRole, hazard_category['key'])
            self.lstHazardCategories.addItem(item)

        # Set values based on existing keywords (if already assigned)
        category_keyword = self.get_existing_keyword('hazard_category')
        if category_keyword:
            categories = []
            for index in xrange(self.lstHazardCategories.count()):
                item = self.lstHazardCategories.item(index)
                categories.append(item.data(QtCore.Qt.UserRole))
            if category_keyword in categories:
                self.lstHazardCategories.setCurrentRow(
                    categories.index(category_keyword))

        self.auto_select_one_item(self.lstHazardCategories)

    # ===========================
    # STEP_KW_LAYERMODE
    # ===========================

    # noinspection PyPep8Naming
    def on_lstLayerModes_itemSelectionChanged(self):
        """Update layer mode description label and unit widgets.

        .. note:: This is an automatic Qt slot
           executed when the subcategory selection changes.
        """
        # Clear all further steps in order to properly calculate the prev step
        self.lstUnits.clear()
        self.lstFields.clear()
        self.lstClassifications.clear()
        # Set widgets
        layer_mode = self.selected_layermode()
        # Exit if no selection
        if not layer_mode:
            self.lblDescribeLayerMode.setText('')
            return
        # Set description label
        self.lblDescribeLayerMode.setText(layer_mode['description'])
        # Enable the next button
        self.pbnNext.setEnabled(True)

    def selected_layermode(self):
        """Obtain the layer mode selected by user.
        :returns: selected layer mode.
        :rtype: string, None
        """
        item = self.lstLayerModes.currentItem()
        try:
            return KeywordIO().definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def set_widgets_step_kw_layermode(self):
        """Set widgets on the LayerMode tab."""
        # Clear all further steps in order to properly calculate the prev step
        self.lstUnits.clear()
        self.lstFields.clear()
        self.lstClassifications.clear()
        # Set widgets
        category = self.selected_category()
        subcategory = self.selected_subcategory()
        layer_mode_question = (
            layermode_raster_question
            if is_raster_layer(self.layer)
            else layermode_vector_question)
        self.lblSelectLayerMode.setText(
            layer_mode_question % (subcategory['name'], category['name']))
        self.lblDescribeLayerMode.setText('')
        self.lstLayerModes.clear()
        self.lstUnits.clear()
        self.lstFields.clear()
        layer_modes = self.layermodes_for_layer()
        for layer_mode in layer_modes:
            item = QListWidgetItem(layer_mode['name'], self.lstLayerModes)
            item.setData(QtCore.Qt.UserRole, layer_mode['key'])
            self.lstUnits.addItem(item)

        # Set value to existing keyword or default value
        layermode_keys = [m['key'] for m in layer_modes]
        layermode_keyword = self.get_existing_keyword('layer_mode')
        if layermode_keyword in layermode_keys:
            indx = layermode_keys.index(layermode_keyword)
        elif layer_mode_continuous['key'] in layermode_keys:
            # Set default value
            indx = layermode_keys.index(layer_mode_continuous['key'])
        else:
            indx = -1
        self.lstLayerModes.setCurrentRow(indx)

        self.auto_select_one_item(self.lstLayerModes)

    # ===========================
    # STEP_KW_UNIT
    # ===========================

    # noinspection PyPep8Naming
    def on_lstUnits_itemSelectionChanged(self):
        """Update unit description label and field widgets.

        .. note:: This is an automatic Qt slot
           executed when the unit selection changes.
        """
        # Clear all further steps in order to properly calculate the prev step
        self.lstFields.clear()
        self.lstClassifications.clear()
        # Set widgets
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
            return KeywordIO().definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def set_widgets_step_kw_unit(self):
        """Set widgets on the Unit tab."""
        # Clear all further steps in order to properly calculate the prev step
        self.lstFields.clear()
        self.lstClassifications.clear()
        # Set widgets
        category = self.selected_category()
        subcategory = self.selected_subcategory()
        self.lblSelectUnit.setText(
            unit_question % (subcategory['name'], category['name']))
        self.lblDescribeUnit.setText('')
        self.lstUnits.clear()
        subcat = self.selected_subcategory()['key']
        laygeo = self.get_layer_geometry_id()
        laymod = self.selected_layermode()['key']
        if category == layer_purpose_hazard:
            hazcat = self.selected_hazard_category()['key']
            units_for_layer = self.impact_function_manager.\
                continuous_hazards_units_for_layer(
                    subcat, laygeo, laymod, hazcat)
        else:
            units_for_layer = self.impact_function_manager\
                .exposure_units_for_layer(
                    subcat, laygeo, laymod)
        for unit_for_layer in units_for_layer:
            # if (self.get_layer_geometry_id() == 'raster' and
            #         'constraint' in unit_for_layer and
            #         unit_for_layer['constraint'] == 'categorical'):
            #     continue
            # else:
            item = QListWidgetItem(unit_for_layer['name'], self.lstUnits)
            item.setData(QtCore.Qt.UserRole, unit_for_layer['key'])
            self.lstUnits.addItem(item)

        # Set values based on existing keywords (if already assigned)
        if self.selected_category() == layer_purpose_hazard:
            key = continuous_hazard_unit['key']
        else:
            key = exposure_unit['key']
        unit_id = self.get_existing_keyword(key)
        # unit_id = definitions.old_to_new_unit_id(unit_id)
        if unit_id:
            units = []
            for index in xrange(self.lstUnits.count()):
                item = self.lstUnits.item(index)
                units.append(item.data(QtCore.Qt.UserRole))
            if unit_id in units:
                self.lstUnits.setCurrentRow(units.index(unit_id))

        self.auto_select_one_item(self.lstUnits)

    # ===========================
    # STEP_KW_CLASSIFICATION
    # ===========================

    def on_lstClassifications_itemSelectionChanged(self):
        """Update classification description label and unlock the Next button.

        .. note:: This is an automatic Qt slot
           executed when the field selection changes.
        """
        self.lstFields.clear()
        self.treeClasses.clear()
        classification = self.selected_classification()
        # Exit if no selection
        if not classification:
            return
        # Set description label
        self.lblDescribeClassification.setText(classification["description"])
        # Enable the next button
        self.pbnNext.setEnabled(True)

    def selected_classification(self):
        """Obtain the classification selected by user.

        :returns: Metadata of the selected classification.
        :rtype: dict, None
        """
        item = self.lstClassifications.currentItem()
        try:
            return KeywordIO().definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def set_widgets_step_kw_classification(self):
        """Set widgets on the Classification tab."""
        self.lstFields.clear()
        self.treeClasses.clear()
        category = self.selected_category()['name']
        subcategory = self.selected_subcategory()['name']
        self.lstClassifications.clear()
        self.lblDescribeClassification.setText('')
        self.lblSelectClassification.setText(
            classification_question % (subcategory, category))
        classifications = self.classifications_for_layer()
        for classification in classifications:
            if not isinstance(classification, dict):
                classification = KeywordIO.definition(classification)
            item = QListWidgetItem(classification['name'],
                                   self.lstClassifications)
            item.setData(QtCore.Qt.UserRole, classification['key'])
            self.lstClassifications.addItem(item)

        # Set values based on existing keywords (if already assigned)
        geom = 'raster' if is_raster_layer(self.layer) else 'vector'
        key = '%s_%s_classification' % (geom, self.selected_category()['key'])
        classification_keyword = self.get_existing_keyword(key)
        if classification_keyword:
            classifications = []
            for index in xrange(self.lstClassifications.count()):
                item = self.lstClassifications.item(index)
                classifications.append(item.data(QtCore.Qt.UserRole))
            if classification_keyword in classifications:
                self.lstClassifications.setCurrentRow(
                    classifications.index(classification_keyword))

        self.auto_select_one_item(self.lstClassifications)

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
        # Exit if the selected field comes from a previous wizard run (vector)
        if is_raster_layer(self.layer):
            return
        fields = self.layer.dataProvider().fields()
        field_index = fields.indexFromName(field)
        # Exit if the selected field comes from a previous wizard run
        if field_index < 0:
            return
        field_type = fields.field(field).typeName()
        unique_values = self.layer.uniqueValues(field_index)[0:48]
        unique_values_str = [i is not None and unicode(i) or 'NULL'
                             for i in unique_values]
        if unique_values != self.layer.uniqueValues(field_index):
            unique_values_str += ['...']
        desc = '<br/>%s: %s<br/><br/>' % (self.tr('Field type'), field_type)
        desc += self.tr('Unique values: %s') % ', '.join(unique_values_str)
        self.lblDescribeField.setText(desc)
        # Enable the next buttonlayer_purpose_aggregation
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
        self.treeClasses.clear()
        category = self.selected_category()
        subcategory = self.selected_subcategory()
        unit = self.selected_unit()
        if category == layer_purpose_aggregation:
            question_text = field_question_aggregation
        elif self.selected_layermode() == layer_mode_continuous and unit:
            # unique values, continuous or categorical data
            subcategory_unit_relation = get_question_text(
                '%s_%s_question' % (subcategory['key'], unit['key']))
            question_text = field_question_subcategory_unit % (
                category['name'],
                subcategory['name'],
                unit['name'],
                subcategory_unit_relation)
        else:
            question_text = field_question_subcategory_classified % (
                subcategory['name'])
        self.lblSelectField.setText(question_text)
        self.lstFields.clear()
        default_item = None
        for field in self.layer.dataProvider().fields():
            field_name = field.name()
            item = QListWidgetItem(field_name, self.lstFields)
            item.setData(QtCore.Qt.UserRole, field_name)
            # Select the item if it match the unit's default_attribute
            if unit and 'default_attribute' in unit \
                    and field_name == unit['default_attribute']:
                default_item = item
            # For continuous data, gray out id, gid, fid and text fields
            if self.selected_layermode() == layer_mode_continuous and unit:
                field_type = field.type()
                if field_type > 9 or re.match(
                        '.{0,2}id$', field_name, re.I):
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
        if default_item:
            self.lstFields.setCurrentItem(default_item)
        self.lblDescribeField.clear()

        # Set values based on existing keywords (if already assigned)
        field_keyword = self.field_keyword_for_the_layer()
        field = self.get_existing_keyword(field_keyword)
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

    def selected_allowresampling(self):
        """Obtain the allow_resampling state selected by user.

        .. note:: Returns none if not set or not relevant

        :returns: Value of the allow_resampling or None for not-set.
        :rtype: boolean or None
        """
        if not is_raster_layer(self.layer):
            return None

        if self.selected_category() != layer_purpose_exposure:
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
        layer_mode = self.selected_layermode()
        self.lblSelectAllowResample.setText(
            allow_resampling_question % (
                subcategory['name'], category['name'], layer_mode['name']))

        # Set value based on existing keyword (if already assigned)
        if self.get_existing_keyword('allow_resampling') is False:
            self.chkAllowResample.setChecked(True)

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
                value_list += [tree_leaf.data(0, QtCore.Qt.UserRole)]
            if value_list:
                value_map[tree_branch.text(0)] = value_list
        return value_map

    def set_widgets_step_kw_classify(self):
        """Set widgets on the Classify tab."""
        category = self.selected_category()
        subcategory = self.selected_subcategory()
        classification = self.selected_classification()
        default_classes = classification['classes']
        if is_raster_layer(self.layer):
            self.lblClassify.setText(classify_raster_question % (
                subcategory['name'], category['name'], classification['name']))
            ds = gdal.Open(self.layer.source(), GA_ReadOnly)
            unique_values = numpy.unique(numpy.array(
                ds.GetRasterBand(1).ReadAsArray()))
            field_type = 0
            # Convert datatype to a json serializable type
            if numpy.issubdtype(unique_values.dtype, float):
                unique_values = [float(i) for i in unique_values]
            else:
                unique_values = [int(i) for i in unique_values]
        else:
            field = self.selected_field()
            field_index = self.layer.dataProvider().fields().indexFromName(
                self.selected_field())
            field_type = self.layer.dataProvider().fields()[field_index].type()
            self.lblClassify.setText(classify_vector_question % (
                subcategory['name'], category['name'],
                classification['name'], field.upper()))
            unique_values = self.layer.uniqueValues(field_index)

        # Assign unique values to classes (according to defauls)
        unassigned_values = list()
        assigned_values = dict()
        for default_class in default_classes:
            assigned_values[default_class['name']] = list()
        for unique_value in unique_values:
            if unique_value is None or isinstance(
                    unique_value, QPyNullVariant):
                # Don't classify features with NULL value
                continue
            value_as_string = unicode(unique_value)
            assigned = False
            for default_class in default_classes:
                condition_1 = (
                    field_type > 9 and
                    value_as_string.upper() in [
                        c.upper() for c in default_class['string_defaults']])
                condition_2 = (
                    field_type < 10 and (
                        default_class['numeric_default_min'] <= unique_value <=
                        default_class['numeric_default_max']))
                if condition_1 or condition_2:
                    assigned_values[default_class['name']] += [unique_value]
                    assigned = True
            if not assigned:
                # add to unassigned values list otherwise
                unassigned_values += [unique_value]
        self.populate_classified_values(
            unassigned_values, assigned_values, default_classes)

        # Overwrite assigned values according to existing keyword (if present).
        # Note the default_classes and unique_values are already loaded!

        value_map = self.get_existing_keyword('value_map')
        # Do not continue if there is no value_map in existing keywords
        if value_map is None:
            return

        # Do not continue if user selected different field
        field_keyword = self.field_keyword_for_the_layer()
        field = self.get_existing_keyword(field_keyword)
        if not is_raster_layer(self.layer) and field != self.selected_field():
            return

        unassigned_values = list()
        assigned_values = dict()
        for default_class in default_classes:
            assigned_values[default_class['name']] = list()
        if isinstance(value_map, str):
            try:
                value_map = json.loads(value_map)
            except ValueError:
                return
        for unique_value in unique_values:
            if unique_value is None or isinstance(
                    unique_value, QPyNullVariant):
                # Don't classify features with NULL value
                continue
            # check in value map
            assigned = False
            for key, value_list in value_map.iteritems():
                if unique_value in value_list and key in assigned_values:
                    assigned_values[key] += [unique_value]
                    assigned = True
            if not assigned:
                unassigned_values += [unique_value]
        self.populate_classified_values(
            unassigned_values, assigned_values, default_classes)

    def populate_classified_values(
            self, unassigned_values, assigned_values, default_classes):
        """Populate lstUniqueValues and treeClasses.from the parameters.

        :param unassigned_values: List of values that haven't been assigned
            to a class. It will be put in self.lstUniqueValues.
        :type unassigned_values: list

        :param assigned_values: Dictionary with class as the key and list of
            value as the value of the dictionary. It will be put in
            self.treeClasses.
        :type assigned_values: dict

        :param default_classes: Default classes from unit.
        :type default_classes: list
        """
        # Populate the unique values list
        self.lstUniqueValues.clear()
        for value in unassigned_values:
            value_as_string = value is not None and unicode(value) or 'NULL'
            list_item = QtGui.QListWidgetItem(self.lstUniqueValues)
            list_item.setFlags(QtCore.Qt.ItemIsEnabled |
                               QtCore.Qt.ItemIsSelectable |
                               QtCore.Qt.ItemIsDragEnabled)
            list_item.setData(QtCore.Qt.UserRole, value)
            list_item.setText(value_as_string)
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
                string_value = value is not None and unicode(value) or 'NULL'
                tree_leaf = QtGui.QTreeWidgetItem(tree_branch)
                tree_leaf.setFlags(QtCore.Qt.ItemIsEnabled |
                                   QtCore.Qt.ItemIsSelectable |
                                   QtCore.Qt.ItemIsDragEnabled)
                tree_leaf.setData(0, QtCore.Qt.UserRole, value)
                tree_leaf.setText(0, string_value)

    # ===========================
    # STEP_KW_EXTRAKEYWORDS
    # ===========================

    # noinspection PyPep8Naming
    def on_cboExtraKeyword1_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           1st extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[0])

    # noinspection PyPep8Naming
    def on_cboExtraKeyword2_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           2nd extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[1])

    # noinspection PyPep8Naming
    def on_cboExtraKeyword3_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           3rd extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[2])

    # noinspection PyPep8Naming
    def on_cboExtraKeyword4_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           4th extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[3])

    # noinspection PyPep8Naming
    def on_cboExtraKeyword5_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           5th extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[4])

    # noinspection PyPep8Naming
    def on_cboExtraKeyword6_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           6th extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[5])

    # noinspection PyPep8Naming
    def on_cboExtraKeyword7_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           7th extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[6])

    # noinspection PyPep8Naming
    def on_cboExtraKeyword8_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           8th extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[7])

    def extra_keyword_changed(self, widget):
        """Populate slave widget if exists and enable the Next button
           if all extra keywords are set.

        :param widget: Metadata of the widget where the event happened.
        :type widget: dict
        """
        if 'slave_key' in widget and widget['slave_key']:
            for w in self.extra_keywords_widgets:
                if w['key'] == widget['slave_key']:
                    field_name = widget['cbo'].itemData(
                        widget['cbo'].currentIndex(), QtCore.Qt.UserRole)
                    self.populate_value_widget_from_field(w['cbo'], field_name)

        self.pbnNext.setEnabled(self.are_all_extra_keywords_selected())

    def selected_extra_keywords(self):
        """Obtain the extra keywords selected by user.

        :returns: Metadata of the extra keywords.
        :rtype: dict, None
        """
        extra_keywords = {}
        for ekw in self.extra_keywords_widgets:
            if ekw['key'] is not None and ekw['cbo'].currentIndex() != -1:
                key = ekw['key']
                val = ekw['cbo'].itemData(ekw['cbo'].currentIndex(),
                                          QtCore.Qt.UserRole)
                extra_keywords[key] = val
        return extra_keywords

    def are_all_extra_keywords_selected(self):
        """Ensure all all additional keyword are set by user

        :returns: True if all additional keyword widgets are set
        :rtype: boolean
        """
        for ekw in self.extra_keywords_widgets:
            if ekw['key'] is not None and ekw['cbo'].currentIndex() == -1:
                return False
        return True

    def populate_value_widget_from_field(self, widget, field_name):
        """Populate the slave widget with unique values of the field
           selected in the master widget.

        :param widget: The widget to be populated
        :type widget: QComboBox

        :param field_name: Name of the field to take the values from
        :type field_name: str
        """
        fields = self.layer.dataProvider().fields()
        field_index = fields.indexFromName(field_name)
        widget.clear()
        for v in self.layer.uniqueValues(field_index):
            widget.addItem(unicode(v), unicode(v))
        widget.setCurrentIndex(-1)

    def set_widgets_step_kw_extrakeywords(self):
        """Set widgets on the Extra Keywords tab."""
        # Hide all widgets
        for ekw in self.extra_keywords_widgets:
            ekw['cbo'].clear()
            ekw['cbo'].hide()
            ekw['lbl'].hide()
            ekw['key'] = None
            ekw['master_key'] = None

        # Set and show used widgets
        extra_keywords = self.additional_keywords_for_the_layer()
        for i in range(len(extra_keywords)):
            extra_keyword = extra_keywords[i]
            extra_keywords_widget = self.extra_keywords_widgets[i]
            extra_keywords_widget['key'] = extra_keyword['key']
            extra_keywords_widget['lbl'].setText(extra_keyword['description'])
            if extra_keyword['type'] == 'value':
                field_widget = self.extra_keywords_widgets[i - 1]['cbo']
                field_name = field_widget.itemData(
                    field_widget.currentIndex(), QtCore.Qt.UserRole)
                self.populate_value_widget_from_field(
                    extra_keywords_widget['cbo'], field_name)
            else:
                for field in self.layer.dataProvider().fields():
                    field_name = field.name()
                    field_type = field.typeName()
                    extra_keywords_widget['cbo'].addItem('%s (%s)' % (
                        field_name, field_type), field_name)
            # If there is a master keyword, attach this widget as a slave
            # to the master widget. It's used for values of a given field.
            if ('master_keyword' in extra_keyword and
                    extra_keyword['master_keyword']):
                master_key = extra_keyword['master_keyword']['key']
                for master_candidate in self.extra_keywords_widgets:
                    if master_candidate['key'] == master_key:
                        master_candidate['slave_key'] = extra_keyword['key']
            # Show the widget
            extra_keywords_widget['cbo'].setCurrentIndex(-1)
            extra_keywords_widget['lbl'].show()
            extra_keywords_widget['cbo'].show()

        # Set values based on existing keywords (if already assigned)
        for ekw in self.extra_keywords_widgets:
            if not ekw['key']:
                continue
            value = self.get_existing_keyword(ekw['key'])
            indx = ekw['cbo'].findData(value, QtCore.Qt.UserRole)
            if indx != -1:
                ekw['cbo'].setCurrentIndex(indx)

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

    # noinspection PyPep8Naming
    def on_ckbSource_date_toggled(self, state):
        """This is an automatic Qt slot executed when the checkbox is toggled

        :param state: the new state
        :type state: boolean
        """
        self.dtSource_date.setEnabled(state)

    def set_widgets_step_kw_source(self):
        """Set widgets on the Source tab."""
        # Just set values based on existing keywords
        source = self.get_existing_keyword('source')
        if source or source == 0:
            self.leSource.setText(get_unicode(source))
        else:
            self.leSource.clear()

        source_scale = self.get_existing_keyword('scale')
        if source_scale or source_scale == 0:
            self.leSource_scale.setText(get_unicode(source_scale))
        else:
            self.leSource_scale.clear()

        source_date = self.get_existing_keyword('date')
        if source_date:
            self.ckbSource_date.setChecked(True)
            self.dtSource_date.setDateTime(
                QDateTime.fromString(get_unicode(source_date),
                                     'dd-MM-yyyy HH:mm'))
        else:
            self.ckbSource_date.setChecked(False)
            self.dtSource_date.clear()

        source_url = self.get_existing_keyword('url')
        if source_url or source_url == 0:
            self.leSource_url.setText(get_unicode(source_url))
        else:
            self.leSource_url.clear()

        source_license = self.get_existing_keyword('license')
        if source_license or source_license == 0:
            self.leSource_license.setText(get_unicode(source_license))
        else:
            self.leSource_license.clear()

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
    # STEP_KW_SUMMARY
    # ===========================

    def set_widgets_step_kw_summary(self):
        """Set widgets on the Keywords Summary tab."""

        current_keywords = self.get_keywords()
        current_keywords[inasafe_keyword_version_key] = inasafe_keyword_version

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.pardir,
                                                os.pardir,
                                                os.pardir,
                                                'resources'))
        header_path = os.path.join(base_dir, 'header.html')
        footer_path = os.path.join(base_dir, 'footer.html')
        header_file = file(header_path)
        footer_file = file(footer_path)
        header = header_file.read()
        footer = footer_file.read()
        header_file.close()
        footer_file.close()
        header = header.replace('PATH', base_dir)

        # TODO: Clone the dict inside keyword_io.to_message rather then here.
        #       It pops the dict elements damaging the function parameter
        body = self.keyword_io.to_message(dict(current_keywords)).to_html()
        # remove the branding div
        body = re.sub(r'^.*div class="branding".*$', "",
                      body, flags=re.MULTILINE)

        if self.parent_step:
            # It's the KW mode embedded in IFCW mode,
            # so check if the layer is compatible
            im_func = self.selected_function()
            if not self.is_layer_compatible(self.layer,
                                            None,
                                            current_keywords):
                msg = self.tr(
                    'The selected keywords don\'t match requirements of the '
                    'selected impact fuction (%s). You can confinue with '
                    'registering the layer, however, you\'ll need to choose '
                    'another layer for that function.') % im_func['name']
                body = '<br/><h5 class="problem">%s</h5> %s' % (msg, body)

        html = header + body + footer
        self.wvKwSummary.setHtml(html)

    # ===========================
    # STEP_FC_FUNCTION_1
    # ===========================

    def selected_functions_1(self):
        """Obtain functions available for hazard an exposure selected by user.

        :returns: List of the available functions metadata.
        :rtype: list, None
        """
        selection = self.tblFunctions1.selectedItems()
        if len(selection) != 1:
            return []
        try:
            return selection[0].data(RoleFunctions)
        except (AttributeError, NameError):
            return None

    def selected_impact_function_constraints(self):
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
            txt = self.tr('Available functions:') + ' ' + ', '.join(
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
    # noinspection PyPep8Naming
    def on_tblFunctions1_cellDoubleClicked(self, row, column):
        """Choose selected hazard x exposure combination and go ahead.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        self.pbnNext.click()
    # pylint: enable=W0613

    def populate_function_table_1(self):
        """Populate the tblFunctions1 table with available functions."""
        # The hazard category radio buttons are now removed -
        # make this parameter of IFM.available_hazards() optional
        hazard_category = hazard_category_single_event
        hazards = self.impact_function_manager\
            .available_hazards(hazard_category['key'])
        # Remove 'generic' from hazards
        for h in hazards:
            if h['key'] == 'generic':
                hazards.remove(h)
        exposures = self.impact_function_manager.available_exposures()

        self.lblAvailableFunctions1.clear()
        self.tblFunctions1.clear()
        self.tblFunctions1.setColumnCount(len(hazards))
        self.tblFunctions1.setRowCount(len(exposures))
        for i in range(len(hazards)):
            h = hazards[i]
            item = QtGui.QTableWidgetItem()
            item.setIcon(QtGui.QIcon(
                resources_path('img', 'wizard', 'keyword-subcategory-%s.svg'
                               % (h['key'] or 'notset'))))
            item.setText(h['name'].capitalize())
            self.tblFunctions1.setHorizontalHeaderItem(i, item)
        for i in range(len(exposures)):
            e = exposures[i]
            item = QtGui.QTableWidgetItem()
            item.setIcon(QtGui.QIcon(
                resources_path('img', 'wizard', 'keyword-subcategory-%s.svg'
                               % (e['key'] or 'notset'))))
            item.setText(e['name'].capitalize())
            self.tblFunctions1.setVerticalHeaderItem(i, item)

        big_font = QtGui.QFont()
        big_font.setPointSize(80)

        for h in hazards:
            for e in exposures:
                item = QtGui.QTableWidgetItem()
                functions = \
                    self.impact_function_manager.functions_for_constraint(
                        h['key'], e['key'])
                if len(functions):
                    background_colour = QtGui.QColor(120, 255, 120)
                else:
                    background_colour = QtGui.QColor(220, 220, 220)
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
                item.setBackground(QtGui.QBrush(background_colour))
                item.setFont(big_font)
                item.setTextAlignment(QtCore.Qt.AlignCenter |
                                      QtCore.Qt.AlignHCenter)
                item.setData(RoleFunctions, functions)
                item.setData(RoleHazard, h)
                item.setData(RoleExposure, e)
                self.tblFunctions1.setItem(
                    exposures.index(e), hazards.index(h), item)
        self.pbnNext.setEnabled(False)

    def set_widgets_step_fc_function_1(self):
        """Set widgets on the Impact Functions Table 1 tab."""

        self.tblFunctions1.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)
        self.tblFunctions1.verticalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)

        self.populate_function_table_1()

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
            text = self.tr('Available functions:') + ' ' + ', '.join(
                [f['name'] for f in functions])
            self.lblAvailableFunctions2.setText(text)
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
    # noinspection PyPep8Naming,PyUnusedLocal
    def on_tblFunctions2_cellDoubleClicked(self, row, column):
        """Click handler for selecting hazard and exposure constraints.

        :param row: The row that the user clicked on.
        :type row: int

        :param column: The column that the user clicked on.
        :type column: int

        .. note:: This is an automatic Qt slot executed when the category
            selection changes.
        """
        self.pbnNext.click()
    # pylint: enable=W0613

    def set_widgets_step_fc_function_2(self):
        """Set widgets on the Impact Functions Table 2 tab."""
        self.tblFunctions2.clear()
        h, e, _hc, _ec = self.selected_impact_function_constraints()
        hazard_layer_geometries = [
            layer_geometry_raster,
            layer_geometry_point,
            layer_geometry_line,
            layer_geometry_polygon]
        exposure_layer_geometries = [
            layer_geometry_raster,
            layer_geometry_point,
            layer_geometry_line,
            layer_geometry_polygon]
        self.lblSelectFunction2.setText(
            select_function_constraints2_question % (h['name'], e['name']))
        self.tblFunctions2.setColumnCount(len(hazard_layer_geometries))
        self.tblFunctions2.setRowCount(len(exposure_layer_geometries))
#         self.tblFunctions2.setHorizontalHeaderLabels(
#             [i['layer_geometry'].capitalize() if i['layer_mode'] != 'raster'
#              else ('%s %s' % (i['layer_geometry'],
#                               i['layer_mode'])).capitalize()
#              for i in hazard_layer_geometries])
#         for i in range(len(exposure_layer_geometries)):
#             constr = exposure_layer_geometries[i]
#             item = QtGui.QTableWidgetItem()
#             if constr['layer_mode'] == 'raster':
#                 text = '%s\n%s' % (constr['layer_geometry'],
#                                    constr['layer_mode'])
#             else:
#                 text = constr['layer_geometry']
#             item.setText(text.capitalize())
#             item.setTextAlignment(QtCore.Qt.AlignCenter)
#             self.tblFunctions2.setVerticalHeaderItem(i, item)
        self.tblFunctions2.setHorizontalHeaderLabels(
            [i['name'].capitalize() for i in hazard_layer_geometries])
        for i in range(len(exposure_layer_geometries)):
            item = QtGui.QTableWidgetItem()
            item.setText(exposure_layer_geometries[i]['name'].capitalize())
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tblFunctions2.setVerticalHeaderItem(i, item)

        self.tblFunctions2.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)
        self.tblFunctions2.verticalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)

        big_font = QtGui.QFont()
        big_font.setPointSize(80)

        active_items = []
        for col in range(len(hazard_layer_geometries)):
            for row in range(len(exposure_layer_geometries)):
                hc = hazard_layer_geometries[col]
                ec = exposure_layer_geometries[row]
                functions = self.impact_function_manager\
                    .functions_for_constraint(
                        h['key'], e['key'], hc['key'], ec['key'])
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
        description = '<table border="0">'
        if "name" in imfunc.keys():
            description += '<tr><td><b>%s</b>: </td><td>%s</td></tr>' % (
                self.tr('Function'), imfunc['name'])
        if "overview" in imfunc.keys():
            description += '<tr><td><b>%s</b>: </td><td>%s</td></tr>' % (
                self.tr('Overview'), imfunc['overview'])
        description += '</table>'
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

        h, e, hc, ec = self.selected_impact_function_constraints()
        functions = self.impact_function_manager.functions_for_constraint(
            h['key'], e['key'], hc['key'], ec['key'])
        self.lblSelectFunction.setText(
            select_function_question % (
                hc['name'], h['name'], ec['name'], e['name']))
        for f in functions:
            item = QtGui.QListWidgetItem(self.lstFunctions)
            item.setText(f['name'])
            item.setData(QtCore.Qt.UserRole, f)
        self.auto_select_one_item(self.lstFunctions)

        # Set hazard and exposure icons on next steps
        icon_path = resources_path('img', 'wizard',
                                   'keyword-subcategory-%s.svg'
                                   % (h['key'] or 'notset'))
        self.lblIconFunctionHazard.setPixmap(QPixmap(icon_path))
        self.lblIconIFCWHazardOrigin.setPixmap(QPixmap(icon_path))
        self.lblIconIFCWHazardFromCanvas.setPixmap(QPixmap(icon_path))
        self.lblIconIFCWHazardFromBrowser.setPixmap(QPixmap(icon_path))
        icon_path = resources_path('img', 'wizard',
                                   'keyword-subcategory-%s.svg'
                                   % (e['key'] or 'notset'))
        self.lblIconFunctionExposure.setPixmap(QPixmap(icon_path))
        self.lblIconIFCWExposureOrigin.setPixmap(QPixmap(icon_path))
        self.lblIconIFCWExposureFromCanvas.setPixmap(QPixmap(icon_path))
        self.lblIconIFCWExposureFromBrowser.setPixmap(QPixmap(icon_path))

        icon_path = resources_path('img', 'wizard',
                                   'keyword-category-aggregation.svg')
        # Temporarily hide aggregation icon until we have one suitable
        # (as requested in a comment to PR #2060)
        icon_path = None
        self.lblIconIFCWAggregationOrigin.setPixmap(QPixmap(icon_path))
        self.lblIconIFCWAggregationFromCanvas.setPixmap(QPixmap(icon_path))
        self.lblIconIFCWAggregationFromBrowser.setPixmap(QPixmap(icon_path))

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

    def is_layer_compatible(self, layer, layer_purpose=None, keywords=None):
        """Validate if a given layer is compatible for selected IF
           as a given layer_purpose

        :param layer: The layer to be validated
        :type layer: QgsVectorLayer | QgsRasterLayer

        :param layer_purpose: The layer_purpose the layer is validated for
        :type layer_purpose: None, string

        :param keywords: The layer keywords
        :type keywords: None, dict

        :returns: True if layer is appropriate for the selected role
        :rtype: boolean
        """

        # If not explicitly stated, find the desired purpose
        # from the parent step
        if not layer_purpose:
            layer_purpose = self.get_parent_mode_constraints()[0]['key']

        # If not explicitly stated, read the layer's keywords
        if not keywords:
            try:
                keywords = self.keyword_io.read_keywords(layer)
                if ('layer_purpose' not in keywords and
                        'impact_summary' not in keywords):
                    keywords = None
            except (HashNotFoundError,
                    OperationalError,
                    NoKeywordsFoundError,
                    KeywordNotFoundError,
                    InvalidParameterError,
                    UnsupportedProviderError):
                keywords = None

        # Get allowed subcategory and layer_geometry from IF constraints
        h, e, hc, ec = self.selected_impact_function_constraints()
        if layer_purpose == 'hazard':
            subcategory = h['key']
            layer_geometry = hc['key']
        elif layer_purpose == 'exposure':
            subcategory = e['key']
            layer_geometry = ec['key']
        else:
            # For aggregation layers, use a simplified test and return
            if (keywords and 'layer_purpose' in keywords and
                    keywords['layer_purpose'] == layer_purpose):
                return True
            if not keywords and is_polygon_layer(layer):
                return True
            return False

        # Compare layer properties with explicitly set constraints
        # Reject if layer geometry doesn't match
        if layer_geometry != self.get_layer_geometry_id(layer):
            return False

        # If no keywords, there's nothing more we can check.
        # The same if the keywords version doesn't match
        if not keywords or 'keyword_version' not in keywords:
            return True
        keyword_version = str(keywords['keyword_version'])
        if compare_version(keyword_version, get_version()) != 0:
            return True

        # Compare layer keywords with explicitly set constraints
        # Reject if layer purpose missing or doesn't match
        if ('layer_purpose' not in keywords or
                keywords['layer_purpose'] != layer_purpose):
            return False

        # Reject if layer subcategory doesn't match
        if (layer_purpose in keywords and
                keywords[layer_purpose] != subcategory):
            return False

        # Compare layer keywords with the chosen function's constraints

        imfunc = self.selected_function()
        lay_req = imfunc['layer_requirements'][layer_purpose]

        # Reject if layer mode doesn't match
        if ('layer_mode' in keywords and
                lay_req['layer_mode']['key'] != keywords['layer_mode']):
            return False

        # Reject if classification doesn't match
        classification_key = '%s_%s_classification' % (
            'raster' if is_raster_layer(layer) else 'vector',
            layer_purpose)
        classification_keys = classification_key + 's'
        if (lay_req['layer_mode'] == layer_mode_classified and
                classification_key in keywords and
                classification_keys in lay_req):
            allowed_classifications = [
                c['key'] for c in lay_req[classification_keys]]
            if keywords[classification_key] not in allowed_classifications:
                return False

        # Reject if unit doesn't match
        unit_key = ('continuous_hazard_unit'
                    if layer_purpose == layer_purpose_hazard['key']
                    else 'exposure_unit')
        unit_keys = unit_key + 's'
        if (lay_req['layer_mode'] == layer_mode_continuous and
                unit_key in keywords and
                unit_keys in lay_req):
            allowed_units = [
                c['key'] for c in lay_req[unit_keys]]
            if keywords[unit_key] not in allowed_units:
                return False

        # Finally return True
        return True

    def get_compatible_layers_from_canvas(self, category):
        """Collect compatible layers from map canvas.

        .. note:: Returns layers with keywords and layermode matching
           the category and compatible with the selected impact function.
           Also returns layers without keywords with layermode
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
                if ('layer_purpose' not in keywords and
                        'impact_summary' not in keywords):
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
            self.rbHazLayerFromCanvas.setText(tr(
                'I would like to use a hazard layer already loaded in QGIS\n'
                '(launches the %s for hazard if needed)'
            ) % self.keyword_creation_wizard_name)
            self.rbHazLayerFromCanvas.setEnabled(True)
            self.rbHazLayerFromCanvas.click()
        else:
            self.rbHazLayerFromCanvas.setText(tr(
                'I would like to use a hazard layer already loaded in QGIS\n'
                '(no suitable layers found)'))
            self.rbHazLayerFromCanvas.setEnabled(False)
            self.rbHazLayerFromBrowser.click()

        # Set the memo labels on this and next (hazard) steps
        (hazard,
         _,
         hazard_constraints,
         _) = self.selected_impact_function_constraints()

        layer_geometry = hazard_constraints['name']

        text = (select_hazard_origin_question % (
            layer_geometry,
            hazard['name'],
            self.selected_function()['name']))
        self.lblSelectHazLayerOriginType.setText(text)

        text = (select_hazlayer_from_canvas_question % (
            layer_geometry,
            hazard['name'],
            self.selected_function()['name']))
        self.lblSelectHazardLayer.setText(text)

        text = (select_hazlayer_from_browser_question % (
            layer_geometry,
            hazard['name'],
            self.selected_function()['name']))
        self.lblSelectBrowserHazLayer.setText(text)

    # ===========================
    # STEP_FC_HAZLAYER_FROM_CANVAS
    # ===========================

    def get_layer_description_from_canvas(self, layer, purpose):
        """Obtain the description of a canvas layer selected by user.

        :param layer: The QGIS layer.
        :type layer: QgsMapLayer

        :param category: The category of the layer to get the description.
        :type category: string

        :returns: description of the selected layer.
        :rtype: string
        """
        if not layer:
            return ""

        try:
            keywords = self.keyword_io.read_keywords(layer)
            if 'layer_purpose' not in keywords:
                keywords = None
        except (HashNotFoundError,
                OperationalError,
                NoKeywordsFoundError,
                KeywordNotFoundError,
                InvalidParameterError,
                UnsupportedProviderError):
            keywords = None

        # set the current layer (e.g. for the keyword creation sub-thread)
        self.layer = layer
        if purpose == 'hazard':
            self.hazard_layer = layer
        elif purpose == 'exposure':
            self.exposure_layer = layer
        else:
            self.aggregation_layer = layer

        # Check if the layer is keywordless
        if keywords and 'keyword_version' in keywords:
            kw_ver = str(keywords['keyword_version'])
            self.is_selected_layer_keywordless = bool(
                compare_version(kw_ver, get_version()) != 0)
        else:
            self.is_selected_layer_keywordless = True

        desc = self.layer_description_html(layer, keywords)
        return desc

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_lstCanvasHazLayers_itemSelectionChanged(self):
        """Update layer description label

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """

        self.hazard_layer = self.selected_canvas_hazlayer()
        lblText = self.get_layer_description_from_canvas(self.hazard_layer,
                                                         'hazard')
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

    def layer_description_html(self, layer, keywords=None):
        """Form a html description of a given layer based on the layer
           parameters and keywords if provided

        :param layer: The layer to get the description
        :type layer: QgsMapLayer

        :param keywords: The layer keywords
        :type keywords: None, dict

        :returns: The html description in tabular format,
            ready to use in a label or tool tip.
        :rtype: str
        """

        if keywords and 'keyword_version' in keywords:
            keyword_version = str(keywords['keyword_version'])
        else:
            keyword_version = None

        if (keywords and keyword_version and
                compare_version(keyword_version, get_version()) == 0):
            # The layer has valid keywords
            purpose = keywords.get('layer_purpose')
            if purpose == layer_purpose_hazard['key']:
                subcategory = '<tr><td><b>%s</b>: </td><td>%s</td></tr>' % (
                    self.tr('Hazard'), keywords.get(purpose))
                unit = keywords.get('continuous_hazard_unit')
            elif purpose == layer_purpose_exposure['key']:
                subcategory = '<tr><td><b>%s</b>: </td><td>%s</td></tr>' % (
                    self.tr('Exposure'), keywords.get(purpose))
                unit = keywords.get('exposure_unit')
            else:
                subcategory = ''
                unit = None
            if keywords.get('layer_mode') == layer_mode_classified['key']:
                unit = self.tr('classified data')
            if unit:
                unit = '<tr><td><b>%s</b>: </td><td>%s</td></tr>' % (
                    self.tr('Unit'), unit)

            desc = """
                <table border="0" width="100%%">
                <tr><td><b>%s</b>: </td><td>%s</td></tr>
                <tr><td><b>%s</b>: </td><td>%s</td></tr>
                %s
                %s
                <tr><td><b>%s</b>: </td><td>%s</td></tr>
                </table>
            """ % (self.tr('Title'), keywords.get('title'),
                   self.tr('Purpose'), keywords.get('layer_purpose'),
                   subcategory,
                   unit,
                   self.tr('Source'), keywords.get('source'))
        elif keywords:
            # The layer has keywords, but the version is wrong
            desc = self.tr(
                'Your layer\'s keyword\'s version (%s) does not match with '
                'your InaSAFE version (%s). If you wish to use it as an '
                'exposure, hazard, or aggregation layer in an analysis, '
                'please update the keywords. Click Next if you want to assign '
                'keywords now.' % (keyword_version or 'No Version',
                                   get_version()))
        else:
            # The layer is keywordless
            if is_point_layer(layer):
                geom_type = 'point'
            elif is_polygon_layer(layer):
                geom_type = 'polygon'
            else:
                geom_type = 'line'

            # hide password in the layer source
            source = re.sub(
                r'password=\'.*\'', r'password=*****', layer.source())

            desc = """
                %s<br/><br/>
                <b>%s</b>: %s<br/>
                <b>%s</b>: %s<br/><br/>
                %s
            """ % (self.tr('This layer has no valid keywords assigned'),
                   self.tr('SOURCE'), source,
                   self.tr('TYPE'), is_raster_layer(layer) and 'raster' or
                   'vector (%s)' % geom_type,
                   self.tr('In the next step you will be able' +
                           ' to assign keywords to this layer.'))
        return desc

    def unsuitable_layer_description_html(self, layer, layer_purpose,
                                          keywords=None):
        """Form a html description of a given non-matching layer based on
           the currently selected impact function requirements vs layer\'s
           parameters and keywords if provided, as

        :param layer: The layer to be validated
        :type layer: QgsVectorLayer | QgsRasterLayer

        :param layer_purpose: The layer_purpose the layer is validated for
        :type layer_purpose: string

        :param keywords: The layer keywords
        :type keywords: None, dict

        :returns: The html description in tabular format,
            ready to use in a label or tool tip.
        :rtype: str
        """

        def emphasize(str1, str2):
            ''' Compare two strings and emphasize both if differ '''
            if str1 != str2:
                str1 = '<i>%s</i>' % str1
                str2 = '<i>%s</i>' % str2
            return (str1, str2)

        # Get allowed subcategory and layer_geometry from IF constraints
        h, e, hc, ec = self.selected_impact_function_constraints()
        imfunc = self.selected_function()
        lay_req = imfunc['layer_requirements'][layer_purpose]

        if layer_purpose == layer_purpose_hazard['key']:
            layer_purpose_key_name = layer_purpose_hazard['name']
            req_subcategory = h['key']
            req_geometry = hc['key']
        elif layer_purpose == layer_purpose_exposure['key']:
            layer_purpose_key_name = layer_purpose_exposure['name']
            req_subcategory = e['key']
            req_geometry = ec['key']
        else:
            layer_purpose_key_name = layer_purpose_aggregation['name']
            req_subcategory = ''
            # For aggregation layers, only accept polygons
            req_geometry = layer_geometry_polygon['key']
        req_layer_mode = lay_req['layer_mode']['key']

        lay_geometry = self.get_layer_geometry_id(layer)
        lay_purpose = '&nbsp;&nbsp;-'
        lay_subcategory = '&nbsp;&nbsp;-'
        lay_layer_mode = '&nbsp;&nbsp;-'

        if keywords:
            if 'layer_purpose' in keywords:
                lay_purpose = keywords['layer_purpose']
            if layer_purpose in keywords:
                lay_subcategory = keywords[layer_purpose]
            if 'layer_mode' in keywords:
                lay_layer_mode = keywords['layer_mode']

        lay_geometry, req_geometry = emphasize(lay_geometry, req_geometry)
        lay_purpose, layer_purpose = emphasize(lay_purpose, layer_purpose)
        lay_subcategory, req_subcategory = emphasize(lay_subcategory,
                                                     req_subcategory)
        lay_layer_mode, req_layer_mode = emphasize(lay_layer_mode,
                                                   req_layer_mode)

        # Classification
        classification_row = ''
        if (lay_req['layer_mode'] == layer_mode_classified and
                layer_purpose == layer_purpose_hazard['key']):
            # Determine the keyword key for the classification
            classification_obj = (raster_hazard_classification
                                  if is_raster_layer(layer)
                                  else vector_hazard_classification)
            classification_key = classification_obj['key']
            classification_key_name = classification_obj['name']
            classification_keys = classification_key + 's'

            if classification_keys in lay_req:
                allowed_classifications = [
                    c['key'] for c in lay_req[classification_keys]]
                req_classifications = ', '.join(allowed_classifications)

                lay_classification = '&nbsp;&nbsp;-'
                if classification_key in keywords:
                    lay_classification = keywords[classification_key]

                if lay_classification not in allowed_classifications:
                    # We already know we want to empasize them and the test
                    # inside the function will always pass.
                    lay_classification, req_classifications = emphasize(
                        lay_classification, req_classifications)
                classification_row = (('<tr><td><b>%s</b></td>' +
                                       '<td>%s</td><td>%s</td></tr>')
                                      % (classification_key_name,
                                         lay_classification,
                                         req_classifications))

        # Unit
        units_row = ''
        if lay_req['layer_mode'] == layer_mode_continuous:
            # Determine the keyword key for the unit
            unit_obj = (continuous_hazard_unit
                        if layer_purpose == layer_purpose_hazard['key']
                        else exposure_unit)
            unit_key = unit_obj['key']
            unit_key_name = unit_obj['name']
            unit_keys = unit_key + 's'

            if unit_keys in lay_req:
                allowed_units = [c['key'] for c in lay_req[unit_keys]]
                req_units = ', '.join(allowed_units)

                lay_unit = '&nbsp;&nbsp;-'
                if unit_key in keywords:
                    lay_unit = keywords[unit_key]

                if lay_unit not in allowed_units:
                    # We already know we want to empasize them and the test
                    # inside the function will always pass.
                    lay_unit, req_units = emphasize(lay_unit, req_units)
                units_row = (('<tr><td><b>%s</b></td>' +
                              '<td>%s</td><td>%s</td></tr>')
                             % (unit_key_name, lay_unit, req_units))

        html = '''
            <table border="0" width="100%%" cellpadding="2">
                <tr><td width="33%%"></td>
                    <td width="33%%"><b>%s</b></td>
                    <td width="33%%"><b>%s</b></td>
                </tr>
                <tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>
                <tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>
                <tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>
                <tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>
                %s
                %s
            </table>
        ''' % (self.tr('Layer'), self.tr('Required'),
               safe.definitions.layer_geometry['name'],
               lay_geometry, req_geometry,
               safe.definitions.layer_purpose['name'],
               lay_purpose, layer_purpose,
               layer_purpose_key_name, lay_subcategory, req_subcategory,
               safe.definitions.layer_mode['name'],
               lay_layer_mode, req_layer_mode,
               classification_row,
               units_row)
        return html

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
        elif category == 'aggregation':
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
            return False, self.tr('Not a valid layer.')

        try:
            keywords = self.keyword_io.read_keywords(layer)
            if ('layer_purpose' not in keywords and
                    'impact_summary' not in keywords):
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
            label_text = '%s<br/>%s' % (self.tr('This layer\'s keywords ' +
                                                'or type are not suitable:'),
                                        self.unsuitable_layer_description_html(
                                            layer, category, keywords))
            return False, label_text

        # set the current layer (e.g. for the keyword creation sub-thread
        #                          or for adding the layer to mapCanvas)
        self.layer = layer
        if category == 'hazard':
            self.hazard_layer = layer
        elif category == 'exposure':
            self.exposure_layer = layer
        else:
            self.aggregation_layer = layer

        # Check if the layer is keywordless
        if keywords and 'keyword_version' in keywords:
            kw_ver = str(keywords['keyword_version'])
            self.is_selected_layer_keywordless = bool(
                compare_version(kw_ver, get_version()) != 0)
        else:
            self.is_selected_layer_keywordless = True

        desc = self.layer_description_html(layer, keywords)
        return True, desc

    # noinspection PyPep8Naming
    def tvBrowserHazard_selection_changed(self):
        """Update layer description label"""
        (is_compatible, desc) = self.get_layer_description_from_browser(
            'hazard')
        self.lblDescribeBrowserHazLayer.setText(desc)
        self.lblDescribeBrowserHazLayer.setEnabled(is_compatible)
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
            self.rbExpLayerFromCanvas.setText(tr(

                'I would like to use an exposure layer already loaded in QGIS'
                '\n'
                '(launches the %s for exposure if needed)'
            ) % self.keyword_creation_wizard_name)
            self.rbExpLayerFromCanvas.setEnabled(True)
            self.rbExpLayerFromCanvas.click()
        else:
            self.rbExpLayerFromCanvas.setText(tr(

                'I would like to use an exposure layer already loaded in QGIS'
                '\n'
                '(no suitable layers found)'))
            self.rbExpLayerFromCanvas.setEnabled(False)
            self.rbExpLayerFromBrowser.click()

        # Set the memo labels on this and next (exposure) steps
        (_,
         exposure,
         _,
         exposure_constraints) = self.selected_impact_function_constraints()

        layer_geometry = exposure_constraints['name']

        text = (select_exposure_origin_question % (
            layer_geometry,
            exposure['name'],
            self.selected_function()['name']))
        self.lblSelectExpLayerOriginType.setText(text)

        text = (select_explayer_from_canvas_question % (
            layer_geometry,
            exposure['name'],
            self.selected_function()['name']))
        self.lblSelectExposureLayer.setText(text)

        text = (select_explayer_from_browser_question % (
            layer_geometry,
            exposure['name'],
            self.selected_function()['name']))
        self.lblSelectBrowserExpLayer.setText(text)

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
        lblText = self.get_layer_description_from_canvas(self.exposure_layer,
                                                         'exposure')
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
        if layer_a.crs() != layer_b.crs():
            coord_transform = QgsCoordinateTransform(
                layer_a.crs(), layer_b.crs())
            extent_b = (coord_transform.transform(
                extent_b, QgsCoordinateTransform.ReverseTransform))
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
            'aggregation', self.lstCanvasAggLayers)
        if self.lstCanvasAggLayers.count():
            self.rbAggLayerFromCanvas.setText(tr(
                'I would like to use an aggregation layer already loaded in '
                'QGIS\n'
                '(launches the %s for aggregation if needed)'
            ) % self.keyword_creation_wizard_name)
            self.rbAggLayerFromCanvas.setEnabled(True)
            self.rbAggLayerFromCanvas.click()
        else:
            self.rbAggLayerFromCanvas.setText(tr(
                'I would like to use an aggregation layer already loaded in '
                'QGIS\n'
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
            self.aggregation_layer, 'aggregation')
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
            'aggregation', self.lstCanvasAggLayers)
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
            'aggregation')
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

    def start_capture_coordinates(self):
        """Enter the coordinate capture mode"""
        self.hide()

    def stop_capture_coordinates(self):
        """Exit the coordinate capture mode"""
        self.extent_dialog._populate_coordinates()
        self.extent_dialog.canvas.setMapTool(
            self.extent_dialog.previous_map_tool)
        self.show()

    def set_widgets_step_fc_extent(self):
        """Set widgets on the Extent tab"""
        # import here only so that it is AFTER i18n set up
        from safe.gui.tools.extent_selector_dialog import ExtentSelectorDialog
        self.extent_dialog = ExtentSelectorDialog(
            self.iface,
            self.iface.mainWindow(),
            extent=self.dock.extent.user_extent,
            crs=self.dock.extent.user_extent_crs)
        self.extent_dialog.tool.rectangle_created.disconnect(
            self.extent_dialog.stop_capture)
        self.extent_dialog.clear_extent.connect(
            self.dock.extent.clear_user_analysis_extent)
        self.extent_dialog.extent_defined.connect(
            self.dock.define_user_analysis_extent)
        self.extent_dialog.capture_button.clicked.connect(
            self.start_capture_coordinates)
        self.extent_dialog.tool.rectangle_created.connect(
            self.stop_capture_coordinates)

        self.extent_dialog.label.setText(self.tr(
            'Please specify extent of your analysis:'))

        if self.swExtent:
            self.swExtent.hide()

        self.swExtent = self.extent_dialog.main_stacked_widget
        self.layoutAnalysisExtent.addWidget(self.swExtent)

    def write_extent(self):
        """ After the extent selection,
            save the extent and disconnect signals
        """
        self.extent_dialog.accept()
        self.extent_dialog.clear_extent.disconnect(
            self.dock.extent.clear_user_analysis_extent)
        self.extent_dialog.extent_defined.disconnect(
            self.dock.define_user_analysis_extent)
        self.extent_dialog.capture_button.clicked.disconnect(
            self.start_capture_coordinates)
        self.extent_dialog.tool.rectangle_created.disconnect(
            self.stop_capture_coordinates)

    # ===========================
    # STEP_FC_EXTENT_DISJOINT
    # ===========================

    def validate_extent(self):
        """Check if the selected extent intersects source data.

        :returns: true if extent intersects both layers, false if is disjoint
        :rtype: boolean
        """
        self.analysis_handler = AnalysisHandler(self)
        self.analysis_handler.init_analysis()
        try:
            self.analysis_handler.analysis.setup_analysis()
        except InsufficientOverlapError:
            self.analysis_handler = None
            return False

        self.analysis_handler = None
        return True

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
        impact_function_id = self.selected_function()['id']
        impact_function = self.impact_function_manager.get(
            impact_function_id)
        if not impact_function:
            return
        self.if_params = None
        if hasattr(impact_function, 'parameters'):
            self.if_params = impact_function.parameters

        text = self.tr(
            'Please set impact functions parameters.<br/>Parameters for '
            'impact function "%s" that can be modified are:' %
            impact_function_id)
        self.lblSelectIFParameters.setText(text)

        self.parameter_dialog = FunctionOptionsDialog(self)
        self.parameter_dialog.set_dialog_info(impact_function_id)
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
        def format_postprocessor(pp):
            """ make nested OrderedDicts more flat"""
            if isinstance(pp, OrderedDict):
                result = []
                for v in pp:
                    if isinstance(pp[v], OrderedDict):
                        # omit the v key and unpack the dict directly
                        result += [u'%s: %s' % (unicode(k), unicode(pp[v][k]))
                                   for k in pp[v]]
                    else:
                        result += [u'%s: %s' % (unicode(v), unicode(pp[v]))]
                return u', '.join(result)
            elif isinstance(pp, list):
                result = []
                for i in pp:
                    name = i.serialize()['name']
                    val = i.serialize()['value']
                    if isinstance(val, bool):
                        val = val and self.tr('Enabled') or self.tr('Disabled')
                    if isinstance(i, GroupParameter):
                        # val is a list od *Parameter instances
                        jresult = []
                        for j in val:
                            jname = j.serialize()['name']
                            jval = j.serialize()['value']
                            if isinstance(jval, bool):
                                jval = (jval and self.tr('Enabled') or
                                        self.tr('Disabled'))
                            else:
                                jval = unicode(jval)
                            jresult += [u'%s: %s' % (jname, jval)]
                        val = u', '.join(jresult)
                    else:
                        val = unicode(val)
                    if pp.index(i) == 0:
                        result += [val]
                    else:
                        result += [u'%s: %s' % (name, val)]
                return u', '.join(result)
            else:
                return unicode(pp)

        self.if_params = self.parameter_dialog.parse_input(
            self.parameter_dialog.values)

        # (IS) Set the current impact function to use parameter from user.
        # We should do it prettier (put it on analysis or impact calculator
        impact_function_id = self.selected_function()['id']
        impact_function = self.impact_function_manager.get(
            impact_function_id)
        if not impact_function:
            return
        impact_function.parameters = self.if_params

        params = []
        for p in self.if_params:
            if isinstance(self.if_params[p], OrderedDict):
                subparams = [
                    u'<tr><td>%s &nbsp;</td><td>%s</td></tr>' % (
                        unicode(pp),
                        format_postprocessor(self.if_params[p][pp]))
                    for pp in self.if_params[p]
                ]
                if subparams:
                    subparams = ''.join(subparams)
                    subparams = '<table border="0">%s</table>' % subparams
            elif isinstance(self.if_params[p], list) and p == 'minimum needs':
                subparams = ''
                for need in self.if_params[p]:
                    # concatenate all ResourceParameter
                    name = unicode(need.serialize()['name'])
                    val = unicode(need.serialize()['value'])
                    if isinstance(need, ResourceParameter):
                        if need.unit and need.unit.abbreviation:
                            val += need.unit.abbreviation
                    subparams += u'<tr><td>%s &nbsp;</td><td>%s</td></tr>' % (
                        name, val)
                if subparams:
                    subparams = '<table border="0">%s</table>' % subparams
                else:
                    subparams = 'Not applicable'
            elif isinstance(self.if_params[p], list):
                subparams = ', '.join([unicode(i) for i in self.if_params[p]])
            else:
                subparams = unicode(self.if_params[p].serialize()['value'])

            params += [(p, subparams)]

        if self.aggregation_layer:
            aggr = self.aggregation_layer.name()
        else:
            aggr = self.tr('no aggregation')

        html = self.tr('Please ensure the following information '
                       'is correct and press Run.')

        # TODO: update this to use InaSAFE message API rather...
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
            html += (
                '<tr>'
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
        self.lblAnalysisStatus.setText(self.tr('Running analysis...'))

    # ===========================
    # STEPS NAVIGATION
    # ===========================

    def go_to_step(self, step):
        """Set the stacked widget to the given step, set up the buttons,
           and run all operations that should start immediately after
           entering the new step.

        :param step: The step number to be moved to.
        :type step: int
        """
        self.stackedWidget.setCurrentIndex(step - 1)
        self.lblStep.clear()

        # Disable the Next button unless new data already entered
        self.pbnNext.setEnabled(self.is_ready_to_next_step(step))

        # Enable the Back button unless it's not the first step
        self.pbnBack.setEnabled(
            step not in [step_kw_category, step_fc_function_1] or
            self.parent_step is not None)

        # Set Next button label
        if (step in [step_kw_summary, step_fc_analysis] and
                self.parent_step is None):
            self.pbnNext.setText(self.tr('Finish'))
        elif step == step_fc_summary:
            self.pbnNext.setText(self.tr('Run'))
        else:
            self.pbnNext.setText(self.tr('Next'))

        # Run analysis after switching to the new step
        if step == step_fc_analysis:
            # self.update_MessageViewer_size()
            self.setup_and_run_analysis()

        # Set lblSelectCategory label if entering the kw mode
        # from the ifcw mode
        if step == step_kw_category and self.parent_step:
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
    def on_pbnNext_released(self):
        """Handle the Next button release.

        .. note:: This is an automatic Qt slot
           executed when the Next button is released.
        """
        current_step = self.get_current_step()

        # Save keywords if it's the end of the keyword creation mode
        if current_step == step_kw_summary:
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

        # After any step involving Browser, add selected layer to map canvas
        if current_step in [step_fc_hazlayer_from_browser,
                            step_fc_explayer_from_browser,
                            step_fc_agglayer_from_browser]:
            if not QgsMapLayerRegistry.instance().mapLayersByName(
                    self.layer.name()):
                QgsMapLayerRegistry.instance().addMapLayers([self.layer])

        # After the extent selection, save the extent and disconnect signals
        if current_step == step_fc_extent:
            self.write_extent()

        # Determine the new step to be switched
        new_step = self.compute_next_step(current_step)

        # Prepare the next tab
        if new_step == step_kw_category:
            self.set_widgets_step_kw_category()
        if new_step == step_kw_subcategory:
            self.set_widgets_step_kw_subcategory()
        if new_step == step_kw_hazard_category:
            self.set_widgets_step_kw_hazard_category()
        elif new_step == step_kw_layermode:
            self.set_widgets_step_kw_layermode()
        elif new_step == step_kw_unit:
            self.set_widgets_step_kw_unit()
        elif new_step == step_kw_classification:
            self.set_widgets_step_kw_classification()
        elif new_step == step_kw_field:
            self.set_widgets_step_kw_field()
        elif new_step == step_kw_resample:
            self.set_widgets_step_kw_resample()
        elif new_step == step_kw_classify:
            self.set_widgets_step_kw_classify()
        elif new_step == step_kw_extrakeywords:
            self.set_widgets_step_kw_extrakeywords()
        elif new_step == step_kw_aggregation:
            self.set_widgets_step_kw_aggregation()
        elif new_step == step_kw_source:
            self.set_widgets_step_kw_source()
        elif new_step == step_kw_title:
            self.set_widgets_step_kw_title()
        elif new_step == step_kw_summary:
            self.set_widgets_step_kw_summary()
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

        self.go_to_step(new_step)

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
        # Re-connect disconnected signals when coming back to the Extent step
        if new_step == step_fc_extent:
            self.set_widgets_step_fc_extent()
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
        if step == step_kw_hazard_category:
            return bool(self.selected_hazard_category())
        if step == step_kw_layermode:
            return bool(self.selected_layermode())
        if step == step_kw_unit:
            return bool(self.selected_unit())
        if step == step_kw_classification:
            return bool(self.selected_classification())
        if step == step_kw_field:
            return bool(self.selected_field() or not self.lstFields.count())
        if step == step_kw_resample:
            return True
        if step == step_kw_classify:
            # Allow to not classify any values
            return True
        if step == step_kw_extrakeywords:
            return self.are_all_extra_keywords_selected()
        if step == step_kw_aggregation:
            # Not required
            return True
        if step == step_kw_source:
            # The source_* keywords are not required
            return True
        if step == step_kw_title:
            return bool(self.leTitle.text())
        if step == step_kw_summary:
            return True
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
            return self.get_layer_description_from_browser('hazard')[0]
        if step == step_fc_explayer_origin:
            return (bool(self.rbExpLayerFromCanvas.isChecked() or
                         self.rbExpLayerFromBrowser.isChecked()))
        if step == step_fc_explayer_from_canvas:
            return bool(self.selected_canvas_explayer())
        if step == step_fc_explayer_from_browser:
            return self.get_layer_description_from_browser('exposure')[0]
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
            return self.get_layer_description_from_browser('aggregation')[0]
        if step == step_fc_agglayer_disjoint:
            # Never go further if layers disjoint
            return False
        if step == step_fc_extent:
            return True
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
            if self.selected_category() == layer_purpose_aggregation:
                new_step = step_kw_field
            else:
                new_step = step_kw_subcategory
        elif current_step == step_kw_subcategory:
            if self.selected_category() == layer_purpose_hazard:
                new_step = step_kw_hazard_category
            else:
                new_step = step_kw_layermode
        elif current_step == step_kw_hazard_category:
            new_step = step_kw_layermode
        elif current_step == step_kw_layermode:
            if self.selected_layermode() == layer_mode_classified:
                if is_point_layer(self.layer) \
                        and self.selected_category() == layer_purpose_hazard:
                    # Skip FIELD and CLASSIFICATION for point volcanos
                    new_step = step_kw_extrakeywords
                elif self.classifications_for_layer():
                    new_step = step_kw_classification
                elif is_raster_layer(self.layer):
                    new_step = step_kw_extrakeywords
                else:
                    new_step = step_kw_field
            else:
                # CONTINUOUS DATA, ALL GEOMETRIES
                new_step = step_kw_unit
        elif current_step == step_kw_unit:
            if is_raster_layer(self.layer):
                if self.selected_category() == layer_purpose_exposure:
                    # Only go to resample for continuous raster exposures
                    new_step = step_kw_resample
                else:
                    new_step = step_kw_extrakeywords
            else:
                # Currently not used, as we don't have continuous vectors
                new_step = step_kw_field
        elif current_step == step_kw_classification:
            if is_raster_layer(self.layer):
                new_step = step_kw_classify
            else:
                new_step = step_kw_field
        elif current_step == step_kw_field:
            if self.selected_category() == layer_purpose_aggregation:
                new_step = step_kw_aggregation
            elif self.selected_layermode() == layer_mode_classified and \
                    self.classifications_for_layer():
                new_step = step_kw_classify
            else:
                new_step = step_kw_extrakeywords
        elif current_step == step_kw_resample:
            new_step = step_kw_extrakeywords
        elif current_step == step_kw_classify:
            new_step = step_kw_extrakeywords
        elif current_step == step_kw_extrakeywords:
            new_step = step_kw_source
        elif current_step == step_kw_aggregation:
            new_step = step_kw_source
        elif current_step == step_kw_source:
            new_step = step_kw_title
        elif current_step == step_kw_title:
            new_step = step_kw_summary
        elif current_step == step_kw_summary:
            if self.parent_step:
                # Come back from KW to the parent IFCW thread.
                new_step = self.parent_step
                if self.is_layer_compatible(self.layer):
                    # If the layer is compatible,
                    # go to the next step (issue #2347)
                    if new_step in [step_fc_hazlayer_from_canvas,
                                    step_fc_explayer_from_canvas,
                                    step_fc_agglayer_from_canvas]:
                        new_step += 2
                    else:
                        new_step += 1
                else:
                    # If the layer is incompatible, stay on the parent step.
                    # However, if the step is xxxLayerFromCanvas and there are
                    # no compatible layers, the list will be empty,
                    # so go one step back.
                    haz = layer_purpose_hazard['key']
                    exp = layer_purpose_exposure['key']
                    agg = layer_purpose_aggregation['key']
                    if (new_step == step_fc_hazlayer_from_canvas and not
                            self.get_compatible_layers_from_canvas(haz)):
                        new_step -= 1
                    elif (new_step == step_fc_explayer_from_canvas and not
                          self.get_compatible_layers_from_canvas(exp)):
                        new_step -= 1
                    elif (new_step == step_fc_agglayer_from_canvas and not
                          self.get_compatible_layers_from_canvas(agg)):
                        new_step -= 1

                self.parent_step = None
                self.is_selected_layer_keywordless = False
                self.set_mode_label_to_ifcw()
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
                self.existing_keywords = None
                self.set_mode_label_to_keywords_creation()
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
                self.set_mode_label_to_keywords_creation()
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
                self.set_mode_label_to_keywords_creation()
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

        # Skip the extra_keywords tab if no extra keywords available:
        if (new_step == step_kw_extrakeywords and not
                self.additional_keywords_for_the_layer()):
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
                self.set_mode_label_to_ifcw()
                new_step = self.parent_step
                self.parent_step = None
            else:
                new_step = step_kw_category
        elif current_step == step_kw_subcategory:
            new_step = step_kw_category
        elif current_step == step_kw_hazard_category:
            new_step = step_kw_subcategory
        elif current_step == step_kw_layermode:
            if self.selected_category() == layer_purpose_hazard:
                new_step = step_kw_hazard_category
            else:
                new_step = step_kw_subcategory
        elif current_step == step_kw_unit:
            new_step = step_kw_layermode
        elif current_step == step_kw_classification:
            new_step = step_kw_layermode
        elif current_step == step_kw_field:
            if self.selected_category() == layer_purpose_aggregation:
                new_step = step_kw_category
            elif self.selected_layermode() == layer_mode_continuous:
                new_step = step_kw_unit
            elif self.classifications_for_layer():
                new_step = step_kw_classification
            else:
                new_step = step_kw_layermode
        elif current_step == step_kw_resample:
            new_step = step_kw_unit
        elif current_step == step_kw_classify:
            if is_raster_layer(self.layer):
                new_step = step_kw_classification
            else:
                new_step = step_kw_field
        elif current_step == step_kw_aggregation:
            new_step = step_kw_field
        elif current_step == step_kw_extrakeywords:
            if self.selected_layermode() == layer_mode_classified:
                if self.selected_classification():
                    new_step = step_kw_classify
                elif self.selected_field():
                    new_step = step_kw_field
                else:
                    new_step = step_kw_layermode
            else:
                if self.selected_allowresampling() is not None:
                    new_step = step_kw_resample
                else:
                    new_step = step_kw_unit
        elif current_step == step_kw_source:
            if self.selected_category() == layer_purpose_aggregation:
                new_step = step_kw_aggregation
            elif self.selected_extra_keywords():
                new_step = step_kw_extrakeywords
            # otherwise behave like it was step_kw_extrakeywords
            elif self.selected_layermode() == layer_mode_classified:
                if self.selected_classification():
                    new_step = step_kw_classify
                elif self.selected_field():
                    new_step = step_kw_field
                else:
                    new_step = step_kw_layermode
            else:
                if self.selected_allowresampling() is not None:
                    new_step = step_kw_resample
                else:
                    new_step = step_kw_unit
        elif current_step == step_kw_title:
            new_step = step_kw_source
        elif current_step == step_kw_summary:
            new_step = step_kw_title
        elif current_step == step_fc_function_1:
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

    def get_layer_geometry_id(self, layer=None):
        """Obtain layer mode of a given layer.

        If no layer specified, the current layer is used

        :param layer : layer to examine
        :type layer: QgsMapLayer or None

        :returns: The layer mode.
        :rtype: str
        """
        if not layer:
            layer = self.layer
        if is_raster_layer(layer):
            return 'raster'
        elif is_point_layer(layer):
            return 'point'
        elif is_polygon_layer(layer):
            return 'polygon'
        else:
            return 'line'

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
        keywords['layer_geometry'] = self.get_layer_geometry_id()
        if self.selected_category():
            keywords['layer_purpose'] = self.selected_category()['key']
            if keywords['layer_purpose'] == 'aggregation':
                keywords.update(self.get_aggregation_attributes())
        if self.selected_subcategory():
            key = self.selected_category()['key']
            keywords[key] = self.selected_subcategory()['key']
        if self.selected_hazard_category():
            keywords['hazard_category'] \
                = self.selected_hazard_category()['key']
        if self.selected_layermode():
            keywords['layer_mode'] = self.selected_layermode()['key']
        if self.selected_unit():
            if self.selected_category() == layer_purpose_hazard:
                key = continuous_hazard_unit['key']
            else:
                key = exposure_unit['key']
            keywords[key] = self.selected_unit()['key']
        if self.selected_allowresampling() is not None:
            keywords['allow_resampling'] = (
                self.selected_allowresampling() and 'true' or 'false')
        if self.lstFields.currentItem():
            field_keyword = self.field_keyword_for_the_layer()
            keywords[field_keyword] = self.lstFields.currentItem().text()
        if self.selected_classification():
            geom = 'raster' if is_raster_layer(self.layer) else 'vector'
            key = '%s_%s_classification' % (geom,
                                            self.selected_category()['key'])
            keywords[key] = self.selected_classification()['key']
        value_map = self.selected_mapping()
        if value_map:
            keywords['value_map'] = json.dumps(value_map)
        extra_keywords = self.selected_extra_keywords()
        for key in extra_keywords:
            keywords[key] = extra_keywords[key]
        if self.leSource.text():
            keywords['source'] = get_unicode(self.leSource.text())
        if self.leSource_url.text():
            keywords['url'] = get_unicode(self.leSource_url.text())
        if self.leSource_scale.text():
            keywords['scale'] = get_unicode(self.leSource_scale.text())
        if self.ckbSource_date.isChecked():
            keywords['date'] = get_unicode(
                self.dtSource_date.dateTime().toString('dd-MM-yyyy HH:mm'))
        if self.leSource_license.text():
            keywords['license'] = get_unicode(self.leSource_license.text())
        if self.leTitle.text():
            keywords['title'] = get_unicode(self.leTitle.text())

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
                    'An error was encountered when saving the following '
                    'keywords:\n %s') % error_message.to_html())))
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
        self.dtSource_date.setToolTip(date_tooltip)
        self.leSource_scale.setToolTip(scale_tooltip)
        self.leSource_url.setToolTip(url_tooltip)
