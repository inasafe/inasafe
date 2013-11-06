# coding=utf-8
"""The implementation of pickle reader."""

import os
import shutil
import sys
from glob import glob
#noinspection PyPep8Naming
import cPickle as pickle
import logging


def create_index(shakemap_dir, locale):
    """Pass dictionary from pickle to index.html.

    :param shakemap_dir: Directory containing pickle shakemap metadata.
    :type shakemap_dir: str

    :returns: Path to index file.
    :rtype: str

    :param locale: Language of output index.html. id = Bahasa, en = English
    :type locale: str
    """
    if locale == 'en':
        index_path = os.path.join(shakemap_dir, 'index-en.html')
        path_list = glob(os.path.join(shakemap_dir, '*en.pickle'))
        header_html_file_path = os.path.join(os.path.dirname(__file__),
                                             'fixtures',
                                             'web',
                                             'resource',
                                             'header.html')

    elif locale == 'id':
        index_path = os.path.join(shakemap_dir, 'index-id.html')
        path_list = glob(os.path.join(shakemap_dir, '*id.pickle'))
        header_html_file_path = os.path.join(os.path.dirname(__file__),
                                             'fixtures',
                                             'web',
                                             'resource',
                                             'header-id.html')
    else:
        raise logging.exception(
            'Locale ID other than id and en is not supported!')
    # Check if index_path is exist. Remove if it's exist
    if os.path.exists(index_path):
        os.remove(index_path)
    path_list.reverse()

    # Prepare header of the html file
    header_html_file = open(header_html_file_path)
    header_html = header_html_file.read()
    header_html_file.close()

    # Prepare footer of the html file
    footer_html_file = open(os.path.join(os.path.dirname(__file__),
                                         'fixtures',
                                         'web',
                                         'resource',
                                         'footer.html'), 'r')
    footer_html = footer_html_file.read()
    footer_html_file.close()

    # Generate Table HTML for all of the pickle_path
    table_html = ('\t'
                  '<table class="table table-bordered table-hover>\n'
                  '\t\t<thead>'
                  '\n\t\t\t<tr>'
                  '\n\t\t\t\t<th>Max MMI</th>'
                  '\n\t\t\t\t<th>Time</th>'
                  '\n\t\t\t\t<th>Location</th>'
                  '\n\t\t\t\t<th>Magnitude</th>'
                  '\n\t\t\t\t<th>Report</th>'
                  '\n\t\t\t</tr>'
                  '\n\t</thead>'
                  '\n\t<tbody>\n')

    for pickle_path in path_list:
        pickle_file = file(pickle_path, 'rb')
        metadata = pickle.load(pickle_file)
        mmi_class = 'mmi-2'  # TODO
        table_html += ('\t\t<tr>'
                       '\n\t\t\t<td class="%s">%s</td>'
                       '\n\t\t\t<td>%s</td>'
                       '\n\t\t\t<td>%s</td>'
                       '\n\t\t\t<td>%s</td>'
                       '\n\t\t\t<td>%s</td>'
                       '\n\t\t</tr>\n' % (mmi_class,
                                          metadata['mmi'],
                                          metadata['formatted-date-time'],
                                          metadata['place-name'],
                                          metadata['mmi'],
                                          metadata['place-name']))
    table_html += ('\t</tbody> \n</table>')

    index_file = file(index_path, 'wt')
    index_file.write(header_html + table_html + footer_html)
    index_file.close()
    return index_path


def generate_pages(shakemap_dir):
    """Generate index.html for en and id and return the path to them.

    :param shakemap_dir: Shakemap directory where pickles are located.
    :type shakemap_dir: str

    :returns: en_index_path, id_index_path
    :rtype: str, str
    """
    en_index_path = create_index(shakemap_dir, 'en')
    id_index_path = create_index(shakemap_dir, 'id')

    return en_index_path, id_index_path


def publish_pages(shakemap_dir):
    """Publish index.html to both en/index.html and id/index.html.

    :param shakemap_dir:Shakemap directory where pickles are located
    """
    en_index_path, id_index_path = generate_pages(shakemap_dir)

    # Move to /home/web/quake/public/
    # public_dir = '/home/web/quake/public/'
    testdir = os.path.join(os.path.dirname(__file__),
                           os.pardir,
                           'realtime',
                           'fixtures',
                           'tests')
    shutil.move(en_index_path, os.path.join(testdir, 'index-en.html'))
    shutil.move(id_index_path, os.path.join(testdir, 'index-id.html'))


if __name__ == '__main__':
    # Checking argument which has been given is valid
    if len(sys.argv) > 2:
        print 'To use: python pickle_reader.py <shakemap_directory>'
        print 'The shakemap directory should contain one or more pickle files.'
    elif len(sys.argv) == 2:
        publish_pages(sys.argv[1])
        exit()
