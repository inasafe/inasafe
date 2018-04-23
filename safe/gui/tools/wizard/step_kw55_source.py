# coding=utf-8
"""InaSAFE Wizard Step Source."""

from safe import messaging as m
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.utilities.i18n import tr
from safe.utilities.str import get_unicode

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwSource(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Source."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)

        source_tooltip = self.tr(
            'Please record who is the custodian of this layer i.e. '
            'OpenStreetMap')
        self.lblSource.setToolTip(source_tooltip)
        self.leSource.setToolTip(source_tooltip)

        date_tooltip = self.tr(
            'When was this data collected or downloaded i.e. 1-May-2014')
        self.lblDate.setToolTip(date_tooltip)
        self.dtSource_date.setToolTip(date_tooltip)

        scale_tooltip = self.tr('What is the scale of this layer?')
        self.lblScale.setToolTip(scale_tooltip)
        self.leSource_scale.setToolTip(scale_tooltip)

        url_tooltip = self.tr(
            'Does the custodians have their own website '
            'i.e. www.openstreetmap.org')
        self.lblURL.setToolTip(url_tooltip)
        self.leSource_url.setToolTip(url_tooltip)

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        if subcategory and subcategory.get('extra_keywords'):
            new_step = self.parent.step_kw_extra_keywords
        else:
            new_step = self.parent.step_kw_title
        return new_step

    # noinspection PyPep8Naming
    def on_ckbSource_date_toggled(self, state):
        """This is an automatic Qt slot executed when the checkbox is toggled

        :param state: the new state
        :type state: boolean
        """
        self.dtSource_date.setEnabled(state)

    def set_widgets(self):
        """Set widgets on the Source tab."""
        # Just set values based on existing keywords
        source = self.parent.get_existing_keyword('source')
        if source or source == 0:
            self.leSource.setText(get_unicode(source))
        else:
            self.leSource.clear()

        source_scale = self.parent.get_existing_keyword('scale')
        if source_scale or source_scale == 0:
            self.leSource_scale.setText(get_unicode(source_scale))
        else:
            self.leSource_scale.clear()

        source_date = self.parent.get_existing_keyword('date')
        if source_date:
            self.ckbSource_date.setChecked(True)
            self.dtSource_date.setDateTime(source_date)
        else:
            self.ckbSource_date.setChecked(False)
            self.dtSource_date.clear()

        source_url = self.parent.get_existing_keyword('url')
        try:
            source_url = source_url.toString()
        except AttributeError:
            pass

        if source_url or source_url == 0:
            self.leSource_url.setText(get_unicode(source_url))
        else:
            self.leSource_url.clear()

        source_license = self.parent.get_existing_keyword('license')
        if source_license or source_license == 0:
            self.leSource_license.setText(get_unicode(source_license))
        else:
            self.leSource_license.clear()

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('InaSAFE Source Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will be able to '
            'set the source, url, scale, date, and license of this '
            'layer.').format(step_name=self.step_name)))
        return message
