# coding=utf-8
"""Context help for minimum needs manager dialog."""

from safe import messaging as m
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path

SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE
INFO_STYLE = styles.BLUE_LEVEL_4_STYLE

__author__ = 'ismailsunni'


def needs_manager_helps():
    """Help message for Batch Dialog.

    .. versionadded:: 3.2.1

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

    .. versionadded:: 3.2.2

    :returns: A heading object.
    :rtype: safe.messaging.heading.Heading
    """
    message = m.Heading(tr('Minimum needs manager help'), **SUBSECTION_STYLE)
    return message


def content():
    """Helper method that returns just the content.

    This method was added so that the text could be reused in the
    dock_help module.

    .. versionadded:: 3.2.2

    :returns: A message object without brand element.
    :rtype: safe.messaging.message.Message
    """
    message = m.Message()
    paragraph = m.Paragraph(
        m.Image(
            'file:///%s/img/screenshots/'
            'minimum-needs-screenshot.png' % resources_path()),
        style_class='text-center'
    )
    message.add(paragraph)
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
        'Minimum needs are grouped into regional or linguistic \'profiles\'. '
        'The default profile is \'BNPB_en\' - the english profile for the '
        'national disaster agency in Indonesia. '
        'You will see that this profile defines requirements for displaced '
        'persons in terms of Rice, Drinking Water, Clean Water (for bathing '
        'etc.), Family Kits (with personal hygiene items) and provision of '
        'toilets.'
    )))
    message.add(m.Paragraph(tr(
        'Each item in the profile can be customised or removed. For example '
        'selecting the first item in the list and then clicking on the '
        '\'pencil\' icon will show the details of how it was defined. '
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
        'The final item in the item configuration is the \'readable '
        'sentence\' which bears special discussion. Using a simple system of '
        'tokens you can construct a sentence that will be used in the '
        'generated needs report.'
    )))
    message.add(m.Heading(tr('Minimum needs profiles'), **INFO_STYLE))
    message.add(m.Paragraph(tr(
        'A profile is a collection of resources that define the minimum needs '
        'for a particular country or region. Typically a profile should be '
        'based on a regional, national or international standard. The '
        'actual definition of which resources are needed in a given '
        'profile is dependent on the local conditions and customs for the '
        'area where the contingency plan is being devised.'
    )))
    message.add(m.Paragraph(tr(
        'For example in the middle east, rice is a staple food whereas in '
        'South Africa, maize meal is a staple food and thus the contingency '
        'planning should take these localised needs into account.'
    )))

    message.add(m.Heading(tr('Minimum needs resources'), **INFO_STYLE))
    message.add(m.Paragraph(tr(
        'Each item in a minimum needs profile is a resource. Each resource '
        'is described as a simple natural language sentence e.g.:'
    )))

    message.add(m.EmphasizedText(tr(
        'Each person should be provided with 2.8 kilograms of Rice weekly.'
    )))
    message.add(m.Paragraph(tr(
        'By clicking on a resource entry in the profile window, and then '
        'clicking the black pencil icon you will be able to edit the '
        'resource using the resource editor. Alternatively you can create a '
        'new resource for a profile by clicking on the black + icon in '
        'the profile manager. You can also remove any resource from a '
        'profile using the - icon in the profile manager.')))

    message.add(m.Heading(tr('Resource Editor'), **INFO_STYLE))
    message.add(m.Paragraph(tr(
        'When switching to edit or add resource mode, the minimum needs '
        'manager will be updated to show the resource editor. Each '
        'resource is described in terms of:'
    )))
    bullets = m.BulletedList()
    bullets.add(m.Text(
        m.ImportantText(tr(
            'resource name')),
        tr(' - e.g. Rice')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'a description of the resource')),
        tr(' - e.g. Basic food')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'unit in which the resource is provided')),
        tr(' - e.g. kilogram')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'pluralised form of the units')),
        tr(' - e.g. kilograms')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'abbreviation for the unit')),
        tr(' - e.g. kg')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'the default allocation for the resource')),
        tr(' - e.g. 2.8. This number can be overridden on a '
           'per-analysis basis')))
    bullets.add(m.Text(
        m.ImportantText(tr(
            'minimum allowed which is used to prevent allocating')),
        tr(' - e.g. no drinking water to displaced persons')))
    bullets.add(m.ImportantText(tr(
        'maximum allowed which is used to set a sensible upper '
        'limit for the resource')))
    bullets.add(m.ImportantText(tr(
        'a readable sentence which is used to compile the '
        'sentence describing the resource in reports.')))
    message.add(bullets)

    message.add(m.Paragraph(tr(
        'These parameters are probably all fairly self explanatory, but '
        'the readable sentence probably needs further detail. The '
        'sentence is compiled using a simple keyword token replacement '
        'system. The following tokens can be used:')))

    bullets = m.BulletedList()
    bullets.add(m.Text('{{ Default }}'))
    bullets.add(m.Text('{{ Unit }}'))
    bullets.add(m.Text('{{ Units }}'))
    bullets.add(m.Text('{{ Unit abbreviation }}'))
    bullets.add(m.Text('{{ Resource name }}'))
    bullets.add(m.Text('{{ Frequency }}'))
    bullets.add(m.Text('{{ Minimum allowed }}'))
    bullets.add(m.Text('{{ Maximum allowed }}'))
    message.add(bullets)

    message.add(m.Paragraph(tr(
        'When the token is placed in the sentence it will be replaced with '
        'the actual value at report generation time. This contrived example '
        'shows a tokenised sentence that includes all possible keywords:'
    )))

    message.add(m.EmphasizedText(tr(
        'A displaced person should be provided with {{ %s }} '
        '{{ %s }}/{{ %s }}/{{ %s }} of {{ %s }}. Though no less than {{ %s }} '
        'and no more than {{ %s }}. This should be provided {{ %s }}.' % (
            'Default',
            'Unit',
            'Units',
            'Unit abbreviation',
            'Resource name',
            'Minimum allowed',
            'Maximum allowed',
            'Frequency'
        )
    )))
    message.add(m.Paragraph(tr(
        'Would generate a human readable sentence like this:')))

    message.add(m.ImportantText(tr(
        'A displaced person should be provided with 2.8 kilogram/kilograms/kg '
        'of rice. Though no less than 0 and no more than 100. This should '
        'be provided daily.'
    )))
    message.add(m.Paragraph(tr(
        'Once you have populated the resource elements, click the Save '
        'resource button to return to the profile view. You will see the '
        'new resource added in the profile\'s resource list.'
    )))

    message.add(m.Heading(tr('Managing profiles'), **INFO_STYLE))
    message.add(m.Paragraph(tr(
        'In addition to the profiles that come as standard with InaSAFE, you '
        'can create new ones, either from scratch, or based on an existing '
        'one (which you can then modify).'
    )))
    message.add(m.Paragraph(tr(
        'Use the New button to create new profile. When prompted, give your '
        'profile a name e.g. \'JakartaProfile\'.'
    )))
    message.add(m.Paragraph(tr(
        'Note: The profile must be saved in your home directory under '
        '.qgis2/minimum_needs in order for InaSAFE to successfully detect it.'
    )))
    message.add(m.Paragraph(tr(
        'An alternative way to create a new profile is to use the Save as to '
        'clone an existing profile. The clone profile can then be edited '
        'according to your specific needs.'
    )))
    message.add(m.Heading(tr('Active profile'), **INFO_STYLE))
    message.add(m.Paragraph(tr(
        'It is important to note, that which ever profile you select in the '
        'Profile pick list, will be considered active and will be used as '
        'the basis for all minimum needs analysis. You need to restart '
        'QGIS before the changed profile become active.'
    )))
    return message
