"""Helper module for gui test suite
"""

import os
import sys
from qgis.core import QgsApplication

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
        if 'QGISPATH' in os.environ:
            myPath = os.environ['QGISPATH']
            myUseDefaultPathFlag = True
            qgis_app.setPrefixPath(myPath, myUseDefaultPathFlag)

        qgis_app.initQgis()

    return qgis_app


def getUiState(ui):
    """Get state of the 3 combos on the form ui
    """

    myHazard = str(ui.cboHazard.currentText())
    myExposure = str(ui.cboExposure.currentText())
    myImpactFunction = str(ui.cboFunction.currentText())

    myRunButton = ui.pbnRunStop.isEnabled()

    return {'Hazard': myHazard,
            'Exposure': myExposure,
            'Impact Function': myImpactFunction,
            'Run Button Enabled': myRunButton}
