# -*- coding: utf-8 -*-
from django.test import TestCase
from ..committees import CommitteesScraper
from ...models import Committee
from ....common.testing.mocks import MockDataserviceObject
from knesset_data.dataservice.committees import Committee as DataserviceCommittee
from datetime import datetime


class MockCommitteesScraper(CommitteesScraper):

    def __init__(self, mock_active_committees, **kwargs):
        super(MockCommitteesScraper, self).__init__(**kwargs)
        self._mock_active_committees = mock_active_committees

    def _mock_committee_has_portal_link(self, committee):
        return "portal_link" in committee

    def _get_all_active_dataservice_committees(self, has_portal_link):
        return [MockDataserviceObject(DataserviceCommittee, **committee)
                for committee in self._mock_active_committees
                if self._mock_committee_has_portal_link(committee) == has_portal_link]


class CommitteesScraperTestCase(TestCase):
    longMessage = True  # works better when using custom assertion messages

    def assertCommittees(self, dataservice_active_committees, expected_return_values, expected_model_committees):
        Committee.objects.all().delete()
        self.assertEqual(Committee.objects.all().count(), 0)
        return_values_iterator = iter(expected_return_values)
        for committee, created in MockCommitteesScraper(dataservice_active_committees).scrape_active_committees():
            expected_values = return_values_iterator.next()
            assertion_msg = "committee_id={}".format(committee.id)
            self.assertEqual(committee.id, expected_values['committee_id'], assertion_msg)
            self.assertEqual(created, expected_values['created'], assertion_msg)
        self.assertEqual(Committee.objects.all().count(), 2)
        for expected_committee in expected_model_committees:
            actual_committee = Committee.objects.get(id=expected_committee["id"])
            for attr_name, expected_value in expected_committee.iteritems():
                assertion_msg = 'committee_id={}, attr_name={}'.format(expected_committee["id"], attr_name)
                self.assertEqual(getattr(actual_committee, attr_name), expected_value, assertion_msg)

    def test(self):
        self.assertCommittees(dataservice_active_committees=[{"id": 1,
                                                              "name": u"ועדת הכספספים",
                                                              "type_id": 1,
                                                              "parent_id": None,
                                                              "name_eng": u"name",
                                                              "name_arb": u"اسم",
                                                              "begin_date": datetime(1950, 1, 1, 0, 0),
                                                              "end_date": None,
                                                              "description": u"תיאור",
                                                              "description_eng": u"description",
                                                              "description_arb": u"وصف",
                                                              "note": u"הערה",
                                                              "note_eng": u"note"},
                                                             {"id": 2,
                                                              "name": u"ועדת הכלכלכלכלה"}],
                              expected_return_values=[{"committee_id": 1, "created": True},
                                                      {"committee_id": 2, "created": True}],
                              expected_model_committees=[{"id": 1,
                                                          "name": u"ועדת הכספספים",
                                                          "knesset_type_id": 1,
                                                          "knesset_parent_id": None,
                                                          "name_eng": u"name",
                                                          "name_arb": u"اسم",
                                                          "start_date": datetime(1950, 1, 1, 0, 0),
                                                          "end_date": None,
                                                          "knesset_description": u"תיאור",
                                                          "knesset_description_eng": u"description",
                                                          "knesset_description_arb": u"وصف",
                                                          "knesset_note": u"הערה",
                                                          "knesset_note_eng": u"note"},
                                                         {"id": 2,
                                                          "name": u"ועדת הכלכלכלכלה"}])
