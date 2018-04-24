"""Test script."""


from safe.definitions.test.test_fields import all_fields


def generate_field_table():
    """Generating all field table in markdown."""
    for key, fields in list(all_fields.items()):
        # fix_print_with_import
        print(('### %s' % key))
        # fix_print_with_import
        print('| Key | Name | Field Name | Description |')
        # fix_print_with_import
        print('| --- | ---- | ---------- | ----------- |')
        for i in fields:
            print(('| %s | %s | %s | %s |' %
                   (i['key'], i['name'], i['field_name'], i['description'])))


if __name__ == '__main__':
    generate_field_table()
