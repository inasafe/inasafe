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

from utilities import ugettext as _

titles = {'title1': _('DKI buildings'),       # Bangunan DKI
          'title2': _('Jakarta 2007 flood'),  # Banjir seperti 2007
          'title3': _('Jakarta flood like 2007 with pump failure at Pluit, '
                      'Ancol and Sunter'),  # Banjir 2007 tanpa pompa di
                                            # Pluit, Ancol dan Sunter
          'title4': _('Sea wall collapse at Pluit'),  # Dam Pluit Runtuh
          'title5': _('Jakarta flood prone areas'),  # Daerah Rawan Banjir
          'title6': _('Population Jakarta'),  # Penduduk Jakarta
          }
