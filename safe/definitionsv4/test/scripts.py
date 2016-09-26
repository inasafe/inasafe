from definitionsv4.test.test_fields import all_fields


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
