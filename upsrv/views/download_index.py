#
# Copyright (c) SAS Institute Inc.
#

from conary.repository import errors as cny_errors
from pyramid import httpexceptions as web_exc
from pyramid.view import view_config
from sqlalchemy import desc
from webob import UTC

from .. import url_sign
from ..db.models import DownloadFile


def _one_file(request, dlfile):
    path = request.route_path('downloads_get', sha1=dlfile.file_sha1)
    path_signed = url_sign.sign_path(request.cfg, path)
    url = request.application_url + path_signed
    return {
        'file_sha1':        dlfile.file_sha1,
        'file_type':        dlfile.file_type,
        'file_modified':    str(dlfile.file_modified.astimezone(UTC)),
        'file_basename':    dlfile.file_basename,
        'file_size':        dlfile.file_size,
        'trove_name':       dlfile.trove_name,
        'trove_version':    dlfile.trove_version,
        'trove_flavor':     dlfile.trove_flavor,
        'trove_timestamp':  dlfile.trove_timestamp,
        'download_url':     url,
        }


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
            ).order_by(desc(DownloadFile.file_modified)
            ).all()
    filtered = _filter_files(files, request)
    formatted = [_one_file(request, x) for x in filtered]
    return formatted


@view_config(route_name='downloads_index', request_method='POST', renderer='json')
def downloads_filter(request):
    return {}


@view_config(route_name='downloads_add', request_method='POST', renderer='json')
def downloads_add(request):
    if not request.checkWriter():
        return web_exc.HTTPForbidden()
    infile = request.json_body
    dlfile = request.db.query(DownloadFile
            ).filter_by(file_sha1=infile['file_sha1']
            ).one()
    if not dlfile:
        dlfile = DownloadFile()
        request.db.add(dlfile)
    for key, value in infile.iteritems():
        if key.startswith('file_') or key.startswith('trove_'):
            setattr(dlfile, key, value)
    request.db.add(dlfile)
