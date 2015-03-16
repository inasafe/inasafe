# coding=utf-8
"""Abstract base class for all impact functions."""

from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.common.exceptions import InvalidExtentError
from safe.utilities.keyword_io import KeywordIO

from safe.utilities.i18n import tr


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
        self._function_type = 'legacy'  # or 'qgis2'
        # Analysis extent to use
        self._extent = None
        # CRS as EPSG number
        self._extent_crs = 4326
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
        # Post analysis Result dictionary (suitable to conversion to json etc.)
        self._tabulated_impact = None
        # Style information for the impact layer - at some point we should
        # formalise this into a more natural model
        # ABC's will normally set this property.
        self._impact_style = None

    @property
    def function_type(self):
        """Property for the type of impact function ('legacy' or 'qgis2').

        QGIS2 impact functions are using the QGIS api and have more
        dependencies. Legacy IF's use only numpy, gdal etc. and can be
        used in contexts where no QGIS is present.
        """
        return self._function_type

    @property
    def extent(self):
        """Property for the extent of impact function analysis.

        :returns: A list in the form [xmin, ymin, xmax, ymax].
        :rtype: list
        """
        return self._extent

    @extent.setter
    def extent(self, extent):
        """Setter for extent property.

        :param extent: Analysis boundaries expressed as
            [xmin, ymin, xmax, ymax]. The extent CRS should match the
            extent_crs property of this IF instance.
        :type extent: list
        """
        # add more robust checks here
        if len(extent) != 4:
            raise InvalidExtentError('%s is not a valid extent.' % extent)
        self._extent = extent

    @property
    def extent_crs(self):
        """Property for the extent CRS of impact function analysis.

        :returns: An number representing the EPSG code for the CRS. e.g. 4326
        :rtype: int
        """
        return self._extent_crs

    @extent_crs.setter
    def extent_crs(self, crs):
        """Setter for extent_crs property.

        .. note:: We break our rule here on not allowing acronyms for
            parameter names.

        :param crs: Analysis boundary EPSG CRS expressed as an integer.
        :type crs: int
        """
        self._extent_crs = crs

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

    @classmethod
    def metadata(cls):
        """Get the metadata for this class."""
        return cls._metadata.get_metadata()

    @classmethod
    def parameters(cls):
        """Get the parameter for this class."""
        return cls._metadata.parameters()

    def prepare(self):
        """Prepare this impact function for running the analysis.

        This method should normally be called in your concrete class's
        run method before it attempts to do any real processing. This
        method will do any needed house keeping such as:

            * checking that the exposure and hazard layers sufficiently overlap
            * clipping or subselecting features from both layers such that
              only features / coverage within the actual analysis extent
              will be analysed.
            * raising errors if any untennable condition exists e.g. extent has
              no valid CRS.

        We suggest to overload this method in your concrete class implementation
        so that it includes any impact function specific checks too.

        :raises:
        """
        if self.extent is None:
            raise InvalidExtentError(
                tr('The analysis extent has not been set.'))

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
        :type layer: QgsMapLayer, QgsVectorLayer, QgsRasterLayer
        """
        # add more robust checks here
        self._hazard = layer

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
        :type layer: QgsMapLayer, QgsVectorLayer, QgsRasterLayer
        """
        # add more robust checks here
        self._exposure = layer

    @property
    def aggregation(self):
        """Property for the aggregation layer to be used for the analysis.

        :returns: A map layer.
        :rtype: QgsMapLayer, QgsVectorLayer, QgsRasterLayer
        """
        return self._aggregation

    @aggregation.setter
    def aggregation(self, layer):
        """Setter for aggregation layer property.

        :param layer: Aggregation layer to be used for the analysis.
        :type layer: QgsMapLayer, QgsVectorLayer, QgsRasterLayer
        """
        # add more robust checks here
        self._aggregation = layer

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
        function_title = self.metadata()['title']
        return (tr('In the event of %(hazard)s how many '
                   '%(exposure)s might %(impact)s')
                % {'hazard': self.hazard.get_name().lower(),
                   'exposure': self.exposure.get_name().lower(),
                   'impact': function_title.lower()})

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
