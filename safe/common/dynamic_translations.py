"""Lookup table mapping layer titles to translatable strings

Layer titles are kept in the associated keywords files. However,
these files are not seen by the internationalisation system and
can therefore not be translated.

To achieve this for selected titles, we maintain a lookup table of the form

{string: translatable_string}

where string e.g. comes from the keywords file or attribute names/values
in datasets and translatable_string is the string that will appear as the
translated at runtime.

e.g (using a neutral symbol)
{'title1': tr('Jakarta 2007 flood')}

or (using existing title)
{'Schools': tr('Schools')}

or (attribute value)
{'school': tr('school')}

With the underscore function, the specified string will be seen by the
translation system and can appear in the supported languages as with
other strings in SAFE.

Note, this module does *not* provide translations! Rather it provides
mappings between strings expected at runtime to strings seen by the
existing translation systems.

To use:

from dynamic_translations import names



"""

# FIXME (Ole): Simplify to just maintain one list of strings and have
#              this module automatically generate the _() versions:
# for s in strings:
#     names[s] = '_(%s)' % s

from safe.common.utilities import ugettext as tr

names = {'title1': tr('DKI buildings'),       # Bangunan DKI
         'title2': tr('Jakarta 2007 flood'),  # Banjir seperti 2007
         'Jakarta 2007 flood': tr('Jakarta 2007 flood'),
         'A flood in Jakarta like in 2007': tr('A flood in Jakarta like '
                                              'in 2007'),
         'title3': tr('Jakarta flood like 2007 with pump failure at Pluit, '
                     'Ancol and Sunter'),  # Banjir 2007 tanpa pompa di
                                           # Pluit, Ancol dan Sunter
         'Jakarta flood like 2007 with pump failure at Pluit and Ancol':
             tr('Jakarta flood like 2007 with pump failure at '
               'Pluit and Ancol'),
         'A flood in Jakarta like in 2007 but with structural improvements':
             tr('A flood in Jakarta like in 2007 but with structural '
               'improvements'),
         'title4': tr('Sea wall collapse at Pluit'),  # Dam Pluit Runtuh
         'title5': tr('Jakarta flood prone areas'),  # Daerah Rawan Banjir
         ('A flood in Jakarta in RW areas '
          'identified as flood prone'): tr('A flood in Jakarta in RW areas '
                                          'identified as flood prone'),
                                          # Daerah Rawan Banjir
         'title6': tr('Population Jakarta'),  # Penduduk Jakarta
         'People': tr('People'),
         'people': tr('people'),
         'People in Jakarta': tr('People in Jakarta'),
         'Flood Depth (design) Jakarta': tr('Flood Depth (design) Jakarta'),
         'Flood Depth (current) Jakarta': tr('Flood Depth (current) Jakarta'),
         'An earthquake in Yogyakarta like in 2006': tr('An earthquake in '
                                                       'Yogyakarta like in '
                                                       '2006'),
         'Indonesian Earthquake Hazard Map': tr('Indonesian Earthquake '
                                               'Hazard Map'),
         'A tsunami in Maumere (Mw 8.1)': tr('A tsunami in Maumere (Mw 8.1)'),
         'A tsunami in Padang (Mw 8.8)': tr('A tsunami in Padang (Mw 8.8)'),
         'An earthquake at the Sumatran fault (Mw 7.8)': tr('An earthquake at '
                                                           'the Sumatran '
                                                           'fault (Mw 7.8)'),
                                                           # Skenario
                                                           # Gempabumi Sesar
                                                           # Sumatra Mw 7.8
         'An earthquake at the Mentawai fault (Mw 9.0)': tr('An earthquake at '
                                                           'the Mentawai fault'
                                                           ' (Mw 9.0)'),
                                                           # Skenario
                                                           # Gempabumi Sesar
                                                           # Mentawai Mw 9.0
         'An earthquake in Padang like in 2009': tr('An earthquake in Padang '
                                                   'like in 2009'),
         'An earthquake in Yogyakarta  like in 2006': tr('An earthquake in '
                                                        'Yogyakarta like in '
                                                        '2006'),
         'An earthquake at the Lembang fault': tr('An earthquake at the '
                                                 'Lembang fault'),
         'OSM building footprints': tr('OSM building '
                                      'footprints'),  # Bangunan OSM
         'OSM buildings': tr('OSM buildings'),  # Bangunan OSM
         'AIBEP schools': tr('AIBEP schools'),
         'Population density (5kmx5km)': tr('Population density '
                                           '(5kmx5km)'),  # Perkiraan penduduk
         'Office buildings Jakarta': tr('Office buildings Jakarta'),
         'Hospitals and clinics Jakarta': tr('Hospitals and '
                                            'clinics Jakarta'),  # Puskesmas
                                                                 # dan
                                                                 # rumah sakit
         'Schools Jakarta': tr('Schools Jakarta'),
         'Schools': tr('Schools'),
         'Industrial buildings Jakarta': tr('Industrial buildings Jakarta'),
         'Industrial areas Jakarta': tr('Industrial areas Jakarta'),
         'Commercial areas Jakarta': tr('Commercial areas Jakarta'),
         'Hospitals Jakarta': tr('Hospitals Jakarta'),
         'An eruption': tr('An eruption'),
         'A volcano eruption': tr('A volcano eruption'),
         'A volcano alert': tr('A volcano alert'),

         # Data attribute value start here
         'office': tr('office'),
         'clinic': tr('clinic'),
         'terrace': tr('terrace'),
         'police': tr('police'),
         'residential': tr('residential'),
         'kindergarten': tr('kindergarten'),
         'bank': tr('bank'),
         'place of worship': tr('place of worship'),
         'school': tr('school'),
         'university': tr('university'),
         'apartments': tr('apartments'),
         'college': tr('college'),
         'commercial': tr('commercial'),
         'hospital': tr('hospital'),
         'industrial': tr('industrial'),
         'civic': tr('civic'),
         'church': tr('church'),
         'hotel': tr('hotel'),
         'public building': tr('public building'),
         'other': tr('other'),
         'fire station': tr('fire station'),
         }
