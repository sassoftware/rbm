#
# Copyright (c) SAS Institute Inc.
#

import errno
import hashlib
import logging
import os
from conary.lib.util import copyfileobj, joinPaths
from pyramid import httpexceptions as web_exc
from pyramid.response import FileResponse
from pyramid.view import view_config

from .. import url_sign
from ..auth import authenticated
from ..db.models import DownloadFile

log = logging.getLogger(__name__)


@view_config(route_name='downloads_get', request_method='GET')
@view_config(route_name='cust_download_get', request_method='GET')
def downloads_get(request):
    if not url_sign.verify_request(request.cfg, request):
        return web_exc.HTTPForbidden("Authorization for this request has "
                "expired or is not valid")
    sha1 = request.matchdict['sha1']
    dlfiles = request.db.query(DownloadFile).filter_by(file_sha1=sha1).all()
    if not dlfiles:
        return web_exc.HTTPNotFound()
    if 'cust_id' in request.matchdict:
        # URL is bound to a specific customer so re-check the entitlement, both
        # to make sure it is still valid and to check the client IP against any
        # GeoIP filters.
        if not request.filterFiles(dlfiles,
                cust_id=request.matchdict['cust_id']):
            log.warning("Rejected download after revalidating entitlement")
            return web_exc.HTTPForbidden()
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


@view_config(route_name='downloads_put', request_method='PUT')
@authenticated('mirror')
def downloads_put(request):
    sha1 = request.matchdict['sha1']
    path = joinPaths(request.cfg.downloadDir, sha1)
    tmppath = path + '.tmp'
    digest = hashlib.sha1()

    inFile = None
    if 'x-uploaded-file' in request.headers:
        # The frontend proxy has already saved the request body to a
        # temporary location, so first try to rename it into place.
        try:
            os.rename(request.headers['x-uploaded-file'], tmppath)
        except OSError, err:
            if err.errno != errno.EXDEV:
                raise
            # Upload dir is on a different filesystem.
            inFile = open(request.headers['x-uploaded-file'], 'rb')
    else:
        # No offloading was done. Copy from the request body.
        inFile = request.body_file

    if inFile:
        # Copy and digest simultaneously
        with open(tmppath, 'wb') as fobj:
            try:
                copyfileobj(request.body_file, fobj, digest=digest)
                os.fsync(fobj)
            except IOError, err:
                log.warning("IOError during upload of %s: %s", path, str(err))
                raise web_exc.HTTPBadRequest()
    else:
        # Just digest
        with open(tmppath, 'rb+') as fobj:
            while True:
                data = fobj.read(1024)
                if not data:
                    break
                digest.update(data)
            os.fsync(fobj)

    if digest.hexdigest() != sha1:
        log.warning("SHA-1 check failed while uploading %s", sha1)
        os.unlink(tmppath)
        return web_exc.HTTPBadRequest("SHA-1 check failed")
    os.rename(tmppath, path)
    return web_exc.HTTPNoContent()


def purge_file(request, sha1):
    dlfiles = request.db.query(DownloadFile).filter_by(file_sha1=sha1).all()
    if dlfiles:
        # Still in use
        return
    path = joinPaths(request.cfg.downloadDir, sha1)
    try:
        os.unlink(path)
    except OSError, err:
        if err.args[0] != errno.ENOENT:
            raise
    else:
        log.info("Deleted %s", path)
