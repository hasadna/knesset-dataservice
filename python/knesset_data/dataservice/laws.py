# -*- coding: utf-8 -*-
import logging

from base import BaseKnessetDataServiceCollectionObject, KnessetDataServiceSimpleField, BaseKnessetDataServiceCollectionResource

logger = logging.getLogger('knesset_data.dataservice.laws')

class PrivateLaw(BaseKnessetDataServiceCollectionObject):
    SERVICE_NAME = "laws"
    METHOD_NAME = "privatelaw"
    DEFAULT_ORDER_BY_FIELD = "id"

    id = KnessetDataServiceSimpleField('plaw_id')
    number = KnessetDataServiceSimpleField('plaw_no')
    name = KnessetDataServiceSimpleField('plaw_name')
    subject = KnessetDataServiceSimpleField('plaw_subject')
    suggest_date = KnessetDataServiceSimpleField('plaw_suggest_dt')
    creation_date = KnessetDataServiceSimpleField('plaw_creation_dt')
    type_id = KnessetDataServiceSimpleField('plaw_type_id')
    link = KnessetDataServiceSimpleField('plaw_link')
    knesset_id = KnessetDataServiceSimpleField('knesset_id')

    def guess_link_url(self):
        return 'http://knesset.gov.il/privatelaw/data/%s/%s'%(self.knesset_id, self.link)


class PrivateLawResource(BaseKnessetDataServiceCollectionResource):
    collection = PrivateLaw
    object_name = "private law"
    get_latest_by_page_estimate = ('id', 5)  # order by id desc, with estimate of 5 laws per day up to given days param value


class PrivateLawMk(BaseKnessetDataServiceCollectionObject):
    SERVICE_NAME = "laws"
    METHOD_NAME = "privatelaw_mk"
    DEFAULT_ORDER_BY_FIELD = "plaw_mk_id"

    id = KnessetDataServiceSimpleField('plaw_mk_id')
    mk_id = KnessetDataServiceSimpleField('mk_id')
    law_number = KnessetDataServiceSimpleField('plaw_no')
    mk_suggest = KnessetDataServiceSimpleField('plaw_mk_suggest')
    plaw_id = KnessetDataServiceSimpleField('plaw_id')

    @classmethod
    def get_by_plaw_id(cls, plaw_id):
        query = 'plaw_id eq %s'%plaw_id
        params = {'$filter': query}
        return cls._get_all_pages(cls._get_url_base(), params)
