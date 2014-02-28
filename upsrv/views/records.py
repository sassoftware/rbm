""" Cornice services.
"""
import json
import datetime

from pyramid.view import view_config

from ..auth import authenticated
from ..db.models import Record


@view_config(route_name='records', request_method='POST', renderer='json')
def records_add(request):
    db = request.db
    newRecord = deserialize(request, Record)
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
        try:
            producerData = json.loads(producerData)
        except ValueError:
            # invalid json
            attributes.pop('content-type', None)
        producerStruct.update(attributes=attributes, data=producerData)

@view_config(route_name='records', request_method='GET', renderer='json')
def records_view(request):
    queryLimit = int(request.GET.get('limit', 100))
    queryStart = int(request.GET.get('start', 0))
    db = request.db
    query = db.query(Record)
    count = query.count()
    records = query.order_by('created_time').offset(queryStart).limit(queryLimit)
    collection = dict(records=[ serialize(request, x) for x in records ])
    _href = request.route_url('records')
    _qtempl = '?start={start}&limit={limit}'
    links = [
            dict(rel='self', href=_href + _qtempl.format(
                start=queryStart, limit=queryLimit)),
            dict(rel='first', href=_href + _qtempl.format(
                start=0, limit=queryLimit)),
            ]
    if queryStart > 0:
        nstart = max(queryStart - queryLimit, 0)
        links.append(dict(rel='prev', href=_href + _qtempl.format(
            start=nstart, limit=queryLimit)))
    if queryStart + queryLimit < count:
        nstart = queryStart + queryLimit
        links.append(dict(rel='next', href=_href + _qtempl.format(
            start=nstart, limit=queryLimit)))

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
            value = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
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
