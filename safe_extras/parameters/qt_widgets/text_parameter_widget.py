# coding=utf-8
"""Docstring for this file."""
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'string_parameter_widget'
__date__ = '8/28/14'
__copyright__ = 'ismail@kartoza.com'
__doc__ = ''


from PyQt4.QtGui import QTextEdit, QSizePolicy

from qt_widgets.generic_parameter_widget import GenericParameterWidget


class TextParameterWidget(GenericParameterWidget):
    """Widget class for string parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 2.2

        :param parameter: A StringParameter object.
        :type parameter: StringParameter

        """
        super(TextParameterWidget, self).__init__(parameter, parent)

        self._line_edit_input = QTextEdit()
        self._line_edit_input.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Minimum)
        # Tooltips
        self.setToolTip('Write the value for %s here ' % self._parameter.name)
        self._line_edit_input.setText(self._parameter.value)

        self._inner_input_layout.addWidget(self._line_edit_input)

    def get_parameter(self):
        """Obtain string parameter object from the current widget state.

        :returns: A StringParameter from the current state of widget
        """
        value = self._line_edit_input.toPlainText()
        if value.__class__.__name__ == 'QString':
            value = str(value)
        self._parameter.value = value
        return self._parameter

    def set_text(self, text):
        """Update the text of the widget

        :param text: The new text
        :type text: str
        """
        self._line_edit_input.setText(text)
