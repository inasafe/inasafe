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

from qgis.core import QgsVectorLayer

from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.storage.core import Vector
from safe.common.exceptions import InvalidExtentError
from safe.common.utilities import get_non_conflicting_attribute_name
from safe.utilities.i18n import tr
from safe.utilities.qgis_layer_wrapper import QgisWrapper
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer


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
        # Requested extent to use
        self._requested_extent = None
        # Requested extent's CRS as EPSG number
        self._requested_extent_crs = 4326
        # Actual extent to use - Read Only
        # For 'old-style' IF we do some manipulation to the requested extent
        self._actual_extent = None
        # Actual extent's CRS as EPSG number - Read Only
        self._actual_extent_crs = 4326
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

    @classmethod
    def data_type(cls):
        """Property for the data type of impact function.

         This property holds value either 'single-scenario' or 'hazard-map'.
         Single scenario data type means that the data is captured by a
         single observation, while 'hazard-map' has been aggregated for some
         observations.
        """
        return cls.metadata().as_dict().get('data_type', None)

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

        :returns: A number representing the EPSG code for the CRS. e.g. 4326
        :rtype: int
        """
        return self._requested_extent_crs

    @requested_extent_crs.setter
    def requested_extent_crs(self, crs):
        """Setter for extent_crs property.

        .. note:: We break our rule here on not allowing acronyms for
            parameter names.

        :param crs: Analysis boundary EPSG CRS expressed as an integer.
        :type crs: int
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

        :returns: A number representing the EPSG code for the CRS. e.g. 4326
        :rtype: int
        """
        return self._actual_extent_crs

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
        :rtype: QgsMapLayer, QgsVectorLayer, QgsRasterLayer
        """
        return self._hazard

    @hazard.setter
    def hazard(self, layer):
        """Setter for hazard layer property.

        :param layer: Hazard layer to be used for the analysis.
        :type layer: QgsVectorLayer, QgsRasterLayer, Vector, Raster
        """
        self._hazard = layer
        # Update the target field to a non-conflicting one
        if isinstance(layer, QgisWrapper):
            if isinstance(layer.data, QgsVectorLayer):
                self._target_field = get_non_conflicting_attribute_name(
                    self.target_field,
                    layer.data.dataProvider().fieldNameMap().keys()
                )
        elif isinstance(layer, Vector):
            attribute_names = layer.get_attribute_names()
            self._target_field = get_non_conflicting_attribute_name(
                self.target_field, attribute_names)

    @property
    def exposure(self):
        """Property for the exposure layer to be used for the analysis.

        :returns: A map layer.
        :rtype: QgsMapLayer, QgsVectorLayer, QgsRasterLayer
        """
        return self._exposure

    @exposure.setter
    def exposure(self, layer):
        """Setter for exposure layer property.

        :param layer: exposure layer to be used for the analysis.
        :type layer: QgsVectorLayer, QgsRasterLayer, Vector, Raster
        """
        self._exposure = layer
        # Update the target field to a non-conflicting one
        if isinstance(layer, QgisWrapper):
            if isinstance(layer.data, QgsVectorLayer):
                self._target_field = get_non_conflicting_attribute_name(
                    self.target_field,
                    layer.data.dataProvider().fieldNameMap().keys()
                )
        elif isinstance(layer, Vector):
            attribute_names = layer.get_attribute_names()
            self._target_field = get_non_conflicting_attribute_name(
                self.target_field, attribute_names)

    @property
    def aggregation(self):
        """Property for the aggregation layer to be used for the analysis.

        :returns: A map layer.
        :rtype: QgsMapLayer, QgsVectorLayer
        """
        return self._aggregation

    @aggregation.setter
    def aggregation(self, layer):
        """Setter for aggregation layer property.

        :param layer: Aggregation layer to be used for the analysis.
        :type layer: QgsMapLayer, QgsVectorLayer
        """
        # add more robust checks here
        self._aggregation = layer

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
    def impact(self):
        """Property for the impact layer generated by the analysis.

        .. note:: It is not guaranteed that all impact functions produce a
            spatial layer.

        :returns: A map layer.
        :rtype: QgsMapLayer, QgsVectorLayer, QgsRasterLayer
        """
        return self._impact

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
                    % {'hazard': self.hazard.get_name().lower(),
                       'exposure': self.exposure.get_name().lower(),
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
        """Validate things needed to run the analysis."""
        # Validate extent, with the QGIS IF, we need requested_extent set
        if self.function_type() == 'qgis2.0' and self.requested_extent is None:
            raise InvalidExtentError(
                'Impact Function with QGIS function type is used, but no '
                'extent is provided.')

    def prepare(self, layers):
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

        :param layers: List of layers (hazard and exposure). This is
            necessary now, until we streamline the preprocess in the base class
            and remove unnecessary routines in analysis, impact_calculator,
            impact_calculator_thread, and calculate_safe_impact module.
        :type layers: list
        # """
        if layers is not None:
            self.hazard = get_hazard_layer(layers)
            self.exposure = get_exposure_layer(layers)
