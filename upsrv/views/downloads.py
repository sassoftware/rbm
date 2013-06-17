#
# Copyright (c) SAS Institute Inc.
#

import errno
import logging
import os
from conary.repository import errors as cny_errors
from pyramid import httpexceptions as web_exc
from pyramid.response import FileResponse
from pyramid.view import view_config
from sqlalchemy import desc
from webob import UTC

from .. import url_sign
from ..models import DownloadFile

log = logging.getLogger(__name__)


def _one_file(request, dlfile):
    tup = dlfile.trove_tup
    path = request.route_path('downloads_get', sha1=dlfile.file_sha1)
    path_signed = url_sign.sign_path(request.cny_cfg, path)
    url = request.application_url + path_signed
    return {
        'file_id':          dlfile.file_id,
        'file_type':        dlfile.file_type,
        'file_modified':    str(dlfile.file_modified.astimezone(UTC)),
        'file_basename':    dlfile.file_basename,
        'file_sha1':        dlfile.file_sha1,
        'trove_name':       tup.name,
        'trove_version':    str(tup.version),
        'trove_flavor':     str(tup.flavor),
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


@view_config(route_name='downloads_get', request_method='GET')
def downloads_get(request):
    if not url_sign.verify_request(request):
        return web_exc.HTTPForbidden("Authorization for this request has "
                "expired or is not valid")
    sha1 = request.matchdict['sha1']
    dlfiles = request.db.query(DownloadFile).filter_by(file_sha1=sha1).all()
    if not dlfiles:
        return web_exc.HTTPNotFound()
    dlfile = dlfiles[0]
    path = os.path.join(request.cny_cfg.downloadDir, dlfile.file_sha1)
    try:
        response = FileResponse(path, request=request,
                content_type='application/octet-stream')
    except (OSError, IOError), err:
        if err.args[0] == errno.ENOENT:
            log.warning("Download file %s is missing (basename='%s')", path,
                    dlfile.file_basename)
            return web_exc.HTTPNotFound()
        raise
    response.headers['Content-Sha1'] = sha1
    response.headers['Content-Disposition'] = ('attachment; filename=' +
            dlfile.file_basename.encode('utf8'))
    return response
