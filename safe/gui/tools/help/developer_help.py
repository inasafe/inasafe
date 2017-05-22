# coding=utf-8
"""Help text for the dock widget."""

import logging
from pprint import pprint
import StringIO
from safe import messaging as m
from safe.messaging import styles
from safe.definitions.units import unit_kilometres_per_hour
from safe.utilities.i18n import tr
LOGGER = logging.getLogger('InaSAFE')
# For chapter sections
# Items marked as numbered below will show section numbering in HTML render
TITLE_STYLE = styles.TITLE_LEVEL_1_STYLE  # h1 Not numbered
SECTION_STYLE = styles.SECTION_LEVEL_2_STYLE  # h2 numbered
SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE  # h3 numbered
BLUE_CHAPTER_STYLE = styles.BLUE_LEVEL_4_STYLE  # h4 numbered
RED_CHAPTER_STYLE = styles.RED_LEVEL_4_STYLE  # h4 numbered
DETAILS_STYLE = styles.ORANGE_LEVEL_5_STYLE  # h5 numbered
DETAILS_SUBGROUP_STYLE = styles.GREY_LEVEL_6_STYLE  # h5 numbered
# For images
SMALL_ICON_STYLE = styles.SMALL_ICON_STYLE
MEDIUM_ICON_STYLE = styles.MEDIUM_ICON_STYLE

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def developer_help():
    """Help message for developers.

    .. versionadded:: 4.1.0

    :returns: A message object containing helpful information.
    :rtype: messaging.message.Message
    """

    message = m.Message()
    message.add(m.Brand())
    message.add(heading())
    message.add(content())
    return message


def heading():
    """Helper method that returns just the header.

    This method was added so that the text could be reused in the
    other contexts.

    .. versionadded:: 4.1.0

    :returns: A heading object.
    :rtype: safe.messaging.heading.Heading
    """
    message = m.Heading(tr('InaSAFE developer help'), **TITLE_STYLE)
    return message

def content():
    """Helper method that returns just the content.

    This method was added so that the text could be reused in the
    dock_help module.

    .. versionadded:: 4.1.0

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    message = m.Message()
    message.add(m.Paragraph(tr(
        'This section of the help documentation is intended for advanced '
        'users who want to modify the internals of InaSAFE. It assumes that '
        'you have basic coding skills. All examples are in python unless '
        'otherwise stated.'
    )))
    message.add(
        m.Heading(tr('Defining a new hazard type'), **SUBSECTION_STYLE))
    message.add(
        m.Heading(tr('Background'), **BLUE_CHAPTER_STYLE))
    paragraph = m.Paragraph(tr(
        'In the previous versions of InaSAFE, we spent a lot of effort '
        'building one impact function per hazard/exposure combination (and '
        'sometimes multiple impact functions per combination). In our new '
        'architecture, we try to deal with everything in the same way - by '
        'following a standardized process of converting the hazard dataset '
        'into a classified polygon layer and then calculating the impacted '
        'and affected areas using a standard work-flow. A simplified version '
        'of this work-flow is described in illustration 1.'))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'Because of this change, you will no longer see an impact function '
        'selector in the dock widget and there are no longer any \'impact '
        'function options\' as we had in previous versions of InaSAFE. In '
        'the new system, almost all configuration is managed through '
        'metadata (created using the keywords wizard).'))

    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'Also, in all versions prior to Version 4.0, we made heavy use of '
        'interpolation in order to determine whether buildings or other '
        'exposure layers are impacted. Whist this is a commonly used '
        'technique in GIS, it often leads to non - intuitive looking '
        'reports. Under our new architecture, we always use geometric '
        'overlay operations to make a determination whether an exposure '
        'feature is affected or not. The implication of this is that we '
        'produce intuitive and easily verifiable impact layers. You can '
        'see an example in Illustration 2.'
    ))
    message.add(paragraph)
    paragraph = m.Paragraph(tr(
        'Stepping away from the two previously mentioned paradigms allows '
        'us to simply add new hazard types to the metadata driven impact '
        'function by adding new metadata types to the InaSafe sources. '
        'In the next chapter we show you how this was achieved and how '
        'it can be repeated for further hazards using the example of '
        'tropical cyclones.'
    ))
    message.add(paragraph)
    message.add(
        m.Heading(tr('Adding a new hazard'), **BLUE_CHAPTER_STYLE))
    message.add(paragraph)
    link = m.Link(
        'https://github.com/inasafe/inasafe/pull/3539/files',
        'Pull Request #3539')
    paragraph = m.Paragraph(
        tr('The whole work needed can be looked at in '),
        link,
        tr(
            '. Please bear in mind that the paths of the files are now '
            'safe/definitions/xxx.py and not safe/definitionsv4/xxx.py since '
            'v4 is the default codebase. In the next sections we will show '
            'each file that needs to be extended in order to add a new hazard '
            'type.'
    ))
    message.add(paragraph)
    output = StringIO.StringIO()
    pprint(unit_kilometres_per_hour, stream=output)
    paragraph = m.PreformattedText(output.getvalue())
    output.close()
    message.add(paragraph)
    return message


