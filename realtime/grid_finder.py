# coding=utf-8
# Walk through a directory heirarchy finding grid.xml files
# and copy them into a single dir renaming them after their
# parent directory

from __future__ import print_function
from os import walk
from shutil import copyfile
from os import path

source = '/Users/timlinux/dev/python/inasafe/safe/test/data/hazard'
destination = '/tmp'

for dirpath, dirnames, filenames in walk(source):
    for filename in filenames:
        if filename == 'grid.xml':
            shake_id = path.basename(path.split(dirpath)[-2])
            # fix_print_with_import
            print('found grid for %s' % shake_id)
            copyfile(
                path.join(dirpath, filename),
                path.join(destination, '%s.xml' % shake_id))
