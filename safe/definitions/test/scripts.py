"""Test script."""

from safe.definitions.test.test_fields import all_fields


def generate_field_table():
    """Generating all field table in markdown."""
    for key, fields in all_fields.items():
        print '### %s' % key
        print '| Key | Name | Field Name | Description |'
        print '| --- | ---- | ---------- | ----------- |'
        for i in fields:
            print('| %s | %s | %s | %s |' %
                  (i['key'], i['name'], i['field_name'], i['description']))


if __name__ == '__main__':
    generate_field_table()
