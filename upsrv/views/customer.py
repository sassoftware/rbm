#
# Copyright (c) SAS Institute Inc.
#

from pyramid.view import view_config

from ..auth import authenticated
from ..db.models import CustomerEntitlements


@view_config(route_name='cust_ents', request_method='GET', renderer='json')
@authenticated
def entitlements_get(request):
    return [x.entitlement for x in request.db.query(CustomerEntitlements
        ).filter_by(cust_id=request.matchdict['cust_id']
        ).all()]


@view_config(route_name='cust_ents', request_method='PUT', renderer='json')
@authenticated
def entitlements_put(request):
    request.db.query(CustomerEntitlements
            ).filter_by(cust_id=request.matchdict['cust_id']
            ).delete()
    for entitlement in request.json_body:
        model = CustomerEntitlements()
        model.cust_id = request.matchdict['cust_id']
        model.entitlement = entitlement
        request.db.add(model)
    return 'ok'
