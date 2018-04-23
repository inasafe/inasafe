# coding=utf-8
"""Resource Parameter Widget."""

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA
# noinspection PyPackageRequirements
from qgis.PyQt.QtWidgets import QLabel

from parameters.qt_widgets.float_parameter_widget import FloatParameterWidget

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


# pylint: disable=super-on-old-class
class ResourceParameterWidget(FloatParameterWidget):

    """Widget class for Resource parameter."""

    # pylint: disable=super-on-old-class
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 2.3

        :param parameter: A ResourceParameter object.
        :type parameter: ResourceParameter, FloatParameter
        """
        # pylint: disable=E1002
        super(ResourceParameterWidget, self).__init__(parameter, parent)
        # pylint: enable=E1002
        self.set_unit()

    def get_parameter(self):
        """Obtain the parameter object from the current widget state.

        :returns: A BooleanParameter from the current state of widget
        """
        self._parameter.value = self._input.value()
        return self._parameter

    def set_unit(self):
        """Set the units label. (Include the frequency.)"""
        label = ''
        if self._parameter.frequency:
            label = self._parameter.frequency
        if self._parameter.unit.plural:
            label = '%s %s' % (self._parameter.unit.plural, label)
        elif self._parameter.unit.name:
            label = '%s %s' % (self._parameter.unit.name, label)
        self._unit_widget = QLabel(label)
        if self._parameter.unit.help_text:
            self._unit_widget.setToolTip(self._parameter.unit.help_text)

# pylint: enable=super-on-old-class
