"""Lookup table mapping layer titles to translatable strings

Layer titles are kept in the associated keywords files. However,
these files are not seen by the internationalisation system and
can therefore not be translated.

To achieve this for selected titles, we maintain a lookup table of the form

{title: translatable_string}

where title comes from the keywords file and translatable_string is
the string that will appear as the translated title

e.g.

{'title1': _('Jakarta 2007 flood')}

With the underscore function, the specified string will be seen by the
translation system and can appear in the supported languages as with
other strings in SAFE.
"""

# FIXME (Ole): This approach can be generalised to any strings that are not
#              statically declared such as attribute values.

from utilities import ugettext as _

titles = {'title1': _('DKI buildings'),       # Bangunan DKI
          'title2': _('Jakarta 2007 flood'),  # Banjir seperti 2007
          'title3': _('Jakarta flood like 2007 with pump failure at Pluit, '
                      'Ancol and Sunter'),  # Banjir 2007 tanpa pompa di
                                            # Pluit, Ancol dan Sunter
          'Jakarta flood like 2007 with pump failure at Pluit and Ancol':
              _('Jakarta flood like 2007 with pump failure at '
                'Pluit and Ancol'),
          'title4': _('Sea wall collapse at Pluit'),  # Dam Pluit Runtuh
          'title5': _('Jakarta flood prone areas'),  # Daerah Rawan Banjir
          'title6': _('Population Jakarta'),  # Penduduk Jakarta
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
          'Shakemap Padang 2009': _('Shakemap Padang 2009'),
          'OSM building footprints': _('OSM building '
                                       'footprints'),  # Bangunan OSM
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
