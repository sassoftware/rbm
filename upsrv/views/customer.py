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


from pyramid.view import view_config

from ..auth import authenticated
from ..db.models import CustomerEntitlement


@view_config(route_name='cust_ents', request_method='GET', renderer='json')
@authenticated('mirror')
def entitlements_get(request):
    return [x.entitlement for x in request.db.query(CustomerEntitlement
        ).filter_by(cust_id=request.matchdict['cust_id']
        ).all()]


@view_config(route_name='cust_ent_put', request_method='PUT', renderer='json')
@authenticated('mirror')
def entitlements_put(request):
    db = request.db
    new_cust_keys = request.json_body
    old_cust_keys = {}
    keys = []
    last_id = None
    CE = CustomerEntitlement
    for cust_id, key in db.query(CE
            ).order_by(CE.cust_id, CE.entitlement
            ).values(CE.cust_id, CE.entitlement):
        if last_id and cust_id != last_id:
            old_cust_keys[last_id] = keys
            keys = []
        keys.append(key)
        last_id = cust_id
    if last_id:
        old_cust_keys[last_id] = keys

    for cust_id, new_keys in new_cust_keys.iteritems():
        old_keys = old_cust_keys.get(cust_id)
        if old_keys != new_keys:
            db.query(CE).filter_by(cust_id=cust_id).delete()
            for key in new_keys:
                db.add(CE(cust_id=cust_id, entitlement=key))

    for cust_id in list(set(old_cust_keys) - set(new_cust_keys)):
        db.query(CE).filter_by(cust_id=cust_id).delete()
