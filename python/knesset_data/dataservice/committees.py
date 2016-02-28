# -*- coding: utf-8 -*-
import logging

from base import (
    BaseKnessetDataServiceCollectionObject, BaseKnessetDataServiceFunctionObject,
    KnessetDataServiceSimpleField, KnessetDataServiceLambdaField
)
from knesset_data.protocols.committee import CommitteeMeetingProtocol

logger = logging.getLogger('knesset_data.dataservice.committees')

IS_COMMITTEE_ACTIVE = 'committee_end_date eq null'
COMMITTEE_HAS_PORTAL_LINK = 'committee_portal_link ne null'


class Committee(BaseKnessetDataServiceCollectionObject):
    SERVICE_NAME = "committees"
    METHOD_NAME = "View_committee"
    DEFAULT_ORDER_BY_FIELD = "id"

    id = KnessetDataServiceSimpleField('committee_id')
    type_id = KnessetDataServiceSimpleField('committee_type_id')
    parent_id = KnessetDataServiceSimpleField('committee_parent_id')
    name = KnessetDataServiceSimpleField('committee_name')
    name_eng = KnessetDataServiceSimpleField('committee_name_eng')
    name_arb = KnessetDataServiceSimpleField('committee_name_arb')
    begin_date = KnessetDataServiceSimpleField('committee_begin_date')
    end_date = KnessetDataServiceSimpleField('committee_end_date')
    description = KnessetDataServiceSimpleField('committee_desc')
    description_eng = KnessetDataServiceSimpleField('committee_desc_eng')
    description_arb = KnessetDataServiceSimpleField('committee_desc_arb')
    note = KnessetDataServiceSimpleField('committee_note')
    note_eng = KnessetDataServiceSimpleField('committee_note_eng')
    portal_link = KnessetDataServiceSimpleField('committee_portal_link')

    @classmethod
    def get_all_active_committees(cls, has_portal_link=True):
        if has_portal_link:
            query = ' '.join((IS_COMMITTEE_ACTIVE, 'and', COMMITTEE_HAS_PORTAL_LINK))
        else:
            query = IS_COMMITTEE_ACTIVE
        params = {'$filter': query}
        return cls._get_all_pages(cls._get_url_base(), params)


class CommitteeMeeting(BaseKnessetDataServiceFunctionObject):
    SERVICE_NAME = "committees"
    METHOD_NAME = "CommitteeAgendaSearch"

    # the primary key of committee meetings
    id = KnessetDataServiceSimpleField('Committee_Agenda_id')

    # id of the committee (linked to Committee object)
    committee_id = KnessetDataServiceSimpleField('Committee_Agenda_committee_id')

    # date/time when the meeting started
    datetime = KnessetDataServiceSimpleField('committee_agenda_date')

    # title of the meeting
    title = KnessetDataServiceSimpleField('title')

    # url to download the protocol
    url = KnessetDataServiceSimpleField('url')

    # a CommitteeMeetingProtocol object which allows to get data from the protocol
    # because parsing the protocol requires heavy IO and processing - we provide it as a generator
    # see tests/test_meetings.py for usage example
    protocol = KnessetDataServiceLambdaField(
        lambda obj, entry: CommitteeMeetingProtocol.get_from_url(obj.url))

    # this seems like a shorter name of the place where meeting took place
    location = KnessetDataServiceSimpleField('committee_location')

    # this looks like a longer field with the specific details of where the meeting took place
    place = KnessetDataServiceSimpleField('Committee_Agenda_place')

    # date/time when the meeting ended
    meeting_stop = KnessetDataServiceSimpleField('meeting_stop')

    ### following fields seem less interesting ###
    session_content = KnessetDataServiceSimpleField('committee_agenda_session_content')
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
    def get(cls, committee_id, from_date, to_date=None):
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
        return super(CommitteeMeeting, cls).get(params)
