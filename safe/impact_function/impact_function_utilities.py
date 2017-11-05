# coding=utf-8

"""Utilities for Impact Function."""

from PyQt4.QtCore import Qt

from safe import messaging as m
from safe.common.exceptions import NoKeywordsFoundError, InvalidLayerError
from safe.definitions.constants import (
    inasafe_keyword_version_key,
    PREPARE_SUCCESS,
    PREPARE_FAILED_BAD_INPUT,
)
from safe.definitions.versions import inasafe_keyword_version
from safe.gis.sanity_check import check_inasafe_fields
from safe.gui.widgets.message import generate_input_error_message
from safe.utilities.gis import is_vector_layer
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.utilities import is_keyword_version_supported

LAYER_ORIGIN_ROLE = Qt.UserRole  # Value defined with the following dict.
FROM_CANVAS = {
    'key': 'FromCanvas',
    'name': tr('Layers from Canvas'),
}
FROM_ANALYSIS = {
    'key': 'FromAnalysis',
    'name': tr('Layers from Analysis'),
}

LAYER_PARENT_ANALYSIS_ROLE = LAYER_ORIGIN_ROLE + 1  # Name of the parent IF
LAYER_PURPOSE_KEY_OR_ID_ROLE = LAYER_PARENT_ANALYSIS_ROLE + 1  # Layer purpose


def check_input_layer(layer, purpose):
    """Function to check if the layer is valid.

    The function will also set the monkey patching if needed.

    :param layer: The layer to test.
    :type layer: QgsMapLayer

    :param purpose: The expected purpose of the layer.
    :type purpose: basestring

    :return: A tuple with the status of the layer and an error message if
        needed.
        The status is 0 if everything was fine.
        The status is 1 if the client should fix something.
    :rtype: (int, m.Message)
    """
    if not layer.isValid():
        title = tr(
            'The {purpose} layer is invalid').format(purpose=purpose)
        content = tr(
            'The impact function needs a {exposure} layer to run. '
            'You must provide a valid {exposure} layer.').format(
            purpose=purpose)
        message = generate_input_error_message(
            title, m.Paragraph(content))
        return PREPARE_FAILED_BAD_INPUT, message

    # We should read it using KeywordIO for the very beginning. To avoid
    # get the modified keywords in the patching.
    try:
        keywords = KeywordIO().read_keywords(layer)
    except NoKeywordsFoundError:

        title = tr(
            'The {purpose} layer does not have keywords.').format(
            purpose=purpose)
        content = tr(
            'The {purpose} layer does not have keywords. Use the wizard '
            'to assign keywords to the layer.').format(purpose=purpose)
        message = generate_input_error_message(
            title, m.Paragraph(content))
        return PREPARE_FAILED_BAD_INPUT, message

    if keywords.get('layer_purpose') != purpose:
        title = tr('The expected {purpose} layer is not an {purpose}.') \
            .format(purpose=purpose)
        content = tr('The expected {purpose} layer is not an {purpose}.') \
            .format(purpose=purpose)
        message = generate_input_error_message(
            title, m.Paragraph(content))
        return PREPARE_FAILED_BAD_INPUT, message

    version = keywords.get(inasafe_keyword_version_key)
    supported = is_keyword_version_supported(version)
    if not supported:
        parameters = {
            'version': inasafe_keyword_version,
            'source': layer.publicSource()
        }
        title = tr('The {purpose} layer is not up to date.').format(
            purpose=purpose)
        content = tr(
            'The layer {source} must be updated to {version}.').format(
            **parameters)
        message = generate_input_error_message(
            title, m.Paragraph(content))
        return PREPARE_FAILED_BAD_INPUT, message

    layer.keywords = keywords

    if is_vector_layer(layer):
        try:
            check_inasafe_fields(layer, keywords_only=True)
        except InvalidLayerError:
            title = tr('The {purpose} layer is not up to date.').format(
                purpose=purpose)
            content = tr(
                'The layer {source} must be updated with the keyword '
                'wizard. Your fields which have been set in the keywords '
                'previously are not matching your layer.').format(
                source=layer.publicSource())
            message = generate_input_error_message(
                title, m.Paragraph(content))
            del layer.keywords
            return PREPARE_FAILED_BAD_INPUT, message

    return PREPARE_SUCCESS, None
