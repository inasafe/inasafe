# coding=utf-8
"""A registry implementation for parameters."""


class Registry(object):
    """A simple registry for keeping track of all parameters.

    We will use a singleton pattern to ensure that there is only
    one canonical registry. The registry can be used by parameters
    to register themselves and their GUID's.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Registry, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance
