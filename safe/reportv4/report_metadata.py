# coding=utf-8
"""
Module for class container of Report and ReportComponent Metadata.
"""
import os
from importlib import import_module

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class ReportComponentsMetadata(object):

    """ReportComponentsMetadata.

    Describing metadata for Report component
    """

    class AvailableComponent(object):
        """Class to hold available component.

        Useful for referencing

        """

        Jinja2 = 'Jinja2'
        QGISComposer = 'QGISComposer'

    def __init__(
            self, key, processor, extractor,
            output_format, template, output_path, extra_args=None):
        """Base class for component metadata

        ReportComponentMetadata is a metadata about the component element of
        a report. This metadata explains what and how this component will be
        rendered.

        :param key: the component element id. Can be referenced by other
            element.
        :type key: str

        :param processor: The processor that able to render this component.
            Can be represented as full method name as string or function
            reference.
        :type processor: str, function

        :param extractor: The extractor that prepare the context for this
            component rendering process. Can be represented as full method
            name as string or function reference.
        :type extractor: str, function

        :param output_format: The output format, can be a string or file or
            object.
        :type output_format: str

        :param template: The template path to use for rendering
        :type template: str

        :param output_path: The output path relatives to the output folder
            of the report. Can be used to dynamically link components in
            base template.
        :type output_path: str

        :param extra_args: Extra args sometimes needed for a component.
            Needed to pass it out to extractors.
        :type extra_args: str
        """
        self._key = key
        if callable(processor):
            self._processor = processor
        elif isinstance(processor, basestring):
            _package, _method = processor.rsplit('.', 1)
            _module = import_module(_package)
            self._processor = getattr(_module, _method)
        self._extractor = extractor
        self._output_format = output_format
        self._output_path = output_path
        self._template = template
        self._output = None
        self._component_context = {}
        self._extra_args = extra_args

    @property
    def key(self):
        """Unique key as ID for the component in the report.

        :rtype: str
        """
        return self._key

    @property
    def processor(self):
        """Function reference for method to render the component.

        :rtype: function
        """
        return self._processor

    @property
    def extractor(self):
        """Function reference for method to provide the data for rendering.

        :rtype: function
        """
        return self._extractor

    @property
    def output_format(self):
        """Output format of the rendering result.

        Can be a string, file, or object

        :rtype: str
        """
        return self._output_format

    @property
    def template(self):
        """Template path for the component.

        Relative to the template_folder property of ReportMetadata containing
        this component

        :rtype: str
        """
        return self._template

    @property
    def output_path(self):
        """Output path of the component rendering result.

        Relative to the output_folder property of ReportMetadata

        :rtype: str
        """
        return self._output_path

    @property
    def output(self):
        """The output of rendering process.

        Can be a string, a path to a file, or an object

        :rtype: str, object
        """
        return self._output

    @output.setter
    def output(self, value):
        """

        :param value: The output will be set only by rendering process and
            impact report
        :type value: str, object
        """
        self._output = value

    @property
    def context(self):
        """The context provided by extractors.

        Will be used by rendering process together with the template to
        generate output. Passed in the form of dict containing key-value pair

        :rtype: dict
        """
        return self._component_context

    @context.setter
    def context(self, value):
        """

        :param value: Only be set by extractors and impact report
        :type value: dict
        """
        self._component_context = value

    @property
    def extra_args(self):
        """Extra arguments that can be specified by report metadata.

        :return: dict
        """
        return self._extra_args

    @extra_args.setter
    def extra_args(self, value):
        """Extra arguments setter.

        :param value: Only be set in the report metadata declarations
        :type value: dict
        """
        self._extra_args = value


class Jinja2ComponentsMetadata(ReportComponentsMetadata):

    """Jinja2 Component.

    Component that can be rendered by Jinja2
    """

    class OutputFormat(object):
        """Class to hold this available output format."""

        String = 'string'
        File = 'file'

    def __init__(
            self, key, processor, extractor,
            output_format, template, output_path, extra_args=None):
        super(Jinja2ComponentsMetadata, self).__init__(
            key, processor, extractor, output_format, template, output_path,
            extra_args=extra_args)


class QgisComposerComponentsMetadata(ReportComponentsMetadata):

    """QGIS Composer Component.

    Component that can be rendered by QGIS Composition class

    """

    class OutputFormat(object):
        """Class to hold this available output format."""

        PDF = 'pdf'
        PNG = 'png'

    def __init__(
            self, key, processor, extractor,
            output_format, template, output_path, extra_args=None,
            page_dpi=300, page_width=210, page_height=297):
        """
        Provides 3 more options

        :param page_dpi: the page dpi of the output
        :type page_dpi: float

        :param page_width: the page width of the output
        :type page_width: float

        :param page_height: the page height of the output
        :type page_height: float
        """
        super(QgisComposerComponentsMetadata, self).__init__(
            key, processor, extractor, output_format, template, output_path,
            extra_args=extra_args)
        self._page_dpi = page_dpi
        self._page_width = page_width
        self._page_height = page_height

    @property
    def page_dpi(self):
        """
        :return: Page DPI of the output
        :rtype: float
        """
        return self._page_dpi

    @property
    def page_width(self):
        """
        :return: Page width of the output
        :rtype: float
        """
        return self._page_width

    @property
    def page_height(self):
        """
        :return: Page height of the output
        :rtype: float
        """
        return self._page_height


class ReportMetadata(object):

    def __init__(self, report_folder=None, metadata_dict=None):
        """
        Initialize report metadata from a dictionary or from report folders
        that contains the definitions and styles templates.

        :param report_folder: Optional param. Denote the location of report
            metadata folder
        :type report_folder: str

        :param metadata_dict: Optional param. Denote the report metadata
            structure
        :type metadata_dict: dict
        """
        if metadata_dict:
            self._template_folder = metadata_dict.get('template_folder')
            self._key = metadata_dict.get('key')
            self._name = metadata_dict.get('name')
            _components = metadata_dict.get('components')
            self._components = []
            for c in _components:
                _comp = self._load_components(c)
                self._components.append(_comp)
            self._output_folder = ''

        # TODO: might add when dealing with report_folder instead of
        #   metadata_dict

    @classmethod
    def _load_components(cls, component_metadata):
        key = component_metadata.get('key')
        component_type = component_metadata.get('type')
        processor = component_metadata.get('processor')
        extractor = component_metadata.get('extractor')
        output_format = component_metadata.get('output_format')
        template = component_metadata.get('template')
        output_path = component_metadata.get('output_path')
        extra_args = component_metadata.get('extra_args', {})
        if (component_type ==
                ReportComponentsMetadata.AvailableComponent.Jinja2):
            return Jinja2ComponentsMetadata(
                key, processor, extractor, output_format, template,
                output_path, extra_args=extra_args)
        elif (component_type ==
                ReportComponentsMetadata.AvailableComponent.QGISComposer):
            return QgisComposerComponentsMetadata(
                key, processor, extractor, output_format, template,
                output_path, extra_args=extra_args)

    @property
    def key(self):
        """Key identifier of Report metadata

        :rtype: str
        """
        return self._key

    @property
    def name(self):
        """

        :return: Recognizable name of report metadata template
        :rtype: str
        """
        return self._name

    @property
    def template_folder(self):
        """

        :return: the template folder where the subcomponent can be located
        :rtype: str
        """
        return self._template_folder

    @property
    def output_folder(self):
        """

        :return: Output folder where the result will be saved
        :rtype: str
        """
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value):
        """

        :param value: Output folder where the result will be saved
        :type value: str
        """
        self._output_folder = value

    @property
    def components(self):
        """List of report components.

        A list of report components that needed to be generated each

        :return: list of ReportComponentsMetadata
        :rtype: [ReportComponentsMetadata]
        """
        return self._components

    def component_by_key(self, key):
        """Retrieve component by its key.

        :param key: Component key
        :type key: str

        :return: ReportComponentsMetadata
        """
        filtered = [c for c in self.components if c.key == key]
        if filtered:
            return filtered[0]
        return None
