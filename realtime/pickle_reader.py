# coding=utf-8
"""The implementation of pickle reader."""

import os
import sys
from glob import glob
#noinspection PyPep8Naming
import cPickle as pickle


def create_index(shakemap_dir):
    """Pass dictionary from pickle to index.html.

    :param shakemap_dir: Directory containing pickle shakemap metadata.
    :type shakemap_dir: str

    :returns: Path to index file.
    :rtype: str
    """
    index_path = os.path.join(shakemap_dir, 'index.html')
    if os.path.exists(index_path):
        os.remove(index_path)

    path_list = glob(os.path.join(shakemap_dir, '*.pickle'))
    path_list.reverse()

    header_html_file = open(os.path.join(os.path.dirname(__file__),
                                         'fixtures',
                                         'header.html'), 'r')

    header_html = header_html_file.read()
    header_html_file.close()

    footer_html_file = open(os.path.join(os.path.dirname(__file__),
                                         'fixtures',
                                         'footer.html'), 'r')
    footer_html = footer_html_file.read()
    footer_html_file.close()
    
    table_html = '\t<table class="table table-bordered table-hover ' \
                 'table-condensed">\n'
    table_html += '\t\t<thead> ' \
                  '\n\t\t\t<tr> ' \
                  '\n\t\t\t\t<th>Max MMI</th> ' \
                  '\n\t\t\t\t<th>Time</th> ' \
                  '\n\t\t\t\t<th>Location</th>' \
                  '\n\t\t\t\t<th>Magnitude</th> ' \
                  '\n\t\t\t\t<th>Report</th> ' \
                  '\n\t\t\t</tr> ' \
                  '\n\t</thead> ' \
                  '\n\t<tbody>\n'

    for pickle_path in path_list:
        pickle_file = file(pickle_path, 'rb')
        metadata = pickle.load(pickle_file)
        mmi_class = 'mmi-2'  # FIXME
        table_html += '\t\t<tr>' \
                      '\n\t\t\t<td class="%s">%s</td>' \
                      '\n\t\t\t<td>%s</td>' \
                      '\n\t\t\t<td>%s</td>' \
                      '\n\t\t\t<td>%s</td>' \
                      '\n\t\t\t<td>%s</td>' \
                      '\n\t\t</tr>\n' % (
                          mmi_class,
                          metadata['mmi'],
                          metadata['formatted-date-time'],
                          metadata['place-name'],
                          metadata['mmi'],
                          metadata['place-name'])
    table_html += '\t</tbody> \n</table>'

    index_file = file(index_path, 'wt')
    index_file.write(header_html + table_html + footer_html)
    index_file.close()
    return index_path


if __name__ == '__main__':
    # Checking argument which has been given is valid
    if len(sys.argv) > 2:
        print 'To use: python pickle_reader.py <shakemap_directory>'
        print 'The shakemap directory should contain one or more pickle files.'
    elif len(sys.argv) == 2:
        create_index(sys.argv[1])
        exit()
