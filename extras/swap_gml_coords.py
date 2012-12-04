"""Swap lat and lon in gml so that ogr can correctly understand it

It is assumed that the raw gml one-line has been converted to a proper format
xmllint --format <name>.gml > <pretty_name>.gml

Usage:

python swap_gml_coords.py <name>.gml
"""

import sys
import os

# Tags for lines where coordinates are to be replaced
position_tag = '<gml:posList>'
lc_tag = '<gml:lowerCorner>'
uc_tag = '<gml:upperCorner>'


def swap_pairs(line, starttag=position_tag):
    """Swap coordinate pairs

    Inputs
        line: gml line assumed to contain pairs of coordinates ordered as
              latitude, longitude
        starttag: tag marking the start of the coordinate pairs.
    """

    endtag = starttag.replace('<', '</')

    index = line.find(starttag)
    if index < 0:
        msg = 'Expected line starting with <gml:posList>, got %s' % line
        raise Exception(msg)

    # Reuse indentation and tag
    k = index + len(starttag)
    new_line = line[:k]
    remaining_line = line[k:]

    # Swap coordinates for the rest of the line
    got_lat = False
    got_lon = False
    for field in remaining_line.split():

        # Clean end-tag from last field if present
        index = field.find(endtag)
        if index > -1:
            # We got e.g. 136.28396002600005</gml:posList>
            x = float(field[:index])
        else:
            x = float(field)

        # Assign latitude or longitude
        if got_lat:
            lon = x
            got_lon = True
        else:
            lat = x
            got_lat = True

        # Swap and write back every time a pair has been found
        # Ensure there are enough decimals for the required precision
        if got_lat and got_lon:
            new_line += ' %.9f %.9f' % (lon, lat)
            got_lat = got_lon = False

    # Close position list and return
    new_line += endtag + '\n'
    return new_line


def swap_coords(filename):
    """Swap lat and lon in filename
    """

    # Read from input file
    fid = open(filename, 'r')
    lines = fid.readlines()
    fid.close()

    # Open output file
    basename, ext = os.path.splitext(filename)
    fid = open(basename + '_converted' + ext, 'w')

    # Report
    N = len(lines)
    print 'There are %i lines in %s' % (N, filename)

    # Process
    reading_positions = False
    got_lat = False
    got_lon = False
    for k, line in enumerate(lines):
        s = line.strip()
        if s.startswith(position_tag):
            # Swap lat and lon pairs in this line and write back
            fid.write(swap_pairs(line))
        elif s.startswith(lc_tag):
            fid.write(swap_pairs(line, starttag=lc_tag))
        elif s.startswith(uc_tag):
            fid.write(swap_pairs(line, starttag=uc_tag))
        else:
            # Store back unchanged
            fid.write(line)

    fid.close()


if __name__ == '__main__':
    filename = sys.argv[1]
    if filename.endswith('.gml'):
        swap_coords(filename)
    else:
        print 'Unsupported file extension:', filename
