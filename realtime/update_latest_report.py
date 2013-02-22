"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Script for pushing new earthquake impact report**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'imajimatika@gmail.com'
__version__ = '0.5.0'
__date__ = '21/02/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import shutil
import sys
from utils import is_event_id
import logging

# The logger is intialised in utils.py by init
LOGGER = logging.getLogger('InaSAFE')
try:
    earth_quake_source_path = os.environ['EQ_SOURCE_PATH']
    earth_quake_public_path = os.environ['EQ_PUBLIC_PATH']
except KeyError:
    LOGGER.exception('QUAKE_SERVER_PASSWORD not set!')
    sys.exit()


def get_list_dir(path_dir, filter_function=None):
    """Return list of file or directory in path_dir
        with filter function filter_function.
    """
    list_dir = os.listdir(path_dir)
    print 'list_dir', len(list_dir)
    if filter_function is None:
        return list_dir
    retval = []
    for my_dir in list_dir:
        if filter_function(my_dir):
            retval.append(my_dir)
    return retval


def get_event_id(report_filename):
    """Custom function to return event id from a filename
    Thi is for filename format like:
    earthquake_impact_map_20120216181705.pdf
    """
    return report_filename[-18:-4]


def filter_eq_map(eq_map_path):
    """Return true if eq_map_path in the following format:
        eartquake_impact_map_YYYYBBDDhhmmss.pdf
        for example : earthquake_impact_map_20120216181705.pdf
    """
    # my_regex = r'earthquake\_impact\_map\_[0-9]{14}\.pdf'
    expected_len = len('earthquake_impact_map_20120216181705.pdf')
    if len(eq_map_path) != expected_len:
        return False
    print 'eq', eq_map_path
#    if not re.match(eq_map_path, my_regex):
#        print 're'
#        return False
    my_event_id = get_event_id(eq_map_path)
    print 'my_event_id', my_event_id
    if is_event_id(my_event_id):
        return True
    else:
        print 'not event id'
        return False


def sort_event(my_events):
    """Sort list of event id my_event as list ascending
    """
    try:
        sorted_events = sorted([int(x) for x in my_events])
        return sorted_events
    except ValueError as e:
        raise e


def get_last_event_id(my_events):
    """Return last event id of my_events.
    """
    sorted_events = sort_event(my_events)[-1]
    return sorted_events


def update_report(my_source_path, my_public_path, last_event_id):
    """Copy latest report to my_public_path and make a copy with
    a latest_earthquake_impact_map.pdf and latest_earthquake_impact_map.png
    """
    last_event_id = str(last_event_id)

    source_dir = os.path.join(my_source_path, last_event_id)
    report_filename = last_event_id + '-id'
    pdf_file = report_filename + '.pdf'
    pdf_path = os.path.join(source_dir, pdf_file)
    png_path = pdf_path.replace('.pdf', '.png')

    public_pdf_file = 'earthquake_impact_map_' + last_event_id + '.pdf'
    public_pdf_path = os.path.join(my_public_path, public_pdf_file)
    latest_pdf_path = os.path.join(my_public_path,
                                   'latest_earthquake_impact_map.pdf')
    latest_png_path = os.path.join(my_public_path,
                                   'latest_earthquake_impact_map.png')

    # copy file
    shutil.copy2(pdf_path, public_pdf_path)
    print 'copied to ' + public_pdf_path
    shutil.copy2(pdf_path, latest_pdf_path)
    print 'copied to ' + latest_pdf_path
    shutil.copy2(png_path, latest_png_path)
    print 'copied to ' + latest_png_path


def main():
    """The implementation
    """
    source_path = earth_quake_source_path
    public_path = earth_quake_public_path

    source_files = get_list_dir(source_path, is_event_id)
    source_events = source_files
    last_source = get_last_event_id(source_events)

    public_files = get_list_dir(public_path, filter_eq_map)
    print ' public_files', public_files
    public_events = [get_event_id(x) for x in public_files]
    print 'public_events', public_events
    last_public = get_last_event_id(public_events)

    if last_source > last_public:
        last_event_id = last_source
        print 'There is new eq impact map.'
        # do_something_here()
        update_report(source_path, public_path, last_event_id)
    else:
        print 'Not new eq impact, everything is safe.'

if __name__ == '__main__':
    main()
