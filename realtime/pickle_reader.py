# coding=utf-8
"""The implementation of pickle reader."""

import os
import sys
from glob import glob
#noinspection PyPep8Naming
import cPickle as pickle


def create_index(shakemap_dir, locale):
    """Pass dictionary from pickle to index.html.

    :param shakemap_dir: Directory containing pickle shakemap metadata. For
     real use based on current environment, this would be a published directory
     either public/en or public/id.
    :type shakemap_dir: str

    :param locale: Language of output index.html. id = Bahasa, en = English
    :type locale: str

    :return: Path to index file.
    :rtype: str
    """
    registered_locales = ['en', 'id']
    clean_locale = locale.lower()
    if clean_locale not in registered_locales:
        raise Exception(
            'Locale ID other than id and en is not supported!')

    localed_pickle_path = '*%s.pickle' % clean_locale
    localed_header_path = 'header-%s.html' % clean_locale
    localed_footer_path = 'footer-%s.html' % clean_locale
    path_list = glob(os.path.join(shakemap_dir, localed_pickle_path))

    header_html_file_path = os.path.join(os.path.dirname(__file__),
                                         'fixtures',
                                         'web',
                                         'resource',
                                         localed_header_path)
    footer_html_file_path = os.path.join(os.path.dirname(__file__),
                                         'fixtures',
                                         'web',
                                         'resource',
                                         localed_footer_path)

    # Check if index_path is exist. Remove if it's exist
    index_path = os.path.join(shakemap_dir, 'index.html')
    if os.path.exists(index_path):
        os.remove(index_path)

    # Sort based on name, which based on the date descending and keep 10 latest
    path_list.sort()
    path_list = path_list[:10]

    # Prepare header of the html file
    header_html_file = open(header_html_file_path)
    header_html = header_html_file.read()
    header_html_file.close()

    # Prepare footer of the html file
    footer_html_file = open(footer_html_file_path)
    footer_html = footer_html_file.read()
    footer_html_file.close()

    # Generate Table HTML for all of the pickle_path
    table_html = ('\t<table class="table" id="earthquake_table">\n'
                  '\t\t<thead>'
                  '\n\t\t\t<tr>'
                  '\n\t\t\t\t<th>Max MMI</th>'
                  '\n\t\t\t\t<th>Date and Time</th>'
                  '\n\t\t\t\t<th>Location</th>'
                  '\n\t\t\t\t<th>Magnitude</th>'
                  '\n\t\t\t\t<th>Depth</th>'
                  '\n\t\t\t\t<th>Report Detail</th>'
                  '\n\t\t\t</tr>'
                  '\n\t\t</thead>'
                  '\n\t\t<tbody>\n')

    for pickle_path in path_list:
        pickle_file = file(pickle_path, 'rb')
        metadata = pickle.load(pickle_file)
        print metadata
        pickle_filename = os.path.basename(pickle_path)
        report_path = pickle_filename.split('-')[0] + '-' + locale
        report_path_pdf_link = '<a href="%s">%s</a>' % (report_path + '.pdf',
                                                        'PDF')
        report_path_png_link = '<a href="%s">%s</a>' % (report_path + '.png',
                                                        'PNG')
        mmi_class = '7'  # TODO: MMI Classification
        table_html += (
            '\t\t\t<tr>'
            '\n\t\t\t\t<td><div class="mmi-%s">%s</div></td>'
            '\n\t\t\t\t<td>%s</td>'
            '\n\t\t\t\t<td><p class="location-info"><em>%s</em></p>%s</td>'
            '\n\t\t\t\t<td><div class="center">%s</div></td>'
            '\n\t\t\t\t<td><div class="center">%s %s</div></td>'
            '\n\t\t\t\t<td>%s | %s</td>'
            '\n\t\t\t</tr>\n' % (
                mmi_class,
                mmi_class,
                metadata['formatted-date-time'],
                format(metadata['location-info']).encode('utf-8'),
                metadata['place-name'].upper(),
                metadata['mmi'],
                metadata['depth-value'],
                format(metadata['depth-unit']).encode('utf-8'),
                report_path_pdf_link,
                report_path_png_link))

    table_html += ('\t\t</tbody>'
                   '\n\t</table>')

    index_file = file(index_path, 'w')
    index_file.write(header_html + table_html + footer_html)
    index_file.close()
    return index_path


def generate_pages(shakemap_dir_en, shakemap_dir_id):
    """Generate index.html, currently for both en and id and return the path to
    them.

    :param shakemap_dir_en: Shakemap directory for en locale where pickles are
     located. For real use based on current environment, this would be a
     published directory public/en
    :type shakemap_dir_en: str

    :param shakemap_dir_id: Shakemap directory for id locale where pickles are
     located. For real use based on current environment, this would be a
     published directory public/id
    :type shakemap_dir_id: str

    :returns: en_index_path, id_index_path
    :rtype: str, str
    """
    en_index_path = create_index(shakemap_dir_en, 'en')
    id_index_path = create_index(shakemap_dir_id, 'id')

    return en_index_path, id_index_path


if __name__ == '__main__':
    # Checking argument which has been given is valid
    if len(sys.argv) > 2:
        print 'To use: python pickle_reader.py <shakemap_directory>'
        print 'The shakemap directory should contain one or more pickle files.'
    elif len(sys.argv) == 2:
        en_path, id_path = generate_pages(sys.argv[1], sys.argv[2])
        print 'en_index is generated and saved in: %s' % en_path
        print 'id_index is generated and saved in: %s' % id_path
        exit()
