from collections import OrderedDict
from safe.definitionsv4.fields import (
    exposure_fields,
    hazard_fields,
    aggregation_fields,
    impact_fields
)

all_fields = OrderedDict([
    ('Exposure Fields', exposure_fields),
    ('Hazard Fields', hazard_fields),
    ('Aggregation Fields', aggregation_fields),
    ('Impact Fields', impact_fields)
])

def generate_field_table():
    """Generating all field table in markdown."""
    for key, fields in all_fields.items():
        print '### %s' % key
        print '| Key | Name | Field Name |'
        print '| --- | ---- | ---------- |'
        for i in fields:
            print '| %s | %s | %s |' % (i['key'], i['name'], i['field_name'])


if __name__ == '__main__':
    generate_field_table()
