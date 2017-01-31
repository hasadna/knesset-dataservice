# -*- coding: utf-8 -*-
import logging
import os
import datetime

from base import (
    BaseKnessetDataServiceCollectionObject, BaseKnessetDataServiceFunctionObject,
    KnessetDataServiceSimpleField, KnessetDataServiceLambdaField
)
from knesset_data.protocols.committee import CommitteeMeetingProtocol
from knesset_data.datapackages.base import CsvResource, BaseDatapackage, BaseResource

logger = logging.getLogger('knesset_data.dataservice.committees')

IS_COMMITTEE_ACTIVE = 'committee_end_date eq null'
COMMITTEE_HAS_PORTAL_LINK = 'committee_portal_link ne null'


class Committee(BaseKnessetDataServiceCollectionObject):
    SERVICE_NAME = "committees"
    METHOD_NAME = "View_committee"
    DEFAULT_ORDER_BY_FIELD = "id"

    ORDERED_FIELDS = [
        ("id", KnessetDataServiceSimpleField('committee_id', "integer")),
        ("type_id", KnessetDataServiceSimpleField('committee_type_id', "integer")),
        ("parent_id", KnessetDataServiceSimpleField('committee_parent_id', "integer")),
        ("name", KnessetDataServiceSimpleField('committee_name', "string")),
        ("name_eng", KnessetDataServiceSimpleField('committee_name_eng', "string")),
        ("name_arb", KnessetDataServiceSimpleField('committee_name_arb', "string")),
        ("begin_date", KnessetDataServiceSimpleField('committee_begin_date', "datetime")),
        ("end_date", KnessetDataServiceSimpleField('committee_end_date', "datetime")),
        ("description", KnessetDataServiceSimpleField('committee_desc', "string")),
        ("description_eng", KnessetDataServiceSimpleField('committee_desc_eng', "string")),
        ("description_arb", KnessetDataServiceSimpleField('committee_desc_arb', "string")),
        ("note", KnessetDataServiceSimpleField('committee_note', "string")),
        ("note_eng", KnessetDataServiceSimpleField('committee_note_eng', "string")),
        ("portal_link", KnessetDataServiceSimpleField('committee_portal_link', "string")),
    ]

    @classmethod
    def get_all(cls, proxies=None):
        return cls._get_all_pages(cls._get_url_base(), proxies=proxies)

    @classmethod
    def get_all_active_committees(cls, has_portal_link=True, proxies=None):
        if has_portal_link:
            query = ' '.join((IS_COMMITTEE_ACTIVE, 'and', COMMITTEE_HAS_PORTAL_LINK))
        else:
            query = IS_COMMITTEE_ACTIVE
        params = {'$filter': query}
        return cls._get_all_pages(cls._get_url_base(), params, proxies=proxies)


class CommitteesResource(CsvResource):

    def __init__(self, name, parent_datapackage_path):
        json_table_schema = Committee.get_json_table_schema()
        super(CommitteesResource, self).__init__(name, parent_datapackage_path, json_table_schema)

    def _data_generator(self, **make_kwargs):
        for committee in self._get_committees(make_kwargs.get('proxies', None)):
            yield committee.all_field_values()

    def _get_committees(self, proxies):
        return Committee.get_all(proxies=proxies)


class ActiveCommitteesResource(CommitteesResource):

    def _get_committees(self, proxies):
        return Committee.get_all_active_committees(has_portal_link=False, proxies=proxies)


class MainCommitteesResource(CommitteesResource):

    def _get_committees(self, proxies):
        return Committee.get_all_active_committees(has_portal_link=True, proxies=proxies)


class CommitteeMeeting(BaseKnessetDataServiceFunctionObject):
    SERVICE_NAME = "committees"
    METHOD_NAME = "CommitteeAgendaSearch"

    # the primary key of committee meetings
    id = KnessetDataServiceSimpleField('Committee_Agenda_id', 'integer')

    # id of the committee (linked to Committee object)
    committee_id = KnessetDataServiceSimpleField('Committee_Agenda_committee_id', 'integer')

    # date/time when the meeting started
    datetime = KnessetDataServiceSimpleField('committee_agenda_date', 'datetime')

    # title of the meeting
    title = KnessetDataServiceSimpleField('title', 'string')
    # seems like in some committee meetings, the title field is empty, in that case title can be taken from this field
    session_content = KnessetDataServiceSimpleField('committee_agenda_session_content', 'string')

    # url to download the protocol
    url = KnessetDataServiceSimpleField('url', 'string')

    # a CommitteeMeetingProtocol object which allows to get data from the protocol
    # because parsing the protocol requires heavy IO and processing - we provide it as a generator
    # see tests/test_meetings.py for usage example
    protocol = KnessetDataServiceLambdaField(lambda obj, entry:
                                             CommitteeMeetingProtocol.get_from_url(obj.url, proxies=obj._proxies)
                                             if obj.url else None)

    # this seems like a shorter name of the place where meeting took place
    location = KnessetDataServiceSimpleField('committee_location', 'string')

    # this looks like a longer field with the specific details of where the meeting took place
    place = KnessetDataServiceSimpleField('Committee_Agenda_place', 'string')

    # date/time when the meeting ended - this is not always available, in some meetings it's empty
    meeting_stop = KnessetDataServiceSimpleField('meeting_stop', 'string')

    ### following fields seem less interesting ###
    agenda_canceled = KnessetDataServiceSimpleField('Committee_Agenda_canceled')
    agenda_sub = KnessetDataServiceSimpleField('Committee_agenda_sub')
    agenda_associated = KnessetDataServiceSimpleField('Committee_agenda_associated')
    agenda_associated_id = KnessetDataServiceSimpleField('Committee_agenda_associated_id')
    agenda_special = KnessetDataServiceSimpleField('Committee_agenda_special')
    agenda_invited1 = KnessetDataServiceSimpleField('Committee_agenda_invited1')
    agenda_invite = KnessetDataServiceSimpleField('sd2committee_agenda_invite')
    note = KnessetDataServiceSimpleField('Committee_agenda_note')
    start_datetime = KnessetDataServiceSimpleField('StartDateTime')
    topid_id = KnessetDataServiceSimpleField('Topic_ID')
    creation_date = KnessetDataServiceSimpleField('Date_Creation')
    streaming_url = KnessetDataServiceSimpleField('streaming_url')
    meeting_start = KnessetDataServiceSimpleField('meeting_start')
    is_paused = KnessetDataServiceSimpleField('meeting_is_paused')
    date_order = KnessetDataServiceSimpleField('committee_date_order')
    date = KnessetDataServiceSimpleField('committee_date')
    day = KnessetDataServiceSimpleField('committee_day')
    month = KnessetDataServiceSimpleField('committee_month')
    material_id = KnessetDataServiceSimpleField('material_id')
    material_committee_id = KnessetDataServiceSimpleField('material_comittee_id')
    material_expiration_date = KnessetDataServiceSimpleField('material_expiration_date')
    material_hour = KnessetDataServiceSimpleField('committee_material_hour')
    old_url = KnessetDataServiceSimpleField('OldUrl')
    background_page_link = KnessetDataServiceSimpleField('CommitteeBackgroundPageLink')
    agenda_invited = KnessetDataServiceSimpleField('Committee_agenda_invited')

    @classmethod
    def get(cls, committee_id, from_date, to_date=None, proxies=None):
        """
        # example usage:
        >>> from datetime import datetime
        # get all meetings of committee 1 from Jan 01, 2016
        >>> CommitteeMeeting.get(1, datetime(2016, 1, 1))
        # get all meetings of committee 2 from Feb 01, 2015 to Feb 20, 2015
        >>> CommitteeMeeting.get(2, datetime(2015, 2, 1), datetime(2015, 2, 20))
        """
        params = {
            "CommitteeId": "'%s'" % committee_id,
            "FromDate": "'%sT00:00:00'" % from_date.strftime('%Y-%m-%d')
        }
        if to_date:
            params["ToDate"] = "'%sT00:00:00'" % to_date.strftime('%Y-%m-%d')
        return super(CommitteeMeeting, cls).get(params, proxies=proxies)


class CommitteeMeetingsResource(CsvResource):
    """
    Committee meetings csv resource - generates the csv with committee meetings for the last DAYS days (default 5 days)
    if __init__ gets a meetings protocols resource it will pass every meeting over to that resource to save the corresponding protocol
    """

    def __init__(self, name, parent_datapackage_path, protocols_resource=None):
        self._protocols_resource = protocols_resource
        json_table_schema = CommitteeMeeting.get_json_table_schema()
        super(CommitteeMeetingsResource, self).__init__(name, parent_datapackage_path, json_table_schema)

    def _data_generator(self, **make_kwargs):
        proxies = make_kwargs.get('proxies', None)
        fromdate = datetime.datetime.now().date() - datetime.timedelta(days=make_kwargs.get('days', 5))
        if make_kwargs.get("committee_ids", None):
            committee_ids = make_kwargs["committee_ids"]
        else:
            committee_ids = (committee.id
                             for committee
                             in Committee.get_all_active_committees(has_portal_link=False,
                                                                    proxies=proxies))
        for committee_id in committee_ids:
            for meeting in CommitteeMeeting.get(committee_id, fromdate, proxies=proxies):
                if self._protocols_resource:
                    self._protocols_resource.save_meeting(committee_id, meeting)
                yield meeting.all_field_values()


class CommitteeMeetingProtocolsResource(BaseResource):

    def __init__(self, name, parent_datapackage_path):
        super(CommitteeMeetingProtocolsResource, self).__init__(name, parent_datapackage_path)
        self.descriptor.update({
            "path": [],
            "description": "protocol file names are in the following format: <COMMITTEE_ID>/<MEETING_ID>.txt"
        })

    def save_meeting(self, committee_id, meeting):
        if meeting.protocol:
            if not os.path.exists(self._base_path):
                os.mkdir(self._base_path)
            committee_path = os.path.join(self._base_path, str(committee_id))
            if not os.path.exists(committee_path):
                os.mkdir(committee_path)
            path = os.path.join(committee_path, "{}.txt".format(meeting.id))
            with meeting.protocol as protocol:
                with open(path, 'w') as f:
                    f.write(protocol.text.encode('utf8'))
            self.descriptor["path"].append(path)


class CommitteeMeetingsDatapackage(BaseDatapackage):
    name = "knesset-data-dataservice-committee-meetings"

    def _load_resources(self, descriptor, base_path):
        self.meeting_protocols_resource = CommitteeMeetingProtocolsResource("committee-meeting-protocols", base_path)
        self.committee_meetings_resource = CommitteeMeetingsResource("committee-meetings", base_path, self.meeting_protocols_resource)
        descriptor["resources"] = [
            self.committee_meetings_resource,
            self.meeting_protocols_resource
        ]
        return super(CommitteeMeetingsDatapackage, self)._load_resources(descriptor, base_path)
