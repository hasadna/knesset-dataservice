# -*- coding: utf-8 -*-
import logging
from base import BaseKnessetDataServiceCollectionObject, KnessetDataServiceSimpleField
from knesset_data.datapackages.base import CsvResource

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


class MembersResource(CsvResource):

    def __init__(self, name, parent_datapackage_path):
        json_table_schema = Member.get_json_table_schema()
        super(MembersResource, self).__init__(name, parent_datapackage_path, json_table_schema)
        self._generated_members = []

    def _data_generator(self, **make_kwargs):
        proxies = make_kwargs.get('proxies')
        if make_kwargs.get('member_ids'):
            self.logger.info('fetching member ids: {}'.format(make_kwargs["member_ids"]))
            self.descriptor["description"] = "specific member ids"
            members = (Member.get(member_id, proxies=proxies)
                          for member_id in make_kwargs["member_ids"])
        elif make_kwargs.get('all_members'):
            self.logger.info('fetching all members')
            self.descriptor["description"] = "all members"
            members = Member.get_all(proxies=proxies)
        else:
            self.logger.info('fetching present members')
            self.descriptor["description"] = "present members"
            members = Member.get_all_present_members(proxies=proxies)
        for member in members:
            self.logger.debug('appending member {}'.format(member.id))
            self._generated_members.append(member)
            yield member.all_field_values()

    def get_generated_members(self):
        # this can be used by other resources which depend on list of members
        return self._generated_members
