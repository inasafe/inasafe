"""Collection of mappings for standard vulnerability classes
"""
import numpy
from safe.storage.vector import Vector
from safe.common.utilities import verify


#def padang2itb(E):
#    """
#    To be updated
#    """
#    print E.get_attribute_names()


def osm2padang(E):
    """Map OSM attributes to Padang vulnerability classes

    This maps attributes collected in the OpenStreetMap exposure data
    (data.kompetisiosm.org) to 9 vulnerability classes identified by
    Geoscience Australia and ITB in the post 2009 Padang earthquake
    survey (http://trove.nla.gov.au/work/38470066).
    The mapping was developed by Abigail Baca, World Bank-GFDRR.

    Input
        E: Vector object representing the OSM data

    Output:
        Vector object like E, but with one new attribute ('VCLASS')
        representing the vulnerability class used in the Padang dataset


    Algorithm

    1. Class the "levels" field into height bands where 1-3 = low,
       4-10 = mid, >10 = high
    2. Where height band = mid then building type = 4
       "RC medium rise Frame with Masonry in-fill walls"
    3. Where height band = high then building type = 6
       "Concrete Shear wall high rise* Hazus C2H"
    4. Where height band = low and structure = (plastered or
       reinforced_masonry) then building type = 7
       "RC low rise Frame with Masonry in-fill walls"
    5. Where height band = low and structure = confined_masonry then
       building type = 8 "Confined Masonry"
    6. Where height band = low and structure = unreinforced_masonry then
       building type = 2 "URM with Metal Roof"
    """

    # Input check
    required = ['building_l', 'building_s']
    actual = E.get_attribute_names()
    msg = ('Input data to osm2padang must have attributes %s. '
           'It has %s' % (str(required), str(actual)))
    for attribute in required:
        verify(attribute in actual, msg)

    # Start mapping
    N = len(E)
    attributes = E.get_data()

    # FIXME (Ole): Pylint says variable count is unused. Why?
    # pylint: disable=W0612
    count = 0
    # pylint: enable=W0612
    for i in range(N):
        levels = E.get_data('building_l', i)
        structure = E.get_data('building_s', i)
        if levels is None or structure is None:
            vulnerability_class = 2
            count += 1
        else:
            # Map string variable levels to integer
            if levels.endswith('+'):
                levels = 100

            try:
                levels = int(levels)
            except ValueError:
                # E.g. 'ILP jalan'
                vulnerability_class = 2
                count += 1
            else:
                # Start mapping depending on levels
                if levels >= 10:
                    # High
                    vulnerability_class = 6  # Concrete shear
                elif 4 <= levels < 10:
                    # Mid
                    vulnerability_class = 4  # RC mid
                elif 1 <= levels < 4:
                    # Low
                    if structure in ['plastered',
                                     'reinforced masonry',
                                     'reinforced_masonry']:
                        vulnerability_class = 7  # RC low
                    elif structure == 'confined_masonry':
                        vulnerability_class = 8  # Confined
                    elif 'kayu' in structure or 'wood' in structure:
                        vulnerability_class = 9  # Wood
                    else:
                        vulnerability_class = 2  # URM
                elif numpy.allclose(levels, 0):
                    # A few buildings exist with 0 levels.

                    # In general, we should be assigning here the most
                    # frequent building in the area which could be defined
                    # by admin boundaries.
                    vulnerability_class = 2
                else:
                    msg = 'Unknown number of levels: %s' % levels
                    raise Exception(msg)

        # Store new attribute value
        attributes[i]['VCLASS'] = vulnerability_class

        # Selfcheck for use with osm_080811.shp
        if E.get_name() == 'osm_080811':
            if levels > 0:
                msg = ('Got %s expected %s. levels = %f, structure = %s'
                       % (vulnerability_class,
                          attributes[i]['TestBLDGCl'],
                          levels,
                          structure))
                verify(numpy.allclose(attributes[i]['TestBLDGCl'],
                                      vulnerability_class), msg)

    #print 'Got %i without levels or structure (out of %i total)' % (count, N)

    # Create new vector instance and return
    V = Vector(data=attributes,
               projection=E.get_projection(),
               geometry=E.get_geometry(),
               name=E.get_name() + ' mapped to Padang vulnerability classes',
               keywords=E.get_keywords())
    return V


def sigab2padang(E):
    """Map SIGAB attributes to Padang vulnerability classes

    Input
        E: Vector object representing the SIGAB data

    Output:
        Vector object like E, but with one new attribute ('VCLASS')
        representing the vulnerability class used in the Padang dataset

    """

    # Input check
    required = ['Struktur_B', 'Lantai', 'Atap', 'Dinding', 'Tingkat']
    actual = E.get_attribute_names()

    msg = ('Input data to sigab2bnpb must have attributes %s. '
           'It has %s' % (str(required), str(actual)))
    for attribute in required:
        verify(attribute in actual, msg)

    # Start mapping
    N = len(E)
    attributes = E.get_data()
    for i in range(N):
        levels = E.get_data('Tingkat', i).lower()
        structure = E.get_data('Struktur_B', i).lower()
        #roof_type = E.get_data('Atap', i).lower()
        #wall_type = E.get_data('Dinding', i).lower()
        #floor_type = E.get_data('Lantai', i).lower()
        if levels == 'none' or structure == 'none':
            vulnerability_class = 2
        else:
            if int(levels) >= 2:
                vulnerability_class = 7  # RC low
            else:
                # Low
                if structure in ['beton bertulang']:
                    vulnerability_class = 6  # Concrete shear
                elif structure.startswith('rangka'):
                    vulnerability_class = 8  # Confined
                elif 'kayu' in structure or 'wood' in structure:
                    vulnerability_class = 9  # Wood
                else:
                    vulnerability_class = 2  # URM

        # Store new attribute value
        attributes[i]['VCLASS'] = vulnerability_class

        # Selfcheck for use with osm_080811.shp
        if E.get_name() == 'osm_080811':
            if levels > 0:
                msg = ('Got %s expected %s. levels = %f, structure = %s'
                       % (vulnerability_class,
                          attributes[i]['TestBLDGCl'],
                          levels,
                          structure))
                verify(numpy.allclose(attributes[i]['TestBLDGCl'],
                                      vulnerability_class), msg)

    # Create new vector instance and return
    V = Vector(data=attributes,
               projection=E.get_projection(),
               geometry=E.get_geometry(),
               name=E.get_name() + ' mapped to Padang vulnerability classes',
               keywords=E.get_keywords())
    return V


def osm2bnpb(E, target_attribute='VCLASS'):
    """Map OSM attributes to BNPB vulnerability classes

    This maps attributes collected in the OpenStreetMap exposure data
    (data.kompetisiosm.org) to 2 vulnerability classes identified by
    BNPB in Kajian Risiko Gempabumi VERS 1.0, 2011. They are
    URM: Unreinforced Masonry and RM: Reinforced Masonry

    Input
        E: Vector object representing the OSM data
        target_attribute: Optional name of the attribute containing
                          the mapped vulnerability class. Default
                          value is 'VCLASS'

    Output:
        Vector object like E, but with one new attribute (e.g. 'VCLASS')
        representing the vulnerability class used in the guidelines
    """

    # Input check
    required = ['building_l', 'building_s']
    actual = E.get_attribute_names()
    msg = ('Input data to osm2bnpb must have attributes %s. '
           'It has %s' % (str(required), str(actual)))
    for attribute in required:
        verify(attribute in actual, msg)

    # Start mapping
    N = len(E)
    attributes = E.get_data()

    # FIXME (Ole): Pylint says variable count is unused. Why?
    # pylint: disable=W0612
    count = 0
    # pylint: enable=W0612
    for i in range(N):
        levels = E.get_data('building_l', i)
        structure = E.get_data('building_s', i)
        if levels is None or structure is None:
            vulnerability_class = 'URM'
            count += 1
        else:
            # Map string variable levels to integer
            if levels.endswith('+'):
                levels = 100

            try:
                levels = int(levels)
            except ValueError:
                # E.g. 'ILP jalan'
                vulnerability_class = 'URM'
                count += 1
            else:
                # Start mapping depending on levels
                if levels >= 4:
                    # High
                    vulnerability_class = 'RM'
                elif 1 <= levels < 4:
                    # Low
                    if structure in ['reinforced_masonry', 'confined_masonry']:
                        vulnerability_class = 'RM'
                    elif 'kayu' in structure or 'wood' in structure:
                        vulnerability_class = 'RM'
                    else:
                        vulnerability_class = 'URM'
                elif numpy.allclose(levels, 0):
                    # A few buildings exist with 0 levels.

                    # In general, we should be assigning here the most
                    # frequent building in the area which could be defined
                    # by admin boundaries.
                    vulnerability_class = 'URM'
                else:
                    msg = 'Unknown number of levels: %s' % levels
                    raise Exception(msg)

        # Store new attribute value
        attributes[i][target_attribute] = vulnerability_class

    #print 'Got %i without levels or structure (out of %i total)' % (count, N)

    # Create new vector instance and return
    V = Vector(data=attributes,
               projection=E.get_projection(),
               geometry=E.get_geometry(),
               name=E.get_name() + ' mapped to BNPB vulnerability classes',
               keywords=E.get_keywords())
    return V


def unspecific2bnpb(E, target_attribute='VCLASS'):
    """Map Unspecific point data to BNPB vulnerability classes

    This makes no assumptions about attributes and maps everything to
    URM: Unreinforced Masonry

    Input
        E: Vector object representing the OSM data
        target_attribute: Optional name of the attribute containing
                          the mapped vulnerability class. Default
                          value is 'VCLASS'

    Output:
        Vector object like E, but with one new attribute (e.g. 'VCLASS')
        representing the vulnerability class used in the guidelines
    """

    # Start mapping
    N = len(E)
    attributes = E.get_data()

    for i in range(N):
        # Store new attribute value
        attributes[i][target_attribute] = 'URM'

    # Create new vector instance and return
    V = Vector(data=attributes,
               projection=E.get_projection(),
               geometry=E.get_geometry(),
               name=E.get_name() + ' mapped to BNPB vulnerability class URM',
               keywords=E.get_keywords())
    return V


def sigab2bnpb(E, target_attribute='VCLASS'):
    """Map SIGAB point data to BNPB vulnerability classes

    Input
        E: Vector object representing the OSM data
        target_attribute: Optional name of the attribute containing
                          the mapped vulnerability class. Default
                          value is 'VCLASS'

    Output:
        Vector object like E, but with one new attribute (e.g. 'VCLASS')
        representing the vulnerability class used in the guidelines
    """

    # Input check
    required = ['Struktur_B', 'Lantai', 'Atap', 'Dinding', 'Tingkat']
    actual = E.get_attribute_names()

    msg = ('Input data to sigab2bnpb must have attributes %s. '
           'It has %s' % (str(required), str(actual)))
    for attribute in required:
        verify(attribute in actual, msg)

    # Start mapping
    N = len(E)
    attributes = E.get_data()
    for i in range(N):
        levels = E.get_data('Tingkat', i).lower()
        structure = E.get_data('Struktur_B', i).lower()
        #roof_type = E.get_data('Atap', i).lower()
        #wall_type = E.get_data('Dinding', i).lower()
        #floor_type = E.get_data('Lantai', i).lower()
        if levels == 'none' or structure == 'none':
            vulnerability_class = 'URM'
        elif structure.startswith('beton') or structure.startswith('kayu'):
            vulnerability_class = 'RM'
        else:
            if int(levels) >= 2:
                vulnerability_class = 'RM'
            else:
                vulnerability_class = 'URM'

        # Store new attribute value
        attributes[i][target_attribute] = vulnerability_class

    # Create new vector instance and return
    V = Vector(data=attributes,
               projection=E.get_projection(),
               geometry=E.get_geometry(),
               name=E.get_name() + ' mapped to BNPB vulnerability classes',
               keywords=E.get_keywords())
    return V


# def printout_stats_only_sigab2bnpb(E, target_attribute='VCLASS'):
#     """Map SIGAB point data to BNPB vulnerability classes

#     Input
#         E: Vector object representing the OSM data
#         target_attribute: Optional name of the attribute containing
#                           the mapped vulnerability class. Default
#                           value is 'VCLASS'

#     Output:
#         Vector object like E, but with one new attribute (e.g. 'VCLASS')
#         representing the vulnerability class used in the guidelines
#     """

#     # Input check
#     #required = ['Bangunan', 'Halaman', 'Struktur_B', 'Level',
#     #            'Lantai', 'Atap', 'Dinding', 'Tingkat']
#     actual = E.get_attribute_names()
#     #print actual

#     #msg = ('Input data to osm2bnpb must have attributes %s. '
#     #       'It has %s' % (str(required), str(actual)))
#     #for attribute in required:
#     #    verify(attribute in actual, msg)

#     # Start mapping
#     fields = {}
#     N = len(E)
#     print 'Total number of attributes', N
#     attributes = E.get_data()
#     count = 0
#     for i in range(N):
#         for key in actual:  # Required:
#             if key not in fields:
#                 fields[key] = {}

#             val = E.get_data(key, i).lower()
#             if val not in fields[key]:
#                 fields[key][val] = 0

#             # Count incidences of each value
#             fields[key][val] += 1

#     fid = open('/home/nielso/sigab_stats.txt', 'w')
#     for key in actual:  # Required:
#         print
#         print key
#         fid.write('\n%s\n' % key)
#         for val in fields[key]:
#             print '    %s: %i' % (str(val), fields[key][val])
#             fid.write('    %s: %i\n' % (str(val), fields[key][val]))

#     fid.close()
