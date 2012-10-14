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

    files = {'QT': '%s/safe_qgis/i18n/inasafe_%s.ts',
             'GT': '%s/safe/i18n/%s/LC_MESSAGES/inasafe.po'}

    commands = {'QT': 'lrelease %s',
                'GT': 'msgfmt --statistics %s'}

    for locale in locales:

        for key in files:
            filename = files[key] % (root, locale)
            cmd = commands[key] % filename
            # messages.mo is generated when called Popen
            p = Popen(cmd, shell=True,
                      stdin=PIPE, stdout=PIPE, stderr=PIPE)

            msg = '%s[%s]: ' % (key, locale)
            status = 'Unknown'

            lines = []
            if key == 'GT' and p.stderr is not None:
                lines = p.stderr.readlines()

            if key == 'QT' and p.stdout is not None:
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

            #print 'untranslated', untranslated
            if missing == 0:
                status = 'OK'
            else:
                status = '%i missing' % missing
                status += ' - please edit %s' % filename

            if status != 'OK':
                msg += status
                print msg

    # Deleted messages.mo generated file, not so good approach actually
    fname = root + '/messages.mo'
    if os.path.isfile(fname):
        os.remove(fname)
