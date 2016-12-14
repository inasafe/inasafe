"""
raven.scripts.runner
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import
from __future__ import print_function

import logging
import os
import sys
import pwd
import simplejson as json
from optparse import OptionParser

from raven import Client


def store_json(option, opt_str, value, parser):
    try:
        value = json.loads(value)
    except ValueError:
        # fix_print_with_import
        print("Invalid JSON was used for option %s.  Received: %s" % (opt_str, value))
        sys.exit(1)
    setattr(parser.values, option.dest, value)


def main():
    root = logging.getLogger('sentry.errors')
    root.setLevel(logging.DEBUG)
    root.addHandler(logging.StreamHandler())

    parser = OptionParser()
    parser.add_option("--data", action="callback", callback=store_json,
                      type="string", nargs=1, dest="data")
    (opts, args) = parser.parse_args()

    dsn = ' '.join(args[1:]) or os.environ.get('SENTRY_DSN')
    if not dsn:
        # fix_print_with_import
        print("Error: No configuration detected!")
        # fix_print_with_import
        print("You must either pass a DSN to the command, or set the SENTRY_DSN environment variable.")
        sys.exit(1)

    # fix_print_with_import
    print("Using DSN configuration:")
    # fix_print_with_import
    print(" ", dsn)
    print()

    client = Client(dsn, include_paths=['raven'])

    # fix_print_with_import
    print("Client configuration:")
    for k in ('servers', 'project', 'public_key', 'secret_key'):
        # fix_print_with_import
        print('  %-15s: %s' % (k, getattr(client, k)))
    print()

    if not all([client.servers, client.project, client.public_key, client.secret_key]):
        # fix_print_with_import
        print("Error: All values must be set!")
        sys.exit(1)

    # fix_print_with_import
    print('Sending a test message...', end=' ')
    ident = client.get_ident(client.captureMessage(
        message='This is a test message generated using ``raven test``',
        data=opts.data or {
            'culprit': 'raven.scripts.runner',
            'logger': 'raven.test',
            'sentry.interfaces.Http': {
                'method': 'GET',
                'url': 'http://example.com',
            }
        },
        level=logging.INFO,
        stack=True,
        extra={
            'user': pwd.getpwuid(os.geteuid())[0],
            'loadavg': os.getloadavg(),
        }
    ))

    if client.state.did_fail():
        # fix_print_with_import
        print('error!')
        return False

    # fix_print_with_import
    print('success!')
    print()
    # fix_print_with_import
    print('The test message can be viewed at the following URL:')
    url = client.servers[0].split('/api/store/', 1)[0]
    # fix_print_with_import
    print('  %s/%s/search/?q=%s' % (url, client.project, ident))
