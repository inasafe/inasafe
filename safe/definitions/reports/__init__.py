# coding=utf-8
"""Definitions for basic report.
"""


from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# Meta description about component

# component generation type
jinja2_component_type = {
    'key': 'jinja2_component_type',
    'name': 'Jinja2',
    'description': tr('A component that is generated using Jinja2 API.')
}

qgis_composer_component_type = {
    'key': 'qgis_composer_component_type',
    'name': 'QGISComposer',
    'description': tr('A component that is generated using QGISComposer API.')
}

qt_renderer_component_type = {
    'key': 'qt_renderer_component_type',
    'name': 'QtRenderer',
    'description': tr('A component that is generated using QtRenderer API.')
}

available_component_type = [
    jinja2_component_type,
    qgis_composer_component_type,
    qt_renderer_component_type
]

# Tags
# Tags is a way to categorize different component quickly for easy
# retrieval
final_product_tag = {
    'key': 'final_product_tag',
    'name': tr('Final Product'),
    'description': tr(
        'Tag this component as a Final Product of report generation.')
}

infographic_product_tag = {
    'key': 'infographic_product_tag',
    'name': tr('Infographic'),
    'description': tr(
        'Tag this component as an Infographic related product.')
}

map_product_tag = {
    'key': 'map_product_tag',
    'name': tr('Map'),
    'description': tr(
        'Tag this component as a product mainly to show map.')
}

table_product_tag = {
    'key': 'table_product_tag',
    'name': tr('Table'),
    'description': tr(
        'Tag this component as a product mainly with table.')
}

template_product_tag = {
    'key': 'template_product_tag',
    'name': tr(
        'Tag this component as a QGIS Template product.')
}

product_type_tag = [
    table_product_tag,
    map_product_tag,
    template_product_tag,
    infographic_product_tag
]


html_product_tag = {
    'key': 'html_product_tag',
    'name': tr('HTML'),
    'description': tr('Tag this product as HTML output.')
}

pdf_product_tag = {
    'key': 'pdf_product_tag',
    'name': tr('PDF'),
    'description': tr('Tag this product as PDF output.')
}

qpt_product_tag = {
    'key': 'qpt_product_tag',
    'name': tr('QPT'),
    'description': tr('Tag this product as QPT output.')
}

png_product_tag = {
    'key': 'png_product_tag',
    'name': tr('PNG'),
    'description': tr('Tag this product as PNG output.')
}

svg_product_tag = {
    'key': 'svg_product_tag',
    'name': tr('SVG'),
    'description': tr('Tag this product as SVG output.')
}

product_output_type_tag = [
    html_product_tag,
    pdf_product_tag,
    qpt_product_tag,
    png_product_tag,
]
