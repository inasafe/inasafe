from float_parameter import FloatParameter

class ResourceParameter(FloatParameter):
    def __init__(self, guid=None):
        super(ResourceParameter, self).__init__(guid)
        self._freuency = ''
