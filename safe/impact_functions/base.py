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
import platform
from datetime import datetime
from qgis.utils import QGis
from osgeo import gdal
from PyQt4.QtCore import QT_VERSION_STR
from PyQt4.Qt import PYQT_VERSION_STR

from safe.impact_functions.impact_function_metadata import \
    ImpactFunctionMetadata
from safe.common.exceptions import (
    InvalidExtentError, FunctionParametersError, NoValidLayerError)
from safe.common.signals import send_static_message
from safe.postprocessors.postprocessor_factory import (
    get_postprocessors,
    get_postprocessor_human_name)
from safe import messaging as m
from safe.messaging import styles
from safe.common.utilities import get_non_conflicting_attribute_name
from safe.utilities.i18n import tr
from safe.utilities.gis import convert_to_safe_layer
from safe.storage.safe_layer import SafeLayer
from safe.definitions import inasafe_keyword_version
from safe.metadata.provenance import Provenance
from safe.common.version import get_version

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
        """
        # self.message_pre_run()
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

    def message_pre_run(self):
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
