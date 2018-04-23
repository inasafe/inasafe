"""Basic XML utilities based on minidom - the built in Document Object Model
"""

import sys
from xml.dom import minidom, Node
from safe.common.utilities import verify

def print_tree(n, indent=0):
    while n:
        # print 'nodeType', n.nodeType, Node.ELEMENT_NODE
        #if n.nodeType != Node.ELEMENT_NODE:
        #    break

        print ' '*indent,\
              'Node name: "%s",' %n.nodeName,\
              'Node type: "%s",' %n.nodeType,\
              'Node value: "%s"' %str(n.nodeValue).strip()


        print_tree(n.firstChild, indent+4)
        n = n.nextSibling


def pretty_print_tree(n, indent=0):
    print n

def parse(fid):
    """Parse XML file descriptor and return DOM object.
    """

    # FIXME (OLE): XML code should be validated against the DTD
    #validate(fid, handler)
    #doc = minidom.parse(fid, make_parser())

    fid.seek(0)
    doc = minidom.parse(fid)
    return doc


def get_elements(nodelist):
    """Return list of nodes that are ELEMENT_NODE
    """

    element_list = []
    for node in nodelist:
        if node.nodeType == Node.ELEMENT_NODE:
            element_list.append(node)

    return element_list


def get_text(nodelist):
    """Return a concatenation of text fields from list of nodes
    """

    s = ''
    for node in nodelist:
        if node.nodeType == Node.TEXT_NODE:
            s += node.nodeValue + ', '

    if len(s)>0: s = s[:-2]
    return s



def remove_whitespace(s):
    """Remove excess whitespace including newlines from string
    """
    import string
    words = s.split() # Split on whitespace

    return string.join(words)

    #return s.replace('\n', '')
    #s.translate(string.maketrans)



#----------------------------
# XML object model
#----------------------------

class XML_element(dict):
    def __init__(self,
                 tag=None,
                 value=None,
                 version='1.0',
                 encoding='iso-8859-1'):
        """
        value can be either
          * An XML_element
          * a list of XML_value
          * a text string

        """

        if isinstance(value, XML_element):
            value = [value]

        self.value = value



        if tag is None:
            tag = '?xml version="%s" encoding="%s"?' %(version, encoding)
            self.root_element = True
        else:
            self.root_element = False

        self.tag = tag




        # FIXME: It might be better to represent these objects
        # in a proper dictionary format with
        # {tag: value, ...}
        # No, tried that - it removes any notion of ordering.


    def __add__(self, other):
        return str(self) + str(other)

    def __radd__(self, other):
        return str(other) + str(self)    #Python swaps self and other

    def __repr__(self):
        return str(self)

    def __str__(self, indent=0):
        """String representation of XML element
        """

        if self.root_element is True:
            increment = 0
        else:
            increment = 4

        s = tab = ' '*indent

        s += '<%s>' %self.tag
        if isinstance(self.value, basestring):
            s += remove_whitespace(self.value)
        else:
            s += '\n'
            for e in self.value:
                s += e.__str__(indent+increment)
            s += tab

        if self.root_element is False:
            s += '</%s>\n' %self.tag

        return s


    def __getitem__(self, key):
        """Return sub-tree starting at element with tag equal to specified key
        If node is terminal, its text value will be returned instead of itself.
        This will allow expressions such as

        xmlobject['datafile']['accountable'] == 'Jane Sexton'

        If more than one element matches the given key a list of all
        matches will be returned
        """

        result = []
        for node in self.value:
            if node.tag == key:
                # print 'node tag = %s, node value = %s' %(node.tag, node.value)

                if isinstance(node.value, basestring):
                    result.append(str(node.value))
                    #return node.value
                else:
                    result.append(node)
                    #return node

        # print 'result', result
        if len(result) == 0:
            return None
        if len(result) == 1:
            return result[0]
        if len(result) > 1:
            return result


    def has_key(self, key):
        found = False
        for node in self.value:
            if node.tag == key:
                found = True

        return found


    def keys(self):
        return [str(node.tag) for node in self.value]



    def pretty_print(self, indent=0):
        """Print the document without tags using indentation
        """

        s = tab = ' '*indent
        s += '%s: ' %self.tag
        if isinstance(self.value, basestring):
            s += self.value
        else:
            s += '\n'
            for e in self.value:
                s += e.pretty_print(indent+4)
        s += '\n'

        return s


def xml2object(xml, verbose=False):
    """Generate XML object model from XML file or XML text

    This is the inverse operation to the __str__ representation
    (up to whitespace).

    Input xml can be either an
    * xml file
    * open xml file object

    Return XML_document instance.
    """

    # FIXME - can we allow xml to be string?
    # This would depend on minidom's parse function

    # Input tests
    if isinstance(xml, basestring):
        fid = open(xml)
    else:
        fid = xml

    try:
        dom = parse(fid)
    except Exception as e:
        # Throw filename into dom exception
        msg = 'XML file "%s" could not be parsed.\n' %fid.name
        msg += 'Error message from parser: "%s"' %str(e)
        raise Exception, msg

    try:
        xml_object = dom2object(dom)
    except Exception as e:
        msg = 'Could not convert %s into XML object.\n' %fid.name
        msg += str(e)
        raise Exception, msg

    return xml_object



def dom2object(node):
    """Convert DOM representation to XML_object hierarchy.
    """

    value = []
    textnode_encountered = None
    for n in node.childNodes:

        if n.nodeType == 3:
            # Child is a text element - omit the dom tag #text and
            # go straight to the text value.

            # Note - only the last text value will be recorded

            msg = 'Text element has child nodes - this shouldn\'t happen'
            verify(len(n.childNodes) == 0, msg)


            x = n.nodeValue.strip()
            if len(x) == 0:
                # Skip empty text children
                continue

            textnode_encountered = value = x
        else:
            # XML element


            if textnode_encountered is not None:
                msg = 'A text node was followed by a non-text tag. This is not allowed.\n'
                msg += 'Offending text node: "%s" ' %str(textnode_encountered)
                msg += 'was followed by node named: "<%s>"' %str(n.nodeName)
                raise Exception, msg


            value.append(dom2object(n))


    # Deal with empty elements
    if len(value) == 0: value = ''


    if node.nodeType == 9:
        # Root node (document)
        tag = None
    else:
        # Normal XML node
        tag = node.nodeName


    X = XML_element(tag=tag,
                    value=value)

    return X





    #=================== Useful print statement
    #if n.nodeType == 3 and str(n.nodeValue).strip() == '':
    #    pass
    #else:
    #    print 'Node name: "%s",' %n.nodeName,\
    #          'Node type: "%s",' %n.nodeType,\
    #          'Node value: "%s",' %str(n.nodeValue).strip(),\
    #          'Node children: %d' %len(n.childNodes)
