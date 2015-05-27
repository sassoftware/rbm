#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""
Sign URLs in a way that can be validated by any mirror with the right key,
without shared state.

The following query parameters are added to the URL during signing:
* e - When the URL expires, in seconds since the UNIX epoch
* s - The actual signature. Must come last.
"""

import hashlib
import hmac
import time
import urlparse
from pyramid.util import strings_differ


def sign_path(cfg, path):
    if not cfg.downloadSignatureKey:
        raise RuntimeError("At least one downloadSignatureKey must be configured")
    expires = int(time.time() + cfg.downloadSignatureExpiry)
    path += ('&' if '?' in path else '?') + 'e=%d' % expires
    mac = hmac.new(cfg.downloadSignatureKey[0], path, hashlib.sha1)
    path += '&s=' + mac.hexdigest()
    return path


def verify_request(cfg, request):
    # Reconstruct the original path. Discard any query parameters that come
    # after the signature, because they can't be trusted.
    query = request.query_string
    if '&s=' not in query:
        # No signature
        return False
    query, sig = query.split('&s=', 1)
    sig = sig.split('&')[0].split(';')[0]
    path = request.path_info + '?' + query
    # Try all configured keys to find a match
    if not cfg.downloadSignatureKey:
        raise RuntimeError("At least one downloadSignatureKey must be configured")
    found = False
    for key in cfg.downloadSignatureKey:
        sig2 = hmac.new(key, path, hashlib.sha1).hexdigest()
        # Use constant-time comparison to avoid timing attacks.
        if not strings_differ(sig, sig2):
            found = True
            break
    if not found:
        # Signature not valid
        return False
    # Now look at the query parameters and ensure that all constraints are met.
    for name, value in urlparse.parse_qsl(query):
        if name == 'e':
            # Expiration
            expiry = int(value)
            if time.time() > expiry:
                return False
    # Everything checks out, return the constraints to the caller for
    # verification
    return True
