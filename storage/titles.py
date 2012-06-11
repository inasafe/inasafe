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
{'title1': _('Jakarta 2007 flood')}

or (using existing title)
{'Schools': _('Schools')}

or (attribute value)
{'school': _('school')}

With the underscore function, the specified string will be seen by the
translation system and can appear in the supported languages as with
other strings in SAFE.

Note, this module does *not* provide translations! Rather it provides
mappings between strings expected at runtime to strings seen by the
existing translation systems.
"""

# FIXME (Ole): This approach can be generalised to any strings that are not
#              statically declared such as attribute values.
#              So, we should merge the two dictionaries and just have one
#              with strings that need to be recognised by the translation
#              tools.
#              Also rename this module to something more fitting, such as
#              dynamic_translations.py
#              See issue #168

from utilities import ugettext as _

titles = {'title1': _('DKI buildings'),       # Bangunan DKI
          'title2': _('Jakarta 2007 flood'),  # Banjir seperti 2007
          'Jakarta 2007 flood': _('Jakarta 2007 flood'),
          'title3': _('Jakarta flood like 2007 with pump failure at Pluit, '
                      'Ancol and Sunter'),  # Banjir 2007 tanpa pompa di
                                            # Pluit, Ancol dan Sunter
          'Jakarta flood like 2007 with pump failure at Pluit and Ancol':
              _('Jakarta flood like 2007 with pump failure at '
                'Pluit and Ancol'),
          'Jakarta flood like 2007 with structural improvements':
              _('Jakarta flood like 2007 with structural improvements'),
          'title4': _('Sea wall collapse at Pluit'),  # Dam Pluit Runtuh
          'title5': _('Jakarta flood prone areas'),  # Daerah Rawan Banjir
          'title6': _('Population Jakarta'),  # Penduduk Jakarta
          'People': _('People'),
          'people': _('people'),
          'Flood Depth (design) Jakarta': _('Flood Depth (design) Jakarta'),
          'Flood Depth (current) Jakarta': _('Flood Depth (current) Jakarta'),
          'Yogyakarta 2006 earthquake': _('Yogyakarta 2006 earthquake'),
          'Indonesian Earthquake Hazard Map': _('Indonesian Earthquake '
                                                'Hazard Map'),
          'Maumere tsunami inundation': _('Maumere tsunami inundation'),
          'Sumatran fault Mw 7.8 scenario': _('Sumatran fault Mw 7.8 '
                                              'scenario'),  # Skenario
                                                            # Gempabumi Sesar
                                                            # Sumatra Mw 7.8
          'Mentawai fault Mw 9.0 scenario': _('Mentawai fault Mw 9.0 '
                                              'scenario'),  # Skenario
                                                            # Gempabumi Sesar
                                                            # Mentawai Mw 9.0
          'Padang 2009 scenario': _('Padang 2009 scenario'),
          'Yogya 2006 scenario': _('Yogya 2006 scenario'),
          'Lembang fault scenario': _('Lembang fault scenario'),
          'OSM building footprints': _('OSM building '
                                       'footprints'),  # Bangunan OSM
          'OSM buildings': _('OSM buildings'),  # Bangunan OSM
          'AIBEP schools': _('AIBEP schools'),
          'Population density (5kmx5km)': _('Population density '
                                            '(5kmx5km)'),  # Perkiraan penduduk
          'Office buildings Jakarta': _('Office buildings Jakarta'),
          'Hospitals and clinics Jakarta': _('Hospitals and '
                                     'clinics Jakarta'),  # Puskesmas dan
                                                          # rumah sakit
          'Schools Jakarta': _('Schools Jakarta'),
          'Schools': _('Schools'),
          'Industrial buildings Jakarta': _('Industrial buildings Jakarta'),
          'Industrial areas Jakarta': _('Industrial areas Jakarta'),
          'Commercial areas Jakarta': _('Commercial areas Jakarta'),
          'Hospitals Jakarta': _('Hospitals Jakarta'),
          }


values = {'office': _('office'),
          'clinic': _('clinic'),
          'terrace': _('terrace'),
          'police': _('police'),
          'residential': _('residential'),
          'kindergarten': _('kindergarten'),
          'bank': _('bank'),
          'place of worship': _('place of worship'),
          'school': _('school'),
          'university': _('university'),
          'apartments': _('apartments'),
          'college': _('college'),
          'commercial': _('commercial'),
          'hospital': _('hospital'),
          'industrial': _('industrial'),
          'civic': _('civic'),
          'church': _('church'),
          'hotel': _('hotel'),
          'public building': _('public building'),
          'other': _('other'),
          'fire station': _('fire station'),
          }
