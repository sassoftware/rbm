#
# Copyright (c) SAS Institute Inc.
#

import datetime
from conary.repository import errors as cny_errors
from pyramid.view import view_config
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from webob import UTC

from .. import url_sign
from ..auth import authenticated
from ..db.models import DownloadFile, DownloadMetadata


def _one_file(request, dlfile):
    path = request.route_path('downloads_get', sha1=dlfile.file_sha1)
    path_signed = url_sign.sign_path(request.cfg, path)
    out = {}
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


def _filter_files(files, request):
    repos = request.getConaryClient().repos
    try:
        has_files = repos.hasTroves(x.trove_tup for x in files)
        return [x for x in files if has_files[x.trove_tup]]
    except cny_errors.InsufficientPermission:
        return []


@view_config(route_name='downloads_index', request_method='GET', renderer='json')
def downloads_index(request):
    files = request.db.query(DownloadFile
            ).options(joinedload(DownloadFile.meta_items)
            ).order_by(desc(DownloadFile.file_modified)
            ).all()
    filtered = _filter_files(files, request)
    formatted = [_one_file(request, x) for x in filtered]
    return formatted


@view_config(route_name='downloads_index', request_method='POST', renderer='json')
def downloads_filter(request):
    return {}


@view_config(route_name='downloads_add', request_method='POST', renderer='json')
@authenticated
def downloads_add(request):
    infile = request.json_body
    dlfile = request.db.query(DownloadFile
            ).filter_by(file_sha1=infile['file_sha1']
            ).one()
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
