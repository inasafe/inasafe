# coding=utf-8
"""Report missing translations for given locales."""

import os
import sys
from subprocess import Popen, PIPE


if __name__ == '__main__':
    if len(sys.argv) < 3:
        message = (
            'One or more locales must be specified: \n'
            'E.g. python missing_translations.py <rootdir> id')
        raise Exception(message)

    root = sys.argv[1]

    if not os.path.isdir(root):
        message = (
            'Root dir must be specified as first argument. I got %s' % root)
        raise Exception(message)

    locales = sys.argv[2:]

    for locale in locales:
        relative_path = os.path.join('safe', 'i18n', 'inasafe_%s.ts' % locale)
        absolute_path = os.path.join(root, relative_path)
        command = 'lrelease %s' % absolute_path

        # messages.mo is generated when called Popen
        p = Popen(
            command,
            shell=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE)

        message = '%s[%s]: ' % ('QT', locale)
        status = 'Unknown'

        lines = []

        if p.stdout is not None:
            lines = p.stdout.readlines()

        missing = 0
        for line in lines:
            if 'untranslated' in line:
                fields = line.split()
                i = fields.index('untranslated')
                missing += int(fields[i - 1])

            if 'unfinished' in line:
                fields = line.strip().split()
                i = fields.index('unfinished)')
                missing += int(fields[i - 1])

        if missing == 0:
            status = 'OK'
        else:
            status = '%i missing' % missing
            status += ' - please edit %s' % relative_path

        message += status
        print(message)
