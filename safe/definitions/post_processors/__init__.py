# coding=utf-8
from post_processors import *
from population_post_processors import *

# This is the order of execution, so the order is important.
# For instance, the size post processor must run before size_rate.
# and hygiene packs post processor must run after gender post processor

# Postprocessor tree
# # Root : impact layer
# |--- size
# |   `--- size rate  disabled in V4.0, ET 13/02/17
# |--- affected
# |--- displaced ratio
# |   |--- displaced count
# |      |--- gender
# |      |   |--- hygiene packs
# |      |--- additional rice
# |      |--- youth
# |      |--- adult
# |      |--- elderly
# |      `--- minimum needs

post_processors = [
    post_processor_size,
    # post_processor_size_rate, disabled in V4.0, ET 13/02/17
    post_processor_affected,
    post_processor_displaced_ratio,
    post_processor_displaced,
] + (female_postprocessors +
     age_postprocessors +
     minimum_needs_post_processors +
     vulnerability_postprocessors +
     gender_postprocessors) + [
    post_processor_additional_rice
]