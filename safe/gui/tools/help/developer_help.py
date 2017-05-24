# coding=utf-8
"""Help text for the dock widget."""

import logging
from pprint import pprint
import StringIO
from safe import messaging as m
from safe.messaging import styles
from safe.definitions.units import unit_kilometres_per_hour
from safe.definitions.hazard import hazard_cyclone, hazard_all
from safe.definitions.hazard_classifications import\
    cyclone_au_bom_hazard_classes
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

    # Setting up units

    message.add(
        m.Heading(tr('safe/definitions/units.py'), **BLUE_CHAPTER_STYLE))
    paragraph = m.Paragraph(
        'If you are adding an hazard that uses units that are not yet known '
        'to InaSafe, you need to define them in units.py'
    )
    message.add(paragraph)
    _definition_to_string(
        message, unit_kilometres_per_hour=unit_kilometres_per_hour)

    # Setting up style

    message.add(
        m.Heading(tr('safe/definitions/colors.py'), **BLUE_CHAPTER_STYLE))
    paragraph = m.Paragraph(
        'If you are adding an hazard that has more classes than any other '
        'hazards you’ll need to add additional colors for the additional '
        'classes in colors.py. You might also define other colors if you '
        'don\'t want to use the standard colors. For the sake of homogeneous '
        'map reports, this addition should not be taken lightly.'
    )
    message.add(paragraph)
    # Don't translate this
    paragraph = m.PreformattedText('very_dark_red = Qcolor(\'#710017\')')
    message.add(paragraph)

    # Setting up hazard classification

    message.add(
        m.Heading(
            tr('safe/definitions/hazard_classifications.py'),
            **BLUE_CHAPTER_STYLE))
    paragraph = m.Paragraph(
        'Add the classifications you want to make available for your new '
        'hazard type. You can add as many classes as you want in the '
        'classes list.')
    message.add(paragraph)
    paragraph = m.Paragraph(
        'Also, a classification can support multiple units so you don\'t '
        'have to define different classifications just to have the same '
        'classification in two or more different units. These are defined '
        'in the multiple_units attribute of the classification.'
    )
    message.add(paragraph)
    _definition_to_string(
        message, cyclone_au_bom_hazard_classes=cyclone_au_bom_hazard_classes)

    # Setting up wizard questions

    message.add(
        m.Heading(
            tr('safe/gui/tools/wizard/wizard_strings.py'),
            **BLUE_CHAPTER_STYLE))
    paragraph = m.Paragraph(
        'Define the questions for the wizard:'
    )
    message.add(paragraph)
    # don not translate
    message.add(m.PreformattedText(
        'cyclone_kilometres_per_hour_question = tr(\'wind speed in km/h\')'))
    message.add(m.PreformattedText(
        'cyclone_miles_per_hour_question = tr(\'wind speed in mph\')'))
    message.add(m.PreformattedText(
        'cyclone_knots_question = tr(\'wind speed in kn\')'))

    # Setting up

    message.add(
        m.Heading(tr('safe/definitions/hazard.py'), **BLUE_CHAPTER_STYLE))
    paragraph = m.Paragraph(
        'Finally define new hazard and add it to the hazard_all list:'
    )
    message.add(paragraph)
    _definition_to_string(message, hazard_cyclone=hazard_cyclone)
    # Be careful, pretty print unpacks lists so this will turn into a 50 pager
    # zoom_definition_to_string(message, hazard_all=hazard_all)

    return message


def _definition_to_string(message, **kwargs):
    """Use pprint for dict and list examples.
    
    The argument name will be prepended to the pretty printed text of the 
    argument content e.g.:
    
    foo = { 'bar': 'baz' }
    _definition_to_string(message, foo=foo)
     
    will print this in the message as a preformatted paragraph:
    
        foo = { 'bar': 'baz' }
    """

    for key, value in kwargs.iteritems():
        output = StringIO.StringIO()
        output.write(key + ' = ')
        pprint(value, stream=output)
        paragraph = m.PreformattedText(output.getvalue())
        output.close()
        message.add(paragraph)


