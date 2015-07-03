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

from socket import gethostname
import getpass

from qgis.core import QgsVectorLayer

from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.common.exceptions import InvalidExtentError, FunctionParametersError
from safe.common.utilities import get_non_conflicting_attribute_name
from safe.utilities.i18n import tr
from safe.utilities.qgis_layer_wrapper import QgisWrapper
from safe.utilities.gis import convert_to_safe_layer


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
        # Keyword for hazard layer
        self._hazard_keyword = None
        # Keyword for exposure layer
        self._exposure_keyword = None
        # Keyword for aggregation layer
        self._aggregation_keyword = None
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
    def function_category(cls):
        """Property for function category based on hazard categories.

         Function category could be 'single_event' or/and 'multiple_event'.
         Single event data type means that the data is captured by a
         single observation, while 'multiple_event' has been aggregated for
         some observations.

         :returns: The hazard categories that this function supports.
         :rtype: list
        """
        return cls.metadata().as_dict().get('layer_requirements').get(
            'hazard').get('hazard_categories')

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
        if self.function_type() == 'old-style':
            self._hazard = convert_to_safe_layer(layer)
        elif self.function_type() == 'qgis2.0':
            # convert for new style impact function
            self._hazard = QgisWrapper(layer)
        else:
            message = tr('Error: Impact Function has unknown style.')
            raise Exception(message)

        # Update the target field to a non-conflicting one
        if isinstance(layer, QgsVectorLayer):
            self._target_field = get_non_conflicting_attribute_name(
                self.target_field,
                layer.dataProvider().fieldNameMap().keys()
            )
        # Automatically set the hazard keyword from the hazard layer.
        self.hazard_keyword = self.hazard.keywords

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
        if self.function_type() == 'old-style':
            self._exposure = convert_to_safe_layer(layer)
        elif self.function_type() == 'qgis2.0':
            # convert for new style impact function
            self._exposure = QgisWrapper(layer)
        else:
            message = tr('Error: Impact Function has unknown style.')
            raise Exception(message)

        # Update the target field to a non-conflicting one
        if isinstance(layer, QgsVectorLayer):
            self._target_field = get_non_conflicting_attribute_name(
                self.target_field,
                layer.dataProvider().fieldNameMap().keys()
            )

        # Automatically set the exposure from the hazard layer.
        self.exposure_keyword = self.exposure.keywords

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

        # Automatically set the exposure from the hazard layer.
        self.aggregation_keyword = self.aggregation.keywords

    @property
    def hazard_keyword(self):
        """Property for the hazard keyword to be used for the analysis.

        :returns: A dictionary representing keyword.
        :rtype: dict
        """
        return self._hazard_keyword

    @hazard_keyword.setter
    def hazard_keyword(self, keyword):
        """Setter for the hazard keyword property.

        :param keyword: A dictionary representing keyword.
        :type keyword: dict
        """
        self._hazard_keyword = keyword

    @property
    def exposure_keyword(self):
        """Property for the exposure keyword to be used for the analysis.

        :returns: A dictionary representing keyword.
        :rtype: dict
        """
        return self._exposure_keyword

    @exposure_keyword.setter
    def exposure_keyword(self, keyword):
        """Setter for the exposure keyword property.

        :param keyword: A dictionary representing keyword.
        :type keyword: dict
        """
        self._exposure_keyword = keyword

    @property
    def aggregation_keyword(self):
        """Property for the aggregation keyword to be used for the analysis.

        :returns: A dictionary representing keyword.
        :rtype: dict
        """
        return self._aggregation_keyword

    @aggregation_keyword.setter
    def aggregation_keyword(self, keyword):
        """Setter for the aggregation keyword property.

        :param keyword: A dictionary representing keyword.
        :type keyword: dict
        """
        self._aggregation_keyword = keyword

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
        """Validate things needed before running the analysis."""
        # Validate that input layers are valid
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
        pass
