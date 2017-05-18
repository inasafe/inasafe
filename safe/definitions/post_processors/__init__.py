# coding=utf-8
from population_post_processors import *
from post_processors import *
from minimum_needs_post_processors import *
from post_processor_inputs import *
from post_processor_functions import *
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
from safe.definitions.post_processors.minimum_needs_post_processors import \
    minimum_needs_post_processors

# This is the order of execution, so the order is important.
# For instance, the size post processor must run before size_rate.
# and hygiene packs post processor must run after gender post processor

post_processors = [
    post_processor_size,
    # post_processor_size_rate, disabled in V4.0, ET 13/02/17
    post_processor_affected,
    post_processor_displaced_ratio,
    post_processor_displaced,
] + (female_postprocessors +
     age_postprocessors +
     minimum_needs_post_processors +
     age_vulnerability_postprocessors +
     disabled_vulnerability_postprocessors +
     gender_postprocessors) + [
    post_processor_additional_rice
]
