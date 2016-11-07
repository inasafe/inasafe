# coding=utf-8
from importlib import import_module

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '10/22/16'


class ReportComponentsMetadata(object):

    def __init__(
            self, key, processor, extractor,
            output_format, template, output_path):
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

    @property
    def key(self):
        return self._key

    @property
    def processor(self):
        return self._processor

    @property
    def extractor(self):
        return self._extractor

    @property
    def output_format(self):
        return self._output_format

    @property
    def template(self):
        return self._template

    @property
    def output_path(self):
        return self._output_path

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        self._output = value

    @property
    def context(self):
        return self._component_context

    @context.setter
    def context(self, value):
        self._component_context = value


class Jinja2ComponentsMetadata(ReportComponentsMetadata):

    def __init__(
            self, key, processor, extractor,
            output_format, template, output_path):
        super(Jinja2ComponentsMetadata, self).__init__(
            key, processor, extractor, output_format, template, output_path)


class QgisComposerComponentsMetadata(ReportComponentsMetadata):

    def __init__(
            self, key, processor, extractor,
            output_format, template, output_path,
            page_dpi=300, page_width=None, page_height=None):
        super(QgisComposerComponentsMetadata, self).__init__(
            key, processor, extractor, output_format, template, output_path)
        self._page_dpi = page_dpi
        self._page_width = page_width
        self._page_height = page_height

    @property
    def page_dpi(self):
        return self._page_dpi

    @property
    def page_width(self):
        return self._page_width

    @property
    def page_height(self):
        return self._page_height


class ReportMetadata(object):

    def __init__(self, report_folder=None, metadata_dict=None):
        """
        Initialize report metadata from a dictionary or from report folders
        that contains the definitions and styles templates.

        :param report_folder:
        :param metadata_dict:
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

    @classmethod
    def _load_components(cls, component_metadata):
        key = component_metadata.get('key')
        component_type = component_metadata.get('type')
        processor = component_metadata.get('processor')
        extractor = component_metadata.get('extractor')
        output_format = component_metadata.get('output_format')
        template = component_metadata.get('template')
        output_path = component_metadata.get('output_path')
        extra_args = component_metadata.get('extra_args')
        if component_type == 'Jinja2':
            return Jinja2ComponentsMetadata(
                key, processor, extractor, output_format, template,
                output_path)
        elif component_type == 'QGISComposer':
            return QgisComposerComponentsMetadata(
                key, processor, extractor, output_format, template,
                output_path, **extra_args)

    @property
    def key(self):
        return self._key

    @property
    def name(self):
        return self._name

    @property
    def template_folder(self):
        return self._template_folder

    @property
    def output_folder(self):
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value):
        self._output_folder = value

    @property
    def components(self):
        """
        A list of report components that needed to be generated each

        :return: list of ReportComponentsMetadata
        :rtype: [ReportComponentsMetadata]
        """
        return self._components
