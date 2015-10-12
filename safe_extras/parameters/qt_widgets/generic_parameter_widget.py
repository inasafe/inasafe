# coding=utf-8
"""Docstring for this file."""
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'generic_parameter_widget'
__date__ = '8/21/14'
__copyright__ = 'ismail@kartoza.com'
__doc__ = ''

from PyQt4.QtGui import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QToolButton,
    QGridLayout,
    QSizePolicy)


class GenericParameterWidget(QWidget, object):
    """Widget class for generic parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 2.2

        :param parameter: A Generic object.
        :type parameter: GenericParameter

        """
        QWidget.__init__(self, parent)
        self._parameter = parameter

        # Create elements
        # Label (name)
        self._label = QLabel(self._parameter.name)

        # Label (help text)
        # Hacky fix for #1830 - checking the base type
        if isinstance(self._parameter.help_text, basestring):
            self._help_text_label = QLabel(self._parameter.help_text)
        else:
            self._help_text_label = QLabel()

        self._help_text_label.setWordWrap(True)

        # Label (description)
        self._description_label = QLabel(self._parameter.description)
        self._description_label.setWordWrap(True)
        self._description_label.hide()

        # Flag for show-status of description
        self._hide_description = True

        # Tool button for showing and hide detail description
        self._switch_button = QToolButton()
        self._switch_button.setArrowType(4)  # 2=down arrow, 4=right arrow
        # noinspection PyUnresolvedReferences
        self._switch_button.clicked.connect(self.show_hide_description)
        self._switch_button.setToolTip('Click for detail description')
        self._switch_button_stylesheet = 'border: none;'
        self._switch_button.setStyleSheet(self._switch_button_stylesheet)
        # Layouts
        self._main_layout = QVBoxLayout()
        self._input_layout = QHBoxLayout()
        self._help_layout = QGridLayout()
        # _inner_input_layout must be filled with widget in the child class
        self._inner_input_layout = QHBoxLayout()
        self._inner_help_layout = QVBoxLayout()

        # spacing
        self._main_layout.setSpacing(0)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._input_layout.setSpacing(0)
        self._input_layout.setContentsMargins(0, 0, 0, 0)
        self._help_layout.setSpacing(0)
        self._help_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_input_layout.setSpacing(7)
        self._inner_input_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_help_layout.setSpacing(0)
        self._inner_help_layout.setContentsMargins(0, 0, 0, 0)

        # Put elements into layouts
        self._input_layout.addWidget(self._label)
        self._input_layout.addLayout(self._inner_input_layout)
        # self._input_layout.addSpacing(100)

        if self._parameter.description:
            self._help_layout.addWidget(self._switch_button, 0, 0)
            self._help_layout.addWidget(self._description_label, 1, 1)
        if self._parameter.help_text:
            self._help_layout.addWidget(self._help_text_label, 0, 1)

        self._main_layout.addLayout(self._input_layout)
        self._main_layout.addLayout(self._help_layout)

        self.setLayout(self._main_layout)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

    def get_parameter(self):
        """Interface for returning parameter object.

        This must be implemented in child class.

        :raises: NotImplementedError

        """
        raise NotImplementedError('Must be implemented in child class')

    def show_hide_description(self):
        """Show and hide long description."""
        if self._hide_description:
            self._hide_description = False
            self._description_label.show()
            self._switch_button.setArrowType(2)
            self._switch_button.setToolTip('Click for hide detail description')
        else:
            self._hide_description = True
            self._description_label.hide()
            self._switch_button.setArrowType(4)
            self._switch_button.setToolTip('Click for detail description')
