#
# Copyright (c) SAS Institute Inc.
#

import errno
import hashlib
import logging
import os
from conary.lib.util import copyfileobj, joinPaths
from conary.repository import errors as cny_errors
from pyramid import authentication
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
    path_signed = url_sign.sign_path(request.cfg, path)
    url = request.application_url + path_signed
    return {
        'file_id':          dlfile.file_id,
        'file_type':        dlfile.file_type,
        'file_modified':    str(dlfile.file_modified.astimezone(UTC)),
        'file_basename':    dlfile.file_basename,
        'file_sha1':        dlfile.file_sha1,
        'file_size':        dlfile.file_size,
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


def _check_auth(request):
    if not request.cfg.downloadWriterPassword:
        return False
    authz = authentication.BasicAuthAuthenticationPolicy(None)
    creds = authz._get_credentials(request)
    return creds == ('dlwriter', request.cfg.downloadWriterPassword)


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
    if not url_sign.verify_request(request.cfg, request):
        return web_exc.HTTPForbidden("Authorization for this request has "
                "expired or is not valid")
    sha1 = request.matchdict['sha1']
    dlfiles = request.db.query(DownloadFile).filter_by(file_sha1=sha1).all()
    if not dlfiles:
        return web_exc.HTTPNotFound()
    dlfile = dlfiles[0]
    path = joinPaths(request.cfg.downloadDir, dlfile.file_sha1)
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


@view_config(route_name='downloads_get', request_method='PUT')
def downloads_put(request):
    if not _check_auth(request):
        return web_exc.HTTPForbidden()
    sha1 = request.matchdict['sha1']
    path = joinPaths(request.cfg.downloadDir, sha1)
    tmppath = path + '.tmp'
    digest = hashlib.sha1()
    with open(tmppath, 'wb') as fobj:
        copyfileobj(request.body_file, fobj, digest=digest)
        fobj.flush()
        os.fsync(fobj)
    if digest.hexdigest() != sha1:
        log.warning("SHA-1 check failed while uploading %s", sha1)
        os.unlink(tmppath)
        return web_exc.HTTPBadRequest("SHA-1 check failed")
    os.rename(tmppath, path)
    return web_exc.HTTPNoContent()
