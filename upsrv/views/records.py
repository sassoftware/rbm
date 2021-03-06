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


""" Cornice services.
"""
import logging
log = logging.getLogger(__name__)

import base64
import json
import datetime
import urllib

from conary.conaryclient import cml
from conary import errors as cnyerrors, versions
from conary.repository import errors as repoerrors

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPUnauthorized, HTTPBadRequest, HTTPRequestEntityTooLarge

from ..db.models import Record
from ..auth import cryptauth
from .. import filtering


@view_config(route_name='records', request_method='POST', renderer='json')
def records_add(request):
    # Records should not be larger than 1M
    maxSize = 1024 * 1024
    bodyLen = len(request.body)
    if bodyLen > maxSize:
        log.warning("Request too large from %s: %s bytes", request.client_addr,
                bodyLen)
        return HTTPRequestEntityTooLarge()
    authHeader = 'X-Conary-Entitlement'
    entString = request.headers.get(authHeader)
    if not entString:
        log.warning("Missing auth header `%s' from %s", authHeader,
                request.client_addr)
        return HTTPUnauthorized()

    ents = _decodeEntitlements(entString)
    # The entitlement class/server name is completely ignored
    cli = request.getConaryClient(entitlements=[x[1] for x in ents])

    cmlObj = cml.CML(cli.cfg)
    db = request.db
    newRecord = deserialize(request, Record)
    newRecord.entitlement_valid = True

    # Fetch the system model
    systemModel = newRecord.producers.get('conary-system-model', {}).get('data')
    if systemModel is None:
        log.warning("Missing system model from %s", request.client_addr)
        return HTTPBadRequest()
    # cml is very unicode unfriendly
    cmlObj.parse(systemModel.encode("ascii").split('\n'))
    troveTups = []
    for op in cmlObj.modelOps:
        if op.key == 'search':
            troveTups.append(op.item)
        elif op.key in ('install', 'update'):
            troveTups.extend(op.item)
    # Now find versioned troves
    versionedTroves = []
    for trvTup in troveTups:
        if not trvTup.version:
            continue
        if trvTup.version.startswith('/'):
            try:
                vv = versions.VersionFromString(trvTup.version)
            except cnyerrors.ParseError:
                continue
            if not hasattr(vv, 'trailingRevision'):
                # A branch. Unversioned, so ignore
                continue
        elif not trvTup.version.partition('/')[-1]:
            # Plain Label
            continue
        versionedTroves.append(trvTup)
    try:
        cli.repos.findTroves(None, versionedTroves)
    except (repoerrors.InsufficientPermission, repoerrors.TroveNotFound), e:
        log.warning("%s: bad entitlements %s for system model %s: %s",
                request.client_addr, ents, systemModel, e)
        newRecord.entitlement_valid = False

    newRecord.entitlements_json = json.dumps(ents)
    newRecord.client_address = request.client_addr
    # Does this record exist?
    record = db.query(Record).filter_by(uuid=newRecord.uuid).first()
    if record:
        return serialize(request, record)
    # Data under producers may be json
    for producerName, producerStruct in newRecord.producers.items():
        _processProducerData(producerName, producerStruct)
    newRecord.producers = json.dumps(newRecord.producers)
    db.add(newRecord)
    return serialize(request, newRecord)

def _processProducerData(producerName, producerStruct):
    attributes = producerStruct.get('attributes', {})
    if attributes.get('content-type') == 'application/json':
        producerData = producerStruct.get('data', '')
        if isinstance(producerData, basestring):
            try:
                producerData = json.loads(producerData)
            except ValueError:
                # invalid json
                attributes.pop('content-type', None)
        producerStruct.update(attributes=attributes, data=producerData)

def _decodeEntitlements(entString):
    ret = []
    arr = entString.split()
    while len(arr) >= 2:
        entClass, b64EntKey, arr = arr[0], arr[1], arr[2:]
        ret.append((entClass, base64.b64decode(b64EntKey)))
    return ret

@view_config(route_name='records', request_method='GET', renderer='json')
@cryptauth('records-reader')
def records_view(request):
    _qtempl = '?start={start}&limit={limit}'
    queryLimit = int(request.GET.get('limit', 100))
    queryStart = int(request.GET.get('start', 0))
    queryFilter = request.GET.get('filter')
    if queryFilter:
        _qtempl += '&filter={filter}'
        lexer = filtering.Lexer()
        try:
            qf = lexer.scan(queryFilter)
            expression = qf.expression(Record)
        except filtering.InvalidData:
            return HTTPBadRequest()
    db = request.db
    query = db.query(Record)
    if queryFilter:
        query = query.filter(expression)
        queryFilter = urllib.quote(queryFilter, safe='():=,\'"')
    count = query.count()
    # created_time is coming straight from the record, so we should not assume
    # it's chronologically correct.
    records = query.order_by('updated_time')
    records = records.offset(queryStart).limit(queryLimit)
    collection = dict(records=[ serialize(request, x) for x in records ])
    _href = request.route_url('records')
    links = [
            dict(rel='self', href=_href + _qtempl.format(
                start=queryStart, limit=queryLimit, filter=queryFilter)),
            dict(rel='first', href=_href + _qtempl.format(
                start=0, limit=queryLimit, filter=queryFilter)),
            ]
    if queryStart > 0:
        nstart = max(queryStart - queryLimit, 0)
        links.append(dict(rel='prev', href=_href + _qtempl.format(
            start=nstart, limit=queryLimit, filter=queryFilter)))
    if queryStart + queryLimit < count:
        nstart = queryStart + queryLimit
        links.append(dict(rel='next', href=_href + _qtempl.format(
            start=nstart, limit=queryLimit, filter=queryFilter)))

    collection.update(links=links, count=count)
    return collection

def deserialize(request, modelClass):
    jsonBody = request.json_body
    missingFields = []
    record = modelClass()
    for column in modelClass.__table__.columns:
        meta = column.info.get('recordCreate', None)
        if meta and meta.get('readOnly'):
            continue
        if meta and meta.get('required') and column.name not in jsonBody:
            missingFields.append(column.name)
            continue
        value = jsonBody[column.name]
#        if column.info.get('recordEncoding') == 'json':
#            value = json.dumps(value)
        if column.type.__class__.__name__ == 'DateTime':
            value = filtering.parseDate(value)
        setattr(record, column.name, value)
    if missingFields:
        raise Exception(missingFields)
    return record

def serialize(request, record):
    out = {}
    for column in record.__table__.columns:
        meta = column.info.get('recordDisplay', None)
        if meta and meta.get('hidden'):
            continue
        value = getattr(record, column.name)
        if column.info.get('recordEncoding') == 'json':
            value = json.loads(value)
        if isinstance(value, datetime.datetime):
            value = value.isoformat()
        out[column.name] = value
    return out
