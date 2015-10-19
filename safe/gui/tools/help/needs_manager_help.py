# coding=utf-8

__author__ = 'ismailsunni'


from safe.utilities.i18n import tr
from safe import messaging as m
from safe.messaging import styles

INFO_STYLE = styles.INFO_STYLE


def needs_manager_helps():
    """Help message for Batch Dialog.

    ..versionadded:: 3.2.1

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

    This method was added so that the text could be resused in the
    other contexts.

    ..versionadded:: 3.2.2

    :returns: A heading object.
    :rtype: safe.messaging.heading.Heading
    """
    message = m.Heading(tr('Minimum needs manager help'), **INFO_STYLE)
    return message


def content():
    """Helper method that returns just the content.

    This method was added so that the text could be resused in the
    dock_help module.

    ..versionadded:: 3.2.2

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    message = m.Message()
    message.add(m.Paragraph(tr(
        'During and after a disaster, providing for the basic human minimum '
        'needs of food, water, hygiene and shelter is an important element of '
        'your contingency plan. InaSAFE has a customisable minimum needs '
        'system that allows you to define country or region specific '
        'requirements for compiling a needs report where the exposure '
        'layer represents population.'
    )))
    message.add(m.Paragraph(tr(
        'By default InaSAFE uses minimum needs defined for Indonesia - '
        'and ships with additional profiles for the Philippines and Tanzania. '
        'You can customise these or add your own region-specific profiles too.'

    )))
    message.add(m.Paragraph(tr(
        'Minimum needs are grouped into regional or linguistic ‘profiles’. '
        'The default profile is ‘BNPB_en’ - the english profile for the '
        'national disaster agency in Indonesia.'
    )))
    message.add(m.Paragraph(tr(
        'You will see that their profile defines requirements for displaced '
        'persons in terms of Rice, Drinking Water, Clean Water (for bathing '
        'etc.), Family Kits (with personal hygiene items) and provision of '
        'toilets.'
    )))
    message.add(m.Paragraph(tr(
        'Each item in the profile can be customised or removed. For example '
        'selecting the first item in the list and then clicking on the '
        '\'pencil\' icon will show the details of how it was defined.'
        'If you scroll up and down in the panel you will see that for each '
        'item, you can set a name, description, units (in singular, '
        'plural and abbreviated forms), specify maxima and minima for the '
        'quantity of item allowed, a default and a frequency. You would use '
        'the maxima and minima to ensure that disaster managers never '
        'allocate amounts that will not be sufficient for human livelihood, '
        'and also that will not overtax the logistics operation for those '
        'providing humanitarian relief.'
    )))
    message.add(m.Paragraph(tr(
        'The final item in the item configuration is the \'readable sentence\''
        'which bears special discussion. Using a simple system of tokens you '
        'can construct a sentence that will be used in the generated needs '
        'report.'
    )))
    message.add(m.Paragraph(tr(
        ''
    )))
    return message
