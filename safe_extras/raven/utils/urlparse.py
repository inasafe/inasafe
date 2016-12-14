from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import urllib.parse as _urlparse


def register_scheme(scheme):
    for method in [s for s in dir(_urlparse) if s.startswith('uses_')]:
        uses = getattr(_urlparse, method)
        if scheme not in uses:
            uses.append(scheme)


urlparse = _urlparse.urlparse
