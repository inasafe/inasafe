# coding=utf-8

from PyQt4.QtCore import QSettings
from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.GeoAlgorithmExecutionException import (
    GeoAlgorithmExecutionException)
from processing.modeler import ModelerAlgorithm
from processing.gui.AlgorithmExecutor import runalg
from safe.utilities.i18n import tr


class ModelExecutor(object):
    """Class to run a Processing model."""
    def __init__(self, file_path):
        """Constructor

        :param file_path: The file path to the model.
        :type file_path: str
        """
        self.file_path = file_path
        model = ModelerAlgorithm.ModelerAlgorithm.fromFile(file_path)
        self.model = model.getCopy()

    def set_parameters(self, parameters):
        """Set parameters to the model.

        :param parameters: The list of parameters.
        :type parameters: tuple
        """
        i = 0
        for param in self.model.parameters:
            if not param.hidden:
                param.setValue(parameters[i])
                i += 1

        for output in self.model.outputs:
            if not output.hidden:
                output.setValue(parameters[i])
                i += 1

    def validate_parameters(self):
        """Check parameters and layers.

        It will return True if the model can be launched or not.
        It will return a message if something might be wrong wit the model.

        :return: Tuple if it's not critical and a message.
        :rtype: (boolean, str)
        """
        # noinspection PyProtectedMember
        msg = self.model._checkParameterValuesBeforeExecuting()
        if msg:
            return False, msg

        if not self.model.checkInputCRS():
            msg = tr('Warning: Not all input layers use the same CRS.\n'
                     'This can cause unexpected results.')
            return True, msg
        else:
            return True, None

    def run(self):
        """Run the model.

        :returns: A two-tuple where the first element is a Boolean reflecting
         the status of the results and second one is either a message
         indicating why Processing failed or the raw result from Processing.
        :rtype: tuple
        """
        settings = QSettings()
        inasafe_flag = bool(settings.value(
            'inasafe/useSelectedFeaturesOnly', False, type=bool))
        processing_flag = ProcessingConfig.getSetting(
            ProcessingConfig.USE_SELECTED)

        # We use the InaSAFE settings instead of the Processing one.
        if inasafe_flag != processing_flag:
            ProcessingConfig.setSettingValue(
                ProcessingConfig.USE_SELECTED, inasafe_flag)

        try:
            # Add progress if available.
            result = runalg(self.model, None)
        # pylint: disable=catching-non-exception
        except GeoAlgorithmExecutionException as e:
            return False, e.msg

        # We restore the old behaviour from Processing.
        if inasafe_flag != processing_flag:
            ProcessingConfig.setSettingValue(
                ProcessingConfig.USE_SELECTED, processing_flag)

        return True, result
