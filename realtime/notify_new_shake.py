# coding=utf-8
"""This script will tell InaSAFE Realtime the newest shakemap available.

This script will be executed in .bash_logout script of realtime processor.
This will make the script executed after a user is pushing a shakemap.
"""
import sys
import re
import os
from datetime import datetime
from tzlocal import get_localzone
from realtime.push_shake import notify_realtime_rest

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '03/09/15'


if __name__ == '__main__':
    working_dir = sys.argv[1]

    shake_id = sys.argv[2]

    pattern = re.compile(r'^\d{14}$')
    # make sure it is a shake id folder (14 digit of folder name)
    if pattern.search(shake_id):
        # get time attribute
        info = os.stat(os.path.join(working_dir, shake_id))
        modified_time = datetime.fromtimestamp(info.st_mtime).replace(
            tzinfo=get_localzone())
        print 'Last shake pushed : ', str(modified_time)
        print 'Shake ID : ', shake_id
        notify_realtime_rest(modified_time)
