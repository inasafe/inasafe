"""
InaSAFE Disaster risk assessment tool by AusAid - **Error Message example.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""


__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '27/05/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import traceback

from safe.messaging import (
    Message,
    ErrorMessage,
    ImportantText,
    Paragraph)

DYNAMIC_MESSAGE_SIGNAL = 'ImpactFunctionMessage'


class SafeError(Exception):

    """Base class for all SAFE messages that propogates ErrorMessages."""

    def __init__(self, message, error_message=None):
        # print traceback.format_exc()
        Exception.__init__(self, message)

        if error_message is not None:
            self.error_message = error_message
        else:
            self.error_message = ErrorMessage(
                message.message, traceback=traceback.format_exc())


def error_creator1():
    """Simple function that will create an error."""
    raise IOError('File could not be read.')


def error_creator2():
    """Simple function that will extend an error and its traceback."""
    try:
        error_creator1()
    except IOError as e1:
        e1.args = (e1.args[0] + '\nCreator 2 error',)  # Tuple dont remove ,
        raise


def error_creator3():
    """Raise a safe style error."""
    try:
        error_creator2()
    except IOError as e2:
        # e2.args = (e2.args[0] + '\nCreator 3 error',)  # Tuple dont remove ,
        raise SafeError(e2)


def error_creator4():
    """Raise a safe style error."""
    try:
        error_creator3()
    except SafeError as e3:
        e3.error_message.problems.append('Creator 4 error')
        raise


def error_creator5():
    """Raise a safe style error and append a full message."""
    try:
        error_creator4()
    except SafeError as e4:
        message = ErrorMessage(
            'Creator 5 problem',
            detail=Message(
                Paragraph('Could not', ImportantText('call'), 'function.'),
                Paragraph('Try reinstalling your computer with windows.')),
            suggestion=Message(ImportantText('Important note')))
        e4.error_message.append(message)
        raise


if __name__ == '__main__':
    # best practice non safe style errors
    # try:
    #    error_creator2()
    # except IOError, e:
    #    # print e
    #    tb = traceback.format_exc()
    #    print tb

    # Safe style errors
    try:
        error_creator5()
    except SafeError as e:
        # print e
        # tb = traceback.format_exc()
        # print tb
        print((e.error_message.to_text()))
