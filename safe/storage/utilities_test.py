# coding=utf-8
"""**Utilities to to support test suite**
"""

import types


def _same_API(X, Y, exclude=None):
    """Check that public methods of X also exist in Y
    """

    if exclude is None:
        exclude = []

    for name in dir(X):

        # Skip internal symbols
        if name.startswith('_'):
            continue

        # Skip explicitly excluded methods
        if name in exclude:
            continue

        # Check membership of methods
        attr = getattr(X, name)
        if isinstance(attr, types.MethodType):
            if name not in dir(Y):
                msg = ('Method "%s" of "%s" was not found in "%s"'
                       % (name, X, Y))
                raise Exception(msg)


def same_API(X, Y, exclude=None):
    """Check that public methods of X and Y are the same.

    :param X: Python objects to compare api
    :type X: object

    :param Y: Python objects to compare api
    :type Y: object

    :param exclude: List of names to exclude from comparison or None
    :type exclude: list, None
    """

    _same_API(X, Y, exclude=exclude)
    _same_API(Y, X, exclude=exclude)

    return True
