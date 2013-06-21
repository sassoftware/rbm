#
# Copyright (c) SAS Institute Inc.
#

from pyramid.view import view_config

from ..auth import authenticated
from ..db.models import CustomerEntitlement


@view_config(route_name='cust_ents', request_method='GET', renderer='json')
@authenticated('mirror')
def entitlements_get(request):
    return [x.entitlement for x in request.db.query(CustomerEntitlement
        ).filter_by(cust_id=request.matchdict['cust_id']
        ).all()]


@view_config(route_name='cust_ents', request_method='PUT', renderer='json')
@authenticated('mirror')
def entitlements_put(request):
    request.db.query(CustomerEntitlement
            ).filter_by(cust_id=request.matchdict['cust_id']
            ).delete()
    for entitlement in request.json_body:
        model = CustomerEntitlement()
        model.cust_id = request.matchdict['cust_id']
        model.entitlement = entitlement
        request.db.add(model)
    return 'ok'
