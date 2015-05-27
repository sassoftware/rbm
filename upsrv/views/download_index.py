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


import datetime
from pyramid import httpexceptions as web_exc
from pyramid.view import view_config
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from webob import UTC

from .download_content import purge_file
from .. import url_sign
from ..auth import authenticated, authCheck
from ..db.models import DownloadFile, DownloadMetadata


def _one_file(request, dlfile, cust_id=None):
    if cust_id is not None:
        # Use a path with the cust_id encoded into it so that the entitlements
        # can be re-checked and the IP of the client that initiates the
        # download can be checked against the GeoIP filters associated with
        # those entitlements.
        path = request.route_path('customer_content',
                cust_id=cust_id, sha1=dlfile.file_sha1)
    else:
        path = request.route_path('image_content', sha1=dlfile.file_sha1)
    path_signed = url_sign.sign_path(request.cfg, path)
    out = {}
    out['links'] = [
        {
        'rel': 'self',
        'href': request.route_url('image', sha1=dlfile.file_sha1),
        },
        {
        'rel': 'getContent',
        'href': request.application_url + path_signed,
        },
        {
        'rel': 'putContent',
        'method': 'PUT',
        'href': request.route_url('image_content', sha1=dlfile.file_sha1),
        },
        ]
    for column in DownloadFile.__table__.columns:
        column = column.name
        value = getattr(dlfile, column)
        if isinstance(value, datetime.datetime):
            value = value.astimezone(UTC)
        out[column] = unicode(value)
    out['metadata'] = meta = {}
    for meta_item in dlfile.meta_items:
        meta[meta_item.meta_key] = meta_item.value
    return out


@view_config(route_name='images_index', request_method='GET', renderer='json')
def downloads_index(request):
    files = request.db.query(DownloadFile
            ).options(joinedload(DownloadFile.meta_items)
            ).order_by(desc(DownloadFile.file_modified)
            ).all()
    if not authCheck(request, 'reader') and not authCheck(request, 'mirror'):
        # Permit authenticated clients to see all files, otherwise show only
        # public ones
        files = request.filterFiles(files)
    return [_one_file(request, x) for x in files]


@view_config(route_name='customer_images', request_method='GET', renderer='json')
@authenticated('reader')
def downloads_customer(request):
    cust_id = request.matchdict['cust_id']
    assert cust_id is not None
    files = request.db.query(DownloadFile
            ).options(joinedload(DownloadFile.meta_items)
            ).order_by(desc(DownloadFile.file_modified)
            ).all()
    files = request.filterFiles(files, cust_id=cust_id)
    return [_one_file(request, x, cust_id=cust_id) for x in files]


@view_config(route_name='image', request_method='GET', renderer='json')
@authenticated('reader')
def downloads_meta_get(request):
    dlfile = request.db.query(DownloadFile).get(request.matchdict['sha1'])
    if dlfile is None:
        return web_exc.HTTPNotFound()
    return _one_file(request, dlfile)


@view_config(route_name='image', request_method='DELETE', renderer='json')
@authenticated('mirror')
def downloads_meta_delete(request):
    dlfile = request.db.query(DownloadFile).get(request.matchdict['sha1'])
    if dlfile is None:
        return web_exc.HTTPNotFound()
    request.db.delete(dlfile)
    purge_file(request, dlfile.file_sha1)
    return {}


@view_config(route_name='images_index', request_method='POST', renderer='json')
@view_config(route_name='image', request_method='PUT', renderer='json')
@authenticated('mirror')
def downloads_add(request):
    infile = request.json_body
    if 'sha1' in request.matchdict:
        infile['file_sha1'] = request.matchdict['sha1']
    dlfile = request.db.query(DownloadFile
            ).filter_by(file_sha1=infile['file_sha1']
            ).first()
    if not dlfile:
        dlfile = DownloadFile()
        request.db.add(dlfile)
    for column in DownloadFile.__table__.columns:
        column = column.name
        if column in infile:
            setattr(dlfile, column, infile[column])
    for meta_item in dlfile.meta_items:
        request.db.delete(meta_item)
    for key, value in infile.get('metadata', {}).iteritems():
        meta_item = DownloadMetadata()
        meta_item.meta_key = key
        meta_item.value = value
        dlfile.meta_items.append(meta_item)
    dlfile = request.db.query(DownloadFile).get(infile['file_sha1'])
    return _one_file(request, dlfile)
