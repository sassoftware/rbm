#
# Copyright (c) SAS Institute Inc.
#

"""
JSON renderer for Pyramid that sends Content-Type as "text/plain" for browsers.
"""

import json


def json_render(value, system):
    request = system.get('request')
    if request is not None:
        response = request.response
        ct = response.content_type
        if ct == response.default_content_type:
            if 'text/html' in request.headers.get('Accept', ''):
                # Smells like a browser
                response.content_type = 'text/plain'
            else:
                response.content_type = 'application/json'
    return json.dumps(value, sort_keys=True, indent=2)


def json_render_factory(info):
    return json_render
