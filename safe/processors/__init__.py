# coding=utf-8

from safe.processors.minimum_needs_post_processors import *
from safe.processors.population_post_processors import *
from safe.processors.post_processor_functions import *
from safe.processors.post_processor_inputs import *
from safe.processors.post_processors import *
from safe.processors.productivity_post_processors import *
from safe.processors.pre_processors import *

# This is the order of execution, so the order is important.
# For instance, the size post processor must run before size_rate.
# and hygiene packs post processor must run after gender post processor

# Postprocessor tree
# # Root : impact layer
# |--- size
# |   |--- size rate  disabled in V4.0, ET 13/02/17
# |   |--- productivity
# |   |--- production cost
# |   `--- production value
# |--- distance
# |--- bearing angle
# |   `--- cardinality
# |--- affected
# |--- displaced ratio
# |--- fatality ratio
# |   `--- fatality count
# |       `--- displaced count (from fatality count or 0 if no fatalities)
# |          |--- gender
# |          |   `--- hygiene packs
# |          |--- additional rice
# |          |--- youth
# |          |--- adult
# |          |--- elderly
# |          |--- minimum needs
# |          |--- disabled
# |          `--- gender_vulnerability

post_processors = [
    post_processor_size,
    # post_processor_size_rate, disabled in V4.0, ET 13/02/17
    post_processor_affected,
    post_processor_fatality_ratio,
    post_processor_fatalities,
    post_processor_displaced_ratio,
    post_processor_displaced,
    post_processor_distance,
    post_processor_bearing,
    post_processor_cardinality,
    post_processor_pcrafi_flood,
] + (gender_postprocessors +
     female_postprocessors +
     age_postprocessors +
     minimum_needs_post_processors +
     age_vulnerability_postprocessors +
     disabled_vulnerability_postprocessors +
     gender_vulnerability_postprocessors +
     productivity_post_processors) + [
    post_processor_additional_rice,
]

pre_processors = [
    pre_processor_earthquake_contour
]
