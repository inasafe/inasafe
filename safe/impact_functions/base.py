# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Function Base Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '15/03/15'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import numpy

from socket import gethostname
import getpass
import platform
from datetime import datetime
from qgis.utils import QGis
from qgis.core import QgsMapLayer, QgsCoordinateReferenceSystem
from osgeo import gdal
from PyQt4.QtCore import QT_VERSION_STR, QSettings
from PyQt4.Qt import PYQT_VERSION_STR

from safe.impact_statistics.aggregator import Aggregator
from safe.impact_statistics.postprocessor_manager import (
    PostprocessorManager)
from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.common.exceptions import (
    InvalidExtentError,
    CallGDALError,
    FunctionParametersError,
    NoValidLayerError,
    InsufficientOverlapError)
from safe import messaging as m
from safe.messaging import styles
from safe.messaging.utilities import generate_insufficient_overlap_message
from safe.postprocessors.postprocessor_factory import (
    get_postprocessors,
    get_postprocessor_human_name)
from safe.common.utilities import get_non_conflicting_attribute_name
from safe.utilities.i18n import tr
from safe.utilities.clipper import clip_layer
from safe.utilities.gis import (
    convert_to_safe_layer,
    get_wgs84_resolution,
    array_to_geo_array,
    extent_to_array,
    get_optimal_extent)
from safe.utilities.clipper import adjust_clip_extent
from safe.storage.safe_layer import SafeLayer
from safe.storage.utilities import (
    buffered_bounding_box as get_buffered_extent,
    bbox_intersection)
from safe.definitions import inasafe_keyword_version
from safe.metadata.provenance import Provenance
from safe.common.version import get_version
from safe.common.signals import (
    send_static_message,
    send_dynamic_message,
    send_not_busy_signal,
    send_analysis_done_signal
)

PROGRESS_UPDATE_STYLE = styles.PROGRESS_UPDATE_STYLE
WARNING_STYLE = styles.WARNING_STYLE
LOGO_ELEMENT = m.Brand()


class ImpactFunction(object):
    """Abstract base class for all impact functions."""

    # Class properties
    _metadata = ImpactFunctionMetadata

    def __init__(self):
        """Base class constructor.

        All derived classes should normally call this constructor e.g.::

            def __init__(self):
                super(FloodImpactFunction, self).__init__()

        """
        # User who runs this
        self._user = getpass.getuser().replace(' ', '_')
        # The host that runs this
        self._host_name = gethostname()

        # Requested extent to use
        self._requested_extent = None
        # Requested extent's CRS
        self._requested_extent_crs = QgsCoordinateReferenceSystem('EPSG:4326')
        # The current viewport extent of the map canvas
        self._viewport_extent = None
        # Actual extent to use - Read Only
        # For 'old-style' IF we do some manipulation to the requested extent
        self._actual_extent = None
        # Actual extent's CRS - Read Only
        self._actual_extent_crs = QgsCoordinateReferenceSystem('EPSG:4326')
        # set this to a gui call back / web callback etc as needed.
        self._callback = self.console_progress_callback
        # Set the default parameters
        self._parameters = self._metadata.parameters()
        # Layer representing hazard e.g. flood
        self._hazard = None
        # Layer representing people / infrastructure that are exposed
        self._exposure = None
        # Layer used for aggregating results by area / district
        self._aggregation = None
        # Aggregator
        self._aggregator = None
        # Postprocessor manager
        self._postprocessor_manager = None
        # The best extents to use for the assessment
        self._clip_parameters = None
        # Clip features that extend beyond the extents.
        self._clip_hard = False
        # Show intermediate layers.
        self._show_intermediate_layers = False
        # Force memory.
        self._force_memory = False
        # Layer produced by the impact function
        self._impact = None
        # The question of the impact function
        self._question = None
        # Post analysis Result dictionary (suitable to conversion to json etc.)
        self._tabulated_impact = None
        # Style information for the impact layer - at some point we should
        # formalise this into a more natural model
        # ABC's will normally set this property.
        self._impact_style = None
        # The target field for vector impact layer
        self._target_field = 'safe_ag'
        # The string to mark not affected value in the vector impact layer
        self._not_affected_value = 'Not Affected'
        # Store provenances
        self._provenances = Provenance()
        # Start time
        self._start_time = None

        self.provenance.append_step(
            'Initialize Impact Function',
            'Impact function is being initialized')

    @classmethod
    def metadata(cls):
        """Get the metadata class of this impact function."""
        return cls._metadata

    @classmethod
    def function_type(cls):
        """Property for the type of impact function ('old-style' or 'qgis2.0').

        QGIS2 impact functions are using the QGIS api and have more
        dependencies. Legacy IF's use only numpy, gdal etc. and can be
        used in contexts where no QGIS is present.
        """
        return cls.metadata().as_dict().get('function_type', None)

    @property
    def user(self):
        """Property for the user who runs this.

        :returns: User who runs this
        :rtype: basestring
        """
        return self._user

    @property
    def host_name(self):
        """Property for the host name that runs this.

        :returns: The host name.
        :rtype: basestring
        """
        return self._host_name

    @property
    def requested_extent(self):
        """Property for the extent of impact function analysis.

        :returns: A list in the form [xmin, ymin, xmax, ymax].
        :rtype: list
        """
        return self._requested_extent

    @requested_extent.setter
    def requested_extent(self, extent):
        """Setter for extent property.

        :param extent: Analysis boundaries expressed as
            [xmin, ymin, xmax, ymax]. The extent CRS should match the
            extent_crs property of this IF instance.
        :type extent: list
        """
        # add more robust checks here
        if len(extent) != 4:
            raise InvalidExtentError('%s is not a valid extent.' % extent)
        self._requested_extent = extent

    @property
    def requested_extent_crs(self):
        """Property for the extent CRS of impact function analysis.

        :return crs: The coordinate reference system for the analysis boundary.
        :rtype: QgsCoordinateReferenceSystem
        """
        return self._requested_extent_crs

    @requested_extent_crs.setter
    def requested_extent_crs(self, crs):
        """Setter for extent_crs property.

        .. note:: We break our rule here on not allowing acronyms for
            parameter names.

        :param crs: The coordinate reference system for the analysis boundary.
        :type crs: QgsCoordinateReferenceSystem
        """
        self._requested_extent_crs = crs

    @property
    def actual_extent(self):
        """Property for the actual extent for analysis.

        :returns: A list in the form [xmin, ymin, xmax, ymax].
        :rtype: list
        """
        return self._actual_extent

    @property
    def actual_extent_crs(self):
        """Property for the actual extent crs for analysis.

        :returns: The CRS for the actual extent.
        :rtype: QgsCoordinateReferenceSystem
        """
        return self._actual_extent_crs

    @property
    def viewport_extent(self):
        """Property for the viewport extent of the map canvas.

        :returns: Viewport extent in the form [xmin, ymin, xmax, ymax] where
            all coordinates provided are in Geographic / EPSG:4326.
        :rtype: list
        """
        return self._viewport_extent

    @viewport_extent.setter
    def viewport_extent(self, viewport_extent):
        """Setter for the viewport extent of the map canvas.

        :param viewport_extent: Viewport extent in the form
            [xmin, ymin, xmax, ymax] in EPSG:4326.
        :type viewport_extent: list

        """
        self._viewport_extent = viewport_extent

    @property
    def callback(self):
        """Property for the callback used to relay processing progress.

        :returns: A callback function. The callback function will have the
            following parameter requirements.

            progress_callback(current, maximum, message=None)

        :rtype: function

        .. seealso:: console_progress_callback
        """
        return self._callback

    @callback.setter
    def callback(self, callback):
        """Setter for callback property.

        :param callback: A callback function reference that provides the
            following signature:

            progress_callback(current, maximum, message=None)

        :type callback: function
        """
        self._callback = callback

    @classmethod
    def instance(cls):
        """Make an instance of the impact function."""
        return cls()

    @property
    def hazard(self):
        """Property for the hazard layer to be used for the analysis.

        :returns: A map layer.
        :rtype: SafeLayer
        """
        return self._hazard

    @hazard.setter
    def hazard(self, layer):
        """Setter for hazard layer property.

        :param layer: Hazard layer to be used for the analysis.
        :type layer: SafeLayer, Layer, QgsMapLayer
        """
        if isinstance(layer, SafeLayer):
            self._hazard = layer
        else:
            if self.function_type() == 'old-style':
                self._hazard = SafeLayer(convert_to_safe_layer(layer))
            elif self.function_type() == 'qgis2.0':
                # convert for new style impact function
                self._hazard = SafeLayer(layer)
            else:
                message = tr('Error: Impact Function has unknown style.')
                raise Exception(message)

        # Update the target field to a non-conflicting one
        if self._hazard.is_qgsvectorlayer():
            self._target_field = get_non_conflicting_attribute_name(
                self.target_field,
                self._hazard.layer.dataProvider().fieldNameMap().keys()
            )

    @property
    def exposure(self):
        """Property for the exposure layer to be used for the analysis.

        :returns: A map layer.
        :rtype: SafeLayer
        """
        return self._exposure

    @exposure.setter
    def exposure(self, layer):
        """Setter for exposure layer property.

        :param layer: exposure layer to be used for the analysis.
        :type layer: SafeLayer
        """
        if isinstance(layer, SafeLayer):
            self._exposure = layer
        else:
            if self.function_type() == 'old-style':
                self._exposure = SafeLayer(convert_to_safe_layer(layer))
            elif self.function_type() == 'qgis2.0':
                # convert for new style impact function
                self._exposure = SafeLayer(layer)
            else:
                message = tr('Error: Impact Function has unknown style.')
                raise Exception(message)

        # Update the target field to a non-conflicting one
        if self.exposure.is_qgsvectorlayer():
            self._target_field = get_non_conflicting_attribute_name(
                self.target_field,
                self.exposure.layer.dataProvider().fieldNameMap().keys()
            )

    @property
    def aggregation(self):
        """Property for the aggregation layer to be used for the analysis.

        :returns: A map layer.
        :rtype: SafeLayer
        """
        return self._aggregation

    @aggregation.setter
    def aggregation(self, layer):
        """Setter for aggregation layer property.

        :param layer: Aggregation layer to be used for the analysis.
        :type layer: SafeLayer
        """
        if isinstance(layer, SafeLayer):
            self._aggregation = layer
        elif isinstance(layer, QgsMapLayer):
            self._aggregation = SafeLayer(layer)
        else:
            self._aggregation = None

    @property
    def aggregator(self):
        """Get the aggregator.

        :return: The aggregator.
        :rtype: Aggregator
        """
        return self._aggregator

    @property
    def postprocessor_manager(self):
        """Get the postprocessor manager.

        :return: The postprocessor manager.
        :rtype: PostprocessorManager
        """
        return self._postprocessor_manager

    @property
    def parameters(self):
        """Get the parameter."""
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """Set the parameter.

        :param parameters: IF parameters.
        :type parameters: dict
        """
        self._parameters = parameters

    @property
    def clip_hard(self):
        """Property if we need to clip features which are beyond the extents.

        :return: The value.
        :rtype: bool
        """
        return self._clip_hard

    @clip_hard.setter
    def clip_hard(self, clip_hard):
        """Setter if we need to clip features which are beyond the extents.

        :param clip_hard: The value.
        :type clip_hard: bool
        """
        if isinstance(clip_hard, bool):
            self._clip_hard = clip_hard
        else:
            raise Exception('clip_hard is not a boolean.')

    @property
    def show_intermediate_layers(self):
        """Property if we show intermediate layers.

        :return: The value.
        :rtype: bool
        """
        return self._show_intermediate_layers

    @show_intermediate_layers.setter
    def show_intermediate_layers(self, show_intermediate_layers):
        """Setter if we show intermediate layers.

        :param show_intermediate_layers: The value.
        :type show_intermediate_layers: bool
        """
        if isinstance(show_intermediate_layers, bool):
            self._show_intermediate_layers = show_intermediate_layers
        else:
            raise Exception('show_intermediate_layers is not a boolean.')

    @property
    def force_memory(self):
        """Property if we force memory.

        :return: The value.
        :rtype: bool
        """
        return self._force_memory

    @force_memory.setter
    def force_memory(self, flag):
        """Setter if we force memory.

        :param flag: The value.
        :type flag: bool
        """
        if isinstance(flag, bool):
            self._force_memory = flag
        else:
            raise Exception('force_memory is not a boolean.')

    @property
    def impact(self):
        """Property for the impact layer generated by the analysis.

        .. note:: It is not guaranteed that all impact functions produce a
            spatial layer.

        :returns: A map layer.
        :rtype: QgsMapLayer, QgsVectorLayer, QgsRasterLayer
        """
        return self._impact

    @property
    def requires_clipping(self):
        """Check to clip or not to clip layers.

        If function type is a 'qgis2.0' impact function, then
        return False -- clipping is unnecessary, else return True.

        :returns: To clip or not to clip.
        :rtype: bool
        """
        if self.function_type() == 'old-style':
            return True
        elif self.function_type() == 'qgis2.0':
            return False
        else:
            message = tr('Error: Impact Function has unknown style.')
            raise Exception(message)

    @property
    def target_field(self):
        """Property for the target_field of the impact layer.

        :returns: The target field in the impact layer in case it's a vector.
        :rtype: basestring
        """
        return self._target_field

    @property
    def tabulated_impact(self):
        """Property for the result (excluding GIS layer) of the analysis.

        This property is read only.

        :returns: A dictionary containing the analysis results. The format of
            the dictionary may vary between impact function but the following
            sections are expected:

            * title: A brief title for the results
            * headings: column headings for the results
            * totals: totals for all rows in the tabulation area
            * tabulation: detailed line items for the tabulation

            The returned dictionary is probably best described with a simple
            example::

                Example to follow here....

        :rtype: dict
        """
        return self._tabulated_impact

    @property
    def style(self):
        """Property for the style for the impact layer.

        This property is read only.

        :returns: A dictionary containing the analysis style. Generally this
            should be an adjunct to the qml style applied to the impact layer
            so that other types of style (e.g. SLD) can be generated for the
            impact layer.

        :rtype: dict
        """
        return self._impact_style

    @property
    def question(self):
        """Formulate the question for this impact function.

        This method produces a natural language question for this impact
        function derived from the following three inputs:

            * descriptive name of the hazard layer e.g. 'a flood like in
                January 2004'
            * descriptive name of the exposure layer e.g. 'people'
            * question statement in the impact function metadata e.g.
                'will be affected'.

        These inputs will be concatenated into a string e.g.:

            "In the event of a flood like in January 2004, how many people
            will be affected."
        """
        if self._question is None:
            function_title = self.metadata().as_dict()['title']
            return (tr('In the event of %(hazard)s how many '
                       '%(exposure)s might %(impact)s')
                    % {'hazard': self.hazard.name.lower(),
                       'exposure': self.exposure.name.lower(),
                       'impact': function_title.lower()})
        else:
            return self._question

    @question.setter
    def question(self, question):
        """Setter of the question.

        :param question: The question for the impact function.
        :type question: basestring
        """
        if isinstance(question, basestring):
            self._question = question
        else:
            raise Exception('The question should be a basestring instance.')

    @staticmethod
    def console_progress_callback(current, maximum, message=None):
        """Simple console based callback implementation for tests.

        :param current: Current progress.
        :type current: int

        :param maximum: Maximum range (point at which task is complete.
        :type maximum: int

        :param message: Optional message to display in the progress bar
        :type message: str, QString
        """
        # noinspection PyChainedComparisons
        if maximum > 1000 and current % 1000 != 0 and current != maximum:
            return
        if message is not None:
            print message
        print 'Task progress: %i of %i' % (current, maximum)

    def validate(self):
        """Validate things needed before running the analysis."""
        # Set start time.
        self._start_time = datetime.now()
        # Validate that input layers are valid
        self.provenance.append_step(
            'Validating Step',
            'Impact function is validating the inputs.')
        if (self.hazard is None) or (self.exposure is None):
            message = tr(
                'Ensure that hazard and exposure layers are all set before '
                'trying to run the impact function.')
            raise FunctionParametersError(message)

        # Validate extent, with the QGIS IF, we need requested_extent set
        if self.function_type() == 'qgis2.0' and self.requested_extent is None:
            message = tr(
                'Impact Function with QGIS function type is used, but no '
                'extent is provided.')
            raise InvalidExtentError(message)

    def prepare(self):
        """Prepare this impact function for running the analysis.

        This method should normally be called in your concrete class's
        run method before it attempts to do any real processing. This
        method will do any needed house keeping such as:

            * checking that the exposure and hazard layers sufficiently
            overlap (post 3.1)
            * clipping or subselecting features from both layers such that
              only features / coverage within the actual analysis extent
              will be analysed (post 3.1)
            * raising errors if any untenable condition exists e.g. extent has
              no valid CRS. (post 3.1)

        We suggest to overload this method in your concrete class
        implementation so that it includes any impact function specific checks
        too.

        ..note: For 3.1, we will still do those preprocessing in analysis
            class. We will just need to check if the function_type is
            'qgis2.0', it needs to have the extent set.
        # """

        # Fixme : When Analysis.py will not exist anymore, we will uncomment.
        # self.emit_pre_run_message()
        # self.setup_aggregator()

        self.provenance.append_step(
            'Preparation Step',
            'Impact function is being prepared to run the analysis.')

    def generate_impact_keywords(self, extra_keywords=None):
        """Obtain keywords for the impact layer.

        :param extra_keywords: Additional keywords from the analysis.
        :type extra_keywords: dict

        :returns: Impact layer's keywords.
        :rtype: dict
        """
        keywords = {
            'layer_purpose': 'impact',
            'keyword_version': inasafe_keyword_version,
            'if_provenance': self.provenance
        }
        if extra_keywords:
            keywords.update(extra_keywords)

        return keywords

    @property
    def provenance(self):
        """Get the provenances"""
        return self._provenances

    def set_if_provenance(self):
        """Set IF provenance step for the IF."""
        data = {
            'start_time': self._start_time ,
            'finish_time': datetime.now(),
            'hazard_layer': self.hazard.keywords['title'],
            'exposure_layer': self.exposure.keywords['title'],
            'impact_function_id': self.metadata().as_dict()['id'],
            'impact_function_version': '1.0',  # TODO: Add IF version.
            'host_name': self.host_name,
            'user': self.user,
            'qgis_version': QGis.QGIS_VERSION,
            'gdal_version': gdal.__version__,
            'qt_version': QT_VERSION_STR,
            'pyqt_version': PYQT_VERSION_STR,
            'os': platform.version(),
            'inasafe_version': get_version(),
            # Temporary.
            # TODO: Update it later.
            'exposure_pixel_size': '',
            'hazard_pixel_size': '',
            'impact_pixel_size': '',
            'analysis_extent': '',
            'parameter': ''
        }

        self.provenance.append_if_provenance_step(
            'IF Provenance',
            'Impact function\'s provenance.',
            timestamp=None,
            data=data
        )

    def emit_pre_run_message(self):
        """Inform the user about parameters before starting the processing."""
        title = tr('Processing started')
        details = tr(
            'Please wait - processing may take a while depending on your '
            'hardware configuration and the analysis extents and data.')
        # trap for issue 706
        try:
            exposure_name = self.exposure.name
            hazard_name = self.hazard.name
            # aggregation layer could be set to AOI so no check for that
        except AttributeError:
            title = tr('No valid layers')
            details = tr(
                'Please ensure your hazard and exposure layers are set '
                'in the question area and then press run again.')
            message = m.Message(
                LOGO_ELEMENT,
                m.Heading(title, **WARNING_STYLE),
                m.Paragraph(details))
            raise NoValidLayerError(message)
        text = m.Text(
            tr('This analysis will calculate the impact of'),
            m.EmphasizedText(hazard_name),
            tr('on'),
            m.EmphasizedText(exposure_name),
        )
        if self.aggregation is not None:
            try:
                aggregation_name = self.aggregation.name
                # noinspection PyTypeChecker
                text.add(m.Text(
                    tr('and bullet list the results'),
                    m.ImportantText(tr('aggregated by')),
                    m.EmphasizedText(aggregation_name)))
            except AttributeError:
                pass
        text.add('.')
        message = m.Message(
            LOGO_ELEMENT,
            m.Heading(title, **PROGRESS_UPDATE_STYLE),
            m.Paragraph(details),
            m.Paragraph(text))
        try:
            # add which postprocessors will run when appropriated
            # noinspection PyTypeChecker
            post_processors_names = self.parameters['postprocessors']
            post_processors = get_postprocessors(post_processors_names)
            message.add(m.Paragraph(tr(
                'The following postprocessors will be used:')))

            bullet_list = m.BulletedList()

            for name, post_processor in post_processors.iteritems():
                bullet_list.add('%s: %s' % (
                    get_postprocessor_human_name(name),
                    post_processor.description()))
            message.add(bullet_list)

        except (TypeError, KeyError):
            # TypeError is for when function_parameters is none
            # KeyError is for when ['postprocessors'] is unavailable
            pass
        send_static_message(self, message)

    @property
    def clip_parameters(self):
        """Calculate the best extents to use for the assessment.

        :returns: A dictionary consisting of:

            * extra_exposure_keywords: dict - any additional keywords that
                should be written to the exposure layer. For example if
                rescaling is required for a raster, the original resolution
                can be added to the keywords file.
            * adjusted_geo_extent: list - [xmin, ymin, xmax, ymax] - the best
                extent that can be used given the input datasets and the
                current viewport extents.
            * cell_size: float - the cell size that is the best of the
                hazard and exposure rasters.
        :rtype: dict, QgsRectangle, float, QgsMapLayer, QgsRectangle,
            QgsMapLayer
        :raises: InsufficientOverlapError
        """

        if self._clip_parameters is None:

            # Get the Hazard extents as an array in EPSG:4326
            # noinspection PyTypeChecker
            hazard_geoextent = extent_to_array(
                self.hazard.extent(),
                self.hazard.crs())
            # Get the Exposure extents as an array in EPSG:4326
            # noinspection PyTypeChecker
            exposure_geoextent = extent_to_array(
                self.exposure.extent(),
                self.exposure.crs())

            # Set the analysis extents based on user's desired behaviour
            settings = QSettings()
            mode_name = settings.value(
                'inasafe/analysis_extents_mode',
                'HazardExposureView')
            # Default to using canvas extents if no case below matches
            analysis_geoextent = self.viewport_extent
            if mode_name == 'HazardExposureView':
                analysis_geoextent = self.viewport_extent

            elif mode_name == 'HazardExposure':
                analysis_geoextent = None

            elif mode_name == 'HazardExposureBookmark' or \
                    mode_name == 'HazardExposureBoundingBox':
                if self.requested_extent is not None \
                        and self.requested_extent_crs is not None:
                    # User has defined preferred extent, so use that
                    analysis_geoextent = array_to_geo_array(
                        self.requested_extent,
                        self.requested_extent_crs)

            # Now work out the optimal extent between the two layers and
            # the current view extent. The optimal extent is the intersection
            # between the two layers and the viewport.
            try:
                # Extent is returned as an array [xmin,ymin,xmax,ymax]
                # We will convert it to a QgsRectangle afterwards.
                # If the user has defined a preferred analysis extent it will
                # always be used, otherwise the data will be clipped to
                # the viewport unless the user has deselected clip to viewport
                #  in options.
                geo_extent = get_optimal_extent(
                    hazard_geoextent,
                    exposure_geoextent,
                    analysis_geoextent)

            except InsufficientOverlapError, e:
                # noinspection PyTypeChecker
                message = generate_insufficient_overlap_message(
                    e,
                    exposure_geoextent,
                    self.exposure.qgis_layer(),
                    hazard_geoextent,
                    self.hazard.qgis_layer(),
                    analysis_geoextent)
                raise InsufficientOverlapError(message)

            # TODO: move this to its own function
            # Next work out the ideal spatial resolution for rasters
            # in the analysis. If layers are not native WGS84, we estimate
            # this based on the geographic extents
            # rather than the layers native extents so that we can pass
            # the ideal WGS84 cell size and extents to the layer prep routines
            # and do all preprocessing in a single operation.
            # All this is done in the function getWGS84resolution
            adjusted_geo_extent = geo_extent
            cell_size = None
            extra_exposure_keywords = {}
            if self.hazard.layer_type() == QgsMapLayer.RasterLayer:
                # Hazard layer is raster
                hazard_geo_cell_size, _ = get_wgs84_resolution(
                    self.hazard.qgis_layer())

                if self.exposure.layer_type() == QgsMapLayer.RasterLayer:
                    # In case of two raster layers establish common resolution
                    exposure_geo_cell_size, _ = get_wgs84_resolution(
                        self.exposure.qgis_layer())

                    # See issue #1008 - the flag below is used to indicate
                    # if the user wishes to prevent resampling of exposure data
                    keywords = self.exposure.keywords
                    allow_resampling_flag = True
                    if 'allow_resampling' in keywords:
                        resampling_lower = keywords['allow_resampling'].lower()
                        allow_resampling_flag = resampling_lower == 'true'

                    if hazard_geo_cell_size < exposure_geo_cell_size and \
                            allow_resampling_flag:
                        cell_size = hazard_geo_cell_size

                        # Adjust the geo extent to coincide with hazard grids
                        # so gdalwarp can do clipping properly
                        adjusted_geo_extent = adjust_clip_extent(
                            geo_extent,
                            get_wgs84_resolution(self.hazard.qgis_layer()),
                            hazard_geoextent)
                    else:
                        cell_size = exposure_geo_cell_size

                        # Adjust extent to coincide with exposure grids
                        # so gdalwarp can do clipping properly
                        adjusted_geo_extent = adjust_clip_extent(
                            geo_extent,
                            get_wgs84_resolution(self.exposure.qgis_layer()),
                            exposure_geoextent)

                    # Record native resolution to allow rescaling of exposure
                    if not numpy.allclose(cell_size, exposure_geo_cell_size):
                        extra_exposure_keywords['resolution'] = \
                            exposure_geo_cell_size
                else:
                    if self.exposure.layer_type() != QgsMapLayer.VectorLayer:
                        raise RuntimeError

                    # In here we do not set cell_size so that in
                    # _clip_raster_layer we can perform gdalwarp without
                    # specifying cell size as we still want to have the
                    # original pixel size.

                    # Adjust the geo extent to be at the edge of the pixel in
                    # so gdalwarp can do clipping properly
                    adjusted_geo_extent = adjust_clip_extent(
                        geo_extent,
                        get_wgs84_resolution(self.hazard.qgis_layer()),
                        hazard_geoextent)

                    # If exposure is vector data grow hazard raster layer to
                    # ensure there are enough pixels for points at the edge of
                    # the view port to be interpolated correctly. This requires
                    # resolution to be available
                    adjusted_geo_extent = get_buffered_extent(
                        adjusted_geo_extent,
                        get_wgs84_resolution(self.hazard.qgis_layer()))
            else:
                # Hazard layer is vector
                # In case hazard data is a point data set, we will need to set
                # the geo_extent to the extent of exposure and the analysis
                # extent. We check the extent first if the point extent
                # intersects with geo_extent.
                if self.hazard.geometry_type() == QGis.Point:
                    user_extent_enabled = (
                        self.requested_extent is not None and
                        self.requested_extent_crs is not None)
                    if user_extent_enabled:
                        # Get intersection between exposure and analysis extent
                        geo_extent = bbox_intersection(
                            exposure_geoextent, analysis_geoextent)
                        # Check if the point is within geo_extent
                        if bbox_intersection(
                                geo_extent, exposure_geoextent) is None:
                            raise InsufficientOverlapError

                    else:
                        geo_extent = exposure_geoextent
                    adjusted_geo_extent = geo_extent

                if self.exposure.layer_type() == QgsMapLayer.RasterLayer:
                    # Adjust the geo extent to be at the edge of the pixel in
                    # so gdalwarp can do clipping properly
                    adjusted_geo_extent = adjust_clip_extent(
                        geo_extent,
                        get_wgs84_resolution(self.exposure.qgis_layer()),
                        exposure_geoextent)

            self._clip_parameters = {
                'extra_exposure_keywords': extra_exposure_keywords,
                'adjusted_geo_extent': adjusted_geo_extent,
                'cell_size': cell_size
            }

        return self._clip_parameters

    def optimal_clip(self):
        """ A helper function to perform an optimal clip of the input data.
        Optimal extent should be considered as the intersection between
        the three inputs. The InaSAFE library will perform various checks
        to ensure that the extent is tenable, includes data from both
        etc.

        The result of this function will be two layers which are
        clipped and re-sampled if needed, and in the EPSG:4326 geographic
        coordinate reference system.

        :returns: The clipped hazard and exposure layers.
        :rtype: (QgsMapLayer, QgsMapLayer)
        """

        # Get the hazard and exposure layers selected in the combos
        # and other related parameters needed for clipping.
        try:
            clip_parameters = self.clip_parameters
            extra_exposure_keywords = clip_parameters[
                'extra_exposure_keywords']
            adjusted_geo_extent = clip_parameters['adjusted_geo_extent']
            cell_size = clip_parameters['cell_size']
        except:
            raise
        # Find out what clipping behaviour we have - see #2210
        settings = QSettings()
        mode = settings.value(
            'inasafe/analysis_extents_mode',
            'HazardExposureView')
        detail = None
        if mode == 'HazardExposureView':
            detail = tr(
                'Resampling and clipping the hazard layer to match the '
                'intersection of the exposure layer and the current view '
                'extents.')
        elif mode == 'HazardExposure':
            detail = tr(
                'Resampling and clipping the hazard layer to match the '
                'intersection of the exposure layer extents.')
        elif mode == 'HazardExposureBookmark':
            detail = tr(
                'Resampling and clipping the hazard layer to match the '
                'bookmarked extents.')
        elif mode == 'HazardExposureBoundingBox':
            detail = tr(
                'Resampling and clipping the hazard layer to match the '
                'intersection of your preferred analysis area.')
        # Make sure that we have EPSG:4326 versions of the input layers
        # that are clipped and (in the case of two raster inputs) resampled to
        # the best resolution.
        title = tr('Preparing hazard data')

        message = m.Message(
            m.Heading(title, **PROGRESS_UPDATE_STYLE),
            m.Paragraph(detail))
        send_dynamic_message(self, message)
        try:
            clipped_hazard = clip_layer(
                layer=self.hazard.qgis_layer(),
                extent=adjusted_geo_extent,
                cell_size=cell_size,
                hard_clip_flag=self.clip_hard)
        except CallGDALError, e:
            raise e
        except IOError, e:
            raise e

        title = tr('Preparing exposure data')
        # Find out what clipping behaviour we have - see #2210
        settings = QSettings()
        mode = settings.value(
            'inasafe/analysis_extents_mode',
            'HazardExposureView')
        if mode == 'HazardExposureView':
            detail = tr(
                'Resampling and clipping the exposure layer to match '
                'the intersection of the hazard layer and the current view '
                'extents.')
        elif mode == 'HazardExposure':
            detail = tr(
                'Resampling and clipping the exposure layer to match '
                'the intersection of the hazard layer extents.')
        elif mode == 'HazardExposureBookmark':
            detail = tr(
                'Resampling and clipping the exposure layer to match '
                'the bookmarked extents.')
        elif mode == 'HazardExposureBoundingBox':
            detail = tr(
                'Resampling and clipping the exposure layer to match '
                'the intersection of your preferred analysis area.')
        message = m.Message(
            m.Heading(title, **PROGRESS_UPDATE_STYLE),
            m.Paragraph(detail))
        send_dynamic_message(self, message)

        clipped_exposure = clip_layer(
            layer=self.exposure.qgis_layer(),
            extent=adjusted_geo_extent,
            cell_size=cell_size,
            extra_keywords=extra_exposure_keywords,
            hard_clip_flag=self.clip_hard)
        return clipped_hazard, clipped_exposure

    def setup_aggregator(self):
        """Create an aggregator for this analysis run."""
        try:
            buffered_geo_extent = self.impact.extent
        except AttributeError:
            # if we have no runner, set dummy extent
            buffered_geo_extent = self.clip_parameters['adjusted_geo_extent']

        if self.aggregation is not None:
            qgis_layer = self.aggregation.qgis_layer()
        else:
            qgis_layer = None

        # setup aggregator to use buffered_geo_extent to deal with #759
        self._aggregator = Aggregator(buffered_geo_extent, qgis_layer)

        self._aggregator.show_intermediate_layers = \
            self.show_intermediate_layers

    def run_post_processor(self):
        """Carry out any postprocessing required for this impact layer."""
        self._postprocessor_manager = PostprocessorManager(self.aggregator)
        self.postprocessor_manager.function_parameters = self.parameters
        self.postprocessor_manager.run()
        send_not_busy_signal(self)
        send_analysis_done_signal(self)
