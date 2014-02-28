""" Cornice services.
"""
import json
import datetime

from pyramid.view import view_config

#from ..auth import authenticated
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
    db.add(newRecord)
    return serialize(request, newRecord)

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
        if column.info.get('recordEncoding') == 'json':
            value = json.dumps(value)
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
        if column.info.get('encoding') == 'json':
            value = json.loads(value)
        if isinstance(value, datetime.datetime):
            value = value.isoformat()
        out[column.name] = unicode(value)
    return out




