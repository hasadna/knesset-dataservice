# encoding: utf-8
from knesset_data_django.common.exceptions import TooManyObjectsException
from knesset_data.dataservice.committees import Committee as DataserviceCommittee
from ...common.scrapers.base_scraper import BaseScraper
from ..models import Committee


class CommitteesScraper(BaseScraper):

    def _get_all_active_dataservice_committees(self, has_portal_link):
        return DataserviceCommittee.get_all_active_committees(has_portal_link=has_portal_link)

    def _update_or_create_from_dataservice(self, dataservice_committee):
        """
        updates or create a committee object based on dataservice_committee
        :param dataservice_committee: dataservice committee object
        :return: tuple(committee, created) the updated or created committee model object and True/False if it was created
        """
        committee_id = dataservice_committee.id
        committee_model_data = {
            "name": dataservice_committee.name,
            "knesset_type_id": dataservice_committee.type_id,
            "knesset_parent_id": dataservice_committee.parent_id,
            "name_eng": dataservice_committee.name_eng,
            "name_arb": dataservice_committee.name_arb,
            "start_date": dataservice_committee.begin_date,
            "end_date": dataservice_committee.end_date,
            "knesset_description": dataservice_committee.description,
            "knesset_description_eng": dataservice_committee.description_eng,
            "knesset_description_arb": dataservice_committee.description_arb,
            "knesset_note": dataservice_committee.note,
            "knesset_note_eng": dataservice_committee.note_eng,
            "knesset_portal_link": dataservice_committee.portal_link,
        }
        committee_qs = Committee.objects.filter(knesset_id=committee_id)
        committee_qs_count = committee_qs.count()
        if committee_qs_count == 1:
            committee = committee_qs.first()
            [setattr(committee, k, v) for k, v in committee_model_data.iteritems()]
            created = False
        elif committee_qs_count == 0:
            committee = Committee(id=committee_id, **committee_model_data)
            created = True
        else:
            raise TooManyObjectsException()
        committee.save()
        return committee, created

    def scrape_active_committees(self):
        """
        updates the active committees in the DB
        creates new committees / updates data for existing committees
        :return: generator of return values from _update_or_create_from_dataservice
        """
        return (self._update_or_create_from_dataservice(dataservice_committee)
                for dataservice_committee
                in self._get_all_active_dataservice_committees(has_portal_link=False))
