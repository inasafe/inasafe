# coding=utf-8
"""Exceptions related to parameters implementation."""


class InvalidMinimumError(Exception):
    """Error raised when minimum is not valid e.g. exceeds maximum."""
    pass


class InvalidMaximumError(Exception):
    """Error raised when maximum is not valid e.g. less than minimum."""
    pass


class ValueOutOfBounds(Exception):
    """Error raised when a value is outside allowed range of min, max."""
    pass


class CollectionLengthError(Exception):
    """Error raised when a collection is too long or too short."""
    pass
