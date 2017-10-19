# coding=utf-8
"""Module for class container of Report and ReportComponent Metadata.
"""
from copy import deepcopy
from importlib import import_module

from safe.definitions.reports import (
    jinja2_component_type,
    qgis_composer_component_type)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class ReportComponentsMetadata(object):

    """ReportComponentsMetadata.

    Describing metadata for Report component

    .. versionadded:: 4.0
    """

    def __init__(
            self, key, processor, extractor,
            output_format, template, output_path, resources=None,
            tags=None, context=None, extra_args=None, **kwargs):
        """Base class for component metadata.

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

        .. versionadded:: 4.0
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
        self._resources = resources
        self._template = template
        self._tags = tags or []
        self._output = None
        if context:
            self._component_context = context
        else:
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

        :rtype: str, dict, list
        """
        return self._output_path

    @property
    def resources(self):
        """Resources that used by the component.

        :rtype: list
        """
        return self._resources

    @property
    def tags(self):
        """List of tag for easy categorizations.

        :return: list
        """
        return self._tags

    @property
    def output(self):
        """The output of rendering process.

        Can be a string, a path to a file, or an object

        :rtype: str, object
        """
        return self._output

    @output.setter
    def output(self, value):
        """The output of rendering process.

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
        """The context provided by extractors.

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

    @property
    def info(self):
        """Short info about the component.

        :return: Returned dictionary of information about the component.
        :rtype: dict
        """
        return {
            'key': self.key,
            'processor': self.processor,
            'extractor': self.extractor,
            'output_path': self.output_path,
            'output_format': self.output_format,
            'template': self.template,
            'type': type(self)
        }


class Jinja2ComponentsMetadata(ReportComponentsMetadata):

    """Jinja2 Component.

    Component that can be rendered by Jinja2

    .. versionadded:: 4.0
    """

    class OutputFormat(object):

        """Class to hold this available output format."""

        String = 'string'
        File = 'file'

    def __init__(
            self, key, processor, extractor,
            output_format, template, output_path, extra_args=None, **kwargs):
        """Create Jinja2 Components Metadata holder"""
        super(Jinja2ComponentsMetadata, self).__init__(
            key, processor, extractor, output_format, template, output_path,
            extra_args=extra_args, **kwargs)


class QgisComposerComponentsMetadata(ReportComponentsMetadata):

    """QGIS Composer Component.

    Component that can be rendered by QGIS Composition class

    .. versionadded:: 4.0
    """

    class OutputFormat(object):

        """Class to hold this available output format."""

        PDF = 'pdf'
        PNG = 'png'
        QPT = 'qpt'

        DOC_OUTPUT = [PDF, PNG]
        TEMPLATE_OUTPUT = QPT
        SUPPORTED_OUTPUT = [PDF, PNG, QPT]

    def __init__(
            self, key, processor, extractor,
            output_format, template, output_path, extra_args=None,
            orientation='portrait',
            page_dpi=300, page_width=210, page_height=297,
            **kwargs):
        """Create QGISComposer Components Metadata holder.

        Provides 3 more options

        :param orientation: the orientation of the paper
        :type orientation: 'portrait' | 'landscape'

        :param page_dpi: the page dpi of the output
        :type page_dpi: float

        :param page_width: the page width of the output
        :type page_width: float

        :param page_height: the page height of the output
        :type page_height: float

        .. versionadded:: 4.0
        """
        super(QgisComposerComponentsMetadata, self).__init__(
            key, processor, extractor, output_format, template, output_path,
            extra_args=extra_args, **kwargs)
        self._orientation = orientation
        self._page_dpi = page_dpi
        self._page_width = page_width
        self._page_height = page_height

    @property
    def orientation(self):
        """Orientation of the document.

        :return: Page orientation of the output
        :rtype: 'portrait' | 'landscape'
        """
        return self._orientation

    @property
    def page_dpi(self):
        """Page DPI.

        :return: Page DPI of the output
        :rtype: float
        """
        return self._page_dpi

    @property
    def page_width(self):
        """Page Width.

        :return: Page width of the output
        :rtype: float
        """
        return self._page_width

    @property
    def page_height(self):
        """Page Height.

        :return: Page height of the output
        :rtype: float
        """
        return self._page_height

    @property
    def info(self):
        """Short info of the metadata.

        :return: Returned dictionary of information about the component.
        :rtype: dict
        """
        return super(QgisComposerComponentsMetadata, self).info.update({
            'orientation': self.orientation,
            'page_dpi': self.page_dpi,
            'page_width': self.page_width,
            'page_height': self.page_height
        })


class ReportMetadata(object):

    """Class to hold report metadata.

    This class is used to convert report metadata definitions.

    .. versionadded:: 4.0
    """

    def __init__(self, report_folder=None, metadata_dict=None):
        """Create report metadata.

        Initialize report metadata from a dictionary or from report folders
        that contains the definitions and styles templates.

        :param report_folder: Optional param. Denote the location of report
            metadata folder
        :type report_folder: str

        :param metadata_dict: Optional param. Denote the report metadata
            structure
        :type metadata_dict: dict

        .. versionadded:: 4.0
        """
        if metadata_dict:
            self._template_folder = metadata_dict.get('template_folder')
            self._key = metadata_dict.get('key')
            self._name = metadata_dict.get('name')
            self._tags = metadata_dict.get('tags')
            _components = deepcopy(metadata_dict.get('components'))
            self._components = []
            for c in _components:
                _comp = self._load_components(c)
                self._components.append(_comp)
            self._output_folder = ''

        # TODO: might add when dealing with report_folder instead of
        #   metadata_dict

    @classmethod
    def _load_components(cls, component_metadata):
        component_type = component_metadata.get('type')
        template = component_metadata.get('template')
        kwargs = component_metadata
        kwargs['template'] = template

        if component_type == jinja2_component_type:
            return Jinja2ComponentsMetadata(**kwargs)
        elif component_type == qgis_composer_component_type:
            return QgisComposerComponentsMetadata(**kwargs)
        else:
            return ReportComponentsMetadata(**kwargs)

    @property
    def key(self):
        """Key identifier of Report metadata.

        :rtype: str
        """
        return self._key

    @property
    def name(self):
        """Recognizable name of report metadata template.

        :rtype: str
        """
        return self._name

    @property
    def template_folder(self):
        """The template folder where the subcomponent can be located.

        :rtype: str
        """
        return self._template_folder

    @property
    def output_folder(self):
        """Output folder where the result will be saved.

        :rtype: str
        """
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value):
        """Output folder where the result will be saved.

        :param value: Output folder where the result will be saved
        :type value: str
        """
        self._output_folder = value

    @property
    def components(self):
        """List of report components.

        A list of report components that needed to be generated each.

        :return: list of ReportComponentsMetadata
        :rtype: list[ReportComponentsMetadata]
        """
        return self._components

    def component_by_key(self, key):
        """Retrieve component by its key.

        :param key: Component key
        :type key: str

        :return: ReportComponentsMetadata
        :rtype: ReportComponentsMetadata

        .. versionadded:: 4.0
        """
        filtered = [c for c in self.components if c.key == key]
        if filtered:
            return filtered[0]
        return None

    def component_by_tags(self, tags):
        """Retrieve components by tags.

        :param tags: List of tags
        :type tags: list

        :return: List of ReportComponentsMetadata
        :rtype: list[ReportComponentsMetadata]

        .. versionadded:: 4.0
        """
        tags_keys = [t['key'] for t in tags]
        filtered = [
            c for c in self.components
            if set(tags_keys).issubset([ct['key'] for ct in c.tags])]
        return filtered
