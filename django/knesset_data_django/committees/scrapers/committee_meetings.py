from ...common.scrapers.base_scraper import BaseScraper
from knesset_data.dataservice.committees import CommitteeMeeting as DataserviceCommitteeMeeting
from ...common import hebrew_strftime
from ..meetings import reparse_protocol
from ...mks.utils import get_all_mk_names
from ..models import Committee, CommitteeMeeting


class CommitteeMeetingsScraper(BaseScraper):

    def _get_meetings(self, committee_id, from_date, to_date):
        return DataserviceCommitteeMeeting.get(committee_id, from_date, to_date)

    def _has_existing_meeting(self, dataservice_meeting):
        qs = CommitteeMeeting.objects.filter(
            committee__knesset_id=dataservice_meeting.committee_id)
        if qs.filter(knesset_id=dataservice_meeting.id).exists():
            # there is an existing meeting with the same src knesset id
            self.logger.debug('there is an existing meeting with same src knesset id ({})'.format(dataservice_meeting.id))
            return True
        elif qs.filter(date=dataservice_meeting.datetime, knesset_id=None).exists():
            # there is an existing meeting on the same date but without a src knesset id
            # this meeting was scraped before the knesset-data improvements so we can't know for sure
            # if it's not the same meeting
            # for this case we assume it's the same meeting to prevent duplicated meetings
            self.logger.debug('there is an existing meeting on same date ({}) but without id'.format(dataservice_meeting.datetime))
            return True
        else:
            # no existing meeting
            return False

    def _reparse_protocol(self, meeting):
        mks, mk_names = get_all_mk_names()
        reparse_protocol(meeting, mks=mks, mk_names=mk_names)

    def _create_meeting(self, dataservice_meeting, committee):
        meeting_model_data = self._get_committee_meeting_fields_from_dataservice(dataservice_meeting)
        meeting = CommitteeMeeting.objects.create(committee=committee,
                                                                     **meeting_model_data)
        self.logger.debug('created meeting {}'.format(meeting.pk))
        self._reparse_protocol(meeting)
        return meeting

    def _update_meeting(self, committee, dataservice_meeting):
        if not dataservice_meeting.url:
            return (dataservice_meeting, None, "missing meeting url")
        elif self._has_existing_meeting(dataservice_meeting):
            return (dataservice_meeting, None, "meeting exists in DB")
        else:
            return (dataservice_meeting, self._create_meeting(dataservice_meeting, committee), "")

    def _update_committee_meetings(self, committee, from_date, to_date):
        return (self._update_meeting(committee, dataservice_meeting)
                for dataservice_meeting in self._get_meetings(committee.knesset_id,
                                                              from_date, to_date))

    def _get_committees(self, committee_ids):
        return Committee.objects.filter(knesset_id__gt=0, pk__in=committee_ids)

    def _get_committee_meeting_fields_from_dataservice(self, dataservice_meeting):
        meeting_model_data = {
            "date_string": hebrew_strftime(dataservice_meeting.datetime, fmt=u'%d/%m/%Y'),
            "date": dataservice_meeting.datetime,
            "topics": dataservice_meeting.title,
            "datetime": dataservice_meeting.datetime,
            "knesset_id": dataservice_meeting.id,
            "src_url": dataservice_meeting.url,
        }
        if meeting_model_data['topics'] is None or meeting_model_data['topics'] == '':
            meeting_model_data['topics'] = dataservice_meeting.session_content
        return meeting_model_data

    def scrape(self, from_date, to_date, committee_ids=None):
        if not committee_ids:
            committee_ids = Committee.objects.all().values_list('pk', flat=True)
        return ((committee, self._update_committee_meetings(committee, from_date, to_date))
                for committee in self._get_committees(committee_ids))
