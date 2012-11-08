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

This module contains words and phrases that need to be translatable but
would not normally be available in code for example, that originate from
a dataset or external source.

Just put your translations here, and it will be available to the tr function
but never import this module or the functions in it!



"""

# FIXME (Ole): Simplify to just maintain one list of strings and have
#              this module automatically generate the _() versions:
# for s in strings:
#     names[s] = '_(%s)' % s

from safe.common.utilities import ugettext as tr


# Don't call this function
def dynamic_translations():
    """These listed here so they get translated apriori to loading data.
    """
    # Bangunan DKI
    tr('DKI buildings')
    # Banjir seperti 2007
    tr('Jakarta 2007 flood')
    tr('A flood in Jakarta like in 2007')
    tr('Jakarta flood like 2007 with pump failure at Pluit, Ancol and Sunter')
    # Banjir 2007 tanpa pompa di Pluit, Ancol dan Sunter
    tr('Jakarta flood like 2007 with pump failure at Pluit and Ancol')
    tr('A flood in Jakarta like in 2007 but with structural improvements')
    # Dam Pluit Runtuh
    tr('Sea wall collapse at Pluit')
    # Daerah Rawan Banjir
    tr('Jakarta flood prone areas')
    tr('A flood in Jakarta in RW areas identified as flood prone')
    # Daerah Rawan Banjir
    # Penduduk Jakarta
    tr('Population Jakarta')
    tr('People')
    tr('people')
    tr('People in Jakarta')
    tr('Indonesian people')
    tr('Indonesian People')
    tr('People in Indonesia')
    tr('Flood Depth (design) Jakarta')
    tr('Flood Depth (current) Jakarta')
    tr('An earthquake in Yogyakarta like in 2006')
    tr('Yogyakarta 2006 earthquake')
    tr('Indonesian Earthquake Hazard Map')
    tr('A tsunami in Maumere (Mw 8.1)')
    tr('Maumere tsunami inundation')
    tr('A tsunami in Padang (Mw 8.8)')
    tr('An earthquake at the Sumatran fault (Mw 7.8)')
    # Skenario Gempabumi Sesar Sumatra Mw 7.8
    tr('An earthquake at the Mentawai fault (Mw 9.0)')
    # Skenario Gempabumi Sesar Mentawai Mw 9.0
    tr('An earthquake in Padang like in 2009')
    tr('An earthquake in Yogyakarta like in 2006')
    tr('An earthquake at the Lembang fault')
    # Bangunan OSM
    tr('OSM building footprints')
    tr('Structures')
    tr('Structures in Jakarta')
    tr('Buildings')
    tr('Buildings in Jakarta')
    tr('Essential buildings')
    tr('Essential Buildings')
    tr('OSM buildings')
    tr('AIBEP schools')
    # Perkiraan penduduk
    tr('Population density (5kmx5km)')
    tr('Office buildings Jakarta')
    # Puskesmas dan rumah sakit
    tr('Hospitals and clinics Jakarta')
    tr('Schools Jakarta')
    tr('Schools')
    tr('Industrial buildings Jakarta')
    tr('Industrial areas Jakarta')
    tr('Commercial areas Jakarta')
    tr('Hospitals Jakarta')
    tr('An eruption')
    tr('A volcano eruption')
    tr('A volcano alert')

    # Data attribute value start here
    tr('office')
    tr('clinic')
    tr('terrace')
    tr('police')
    tr('residential')
    tr('kindergarten')
    tr('bank')
    tr('place of worship')
    tr('school')
    tr('university')
    tr('apartments')
    tr('college')
    tr('commercial')
    tr('hospital')
    tr('industrial')
    tr('civic')
    tr('church')
    tr('hotel')
    tr('public building')
    tr('other')
    tr('fire station')

    # impact function parameters
    # FIXME (Sunni) It's better to be updated dynamically
    tr('Thresholds')
    tr('Postprocessors')
