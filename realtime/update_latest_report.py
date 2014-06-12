# coding=utf-8
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
from utilities import is_event_id
import logging

from realtime.utilities import realtime_logger_name

# The logger is initialized in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


def get_directory_listing(directory_path, filter_function=None):
    """Return list of file or directory in directory_path.

    If filter_function is not None, it will be used as filter.

    :param directory_path: Directory path.
    :type directory_path: str

    :param filter_function: Function for filtering.
    :type filter_function: function

    :returns: List of files and directory in the directory path.
    :rtype: list
    """
    directories = os.listdir(directory_path)
    if filter_function is None:
        return directories
    filtered_directory = []
    for directory in directories:
        if filter_function(directory):
            filtered_directory.append(directory)
    return filtered_directory


def get_event_id(report_filename):
    """Custom function to return event id from a filename

    The filename format like:
    earthquake_impact_map_20120216181705.pdf

    Will give : 20120216181705

    :param report_filename: Filename of a report.
    :type report_filename: str

    :returns: Event id based on filename.
    :rtype: str
    """
    return report_filename[-18:-4]


def earthquake_event_zip_filter(zip_eq_event):
    """Return true if zip_eq_event in the following format:

    YYYYBBDDhhmmss.out.zip
    for example : 20130226211002.out.zip

    :param zip_eq_event: Filename of zip.
    :type zip_eq_event: str

    :returns: True if it's a valid format.
    :rtype: bool
    """
    expected_length = len('20130226211002.out.zip')
    if len(zip_eq_event) != expected_length:
        return False
    event_id = zip_eq_event[:14]
    if is_event_id(event_id):
        return True
    else:
        return False


def earthquake_map_filter(earthquake_map_path):
    """Return true if earthquake_map_path in correct format.

    Correct format : earthquake_impact_map_YYYYBBDDhhmmss.pdf
    For example : earthquake_impact_map_20120216181705.pdf

    :param earthquake_map_path: A string represent name of the earthquake map.
    :type earthquake_map_path: str

    :returns: True if in correct format, otherwise false.
    :rtype: bool
    """
    expected_length = len('earthquake_impact_map_20120216181705.pdf')
    if len(earthquake_map_path) != expected_length:
        return False

    event_id = get_event_id(earthquake_map_path)
    if is_event_id(event_id):
        return True
    else:
        return False


def sort_event(events):
    """Sort list of event id as list ascending.

    :param events: List of event id.
    :type events: list

    :returns: Ascending sorted events.
    :rtype: list
    """
    try:
        sorted_events = sorted([int(x) for x in events])
        return sorted_events
    except ValueError as e:
        raise e


def get_last_event_id(events):
    """Return last event id of events.

    :param events: List of event id.
    :type events: list

    :returns: Last event id.
    :rtype: int
    """
    last_event_id = sort_event(events)[-1]
    return last_event_id


def update_report(source_path, public_path, last_event_id):
    """Copy latest report to public_path.

    Make a copy with a latest_earthquake_impact_map.pdf and
    latest_earthquake_impact_map.png


    :param source_path: Source path of report.
    :type source_path: str

    :param public_path: Public path to put the report.
    :type public_path: str

    :param last_event_id: Last event id of a earthquake.
    :type last_event_id: str, int
    """
    last_event_id = str(last_event_id)

    source_dir = os.path.join(source_path, last_event_id)
    report_filename = last_event_id + '-id'
    pdf_file = report_filename + '.pdf'
    pdf_path = os.path.join(source_dir, pdf_file)
    png_path = pdf_path.replace('.pdf', '.png')

    public_pdf_file = 'earthquake_impact_map_%s.pdf' % last_event_id
    public_pdf_path = os.path.join(public_path, public_pdf_file)
    latest_pdf_path = os.path.join(
        public_path, 'latest_earthquake_impact_map.pdf')
    latest_png_path = os.path.join(
        public_path, 'latest_earthquake_impact_map.png')

    # copy file
    shutil.copy2(png_path, latest_png_path)
    print 'copied to ' + latest_png_path
    shutil.copy2(pdf_path, latest_pdf_path)
    print 'copied to ' + latest_pdf_path
    shutil.copy2(pdf_path, public_pdf_path)
    print 'copied to ' + public_pdf_path


def main():
    """The implementation"""
    try:
        earth_quake_source_path = os.environ['EQ_SOURCE_PATH']
        earth_quake_public_path = os.environ['EQ_PUBLIC_PATH']
        earth_quake_guide_path = os.environ['EQ_GUIDE_PATH']
    except KeyError:
        LOGGER.exception('EQ_SOURCE_PATH or EQ_PUBLIC_PATH are not set!')
        sys.exit()

    source_path = earth_quake_source_path
    public_path = earth_quake_public_path
    # guide path is a path that has list of event id to be pushed on the
    # website. It's caused because there is a case where we don't want to
    # push all realtime earthquake report, but only the important one.
    # This path usually in the specific format and is used to get the latest
    # event id
    guide_path = earth_quake_guide_path

    guide_files = get_directory_listing(
        guide_path, earthquake_event_zip_filter)
    guide_events = [x[:14] for x in guide_files]
    last_guide = get_last_event_id(guide_events)

    public_files = get_directory_listing(public_path, earthquake_map_filter)
    print ' public_files', public_files
    public_events = [get_event_id(x) for x in public_files]
    print 'public_events', public_events
    last_public = get_last_event_id(public_events)

    if last_guide > last_public:
        last_event_id = last_guide
        print 'There is new eq impact map.'
        # do_something_here()
        update_report(source_path, public_path, last_event_id)
    else:
        print 'Not new eq impact, everything is safe.'

if __name__ == '__main__':
    main()
