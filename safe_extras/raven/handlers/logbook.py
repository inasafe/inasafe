"""
raven.handlers.logbook
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import
from __future__ import print_function

import logbook
import sys
import traceback

from raven.base import Client
from raven.utils.encoding import to_string


class SentryHandler(logbook.Handler):
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, str):
                self.client = kwargs.pop('client_cls', Client)(dsn=arg)
            elif isinstance(arg, Client):
                self.client = arg
            else:
                raise ValueError('The first argument to %s must be either a Client instance or a DSN, got %r instead.' % (
                    self.__class__.__name__,
                    arg,
                ))
            args = []
        else:
            try:
                self.client = kwargs.pop('client')
            except KeyError:
                raise TypeError('Expected keyword argument for SentryHandler: client')
        super(SentryHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        try:
            self.format(record)

            # Avoid typical config issues by overriding loggers behavior
            if record.channel.startswith('sentry.errors'):
                # fix_print_with_import
                print(to_string(record.message), file=sys.stderr)
                return

            return self._emit(record)
        except Exception:
            # fix_print_with_import
            print("Top level Sentry exception caught - failed creating log record", file=sys.stderr)
            # fix_print_with_import
            print(to_string(record.msg), file=sys.stderr)
            # fix_print_with_import
            print(to_string(traceback.format_exc()), file=sys.stderr)

            try:
                self.client.capture('Exception')
            except Exception:
                pass

    def _emit(self, record):
        data = {
            'level': record.level,
            'logger': record.channel,
        }

        # If there's no exception being processed, exc_info may be a 3-tuple of None
        # http://docs.python.org/library/sys.html#sys.exc_info
        if record.exc_info is True or (record.exc_info and all(record.exc_info)):
            handler = self.client.get_handler('raven.events.Exception')

            data.update(handler.capture(exc_info=record.exc_info))

        return self.client.capture('Message',
            message=record.msg,
            params=record.args,
            data=data,
            extra=record.extra,
        )
