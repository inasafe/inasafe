# coding=utf-8
"""Wizard Step Browser."""


import os
from sqlite3 import OperationalError

from qgis.PyQt.QtCore import QSettings
from db_manager.db_plugins.postgis.connector import PostGisDBConnector
from qgis.core import (
    QgsDataItem,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsDataSourceURI,
    QgsBrowserModel)

import safe.definitions.layer_geometry
import safe.definitions.layer_modes
import safe.definitions.layer_purposes
from safe.common.exceptions import (
    HashNotFoundError,
    InaSAFEError,
    InvalidParameterError,
    KeywordNotFoundError,
    MissingMetadata,
    NoKeywordsFoundError,
    UnsupportedProviderError)
from safe.definitions.hazard import continuous_hazard_unit
from safe.definitions.hazard_classifications import hazard_classification
from safe.definitions.layer_geometry import layer_geometry_polygon
from safe.definitions.layer_modes import (
    layer_mode_continuous, layer_mode_classified)
from safe.definitions.layer_purposes import (
    layer_purpose_exposure, layer_purpose_aggregation, layer_purpose_hazard)
from safe.definitions.units import exposure_unit
from safe.gui.tools.wizard.layer_browser_proxy_model import (
    LayerBrowserProxyModel)
from safe.gui.tools.wizard.utilities import layer_description_html
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_strings import (
    create_postGIS_connection_first)
from safe.utilities.gis import qgis_version
from safe.utilities.utilities import is_keyword_version_supported

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class WizardStepBrowser(WizardStep):

    """A base class for steps containing a QGIS Browser."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget
        """
        WizardStep.__init__(self, parent)
        # Set model for browser
        browser_model = QgsBrowserModel()
        self.proxy_model = LayerBrowserProxyModel(self)
        self.proxy_model.setSourceModel(browser_model)

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        This method must be implemented in derived classes.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        raise NotImplementedError("The current step class doesn't implement \
            the get_next_step method")

    def set_widgets(self):
        """Set all widgets on the tab.

        This method must be implemented in derived classes.
        """
        raise NotImplementedError("The current step class doesn't implement \
            the set_widgets method")

    @staticmethod
    def postgis_path_to_uri(path):
        """Convert layer path from QgsBrowserModel to full QgsDataSourceURI.

        :param path: The layer path from QgsBrowserModel
        :type path: string

        :returns: layer uri.
        :rtype: QgsDataSourceURI
        """

        connection_name = path.split('/')[1]
        schema = path.split('/')[2]
        table_name = path.split('/')[3]

        settings = QSettings()
        key = "/PostgreSQL/connections/" + connection_name
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
        tables = connector.getVectorTables(schema)
        tables = [table for table in tables if table[1] == table_name]
        if not tables:
            return None
        table = tables[0]
        geom_col = table[8]

        uri.setDataSource(schema, table_name, geom_col)
        return uri

    def unsuitable_layer_description_html(
            self, layer, layer_purpose, keywords=None):
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
            """Compare two strings and emphasize both if differ.

            :param str1: First string.
            :type str1: str

            :param str2: Second string.
            :type str2: str

            :returns: Return emphasized string if differ.
            :rtype: tuple
            """
            if str1 != str2:
                str1 = '<i>%s</i>' % str1
                str2 = '<i>%s</i>' % str2
            return str1, str2

        # Get allowed subcategory and layer_geometry from IF constraints
        h, e, hc, ec = self.parent.selected_impact_function_constraints()
        imfunc = self.parent.step_fc_function.selected_function()
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

        layer_geometry_key = self.parent.get_layer_geometry_key(layer)
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

        layer_geometry_key, req_geometry = emphasize(
            layer_geometry_key, req_geometry)
        lay_purpose, layer_purpose = emphasize(lay_purpose, layer_purpose)
        lay_subcategory, req_subcategory = emphasize(
            lay_subcategory, req_subcategory)
        lay_layer_mode, req_layer_mode = emphasize(
            lay_layer_mode, req_layer_mode)

        # Classification
        classification_row = ''
        if (lay_req['layer_mode'] == layer_mode_classified and
                layer_purpose == layer_purpose_hazard['key']):
            # Determine the keyword key for the classification
            classification_obj = hazard_classification
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
                    # We already know we want to emphasize them and the test
                    # inside the function will always pass.
                    lay_classification, req_classifications = emphasize(
                        lay_classification, req_classifications)
                classification_row = (
                    (
                        '<tr><td><b>%s</b></td>' +
                        '<td>%s</td><td>%s</td></tr>')
                    % (
                        classification_key_name,
                        lay_classification,
                        req_classifications))

        # Unit
        units_row = ''
        if lay_req['layer_mode'] == layer_mode_continuous:
            # Determine the keyword key for the unit
            unit_obj = (
                continuous_hazard_unit
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
                    # We already know we want to emphasize them and the test
                    # inside the function will always pass.
                    lay_unit, req_units = emphasize(lay_unit, req_units)
                units_row = (
                    (
                        '<tr><td><b>%s</b></td>' +
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
               safe.definitions.layer_geometry.layer_geometry['name'],
               layer_geometry_key, req_geometry,
               safe.definitions.layer_purposes.layer_purpose['name'],
               lay_purpose, layer_purpose,
               layer_purpose_key_name, lay_subcategory, req_subcategory,
               safe.definitions.layer_modes.layer_mode['name'],
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
                'QgsOgrLayerItem', 'QgsGdalLayerItem', 'QgsPGLayerItem',
                'QgsLayerItem', ]:
            return False, ''

        path = item.path()

        if item_class_name in ['QgsOgrLayerItem', 'QgsGdalLayerItem',
                               'QgsLayerItem'] and not os.path.exists(path):
            return False, ''

        # try to create the layer
        if item_class_name == 'QgsOgrLayerItem':
            layer = QgsVectorLayer(path, '', 'ogr')
        elif item_class_name == 'QgsPGLayerItem':
            uri = self.postgis_path_to_uri(path)
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
            if 'layer_purpose' not in keywords:
                keywords = None
        except (HashNotFoundError,
                OperationalError,
                NoKeywordsFoundError,
                KeywordNotFoundError,
                InvalidParameterError,
                UnsupportedProviderError,
                MissingMetadata):
            keywords = None

        # set the layer name for further use in the step_fc_summary
        if keywords:
            if qgis_version() >= 21800:
                layer.setName(keywords.get('title'))
            else:
                layer.setLayerName(keywords.get('title'))

        if not self.parent.is_layer_compatible(layer, category, keywords):
            label_text = '%s<br/>%s' % (
                self.tr(
                    'This layer\'s keywords or type are not suitable:'),
                self.unsuitable_layer_description_html(
                    layer, category, keywords))
            return False, label_text

        # set the current layer (e.g. for the keyword creation sub-thread
        #                          or for adding the layer to mapCanvas)
        self.parent.layer = layer
        if category == 'hazard':
            self.parent.hazard_layer = layer
        elif category == 'exposure':
            self.parent.exposure_layer = layer
        else:
            self.parent.aggregation_layer = layer

        # Check if the layer is keywordless
        if keywords and 'keyword_version' in keywords:
            kw_ver = str(keywords['keyword_version'])
            self.parent.is_selected_layer_keywordless = (
                not is_keyword_version_supported(kw_ver))
        else:
            self.parent.is_selected_layer_keywordless = True

        desc = layer_description_html(layer, keywords)
        return True, desc
