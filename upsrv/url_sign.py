#
# Copyright (c) SAS Institute Inc.
#

"""
Sign URLs in a way that can be validated by any mirror with the right key,
without shared state.

The following query parameters are added to the URL during signing:
* e - When the URL expires, in seconds since the UNIX epoch
* c - Comma-seperated list of constraining "tags". For example, such a tag
      might indicate that the URL is export-restricted and cannot be downloaded
      from certain countries.  If the tag is not recognized the download should
      fail.
* s - The actual signature. Must come last.
"""

import hashlib
import hmac
import time
import urlparse


def sign_path(cfg, path):
    if not cfg.downloadSignatureKey:
        raise RuntimeError("At least one downloadSignatureKey must be configured")
    expires = int(time.time() + cfg.downloadSignatureExpiry)
    path += ('&' if '?' in path else '?') + 'e=%d' % expires
    mac = hmac.new(cfg.downloadSignatureKey[0], path, hashlib.sha1)
    path += '&s=' + mac.hexdigest()
    return path


def verify_request(request):
    cfg = request.cny_cfg
    # Reconstruct the original path. Discard any query parameters that come
    # after the signature, because they can't be trusted.
    query = request.query_string
    if '&s=' not in query:
        # No signature
        return False, None
    query, sig = query.split('&s=', 1)
    sig = sig.split('&')[0].split(';')[0]
    path = request.path_info + '?' + query
    # Try all configured keys to find a match
    if not cfg.downloadSignatureKey:
        raise RuntimeError("At least one downloadSignatureKey must be configured")
    found = False
    for key in cfg.downloadSignatureKey:
        sig2 = hmac.new(key, path, hashlib.sha1).hexdigest()
        if sig == sig2:
            found = True
            break
    if not found:
        # Signature not valid
        return False, None
    # Now look at the query parameters and ensure that all constraints are met.
    constraints = set()
    for name, value in urlparse.parse_qsl(query):
        if name == 'e':
            # Expiration
            expiry = int(value)
            if time.time() > expiry:
                return False, None
        elif name == 'c':
            # Constraint
            constraints.update(value.split(','))
    # Everything checks out, return the constraints to the caller for
    # verification
    return True, constraints
