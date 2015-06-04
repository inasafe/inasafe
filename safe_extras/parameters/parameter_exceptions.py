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


class RequiredException(Exception):
    """Exception raised when a parameter is required but not assigned.
    """
    pass


class InvalidValidationException(Exception):
    """Exception raised when there is validation breaker in ParameterContainer.
    """
    pass


class ValueNotAllowedException(Exception):
    """Exception raised when the value assigned in the ListParameter contains
    items that didn't exists in options list
    """
    pass
