#
# Copyright (c) SAS Institute Inc.
#

import datetime
from pyramid import httpexceptions as web_exc
from pyramid.view import view_config
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from webob import UTC

from .. import url_sign
from ..auth import authenticated, authCheck
from ..db.models import DownloadFile, DownloadMetadata


def _one_file(request, dlfile, cust_id=None):
    if cust_id is not None:
        # Use a path with the cust_id encoded into it so that the entitlements
        # can be re-checked and the IP of the client that initiates the
        # download can be checked against the GeoIP filters associated with
        # those entitlements.
        path = request.route_path('cust_download_get',
                cust_id=cust_id, sha1=dlfile.file_sha1)
    else:
        path = request.route_path('downloads_get', sha1=dlfile.file_sha1)
    path_signed = url_sign.sign_path(request.cfg, path)
    out = {}
    out['links'] = [{
        'rel': 'self',
        'href': request.route_url('downloads_meta', sha1=dlfile.file_sha1),
        }]
    for column in DownloadFile.__table__.columns:
        column = column.name
        value = getattr(dlfile, column)
        if isinstance(value, datetime.datetime):
            value = value.astimezone(UTC)
        out[column] = unicode(value)
    out['metadata'] = meta = {}
    for meta_item in dlfile.meta_items:
        meta[meta_item.meta_key] = meta_item.value
    out['download_url'] = request.application_url + path_signed
    return out


@view_config(route_name='downloads_index', request_method='GET', renderer='json')
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


@view_config(route_name='downloads_customer', request_method='GET', renderer='json')
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


@view_config(route_name='downloads_meta', request_method='GET', renderer='json')
@authenticated('reader')
def downloads_meta_get(request):
    dlfile = request.db.query(DownloadFile).get(request.matchdict['sha1'])
    if dlfile is None:
        return web_exc.HTTPNotFound()
    return _one_file(request, dlfile)


@view_config(route_name='downloads_meta', request_method='DELETE', renderer='json')
@authenticated('mirror')
def downloads_meta_delete(request):
    dlfile = request.db.query(DownloadFile).get(request.matchdict['sha1'])
    if dlfile is None:
        return web_exc.HTTPNotFound()
    request.db.delete(dlfile)
    return {}


@view_config(route_name='downloads_add', request_method='POST', renderer='json')
@view_config(route_name='downloads_meta', request_method='PUT', renderer='json')
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
