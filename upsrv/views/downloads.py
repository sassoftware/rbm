#
# Copyright (c) SAS Institute Inc.
#

from conary.repository import errors as cny_errors
from pyramid.view import view_config
from sqlalchemy import desc
from webob import UTC

from ..models import DownloadFile


def _one_file(dlfile):
    tup = dlfile.trove_tup
    return {
        'file_id':          dlfile.file_id,
        'file_type':        dlfile.file_type,
        'file_modified':    str(dlfile.file_modified.astimezone(UTC)),
        'file_basename':    dlfile.file_basename,
        'trove_name':       tup.name,
        'trove_version':    str(tup.version),
        'trove_flavor':     str(tup.flavor),
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
    formatted = [_one_file(x) for x in filtered]
    return formatted


@view_config(route_name='downloads_index', request_method='POST', renderer='json')
def downloads_filter(request):
    return {}


@view_config(route_name='downloads_get', request_method='GET')
def downloads_get(request):
    request.response.body = repr(request.matchdict)
    request.response.content_type = 'text/plain'
    return request.response
