import os
import sys
import traceback

from qgis.core import QgsApplication


def get_exception_with_stacktrace(e, html=False):
    """Convert exception into a string and and stack trace

    Input
        e: Exception object
        html: Optional flat if output is to wrapped as html

    Output
        Exception with stack trace info suitable for display
    """

    info = ''.join(traceback.format_tb(sys.exc_info()[2]))
    errmsg = str(e)

    if not html:
        return errmsg + "\n" + info
    else:
        # Wrap string in html
        s = '<div>'
        s += '<span class="label important">Problem:</span> ' + errmsg
        s += '</div>'
        s += '<div>'
        s += '<span class="label warning">Traceback:</span> '
        s += '<pre id="traceback" class="prettyprint">\n'
        s += info
        s += '</pre></div>'

        return s

qgis_app = None  # Static variable used to hold hand to running QGis app
def get_qgis_test_app():
    """ Start one QGis application to test agaist

    Input
        NIL

    Output
        handle to qgis app


    If QGis is already running the handle to that app will be returned
    """

    global qgis_app

    if qgis_app is None:
        myGuiFlag = True  # All test will run qgis in gui mode
        qgis_app = QgsApplication(sys.argv, myGuiFlag)
        if os.environ.has_key('QGISPATH'):
            myPath = os.environ['QGISPATH']
            myUseDefaultPathFlag = True
            qgis_app.setPrefixPath(myPath, myUseDefaultPathFlag)

        qgis_app.initQgis()
        #rint 'QGIS settings', qgis_app.showSettings()

    return qgis_app

