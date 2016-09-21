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

import json
import logging
from sqlite3 import OperationalError

from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import (
    QDialog,
    QPixmap)
from qgis.core import QgsMapLayerRegistry

from definitionsv4.definitions_v3 import (
    continuous_hazard_unit,
    exposure_unit,
    layer_purpose_hazard,
    layer_purpose_exposure,
    layer_purpose_aggregation,
    layer_mode_continuous,
    layer_mode_classified)
from safe.common.exceptions import (
    HashNotFoundError,
    NoKeywordsFoundError,
    KeywordNotFoundError,
    InvalidParameterError,
    UnsupportedProviderError,
    InaSAFEError,
    MetadataReadError)
from safe.gui.tools.wizard.wizard_strings import (
    category_question_hazard,
    category_question_exposure,
    category_question_aggregation)
from safe.gui.tools.wizard.wizard_utils import (
    layer_description_html,
    RoleHazard,
    RoleExposure,
    RoleHazardConstraint,
    RoleExposureConstraint)
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.utilities.gis import (
    is_raster_layer,
    is_point_layer,
    is_polygon_layer)
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.resources import get_ui_class, resources_path
from safe.utilities.unicode import get_unicode
from safe.utilities.utilities import (
    get_error_message,
    is_keyword_version_supported)
from step_fc00_functions1 import StepFcFunctions1
from step_fc05_functions2 import StepFcFunctions2
from step_fc10_function import StepFcFunction
from step_fc15_hazlayer_origin import StepFcHazLayerOrigin
from step_fc20_hazlayer_from_canvas import StepFcHazLayerFromCanvas
from step_fc25_hazlayer_from_browser import StepFcHazLayerFromBrowser
from step_fc30_explayer_origin import StepFcExpLayerOrigin
from step_fc35_explayer_from_canvas import StepFcExpLayerFromCanvas
from step_fc40_explayer_from_browser import StepFcExpLayerFromBrowser
from step_fc45_disjoint_layers import StepFcDisjointLayers
from step_fc50_agglayer_origin import StepFcAggLayerOrigin
from step_fc55_agglayer_from_canvas import StepFcAggLayerFromCanvas
from step_fc60_agglayer_from_browser import StepFcAggLayerFromBrowser
from step_fc65_agglayer_disjoint import StepFcAggLayerDisjoint
from step_fc70_extent import StepFcExtent
from step_fc75_extent_disjoint import StepFcExtentDisjoint
from step_fc80_params import StepFcParams
from step_fc85_summary import StepFcSummary
from step_kw00_purpose import StepKwPurpose
from step_kw05_subcategory import StepKwSubcategory
from step_kw10_hazard_category import StepKwHazardCategory
from step_kw15_layermode import StepKwLayerMode
from step_kw20_unit import StepKwUnit
from step_kw25_classification import StepKwClassification
from step_kw30_field import StepKwField
from step_kw35_resample import StepKwResample
from step_kw40_classify import StepKwClassify
from step_kw42_name_field import StepKwNameField
from step_kw43_population_field import StepKwPopulationField
from step_kw45_extrakeywords import StepKwExtraKeywords
from step_kw50_aggregation import StepKwAggregation
from step_kw55_source import StepKwSource
from step_kw60_title import StepKwTitle
from step_kw65_summary import StepKwSummary
from.step_fc90_analysis import StepFcAnalysis

__author__ = 'qgis@borysjurgiel.pl'
__revision__ = '$Format:%H$'
__date__ = '21/02/2011'
__copyright__ = (
    'Copyright 2012, Australia Indonesia Facility for Disaster Reduction')

LOGGER = logging.getLogger('InaSAFE')

FORM_CLASS = get_ui_class('wizard/wizard_dialog_base.ui')


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
        self.lblStep.clear()
        # Set icons
        self.lblMainIcon.setPixmap(
            QPixmap(resources_path('img', 'icons', 'icon-white.svg')))

        self.keyword_io = KeywordIO()
        self.impact_function_manager = ImpactFunctionManager()

        self.is_selected_layer_keywordless = False
        self.parent_step = None

        self.pbnBack.setEnabled(False)
        self.pbnNext.setEnabled(False)
        self.pbnCancel.released.connect(self.reject)

        # Initialize attributes
        self.existing_keywords = None
        self.layer = None
        self.hazard_layer = None
        self.exposure_layer = None
        self.aggregation_layer = None
        self.analysis_handler = None

        self.step_kw_purpose = StepKwPurpose(self)
        self.step_kw_subcategory = StepKwSubcategory(self)
        self.step_kw_hazard_category = StepKwHazardCategory(self)
        self.step_kw_layermode = StepKwLayerMode(self)
        self.step_kw_unit = StepKwUnit(self)
        self.step_kw_classification = StepKwClassification(self)
        self.step_kw_field = StepKwField(self)
        self.step_kw_resample = StepKwResample(self)
        self.step_kw_classify = StepKwClassify(self)
        self.step_kw_name_field = StepKwNameField(self)
        self.step_kw_population_field = StepKwPopulationField(self)
        self.step_kw_extrakeywords = StepKwExtraKeywords(self)
        self.step_kw_aggregation = StepKwAggregation(self)
        self.step_kw_source = StepKwSource(self)
        self.step_kw_title = StepKwTitle(self)
        self.step_kw_summary = StepKwSummary(self)
        self.step_fc_functions1 = StepFcFunctions1(self)
        self.step_fc_functions2 = StepFcFunctions2(self)
        self.step_fc_function = StepFcFunction(self)
        self.step_fc_hazlayer_origin = StepFcHazLayerOrigin(self)
        self.step_fc_hazlayer_from_canvas = StepFcHazLayerFromCanvas(self)
        self.step_fc_hazlayer_from_browser = StepFcHazLayerFromBrowser(self)
        self.step_fc_explayer_origin = StepFcExpLayerOrigin(self)
        self.step_fc_explayer_from_canvas = StepFcExpLayerFromCanvas(self)
        self.step_fc_explayer_from_browser = StepFcExpLayerFromBrowser(self)
        self.step_fc_disjoint_layers = StepFcDisjointLayers(self)
        self.step_fc_agglayer_origin = StepFcAggLayerOrigin(self)
        self.step_fc_agglayer_from_canvas = StepFcAggLayerFromCanvas(self)
        self.step_fc_agglayer_from_browser = StepFcAggLayerFromBrowser(self)
        self.step_fc_agglayer_disjoint = StepFcAggLayerDisjoint(self)
        self.step_fc_extent = StepFcExtent(self)
        self.step_fc_extent_disjoint = StepFcExtentDisjoint(self)
        self.step_fc_params = StepFcParams(self)
        self.step_fc_summary = StepFcSummary(self)
        self.step_fc_analysis = StepFcAnalysis(self)
        self.stackedWidget.addWidget(self.step_kw_purpose)
        self.stackedWidget.addWidget(self.step_kw_subcategory)
        self.stackedWidget.addWidget(self.step_kw_hazard_category)
        self.stackedWidget.addWidget(self.step_kw_layermode)
        self.stackedWidget.addWidget(self.step_kw_unit)
        self.stackedWidget.addWidget(self.step_kw_classification)
        self.stackedWidget.addWidget(self.step_kw_field)
        self.stackedWidget.addWidget(self.step_kw_resample)
        self.stackedWidget.addWidget(self.step_kw_classify)
        self.stackedWidget.addWidget(self.step_kw_name_field)
        self.stackedWidget.addWidget(self.step_kw_population_field)
        self.stackedWidget.addWidget(self.step_kw_extrakeywords)
        self.stackedWidget.addWidget(self.step_kw_aggregation)
        self.stackedWidget.addWidget(self.step_kw_source)
        self.stackedWidget.addWidget(self.step_kw_title)
        self.stackedWidget.addWidget(self.step_kw_summary)
        self.stackedWidget.addWidget(self.step_fc_functions1)
        self.stackedWidget.addWidget(self.step_fc_functions2)
        self.stackedWidget.addWidget(self.step_fc_function)
        self.stackedWidget.addWidget(self.step_fc_hazlayer_origin)
        self.stackedWidget.addWidget(self.step_fc_hazlayer_from_canvas)
        self.stackedWidget.addWidget(self.step_fc_hazlayer_from_browser)
        self.stackedWidget.addWidget(self.step_fc_explayer_origin)
        self.stackedWidget.addWidget(self.step_fc_explayer_from_canvas)
        self.stackedWidget.addWidget(self.step_fc_explayer_from_browser)
        self.stackedWidget.addWidget(self.step_fc_disjoint_layers)
        self.stackedWidget.addWidget(self.step_fc_agglayer_origin)
        self.stackedWidget.addWidget(self.step_fc_agglayer_from_canvas)
        self.stackedWidget.addWidget(self.step_fc_agglayer_from_browser)
        self.stackedWidget.addWidget(self.step_fc_agglayer_disjoint)
        self.stackedWidget.addWidget(self.step_fc_extent)
        self.stackedWidget.addWidget(self.step_fc_extent_disjoint)
        self.stackedWidget.addWidget(self.step_fc_params)
        self.stackedWidget.addWidget(self.step_fc_summary)
        self.stackedWidget.addWidget(self.step_fc_analysis)

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
                UnsupportedProviderError,
                MetadataReadError):
            self.existing_keywords = None
        self.set_mode_label_to_keywords_creation()

        step = self.step_kw_purpose
        step.set_widgets()
        self.go_to_step(step)

    def set_function_centric_mode(self):
        """Set the Wizard to the Function Centric mode"""
        self.set_mode_label_to_ifcw()

        step = self.step_fc_functions1
        step.set_widgets()
        self.go_to_step(step)

    def field_keyword_for_the_layer(self):
        """Return the proper keyword for field for the current layer.
        Expected values are: 'field', 'structure_class_field', road_class_field

        :returns: the field keyword
        :rtype: string
        """

        if self.step_kw_purpose.selected_purpose() == \
                layer_purpose_aggregation:
            # purpose: aggregation
            return 'aggregation attribute'
        elif self.step_kw_purpose.selected_purpose() == layer_purpose_hazard:
            # purpose: hazard
            if (self.step_kw_layermode.selected_layermode() ==
                    layer_mode_classified and
                    is_point_layer(self.layer)):
                # No field for classified point hazards
                return ''
        else:
            # purpose: exposure
            layer_mode_key = self.step_kw_layermode.selected_layermode()['key']
            layer_geometry_key = self.get_layer_geometry_id()
            exposure_key = self.step_kw_subcategory.\
                selected_subcategory()['key']
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
        if self.parent_step in [self.step_fc_hazlayer_from_canvas,
                                self.step_fc_hazlayer_from_browser]:
            category = layer_purpose_hazard
            subcategory = h
        elif self.parent_step in [self.step_fc_explayer_from_canvas,
                                  self.step_fc_explayer_from_browser]:
            category = layer_purpose_exposure
            subcategory = e
        elif self.parent_step:
            category = layer_purpose_aggregation
            subcategory = None
        else:
            category = None
            subcategory = None
        return category, subcategory

    def selected_impact_function_constraints(self):
        """Obtain impact function constraints selected by user.

        :returns: Tuple of metadata of hazard, exposure,
            hazard layer constraints and exposure layer constraints
        :rtype: tuple
        """
        selection = self.step_fc_functions1.tblFunctions1.selectedItems()
        if len(selection) != 1:
            return None, None, None, None

        h = selection[0].data(RoleHazard)
        e = selection[0].data(RoleExposure)

        selection = self.step_fc_functions2.tblFunctions2.selectedItems()
        if len(selection) != 1:
            return h, e, None, None

        hc = selection[0].data(RoleHazardConstraint)
        ec = selection[0].data(RoleExposureConstraint)
        return h, e, hc, ec

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
        if not is_keyword_version_supported(keyword_version):
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

        imfunc = self.step_fc_function.selected_function()
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

    def get_compatible_canvas_layers(self, category):
        """Collect layers from map canvas, compatible for the given category
           and selected impact function

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
        :rtype: str, QUrl
        """
        if self.existing_keywords is None:
            return None
        if keyword is not None:
            return self.existing_keywords.get(keyword, None)
        else:
            return None

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
            self.is_selected_layer_keywordless = (
                not is_keyword_version_supported(kw_ver))
        else:
            self.is_selected_layer_keywordless = True

        desc = layer_description_html(layer, keywords)
        return desc

    # ===========================
    # NAVIGATION
    # ===========================

    def go_to_step(self, step):
        """Set the stacked widget to the given step, set up the buttons,
           and run all operations that should start immediately after
           entering the new step.

        :param step: The step widget to be moved to.
        :type step: QWidget
        """
        self.stackedWidget.setCurrentWidget(step)

        # Disable the Next button unless new data already entered
        self.pbnNext.setEnabled(step.is_ready_to_next_step())

        # Enable the Back button unless it's not the first step
        self.pbnBack.setEnabled(
            step not in [self.step_kw_purpose, self.step_fc_functions1] or
            self.parent_step is not None)

        # Set Next button label
        if (step in [self.step_kw_summary, self.step_fc_analysis] and
                self.parent_step is None):
            self.pbnNext.setText(self.tr('Finish'))
        elif step == self.step_fc_summary:
            self.pbnNext.setText(self.tr('Run'))
        else:
            self.pbnNext.setText(self.tr('Next'))

        # Run analysis after switching to the new step
        if step == self.step_fc_analysis:
            self.step_fc_analysis.setup_and_run_analysis()

        # Set lblSelectCategory label if entering the kw mode
        # from the ifcw mode
        if step == self.step_kw_purpose and self.parent_step:
            if self.parent_step in [self.step_fc_hazlayer_from_canvas,
                                    self.step_fc_hazlayer_from_browser]:
                text_label = category_question_hazard
            elif self.parent_step in [self.step_fc_explayer_from_canvas,
                                      self.step_fc_explayer_from_browser]:
                text_label = category_question_exposure
            else:
                text_label = category_question_aggregation
            self.step_kw_purpose.lblSelectCategory.setText(text_label)

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
        if current_step == self.step_kw_summary:
            self.save_current_keywords()

        if current_step == self.step_kw_aggregation:
            good_age_ratio, sum_age_ratios = self.step_kw_aggregation.\
                age_ratios_are_valid()
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
        if current_step in [self.step_fc_hazlayer_from_browser,
                            self.step_fc_explayer_from_browser,
                            self.step_fc_agglayer_from_browser]:
            if not QgsMapLayerRegistry.instance().mapLayersByName(
                    self.layer.name()):
                QgsMapLayerRegistry.instance().addMapLayers([self.layer])

                # Make the layer visible. Might be hidden by default. See #2925
                legend = self.iface.legendInterface()
                legend.setLayerVisible(self.layer, True)

        # After the extent selection, save the extent and disconnect signals
        if current_step == self.step_fc_extent:
            self.step_fc_extent.write_extent()

        # Determine the new step to be switched
        new_step = current_step.get_next_step()
        if (new_step == self.step_kw_extrakeywords and not
                self.step_kw_extrakeywords.
                additional_keywords_for_the_layer()):
            # Skip the extra_keywords tab if no extra keywords available:
            new_step = self.step_kw_source

        if new_step is not None:
            # Prepare the next tab
            new_step.set_widgets()
        else:
            # Wizard complete
            self.accept()
            return

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
        new_step = current_step.get_previous_step()
        # set focus to table widgets, as the inactive selection style is gray
        if new_step == self.step_fc_functions1:
            self.step_fc_functions1.tblFunctions1.setFocus()
        if new_step == self.step_fc_functions2:
            self.step_fc_functions2.tblFunctions2.setFocus()
        # Re-connect disconnected signals when coming back to the Extent step
        if new_step == self.step_fc_extent:
            self.step_fc_extent.set_widgets()
        # Set Next button label
        self.pbnNext.setText(self.tr('Next'))
        self.pbnNext.setEnabled(True)
        self.go_to_step(new_step)

    def get_current_step(self):
        """Return current step of the wizard.

        :returns: Current step of the wizard.
        :rtype: WizardStep instance
        """
        return self.stackedWidget.currentWidget()

    def get_keywords(self):
        """Obtain the state of the dialog as a keywords dict.

        :returns: Keywords reflecting the state of the dialog.
        :rtype: dict
        """
        keywords = {}
        keywords['layer_geometry'] = self.get_layer_geometry_id()
        if self.step_kw_purpose.selected_purpose():
            keywords['layer_purpose'] = self.step_kw_purpose.\
                selected_purpose()['key']
            if keywords['layer_purpose'] == 'aggregation':
                keywords.update(
                    self.step_kw_aggregation.get_aggregation_attributes())
        if self.step_kw_subcategory.selected_subcategory():
            key = self.step_kw_purpose.selected_purpose()['key']
            keywords[key] = self.step_kw_subcategory.\
                selected_subcategory()['key']
        if self.step_kw_hazard_category.selected_hazard_category():
            keywords['hazard_category'] \
                = self.step_kw_hazard_category.\
                selected_hazard_category()['key']
        if self.step_kw_layermode.selected_layermode():
            keywords['layer_mode'] = self.step_kw_layermode.\
                selected_layermode()['key']
        if self.step_kw_unit.selected_unit():
            if self.step_kw_purpose.selected_purpose() == layer_purpose_hazard:
                key = continuous_hazard_unit['key']
            else:
                key = exposure_unit['key']
            keywords[key] = self.step_kw_unit.selected_unit()['key']
        if self.step_kw_resample.selected_allowresampling() is not None:
            keywords['allow_resampling'] = (
                self.step_kw_resample.selected_allowresampling() and
                'true' or 'false')
        if self.step_kw_field.lstFields.currentItem():
            field_keyword = self.field_keyword_for_the_layer()
            keywords[field_keyword] = self.step_kw_field.\
                lstFields.currentItem().text()
        if self.step_kw_classification.selected_classification():
            geom = 'raster' if is_raster_layer(self.layer) else 'vector'
            key = '%s_%s_classification' % (
                geom, self.step_kw_purpose.selected_purpose()['key'])
            keywords[key] = self.step_kw_classification.\
                selected_classification()['key']
        value_map = self.step_kw_classify.selected_mapping()
        if value_map:
            if self.step_kw_classification.selected_classification():
                # hazard mapping
                keyword = 'value_map'
            else:
                # exposure mapping
                keyword = 'value_mapping'
            keywords[keyword] = json.dumps(value_map)

        name_field = self.step_kw_name_field.selected_field()
        if name_field:
            keywords['name_field'] = name_field

        population_field = self.step_kw_population_field.selected_field()
        if population_field:
            keywords['population_field'] = population_field

        extra_keywords = self.step_kw_extrakeywords.selected_extra_keywords()
        for key in extra_keywords:
            keywords[key] = extra_keywords[key]
        if self.step_kw_source.leSource.text():
            keywords['source'] = get_unicode(
                self.step_kw_source.leSource.text())
        if self.step_kw_source.leSource_url.text():
            keywords['url'] = get_unicode(
                self.step_kw_source.leSource_url.text())
        if self.step_kw_source.leSource_scale.text():
            keywords['scale'] = get_unicode(
                self.step_kw_source.leSource_scale.text())
        if self.step_kw_source.ckbSource_date.isChecked():
            keywords['date'] = self.step_kw_source.dtSource_date.dateTime()
        if self.step_kw_source.leSource_license.text():
            keywords['license'] = get_unicode(
                self.step_kw_source.leSource_license.text())
        if self.step_kw_title.leTitle.text():
            keywords['title'] = get_unicode(self.step_kw_title.leTitle.text())

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
