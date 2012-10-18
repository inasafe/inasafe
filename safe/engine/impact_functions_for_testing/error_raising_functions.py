from safe.impact_functions.core import FunctionProvider

# TODO (MB) Write a test that calls this function and expects this to be in the
# results box
#Error:
#An exception occurred when calculating the results
#Problem:
#Exception : AHAHAH I got you
#Click for Diagnostic Information:


class ExceptionRaisingImpactFunction(FunctionProvider):
    """Risk plugin for error Rising

    :param requires category=='hazard'
                    layertype=='raster'

    :param requires category=='exposure' and \
                    layertype=='raster'
    """

    title = 'Exception riser'

    @staticmethod
    def run(layers):
        """Risk plugin for tephra impact
        """
        del layers
        raise Exception('AHAHAH I got you')


# TODO (MB) Write a test that calls this function and expects this to be in the
# results box
#Error:
#An exception occurred when calculating the results
#Problem:
#AttributeError : 'NoneType' object has no attribute 'keywords'
#Click for Diagnostic Information:

class NoneReturningImpactFunction(FunctionProvider):
    """Risk plugin for error Rising

    :param requires category=='hazard'
                    layertype=='raster'

    :param requires category=='exposure' and \
                    layertype=='raster'
    """

    title = 'None returner'

    @staticmethod
    def run(layers):
        """Risk plugin for tephra impact
        """
        del layers

        return None
