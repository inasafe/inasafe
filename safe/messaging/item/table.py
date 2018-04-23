# coding=utf-8

"""Table."""


from .exceptions import InvalidMessageItemError

from .message_element import MessageElement
from .row import Row

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class Table(MessageElement):

    """A class to model tables in the messaging system."""

    def __init__(self, *args, **kwargs):
        """Creates a table object.

        :param *args: args can be list or Row
        :type *args: list, row


        We pass the kwargs on to the base class so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        self.caption = kwargs.pop('caption', None)
        self.header = kwargs.pop('header', None)
        super(Table, self).__init__(**kwargs)
        self.rows = []

        for arg in args:
            self.add(arg)

    def add(self, item):
        """Add a row to the table.

        List can be passed and are automatically converted to Rows.

        :param item: Item an element to add to the rows can be list or Row
            object
        :type item: row, list

        """
        if isinstance(item, list):
            self.rows.append(Row(item))
        elif isinstance(item, Row):
            self.rows.append(item)
        else:
            raise InvalidMessageItemError(item, item.__class__)

    def to_html(self):
        """Render a Table MessageElement as html.

        :returns: The html representation of the Table MessageElement
        :rtype: basestring
        """
        table = '<table%s>\n' % self.html_attributes()
        if self.caption is not None:
            if isinstance(self.caption, MessageElement):
                caption = self.caption.to_html()
            else:
                caption = self.caption
            table += '<caption>%s</caption>\n' % caption
        if self.header:
            if isinstance(self.header, MessageElement):
                header = self.header.to_html()
            else:
                header = self.header
            table += '<thead>%s</thead>' % header
        table += '<tbody>\n'
        for row in self.rows:
            table += row.to_html()
        table += '</tbody>\n</table>\n'

        return table

    def to_text(self):
        """Render a Table MessageElement as plain text.

        :returns: The text representation of the Table MessageElement
        :rtype: basestring
        """

        table = ''
        if self.caption is not None:
            table += '%s</caption>\n' % self.caption
        table += '\n'
        for row in self.rows:
            table += row.to_text()
        return table

    def to_markdown(self):
        """Render a Table queue as markdown.

        :returns: Markdown representation of the Text Table.
        :rtype: str
        """
        raise NotImplementedError('Please Implement this method')

    def to_dict(self):
        """Render a MessageElement as python dict.

        :return: Python dict representation
        :rtype: dict
        """
        obj_dict = super(Table, self).to_dict()
        rows_dict = [r.to_dict() for r in self.rows]
        child_dict = {
            'type': self.__class__.__name__,
            'caption': self.caption,
            'rows': rows_dict
        }
        obj_dict.update(child_dict)
        return obj_dict
