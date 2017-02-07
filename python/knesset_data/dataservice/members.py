# -*- coding: utf-8 -*-
import logging
from base import BaseKnessetDataServiceCollectionObject, KnessetDataServiceSimpleField, BaseKnessetDataServiceCollectionResource

logger = logging.getLogger('knesset_data.dataservice.members')


class Member(BaseKnessetDataServiceCollectionObject):
    SERVICE_NAME = "members"
    METHOD_NAME = "View_mk_individual"
    DEFAULT_ORDER_BY_FIELD = "mk_individual_id"

    ORDERED_FIELDS = [
        ("id", KnessetDataServiceSimpleField('mk_individual_id', "integer")),
        ("army_rank_id", KnessetDataServiceSimpleField('army_rank_id', 'string')),
        ("army_history_desc", KnessetDataServiceSimpleField('army_history_desc', 'string')),
        ("army_history_desc_eng", KnessetDataServiceSimpleField('army_history_desc_eng', 'string')),
        ("country_id", KnessetDataServiceSimpleField('country_id', 'integer')),
        ("country_desc", KnessetDataServiceSimpleField('country_desc', 'string')),
        ("country_desc_eng", KnessetDataServiceSimpleField('country_desc_eng', 'string')),
        ("minority_type_id", KnessetDataServiceSimpleField('minority_type_id', 'integer')),
        ("education_id", KnessetDataServiceSimpleField('education_id', 'integer')),
        ("education_desc", KnessetDataServiceSimpleField('education_desc', 'string')),
        ("education_desc_eng", KnessetDataServiceSimpleField('education_desc_eng', 'string')),
        ("marital_status_id", KnessetDataServiceSimpleField('marital_status_id', 'integer')),
        ("city_id", KnessetDataServiceSimpleField('city_id', 'integer')),
        ("mk_status_id", KnessetDataServiceSimpleField('mk_status_id', 'integer')),
        ("name", KnessetDataServiceSimpleField('mk_individual_name', 'string')),
        ("name_eng", KnessetDataServiceSimpleField('mk_individual_name_eng', 'string')),
        ("first_name", KnessetDataServiceSimpleField('mk_individual_first_name', 'string')),
        ("first_name_eng", KnessetDataServiceSimpleField('mk_individual_first_name_eng', 'string')),
        ("gender", KnessetDataServiceSimpleField('mk_individual_gender', 'string')),
        ("birth_date", KnessetDataServiceSimpleField('mk_individual_birth_date', 'string')),
        ("immigration_date", KnessetDataServiceSimpleField('mk_individual_immigration_date', 'string')),
        ("children_number", KnessetDataServiceSimpleField('mk_individual_children_number', 'string')),
        ("death_date", KnessetDataServiceSimpleField('mk_individual_death_date', 'string')),
        ("email", KnessetDataServiceSimpleField('mk_individual_email', 'string')),
        ("email_on", KnessetDataServiceSimpleField('mk_individual_email_on', 'string')),
        ("photo", KnessetDataServiceSimpleField('mk_individual_photo', 'string')),
        ("phone1", KnessetDataServiceSimpleField('mk_individual_phone1', 'string')),
        ("phone2", KnessetDataServiceSimpleField('mk_individual_phone2', 'string')),
        ("phone_fax", KnessetDataServiceSimpleField('mk_individual_phone_fax', 'string')),
        ("present", KnessetDataServiceSimpleField('mk_individual_present', 'string')),
        ("public_activity", KnessetDataServiceSimpleField('mk_individual_public_activity', 'string')),
        ("public_activity_eng", KnessetDataServiceSimpleField('mk_individual_public_activity_eng', 'string')),
        ("note", KnessetDataServiceSimpleField('mk_individual_note', 'string')),
        ("note_eng", KnessetDataServiceSimpleField('mk_individual_note_eng', 'string')),
    ]

    @classmethod
    def get_all_present_members(cls, proxies=None):
        params = {'$filter': 'mk_individual_present eq true'}
        return cls._get_all_pages(cls._get_url_base(), params, proxies=proxies)


class MembersResource(BaseKnessetDataServiceCollectionResource):
    collection = Member
    object_name = "member"
    track_generated_objects = True
