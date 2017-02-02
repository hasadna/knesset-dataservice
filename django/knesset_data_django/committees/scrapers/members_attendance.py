from ...common.scrapers.base_scraper import BaseScraper
from .. import members_by_presence
from ..models import Committee
from ...mks.models import Member, Knesset


class MembersAttendanceScraper(BaseScraper):

    def _get_member_ids(self):
        return Member.objects.filter(
            current_party__knesset=Knesset.objects.current_knesset()
            ).values_list('pk', flat=True)

    def _get_committee_members_attendance(self, committee, member_ids, from_date):
        return ((member, member.meetings_percentage)
                for member
                in members_by_presence(committee, ids=member_ids, from_date=from_date))

    def scrape(self, from_date):
        member_ids = self._get_member_ids()
        return ((committee, self._get_committee_members_attendance(committee, member_ids, from_date))
                for committee
                in Committee.objects.exclude(type='plenum').exclude(hide=True))
