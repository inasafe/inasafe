"""Report missing translations for given locales
"""

import os
import sys
from subprocess import Popen, PIPE

if __name__ == '__main__':
    if len(sys.argv) < 3:
        msg = ('One or more locales must be specified: '
               'E.g. python missing_translations.py <rootdir> id')
        raise Exception(msg)

    root = sys.argv[1]

    if not os.path.isdir(root):
        msg = ('Root dir must be specified as first argument. I got '
               '%s' % root)
        raise Exception(msg)

    locales = sys.argv[2:]

    commands = {'QT': 'lrelease %s/gui/i18n/inasafe_%s.ts',
                'GT': 'msgfmt --statistics %s/i18n/%s/LC_MESSAGES/inasafe.po'}

    for locale in locales:

        for key in commands:
            cmd = commands[key] % (root, locale)
            p = Popen(cmd, shell=True,
                      stdin=PIPE, stdout=PIPE, stderr=PIPE)

            msg = '%s[%s]: ' % (key, locale)
            status = 'Unknown'

            lines = []
            if key == 'GT' and p.stderr is not None:
                lines = p.stderr.readlines()

            if key == 'QT' and p.stdout is not None:
                lines = p.stdout.readlines()

            for line in lines:
                if 'untranslated' in line:
                    fields = line.split()
                    i = fields.index('untranslated')
                    untranslated = int(fields[i - 1])
                    if untranslated == 0:
                        status = 'OK'
                    else:
                        status = '%i untranslated' % untranslated

            if status != 'OK':
                msg += status
                print msg


