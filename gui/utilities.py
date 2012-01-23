import sys
import traceback

def get_exception_with_stacktrace(e, html=False):
    """Convert exception into a string and and stack trace

    Input
        e: Exception object
        html: Optional flat if output is to wrapped as html

    Output
        Exception with stack trace info suitable for display
    """

    info = ''.join(traceback.format_tb(sys.exc_info()[2]))
    errmsg = str(e) + '\n\n' + info

    if not html:
        return errmsg
    else:
        # Wrap string in html
        s = '<div id="traceback"><pre>\n'
        s += errmsg
        s += '</pre></div>'

        return s



